import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from extraction import extract_api_info
from version_logic import evaluate_api_safety
from auto_fix import generate_code_fix  # <-- Import the auto-fix agent

load_dotenv()

def run_evoguard(query: str, target_version: str, target_library: str = None, user_code: str = None) -> dict:
    """
    Executes the EvoGuard version-aware pipeline:
    1. Version-aware retrieval of evidence
    2. LLM-based structured lifecycle extraction
    3. Deterministic Python version comparison
    4. Evidence-backed migration recommendation & automated code refactoring
    """
    print(f"\n[Query]: {query}")
    print(f"[Target Version]: {target_version} | [Library]: {target_library or 'Any'}")
    
    # 1. Load Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    try:
        vector_store = FAISS.load_local(os.path.join(os.path.dirname(__file__), "faiss_index"), embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print("Error: Vector store not found. Please run ingestion.py first.")
        return {"status": "error", "message": str(e), "fix": None}

    # 2. Retrieve Relevant Evidence
    search_kwargs = {}
    if target_library:
        search_kwargs["filter"] = {"library": target_library.lower()}
        
    docs = vector_store.similarity_search(query, k=3, **search_kwargs)
    
    if not docs:
        result = {
            "status": "abstained",
            "guidance": "Insufficient evidence to determine the API status for the requested version.",
            "evidence": None,
            "structured_data": None,
            "fix": None
        }
        return result
        
    context_text = "\n".join([f"- [Library: {d.metadata.get('library')} v{d.metadata.get('version')}]: {d.page_content}" for d in docs])
    
    # 3. Structured Extraction using Gemini
    try:
        extracted_data = extract_api_info(context_text)
        
        # --- ROBUSTNESS FIX: Normalize extracted_data if it's a list or Pydantic model ---
        if isinstance(extracted_data, list):
            extracted_data = extracted_data[0] if extracted_data else {}
        if hasattr(extracted_data, "model_dump"):
            extracted_data = extracted_data.model_dump()
        elif hasattr(extracted_data, "dict"):
            extracted_data = extracted_data.dict()
        # -------------------------------------------------------------------------------

    except Exception as e:
        error_msg = f"Extraction Failed: {str(e)}"
        result = {
            "status": "extraction_error",
            "guidance": error_msg,
            "evidence": context_text,
            "structured_data": None,
            "fix": None
        }
        return result
    # 4. Deterministic Version Evaluation
    guidance = evaluate_api_safety(extracted_data, target_version)
    
    # 5. Generative Auto-Fix (Triggered if DANGER or WARNING, and user provided code)
    fix = None
    if ("DANGER" in guidance or "WARNING" in guidance) and user_code:
        try:
            fix = generate_code_fix(user_code, context_text, guidance)
        except Exception as e:
            fix = f"Could not generate code fix: {str(e)}"

    result = {
        "status": "success",
        "guidance": guidance,
        "evidence": context_text,
        "structured_data": extracted_data,
        "fix": fix
    }
    return result