#!/usr/bin/env python3
"""
Test all trading system features without emojis
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8081/api"

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_all_features():
    """Test all system features"""
    print("Testing Trading System Features")
    print("=" * 60)
    
    tests = []
    
    # 1. Test Health Endpoint
    print("\n1. Testing Health Endpoint...")
    success, result = test_api_endpoint("health")
    if success:
        print(f"   OK Health: {result.get('status', 'Unknown')}")
        print(f"   Service: {result.get('service', 'Unknown')}")
        tests.append(("Health Check", True))
    else:
        print(f"   FAIL Health: {result}")
        tests.append(("Health Check", False))
    
    # 2. Test Agents Endpoint
    print("\n2. Testing Agents Endpoint...")
    success, result = test_api_endpoint("agents")
    if success:
        total = result.get('total', 0)
        active = result.get('active', 0)
        print(f"   OK Agents: {active}/{total} active")
        if 'controlEndpoints' in result:
            print(f"   Control endpoints: {len(result['controlEndpoints'])} available")
        tests.append(("Agents API", True))
    else:
        print(f"   FAIL Agents: {result}")
        tests.append(("Agents API", False))
    
    # 3. Test Status Endpoint
    print("\n3. Testing Status Endpoint...")
    success, result = test_api_endpoint("status")
    if success:
        print(f"   OK System status retrieved")
        if 'nextSteps' in result:
            print(f"   Next steps: {len(result['nextSteps'])} items")
        tests.append(("Status API", True))
    else:
        print(f"   FAIL Status: {result}")
        tests.append(("Status API", False))
    
    # 4. Test Trading Signals
    print("\n4. Testing Trading Signals...")
    success, result = test_api_endpoint("trading/signals")
    if success:
        print(f"   OK Trading signals: {len(result.get('signals', []))} signals")
        tests.append(("Trading Signals", True))
    else:
        print(f"   FAIL Trading signals: {result}")
        tests.append(("Trading Signals", False))
    
    # 5. Test Technical Analysis
    print("\n5. Testing Technical Analysis...")
    success, result = test_api_endpoint("trading/analyze/technical", "POST", {"symbol": "AAPL"})
    if success:
        signal = result.get('signal', 'Unknown')
        confidence = result.get('confidence', 0)
        print(f"   OK Technical analysis: {signal} ({confidence:.1%} confidence)")
        tests.append(("Technical Analysis", True))
    else:
        print(f"   FAIL Technical analysis: {result}")
        tests.append(("Technical Analysis", False))
    
    # 6. Test Fundamental Analysis
    print("\n6. Testing Fundamental Analysis...")
    success, result = test_api_endpoint("trading/analyze/fundamental", "POST", {"symbol": "AAPL"})
    if success:
        signal = result.get('signal', 'Unknown')
        confidence = result.get('confidence', 0)
        print(f"   OK Fundamental analysis: {signal} ({confidence:.1%} confidence)")
        tests.append(("Fundamental Analysis", True))
    else:
        print(f"   FAIL Fundamental analysis: {result}")
        tests.append(("Fundamental Analysis", False))
    
    # 7. Test Agent Activation
    print("\n7. Testing Agent Control...")
    success, result = test_api_endpoint("agent/1/status")
    if success:
        status = result.get('status', 'Unknown')
        print(f"   OK Agent 1 status: {status}")
        tests.append(("Agent Control", True))
    else:
        print(f"   WARNING Agent control: {result} (may need activation)")
        tests.append(("Agent Control", False))
    
    # 8. Test Market Data
    print("\n8. Testing Market Data...")
    success, result = test_api_endpoint("market/price/AAPL")
    if success:
        price = result.get('price', 'Unknown')
        print(f"   OK Market price: ${price}")
        tests.append(("Market Data", True))
    else:
        print(f"   FAIL Market data: {result}")
        tests.append(("Market Data", False))
    
    # 9. Test System Capabilities
    print("\n9. Testing System Capabilities...")
    success, result = test_api_endpoint("system/capabilities")
    if success:
        capabilities = result.get('capabilities', [])
        print(f"   OK System capabilities: {len(capabilities)} features")
        tests.append(("System Capabilities", True))
    else:
        print(f"   FAIL Capabilities: {result}")
        tests.append(("System Capabilities", False))
    
    # 10. Test Consensus
    print("\n10. Testing Consensus Analysis...")
    success, result = test_api_endpoint("trading/consensus", "POST", {"symbols": ["AAPL", "MSFT"]})
    if success:
        consensus = result.get('consensus', {})
        print(f"   OK Consensus analysis: {len(consensus)} symbols analyzed")
        tests.append(("Consensus Analysis", True))
    else:
        print(f"   FAIL Consensus: {result}")
        tests.append(("Consensus Analysis", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "PASS" if success else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Frontend check
    print("\nFrontend Status:")
    try:
        frontend_response = requests.get("http://localhost:4201", timeout=5)
        if frontend_response.status_code == 200:
            print("   OK Frontend is running at http://localhost:4201")
            print("   Open in browser to access:")
            print("   - Agent Control Panel with buttons")
            print("   - Real-time activity feed")
            print("   - Progress bars and monitoring")
            print("   - Chat panel for agent communication")
            print("   - Performance metrics dashboard")
        else:
            print(f"   WARNING Frontend status: {frontend_response.status_code}")
    except:
        print("   FAIL Frontend not accessible at http://localhost:4201")
    
    # Recommendations
    print("\nRecommendations:")
    if passed == total:
        print("   OK All systems operational!")
        print("   Open dashboard to monitor all 10 agents")
        print("   Use control panel buttons to trigger analysis")
        print("   Real-time updates should be working")
    else:
        print("   WARNING Some features need attention")
        print("   Check backend logs for errors")
        print("   Restart services if needed")
        print("   Check API connectivity")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = test_all_features()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        exit(1)