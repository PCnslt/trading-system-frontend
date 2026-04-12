import requests
import json
import sys

def test_analysis(symbol="AAPL"):
    url = f"http://localhost:8081/analyze/{symbol}"
    try:
        response = requests.get(url, timeout=60)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            # Check if agents succeeded
            for agent in ["technical", "fundamental", "sentiment"]:
                if agent in data:
                    success = data[agent].get("success", False)
                    print(f"{agent}: {'SUCCESS' if success else 'FAILED'}")
                    if not success:
                        print(f"  Error: {data[agent].get('error', 'Unknown')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    test_analysis(symbol)