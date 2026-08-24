from packaging import version

def evaluate_api_safety(extracted_data: dict, target_version: str) -> str:
    """
    Deterministically compares the user's target version against the API lifecycle.
    """
    api_name = extracted_data.get("api")
    dep_version = extracted_data.get("deprecated_in")
    rem_version = extracted_data.get("removed_in")
    replacement = extracted_data.get("replacement")
    
    # Convert string versions to mathematically comparable objects
    target_v = version.parse(target_version)
    
    # 1. Check if the version is past the removal date
    if rem_version and target_v >= version.parse(rem_version):
        return f"DANGER: '{api_name}' was removed in version {rem_version}. You must migrate to '{replacement}'."
        
    # 2. Check if the version is in the deprecation window
    if dep_version and target_v >= version.parse(dep_version):
        return f"WARNING: '{api_name}' is deprecated in your version ({target_version}). It will be removed in {rem_version}. Plan to use '{replacement}'."
        
    # 3. If target is older than deprecation, it's safe
    if dep_version and target_v < version.parse(dep_version):
        return f"SAFE: '{api_name}' is fully supported in version {target_version}."
        
    return "UNKNOWN: Insufficient evidence to determine the API status for the requested version."

if __name__ == "__main__":
    # We will pass the exact JSON you just generated
    sample_json = {
        "api": "old_function",
        "status": "deprecated",
        "deprecated_in": "1.8",
        "removed_in": "2.0",
        "replacement": "new_function"
    }
    
    print("Testing API safety across different library versions...")
    
    print("\n--- Testing Version 1.5 ---")
    print(evaluate_api_safety(sample_json, "1.5"))
    
    print("\n--- Testing Version 1.9 ---")
    print(evaluate_api_safety(sample_json, "1.9"))
    
    print("\n--- Testing Version 2.1 ---")
    print(evaluate_api_safety(sample_json, "2.1"))