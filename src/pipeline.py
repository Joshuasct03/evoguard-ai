import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Import our custom modules
from extraction import extract_api_info
from version_logic import evaluate_api_safety

load_dotenv()

def run_evoguard(query: str, target_version: str):
    print(f"\n[1] User Query: {query}")
    print(f"[1] Target Environment Version: {target_version}")
    
    # Phase 1: Retrieval
    print("\n[2] Retrieving evidence from vector store...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    try:
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print("Error: Could not load vector store. Run ingestion.py first!")
        return

    # We fetch the top document. (In a full production app, you might filter by library name here)
    docs = vector_store.similarity_search(query, k=1)
    
    # The Abstention Rule: If no evidence is found, do not guess.
    if not docs:
        print("\n--- EvoGuard Final Answer ---")
        print("Insufficient evidence to determine the API status for the requested version.")
        return
        
    context_text = docs[0].page_content
    print(f"    -> Evidence found: {context_text[:50]}...")
    
    # Phase 2: Structured Extraction
    print("\n[3] LLM extracting structured API lifecycle data...")
    try:
        extracted_data = extract_api_info(context_text)
    except Exception as e:
        print("\n--- EvoGuard Final Answer ---")
        print("Insufficient evidence to determine the API status for the requested version.")
        return
    
    # Phase 3: Deterministic Version Reasoning
    print("\n[4] Python reasoning engine applying deterministic version math...")
    final_guidance = evaluate_api_safety(extracted_data, target_version)
    
    # Final Evidence-Backed Output
    print("\n=============================================")
    print("           EVOGUARD FINAL ANSWER             ")
    print("=============================================")
    print(f"Guidance: {final_guidance}")
    print(f"\nEvidence: \"{context_text}\"")
    print("=============================================\n")

if __name__ == "__main__":
    # Simulating a developer asking about the old API while working in version 1.9
    test_query = "What is the status of old_function?"
    run_evoguard(test_query, target_version="1.9")