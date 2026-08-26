import argparse
import sys
import os

# Ensure the src directory is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from scanner import extract_api_calls
from pipeline import run_evoguard

def main():
    parser = argparse.ArgumentParser(description="🛡️ EvoGuard AI: Version-Aware API Scanner")
    parser.add_argument("file", help="Path to the Python file to scan")
    parser.add_argument("--version", required=True, help="Target environment version (e.g., 2.7.0)")
    parser.add_argument("--library", default="torch", help="Target library (default: torch)")
    
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
        
    print(f"\n🛡️ EvoGuard CLI scanning '{args.file}' against {args.library} v{args.version}...\n")
    
    apis = extract_api_calls(content)
    if not apis:
        print("✅ No API calls found to scan. Exiting.")
        sys.exit(0)
        
    danger_found = False
    
    for api in apis:
        sys.stdout = open(os.devnull, 'w')
        result = run_evoguard(f"Is {api} safe?", args.version, args.library, None)
        sys.stdout = sys.__stdout__
        
        guidance = result["guidance"]
        if "DANGER" in guidance:
            print(f"❌ [DANGER] {api}: {guidance.replace('DANGER: ', '')}")
            danger_found = True
        elif "WARNING" in guidance:
            print(f"⚠️  [WARNING] {api}: {guidance.replace('WARNING: ', '')}")
        elif "SAFE" in guidance:
            print(f"✅ [SAFE] {api}")
        else:
            print(f"ℹ️  [INFO] {api}: {guidance}")
            
    print("\n--- Scan Complete ---")
    if danger_found:
        print("🚨 DANGER level conflicts found! Breaking the build (exit code 1).")
        sys.exit(1)  
    else:
        print("✅ All APIs pass version checks. Code is safe to deploy.")
        sys.exit(0)

if __name__ == "__main__":
    main()