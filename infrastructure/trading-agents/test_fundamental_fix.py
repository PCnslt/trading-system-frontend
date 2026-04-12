import sys
sys.path.insert(0, '.')
from fundamental_analyst import analyze_symbol
import json

result = analyze_symbol("AAPL", use_ai=True)
print(json.dumps(result, indent=2))
# Check if reasoning is string
reasoning = result.get("analysis", {}).get("reasoning", "")
print(f"\nReasoning type: {type(reasoning)}")
print(f"Reasoning length: {len(str(reasoning))}")
print(f"Success: {result.get('success', False)}")