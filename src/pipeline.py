import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from extraction import extract_api_info
from version_logic import evaluate_api_safety

load_dotenv()

def run_evoguard(query: str, target_version: str, target_library: str = None) -> dict:
    """
    Executes the EvoGuard version-aware pipeline:
    1. Version-aware retrieval of evidence
    2. LLM-based structured lifecycle extraction
    3. Deterministic Python version comparison
    4. Evidence-backed migration recommendation
    """
    print(f"\n[Query]: {query}")
    print(f"[Target Version]: {target_version} | [Library]: {target_library or 'Any'}")
    
    # 1. Load Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    try:
        vector_store = FAISS.load_local(os.path.join(os.path.dirname(__file__), "faiss_index"), embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print("Error: Vector store not found. Please run ingestion.py first.")
        return {"status": "error", "message": str(e)}

    # 2. Retrieve Relevant Evidence
    search_kwargs = {}
    if target_library:
        search_kwargs["filter"] = {"library": target_library.lower()}
        
    # FIX 1: Increase k=3 to fetch both deprecation and removal documents
    docs = vector_store.similarity_search(query, k=3, **search_kwargs)
    
    if not docs:
        result = {
            "status": "abstained",
            "guidance": "Insufficient evidence to determine the API status for the requested version.",
            "evidence": None,
            "structured_data": None
        }
        _print_result(result)
        return result
        
    # FIX 2: Combine all retrieved chunks so Gemini sees the complete timeline
    # FIX 2: Inject metadata into the context text so Gemini knows the timeline
    context_text = "\n".join([f"- [Library: {d.metadata.get('library')} v{d.metadata.get('version')}]: {d.page_content}" for d in docs])
    print(f"[Retrieved Context]: Pulled {len(docs)} documents to build lifecycle timeline.")
    
    # 3. Structured Extraction using Gemini
    # 3. Structured Extraction using Gemini
    try:
        extracted_data = extract_api_info(context_text)
    except Exception as e:
        error_msg = f"Extraction Failed: {str(e)}"
        print(f"\n[DEBUG ERROR] {error_msg}")
        result = {
            "status": "extraction_error",
            "guidance": error_msg,
            "evidence": context_text,
            "structured_data": None
        }
        _print_result(result)
        return result
        
    # 4. Deterministic Version Evaluation
    guidance = evaluate_api_safety(extracted_data, target_version)
    
    result = {
        "status": "success",
        "guidance": guidance,
        "evidence": context_text,
        "structured_data": extracted_data
    }
    _print_result(result)
    return result

def _print_result(res: dict):
    print("\n=============================================")
    print("           EVOGUARD ANALYSIS RESULT          ")
    print("=============================================")
    print(f"Guidance: {res['guidance']}")
    if res["evidence"]:
        print(f"\nEvidence:\n{res['evidence']}")
    print("=============================================\n")

if __name__ == "__main__":
    # Testing the exact query that just failed
    print("\n--- TEST: torch.lstsq on PyTorch 1.8.0 ---")
    run_evoguard(query="Can I use torch.lstsq to solve linear equations?", target_version="1.8.0", target_library="torch")