import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

# 1. Define the Strict JSON Schema for API Lifecycles
class APILifecycle(BaseModel):
    api: str = Field(description="The name of the API, method, or function.")
    deprecated_in: str = Field(description="The version number where the API was deprecated (e.g. '2.7.0', or null if not deprecated).")
    removed_in: str = Field(description="The version number where the API was removed (or null if not removed).")
    alternative: str = Field(description="The recommended replacement API or migration instruction.")

def extract_api_info(context_text: str):
    parser = PydanticOutputParser(pydantic_object=APILifecycle)
    
    prompt = PromptTemplate(
        template=(
            "You are a precise API documentation extraction engine.\n"
            "Analyze the provided documentation context below. Pay close attention to version tags like [Library: name vX.X.X] "
            "to determine the exact version numbers.\n\n"
            "{context_text}\n\n"
            "Extract the lifecycle details for ONLY the primary API into a SINGLE JSON object. DO NOT RETURN A LIST.\n"
            "{format_instructions}"
        ),
        input_variables=["context_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash", temperature=0)
    chain = prompt | llm
    
    raw_response = chain.invoke({"context_text": context_text})
    
    try:
        # Try normal Pydantic parsing
        parsed = parser.parse(raw_response.content)
        return parsed.dict() if hasattr(parsed, "dict") else parsed.model_dump()
    except Exception as e:
        # BULLETPROOF FALLBACK: If the LLM returned a list anyway, catch it manually
        try:
            clean_json = raw_response.content.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_json)
            
            # If it's a list, grab the first (most relevant) entry
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            # If it wrapped it in a weird dictionary key, extract it
            elif isinstance(data, dict) and "apis" in data:
                return data["apis"][0]
                
            return data
        except Exception:
            raise e # If all fail, throw the original error