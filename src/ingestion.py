import os
import glob
import json
import time
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def map_filename_to_library(filename: str) -> str:
    """Extracts the library name from the research dataset filenames."""
    name = os.path.basename(filename).lower()
    if 'pytorch' in name: return 'torch'
    if 'numpy' in name: return 'numpy'
    if 'pandas' in name: return 'pandas'
    if 'scipy' in name: return 'scipy'
    if 'sklearn' in name: return 'sklearn'
    if 'matplotlib' in name: return 'matplotlib'
    if 'jax' in name: return 'jax'
    if 'keras' in name: return 'keras'
    return 'unknown'

def build_massive_knowledge_base(data_dir: str = "../data/benchmark_dataset", index_output_path: str = "faiss_index"):
    print(f"Scanning directory: {data_dir} for JSON files...")
    
    # Grab all JSON files in the directory
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}. Did you put them in the right folder?")

    documents = []
    for file_path in json_files:
        library_name = map_filename_to_library(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                entries = json.load(f)
            except Exception as e:
                print(f"Skipping {file_path} due to parsing error: {e}")
                continue
                
        for entry in entries:
            # Map the research schema to our fields
            api_name = entry.get("old_name") or entry.get("api_name", "Unknown API")
            version = entry.get("version", "Unknown")
            update_info = entry.get("update_info", "")
            update_desc = entry.get("update_description", "")
            code_ex = entry.get("code_example", "")
            
            # Combine all fields into a rich text chunk for Gemini to read
            content = f"API: {api_name}\nStatus: {update_info}\nDescription: {update_desc}"
            if code_ex:
                content += f"\nMigration Example: {code_ex}"

            doc = Document(
                page_content=content,
                metadata={
                    "library": library_name,
                    "version": str(version),
                    "api": api_name
                }
            )
            documents.append(doc)
            
    print(f"-> Parsed {len(documents)} total documentation entries across {len(json_files)} files.")
    print("Generating embeddings using Google Gemini (batching with rate-limit handling)...")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # 1. Google's API strictly limits batches to 100 requests. We use 90 for safety.
    batch_size = 90
    vector_store = None
    
    # 2. Iterate through the massive dataset in chunks
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        print(f"   -> Embedding batch {(i // batch_size) + 1} (Processing {len(batch)} documents)...")
        
        # 3. If it is the first batch, initialize the FAISS index
        if vector_store is None:
            vector_store = FAISS.from_documents(batch, embeddings)
        # 4. If the index exists, just append the new documents
        else:
            vector_store.add_documents(batch)
            
        # 5. Sleep for 60 seconds to reset the API RPM quota (unless it's the last batch)
        if i + batch_size < len(documents):
            print("      [Waiting 60 seconds to respect API free-tier rate limits...]")
            time.sleep(60)
            
    vector_store.save_local(index_output_path)
    print(f"\nSuccess: Massive research vector store saved to '{index_output_path}'.")

if __name__ == "__main__":
    build_massive_knowledge_base()