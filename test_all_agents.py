#!/usr/bin/env python3
"""
Test all 10 agent endpoints.
"""

import requests
import json
import sys

BASE = "http://localhost:8081"
AGENTS = [
    "technical",
    "fundamental", 
    "sentiment",
    "macro",
    "crypto",
    "options",
    "risk",
    "quant",
    "sector",
    "compliance"
]

def test_agent(agent, symbol="AAPL"):
    url = f"{BASE}/agents/{agent}/{symbol}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            success = data.get("success", False)
            signal = data.get("signal", "ERROR")
            confidence = data.get("confidence", 0)
            return True, f"{agent}: SUCCESS signal={signal} conf={confidence}"
        else:
            return False, f"{agent}: HTTP {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return False, f"{agent}: Exception {e}"

if __name__ == "__main__":
    results = []
    for agent in AGENTS:
        ok, msg = test_agent(agent)
        results.append((ok, msg))
        print(msg)
    
    success_count = sum(1 for ok, _ in results if ok)
    total = len(results)
    print(f"\n✅ {success_count}/{total} agents succeeded")
    if success_count < total:
        print("Failed agents:")
        for ok, msg in results:
            if not ok:
                print(f"  {msg}")
        sys.exit(1)
    else:
        print("🎉 All agents working!")
        sys.exit(0)