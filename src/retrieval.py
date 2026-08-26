import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

load_dotenv()

def retrieve_and_answer(query, target_version):
    print(f"\nQuery: {query}")
    print(f"Target Version: {target_version}")
    
    # 1. Load the Embeddings and Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # 2. Version-Aware Retrieval (The Brain of EvoGuard)
    print("Searching vector store with strict version filtering...")
    docs = vector_store.similarity_search(
        query, 
        k=1, 
        filter={"version": target_version}
    )
    
    print(f"Retrieved {len(docs)} document(s) for version {target_version}.")
    if len(docs) > 0:
        print(f"Context snippet: {docs[0].page_content[:50]}...")
    
    # 3. Initialize the LLM (Gemini)
    print("Sending context and query to Gemini...")
    llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash", temperature=0)
    
    # 4. Create a basic QA chain and run it
    chain = load_qa_chain(llm, chain_type="stuff")
    response = chain.invoke({"input_documents": docs, "question": query}, return_only_outputs=True)
    
    print("\n--- EvoGuard LLM Answer ---")
    print(response["output_text"].strip())

if __name__ == "__main__":
    test_query = "Is the old_function API safe to use?"
    
    print("\n=============================================")
    print("TEST 1: Querying the library at Version 1.5")
    print("=============================================")
    retrieve_and_answer(test_query, target_version="1.5")
    
    print("\n=============================================")
    print("TEST 2: Querying the library at Version 1.8")
    print("=============================================")
    retrieve_and_answer(test_query, target_version="1.8")