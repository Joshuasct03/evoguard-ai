import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

# 1. Load the secret API key
load_dotenv()

def retrieve_and_answer(query):
    print(f"Query: {query}")
    
    # 2. Load the Embeddings and Vector Store
    # We set allow_dangerous_deserialization=True because we trust the local file we just created.
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # 3. Retrieve relevant chunks (Vector Search)
    print("Searching vector store for relevant documents...")
    docs = vector_store.similarity_search(query, k=1)
    print(f"Retrieved {len(docs)} document(s).")
    
    # 4. Initialize the LLM (Gemini)
    # We use temperature=0 for deterministic, factual reasoning.
    print("Sending context and query to Gemini...")
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
    
    # 5. Create a basic QA chain and run it
    chain = load_qa_chain(llm, chain_type="stuff")
    response = chain.invoke({"input_documents": docs, "question": query}, return_only_outputs=True)
    
    print("\n--- EvoGuard LLM Answer ---")
    print(response["output_text"].strip())

if __name__ == "__main__":
    # A test query simulating a developer upgrading their code
    test_query = "What happened to the old_function API and what should I use instead?"
    retrieve_and_answer(test_query)