from packaging import version

def evaluate_api_safety(extracted_data: dict, target_version: str) -> str:
    """
    Evaluates the target version mathematically against the extracted lifecycle JSON.
    """
    if not extracted_data:
        return "UNKNOWN: No data provided."
    
    api_name = extracted_data.get("api", "Unknown API")
    deprecated_in = extracted_data.get("deprecated_in")
    removed_in = extracted_data.get("removed_in")
    alternative = extracted_data.get("alternative")
    
    # Normalize strings that might have been populated as literal "null" or "None"
    if deprecated_in in ["None", "null", ""]: deprecated_in = None
    if removed_in in ["None", "null", ""]: removed_in = None
    
    try:
        target = version.parse(target_version)
    except Exception:
        return f"UNKNOWN: Invalid target version format '{target_version}'."
    
    status = "SAFE"
    
    try:
        if removed_in and target >= version.parse(removed_in):
            status = "DANGER"
        elif deprecated_in and target >= version.parse(deprecated_in):
            status = "WARNING"
    except Exception:
        # If the LLM extracted a malformed version string, default to safest unknown state
        return "UNKNOWN: Could not parse lifecycle version strings mathematically."
        
    if status == "SAFE":
        return f"SAFE: '{api_name}' is fully supported in version {target_version}."
    elif status == "DANGER":
        return f"DANGER: '{api_name}' was removed in version {removed_in}. You must migrate to '{alternative}'."
    elif status == "WARNING":
        guidance = f"WARNING: '{api_name}' is deprecated in your version ({target_version})."
        if removed_in:
            guidance += f" It will be removed in version {removed_in}."
        if alternative:
            guidance += f" Plan to use '{alternative}'."
        return guidance
    
    return "UNKNOWN: Insufficient evidence to determine the API status for the requested version."