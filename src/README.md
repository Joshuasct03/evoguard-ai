# 🛡️ EvoGuard AI
**Version-Aware API Change Intelligence & Migration Assistant**

## 📖 Overview
Large Language Models (LLMs) suffer from severe "context-memory conflict" when answering software engineering queries. When libraries update, LLMs frequently hallucinate outdated migration guidance based on their static parametric memory, or struggle to interpret conflicting documentation chunks in standard Flat RAG architectures.

**EvoGuard AI** is a specialized Retrieval-Augmented Generation (RAG) system designed to solve this. By implementing strict metadata-filtered retrieval, structured lifecycle extraction, and deterministic semantic version reasoning, EvoGuard guarantees mathematically sound migration advice across evolving APIs.

## 🏗️ Architecture
EvoGuard bypasses LLM hallucinations by separating semantic understanding from mathematical reasoning:
1. **Version-Aware Retrieval:** FAISS vector store strictly filters chunks using API library and version metadata.
2. **Structured Extraction (Gemini + Pydantic):** The LLM is restricted to reading the retrieved context and extracting API lifecycle bounds (deprecation/removal dates) into a rigid JSON schema.
3. **Deterministic Reasoning:** A Python logic engine evaluates the user's environment version against the extracted JSON timeline using `packaging.version`, ensuring flawless semantic boundary math (e.g., knowing `1.9.0` < `2.0.0`).
4. **Abstention Rule:** If insufficient evidence is found in the context, the system safely abstains rather than hallucinating an answer.

## 🚀 Features
* **Interactive Streamlit UI:** Clean web interface to query API safety across versions.
* **Automated Evaluation Benchmark:** Built-in testing suite to measure system accuracy against real-world library evolution (PyTorch, NumPy, Pandas).
* **Multi-Library Support:** Context boundaries isolated per library to prevent cross-contamination.

## 🛠️ Tech Stack
* **Language:** Python
* **AI/LLM:** LangChain, Google Gemini (`gemini-3.6-flash`, `gemini-embedding-001`)
* **Vector Store:** FAISS
* **Frontend:** Streamlit
* **Testing:** Pytest

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/evoguard-ai.git](https://github.com/YOUR_USERNAME/evoguard-ai.git)
   cd evoguard-ai