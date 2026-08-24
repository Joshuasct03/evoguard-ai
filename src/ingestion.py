import os
import json
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def build_knowledge_base(data_file_path: str = "../data/api_docs.json", index_output_path: str = "faiss_index"):
    print(f"Loading official API evolution data from: {data_file_path}")
    
    if not os.path.exists(data_file_path):
        raise FileNotFoundError(f"Dataset file not found: {data_file_path}")
        
    with open(data_file_path, "r", encoding="utf-8") as f:
        raw_entries = json.load(f)
        
    documents = []
    for entry in raw_entries:
        doc = Document(
            page_content=entry["content"],
            metadata={
                "library": entry["library"].lower(),
                "version": str(entry["version"]),
                "doc_type": entry.get("doc_type", "release_notes"),
                "api": entry["api"]
            }
        )
        documents.append(doc)
        
    print(f"-> Parsed {len(documents)} documentation entries across libraries: "
          f"{set(d.metadata['library'] for d in documents)}")
    
    print("Generating embeddings using Google Gemini...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.from_documents(documents, embeddings)
    
    vector_store.save_local(index_output_path)
    print(f"Success: Real API evolution vector store saved to '{index_output_path}'.")

if __name__ == "__main__":
    build_knowledge_base()