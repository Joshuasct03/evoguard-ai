import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from pipeline import run_evoguard

def run_benchmark():
    print("Loading Benchmark Dataset...")
    dataset_path = os.path.join(os.path.dirname(__file__), "test_cases.json")
    with open(dataset_path, "r") as f:
        test_cases = json.load(f)
        
    correct = 0
    total = len(test_cases)
    
    print("\nStarting EvoGuard Benchmark Evaluation...")
    for idx, tc in enumerate(test_cases):
        print(f"\n--- Test {idx+1}/{total}: [{tc['target_library']} v{tc['target_version']}] ---")
        
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            result = run_evoguard(tc['query'], tc['target_version'], tc['target_library'])
        finally:
            sys.stdout = old_stdout
            
        guidance = result.get("guidance", "")
        expected = tc["expected_status"]
        
        if expected in guidance:
            print(f"✅ PASS: Correctly identified {expected} state.")
            correct += 1
        else:
            print(f"❌ FAIL: Expected {expected}, got {guidance}")
            
    accuracy = (correct / total) * 100
    print("\n=============================================")
    print(f" FINAL BENCHMARK SCORE: {accuracy:.1f}% ({correct}/{total})")
    print("=============================================\n")

if __name__ == "__main__":
    run_benchmark()