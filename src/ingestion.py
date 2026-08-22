import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Load the secret API key from our .env file
load_dotenv()

def ingest_and_store(file_path):
    print(f"Loading document from: {file_path}")
    
    # 2. Ingest: Load the text file into memory
    loader = TextLoader(file_path)
    documents = loader.load()

    # 3. Chunk: Break the document into manageable pieces.
    # We use a slight overlap so we don't cut a sentence in half and lose its context.
    print("Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200, 
        chunk_overlap=20
    )
    chunks = text_splitter.split_documents(documents)
    print(f"-> Created {len(chunks)} chunk(s).")

    # 4. Embed & Store: Convert text to numerical vectors using Gemini and save to FAISS
    print("Generating embeddings and building FAISS vector store...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # 5. Save the database locally so we can search it later
    vector_store.save_local("faiss_index")
    print("Success! Vector store saved to the 'faiss_index' directory.")

if __name__ == "__main__":
    # Point the script to our dummy data file
    target_file = "../data/sample_doc.txt"
    ingest_and_store(target_file)