import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def generate_code_fix(broken_code: str, context_text: str, guidance: str) -> str:
    """
    Uses Gemini to rewrite broken code based on API lifecycle evidence and guidance.
    """
    prompt = PromptTemplate(
        input_variables=["broken_code", "context", "guidance"],
        template=(
            "You are an expert AI refactoring assistant. A developer is trying to use an evolving API "
            "and has encountered a deprecation or removal issue.\n\n"
            "--- System Guidance ---\n{guidance}\n\n"
            "--- Documentation Evidence ---\n{context}\n\n"
            "--- Developer's Current Code ---\n{broken_code}\n\n"
            "Task: Refactor the developer's code to fix the deprecated or removed API usage. "
            "Provide ONLY the corrected code snippet wrapped in a clean markdown code block, "
            "followed by a brief, 1-sentence explanation of what changed."
        )
    )
    
    # Use temperature=0 for precise, deterministic code generation
    llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash", temperature=0)
    chain = prompt | llm
    
    response = chain.invoke({
        "broken_code": broken_code,
        "context": context_text,
        "guidance": guidance
    })
    
    return response.content

if __name__ == "__main__":
    # Test the auto-fix agent locally
    sample_code = "import torch\nsolution = torch.lstsq(B, A)"
    sample_context = "torch.lstsq is deprecated in favor of torch.linalg.lstsq and will be removed in v2.0.0."
    sample_guidance = "DANGER: 'torch.lstsq' was removed in version 2.0. You must migrate to 'torch.linalg.lstsq'."
    
    print("Testing Auto-Fix Agent...")
    fixed = generate_code_fix(sample_code, sample_context, sample_guidance)
    print("\n--- Refactored Output ---")
    print(fixed)