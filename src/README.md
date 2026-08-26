# 🛡️ EvoGuard AI
> **Version-Aware API Change Intelligence & Generative Migration Assistant**

EvoGuard AI is an advanced static analysis and automated refactoring tool designed to protect Python codebases from API deprecations and breaking changes. By combining a local vector database of academic-grade API lifecycle benchmarks with Abstract Syntax Tree (AST) parsing and deterministic version math, EvoGuard identifies vulnerable code and uses generative AI to automatically rewrite it before it reaches production.

## 🚀 Key Features

*   **Version-Aware RAG Engine:** Queries a FAISS vector store containing 350+ research-grade API deprecation entries to retrieve precise timeline evidence.
*   **Deterministic Safety Math:** Bypasses LLM hallucination by extracting lifecycle data into a strict JSON schema (via LangChain and Pydantic) and mathematically evaluating version boundaries.
*   **Generative Auto-Fix Agent:** Automatically refactors deprecated code snippets to the updated standard using Google Gemini.
*   **Batch AST Scanning:** Parses complete `.py` files to isolate function calls, automatically evaluating entire scripts without executing them.
*   **CI/CD Pipeline Integration:** Includes a native CLI that returns a `sys.exit(1)` upon detecting `DANGER`-level API conflicts, allowing it to seamlessly break the build in GitHub Actions or pre-commit hooks.
*   **Interactive Dual-Tab UI:** A Streamlit frontend for single-query investigation and drag-and-drop file batch scanning.

## 🛠️ Tech Stack

*   **Core Logic:** Python, `ast` (Abstract Syntax Trees), `packaging.version`
*   **AI & Embeddings:** Google Gemini API (`gemini-3.6-flash`, `gemini-embedding-001`)
*   **Retrieval & Orchestration:** LangChain, FAISS (Vector Store)
*   **Interface:** Streamlit (Web UI), `argparse` (CLI)

## 📁 Repository Structure

```text
evoguard-ai/
├── data/
│   └── benchmark_dataset/     # JSON files containing API lifecycle data
├── src/
│   ├── app.py                 # Streamlit frontend
│   ├── cli.py                 # Command-line interface for CI/CD
│   ├── pipeline.py            # Main orchestration engine
│   ├── ingestion.py           # Rate-limited FAISS batch embedding script
│   ├── extraction.py          # LLM schema extraction with fallback parser
│   ├── version_logic.py       # Deterministic version comparison
│   ├── auto_fix.py            # Generative code refactoring agent
│   ├── scanner.py             # AST parsing for batch file processing
│   └── faiss_index/           # Local vector database
└── README.md

⚙️ Getting Started
1. Clone and Configure
Bash
git clone [https://github.com/yourusername/evoguard-ai.git](https://github.com/yourusername/evoguard-ai.git)
cd evoguard-ai
# Create your .venv and install dependencies (langchain, faiss-cpu, streamlit, google-generativeai, etc.)

2. Set up Environment Variables
Create a .env file in the root directory and add your Google API key:
Code snippet
GOOGLE_API_KEY="your_api_key_here"

3. Run the UI
Bash
cd src
python -m streamlit run app.py

4. Run the CI/CD CLI Scanner
Bash
python cli.py path/to/your/script.py --version 2.7.0 --library torch