import ast

def extract_api_calls(code_content: str) -> list:
    """
    Parses a Python file into an Abstract Syntax Tree (AST) and 
    extracts all function/method calls (e.g., 'torch.onnx.export').
    """
    try:
        tree = ast.parse(code_content)
    except SyntaxError:
        return []

    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            attrs = []
            # Traverse nested attributes (module.submodule.function)
            while isinstance(func, ast.Attribute):
                attrs.append(func.attr)
                func = func.value
            if isinstance(func, ast.Name):
                attrs.append(func.id)
            
            if attrs:
                full_call = ".".join(reversed(attrs))
                # Filter out basic Python built-ins like print() or len()
                if full_call not in ["print", "len", "range", "int", "str", "list"]:
                    calls.add(full_call)
                    
    return list(calls)

if __name__ == "__main__":
    # Test it locally
    sample_code = "import torch\ntorch.onnx.dynamo_export(model)\nprint('Done')"
    print(f"Extracted APIs: {extract_api_calls(sample_code)}")