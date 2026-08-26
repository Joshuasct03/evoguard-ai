import streamlit as st
import sys
import os
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ----------------------------------------------

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from pipeline import run_evoguard

st.set_page_config(page_title="EvoGuard AI", layout="centered", page_icon="🛡️")

st.title("🛡️ EvoGuard AI")
st.markdown("**Version-Aware API Change Intelligence & Generative Migration Assistant**")
st.divider()

col1, col2 = st.columns(2)
with col1:
    target_library = st.selectbox("Library", ["torch", "numpy", "scipy", "pandas", "sklearn", "jax", "matplotlib"], index=0)
with col2:
    target_version = st.text_input("Your Environment Version", value="2.7.0")

tab1, tab2 = st.tabs(["🔍 Single API Query", "📁 Batch File Scan"])

with tab1:
    query = st.text_input("API Query / Description", value="Is torch.onnx.dynamo_export deprecated?")
    user_code = st.text_area("Optional: Paste your code snippet here to auto-fix", value="import torch\ntorch.onnx.dynamo_export(model, args)")
    
    if st.button("Analyze API Safety & Refactor", type="primary"):
        with st.spinner("Retrieving timeline evidence, running version math, and generating code fix..."):
            result = run_evoguard(query, target_version, target_library, user_code)
            
            if result["status"] == "abstained":
                st.warning(result["guidance"])
            elif "error" in result["status"]:
                st.error(result["guidance"])
            else:
                guidance = result["guidance"]
                if "SAFE" in guidance:
                    st.success(guidance)
                elif "WARNING" in guidance:
                    st.warning(guidance)
                elif "DANGER" in guidance:
                    st.error(guidance)
                else:
                    st.info(guidance)
                    
                if result.get("fix"):
                    st.subheader("🛠️ Automated Code Migration")
                    st.markdown(result["fix"])
                    
                with st.expander("🔍 View Engine Reasoning & Evidence"):
                    st.markdown("**Retrieved Context (Injected Metadata):**")
                    st.code(result["evidence"], language="text")
                    st.markdown("**Structured Extraction (LLM Output):**")
                    st.json(result["structured_data"])

with tab2:
    st.markdown("**Upload a Python script to scan all APIs against the version boundary.**")
    uploaded_file = st.file_uploader("Upload .py file", type=["py"])
    
    if st.button("Scan Entire File", type="primary") and uploaded_file:
        from scanner import extract_api_calls
        
        file_content = uploaded_file.read().decode("utf-8")
        extracted_apis = extract_api_calls(file_content)
        
        if not extracted_apis:
            st.warning("No valid API calls found in the uploaded file.")
        else:
            st.info(f"Found {len(extracted_apis)} API calls in {uploaded_file.name}. Running EvoGuard analysis...")
            
            for api in extracted_apis:
                st.markdown(f"### Analyzing: `{api}`")
                result = run_evoguard(f"Is {api} safe to use?", target_version, target_library, None)
                
                if result["status"] == "abstained":
                    st.info(f"{result['guidance']}")
                elif "error" in result["status"]:
                    st.error(f"{result['guidance']}")
                else:
                    guidance = result["guidance"]
                    if "SAFE" in guidance:
                        st.success(guidance)
                    elif "WARNING" in guidance:
                        st.warning(guidance)
                    elif "DANGER" in guidance:
                        st.error(guidance)
                    else:
                        st.info(f"{guidance}")
            st.divider()