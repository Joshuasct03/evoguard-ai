import streamlit as st
import sys
import os
import asyncio

# --- FIX: Streamlit Threading Asyncio Patch ---
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
# ----------------------------------------------

# Ensure we can import from the current directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from pipeline import run_evoguard

# Configure the page layout
st.set_page_config(page_title="EvoGuard AI", layout="centered", page_icon="🛡️")

st.title("🛡️ EvoGuard AI")
st.markdown("**Version-Aware API Change Intelligence & Migration Assistant**")
st.divider()

# Input fields
col1, col2 = st.columns(2)
with col1:
    target_library = st.selectbox("Library", ["torch", "numpy", "scipy", "pandas"], index=0)
with col2:
    target_version = st.text_input("Your Environment Version", value="1.8.0")

query = st.text_input("API Query", value="Can I use torch.lstsq to solve linear equations?")

# The Action Button
if st.button("Analyze API Safety", type="primary"):
    with st.spinner("Retrieving evidence and running deterministic version math..."):
        # Call the engine
        result = run_evoguard(query, target_version, target_library)
        
        # Handle the output gracefully
        if result["status"] == "abstained":
            st.warning(result["guidance"])
        elif "error" in result["status"]:
            st.error(result["guidance"])
        else:
            # Color code the output based on danger level
            guidance = result["guidance"]
            if "SAFE" in guidance:
                st.success(guidance)
            elif "WARNING" in guidance:
                st.warning(guidance)
            elif "DANGER" in guidance:
                st.error(guidance)
            else:
                st.info(guidance)
                
            # Allow the user to inspect the engine's reasoning
            with st.expander("🔍 View Engine Reasoning & Evidence"):
                st.markdown("**Retrieved Context (Injected Metadata):**")
                st.code(result["evidence"], language="text")
                st.markdown("**Structured Extraction (LLM Output):**")
                st.json(result["structured_data"])