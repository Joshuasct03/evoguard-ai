import os
import json
from dotenv import load_dotenv
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# 1. Define the exact structure we want the LLM to populate
class APILifecycle(BaseModel):
    api: str = Field(description="The name of the API or function")
    status: str = Field(description="Lifecycle status: active, deprecated, removed, or modified")
    deprecated_in: str = Field(default=None, description="Version string when deprecated, if mentioned")
    removed_in: str = Field(default=None, description="Version string when removed, if mentioned")
    replacement: str = Field(default=None, description="Recommended alternative function, if any")

def extract_api_info(context_text: str) -> dict:
    """Extracts structured lifecycle data from documentation context."""
    # 2. Setup JSON parser and inject format instructions into the prompt
    parser = JsonOutputParser(pydantic_object=APILifecycle)
    
    prompt = PromptTemplate(
        template="Extract the API lifecycle information from the documentation below.\n{format_instructions}\n\nContext:\n{context}\n",
        input_variables=["context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    # 3. Use Gemini with temperature=0 for consistent, deterministic parsing
    llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash", temperature=0)
    chain = prompt | llm | parser
    
    return chain.invoke({"context": context_text})

if __name__ == "__main__":
    sample_context = (
        "The old_function API has been deprecated since version 1.8 "
        "and will be removed in 2.0. Use new_function instead."
    )
    print("Testing Structured Extraction on sample documentation...")
    result = extract_api_info(sample_context)
    print("\n--- Structured JSON Output ---")
    print(json.dumps(result, indent=2))