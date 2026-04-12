import sys
sys.path.insert(0, '.')
from hf_router import analyze_with_llm

prompt = "Hello, how are you?"
try:
    result = analyze_with_llm(prompt, json_output=False, max_tokens=50, temperature=0.2)
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()