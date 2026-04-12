#!/usr/bin/env python3
"""
Run a quick test of the trading system
"""

import os
import sys

print("Testing Trading System Components...")
print("=" * 60)

# Test stock scanner
print("\n1. Testing Stock Scanner...")
try:
    from stock_scanner import StockScanner
    scanner = StockScanner()
    stocks = scanner.get_all_stocks(use_cache=True)
    if len(stocks) > 5:
        stocks = stocks[:5]
    print(f"   Found {len(stocks)} stocks")
    for stock in stocks[:3]:
        print(f"   - {stock['symbol']}: {stock.get('name', 'N/A')}")
    print("   OK: Stock scanner working")
except Exception as e:
    print(f"   ERROR: Stock scanner error: {e}")

# Test technical analyst
print("\n2. Testing Technical Analyst...")
try:
    from enhanced_technical_analyst import EnhancedTechnicalAnalyst
    analyst = EnhancedTechnicalAnalyst()
    result = analyst.calculate_all_indicators("AAPL")
    if "error" not in result:
        print(f"   OK: Technical analysis for AAPL: {result.get('final_signal')}")
        print(f"      Confidence: {result.get('confidence', 0):.1%}")
    else:
        print(f"   WARNING: Technical analysis simulation: {result.get('error')}")
except Exception as e:
    print(f"   ERROR: Technical analyst error: {e}")

# Test trading leader
print("\n3. Testing Trading Leader...")
try:
    from trading_leader import TradingLeader
    leader = TradingLeader()
    
    # Create sample data
    sample_results = [
        {
            "symbol": "AAPL",
            "agent_type": "technical",
            "final_signal": "BUY",
            "confidence": 0.8,
            "reasoning": "Test data",
            "current_price": 175.50
        }
    ]
    
    aggregated = leader.aggregate_signals(sample_results)
    print(f"   OK: Signal aggregation: {aggregated.get('total_analyzed', 0)} stocks")
    
    if aggregated.get("buy_recommendations"):
        final_decision = leader.make_final_decision(aggregated)
        print(f"   OK: Final decision: {final_decision.get('decision', 'N/A')}")
    else:
        print("   WARNING: No BUY recommendations in test data")
        
except Exception as e:
    print(f"   ERROR: Trading leader error: {e}")

print("\n" + "=" * 60)
print("Trading System Test Complete!")
print("\nNext steps:")
print("1. Set API keys in .env file")
print("2. Run: python complete_trading_pipeline.py")
print("3. Access dashboard: http://localhost:4200")
print("4. Check API: http://localhost:8081")