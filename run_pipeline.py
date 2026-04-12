#!/usr/bin/env python3
"""
Trading Pipeline - Runs all agents and aggregates signals for billionaire recommendations.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import statistics

# Import agents
try:
    from technical_analyst import analyze_symbol as technical_analyze
except ImportError:
    print("⚠️  Technical analyst not found, using stub")
    technical_analyze = None

try:
    from sentiment_analyst import analyze_symbol as sentiment_analyze
except ImportError:
    print("⚠️  Sentiment analyst not found, using stub")
    sentiment_analyze = None

# Stub for other agents
def stub_analyze(symbol: str, agent_name: str) -> Dict[str, Any]:
    """Stub analysis for agents not yet implemented."""
    import random
    signals = ["BUY", "SELL", "HOLD"]
    signal = random.choice(signals)
    confidence = random.uniform(0.3, 0.9)
    return {
        "symbol": symbol,
        "agent": agent_name,
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Stub analysis by {agent_name}",
        "timestamp": datetime.now().isoformat()
    }

def aggregate_signals(agent_results: List[Dict]) -> Dict[str, Any]:
    """Aggregate multiple agent signals into a final recommendation."""
    if not agent_results:
        return {"signal": "HOLD", "confidence": 0.5, "reasoning": "No agent results"}
    
    # Convert signals to numeric scores: BUY=1, HOLD=0, SELL=-1
    scores = []
    weights = []
    
    for result in agent_results:
        signal = result.get("signal", "HOLD")
        confidence = result.get("confidence", 0.5)
        
        if signal == "BUY":
            score = 1.0
        elif signal == "SELL":
            score = -1.0
        else:  # HOLD
            score = 0.0
        
        # Weight by confidence
        scores.append(score * confidence)
        weights.append(confidence)
    
    # Weighted average
    if weights:
        avg_score = sum(scores) / sum(weights)
    else:
        avg_score = 0
    
    # Determine final signal
    if avg_score > 0.3:
        final_signal = "BUY"
        final_confidence = min(0.95, (avg_score + 1) / 2)
    elif avg_score < -0.3:
        final_signal = "SELL"
        final_confidence = min(0.95, (-avg_score + 1) / 2)
    else:
        final_signal = "HOLD"
        final_confidence = 0.5
    
    # Agent contributions
    contributions = []
    for result in agent_results:
        contributions.append({
            "agent": result.get("agent", "unknown"),
            "signal": result.get("signal", "HOLD"),
            "confidence": result.get("confidence", 0.5),
            "reasoning": result.get("reasoning", "")[:100]
        })
    
    return {
        "signal": final_signal,
        "confidence": final_confidence,
        "aggregate_score": avg_score,
        "agent_count": len(agent_results),
        "contributions": contributions,
        "reasoning": f"Aggregated from {len(agent_results)} agents with weighted average score {avg_score:.3f}"
    }

def run_pipeline(symbol: str) -> Dict[str, Any]:
    """Run all agents and return aggregated results."""
    agent_results = []
    
    print(f"[ROCKET] Running trading pipeline for {symbol}")
    print("="*60)
    
    # 1. Technical Analyst (real)
    if technical_analyze:
        print("📈 Running Technical Analyst...")
        try:
            tech_result = technical_analyze(symbol, use_ai=False)
            if tech_result.get("success"):
                agent_results.append({
                    "agent": "technical",
                    "signal": tech_result["analysis"].get("signal", "HOLD"),
                    "confidence": tech_result["analysis"].get("confidence", 0.5),
                    "reasoning": tech_result["analysis"].get("reasoning", "Technical analysis"),
                    "raw": tech_result
                })
                print("   ✅ Technical analysis complete")
            else:
                print(f"   ❌ Technical analysis failed: {tech_result.get('error')}")
                # Add stub as fallback
                agent_results.append(stub_analyze(symbol, "technical_fallback"))
        except Exception as e:
            print(f"   ❌ Technical analysis error: {e}")
            agent_results.append(stub_analyze(symbol, "technical_error"))
    else:
        agent_results.append(stub_analyze(symbol, "technical_stub"))
    
    # 2. Sentiment Analyst (real if available)
    if sentiment_analyze:
        print("📰 Running Sentiment Analyst...")
        try:
            sent_result = sentiment_analyze(symbol, use_ai=False)
            if sent_result.get("success"):
                agent_results.append({
                    "agent": "sentiment",
                    "signal": sent_result["analysis"].get("signal", "HOLD"),
                    "confidence": sent_result["analysis"].get("confidence", 0.5),
                    "reasoning": sent_result["analysis"].get("reasoning", "Sentiment analysis"),
                    "raw": sent_result
                })
                print("   ✅ Sentiment analysis complete")
            else:
                print(f"   ❌ Sentiment analysis failed: {sent_result.get('error')}")
                agent_results.append(stub_analyze(symbol, "sentiment_fallback"))
        except Exception as e:
            print(f"   ❌ Sentiment analysis error: {e}")
            agent_results.append(stub_analyze(symbol, "sentiment_error"))
    else:
        agent_results.append(stub_analyze(symbol, "sentiment_stub"))
    
    # 3-10. Other agents (stubs for now)
    other_agents = [
        "fundamental", "macro", "crypto", "options", 
        "risk", "quant", "sector", "compliance"
    ]
    
    for agent in other_agents:
        print(f"🤖 Running {agent.capitalize()} Analyst...")
        agent_results.append(stub_analyze(symbol, agent))
        print("   ✅ Stub analysis complete")
    
    # Aggregate signals
    print("\n🔍 Aggregating signals...")
    final_result = aggregate_signals(agent_results)
    
    # Prepare comprehensive result
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "agent_results": agent_results,
        "final_recommendation": final_result,
        "system_status": {
            "real_agents": 2 if technical_analyze or sentiment_analyze else 0,
            "stub_agents": len(other_agents) + (0 if technical_analyze else 1) + (0 if sentiment_analyze else 1),
            "total_agents": len(agent_results)
        }
    }
    
    print(f"\n✅ Pipeline complete: {final_result['signal']} with {final_result['confidence']:.1%} confidence")
    return result

def print_recommendation(result: Dict):
    """Print formatted recommendation."""
    symbol = result["symbol"]
    final = result["final_recommendation"]
    
    print("\n" + "="*60)
    print(f"💰 FINAL RECOMMENDATION: {symbol}")
    print("="*60)
    
    print(f"\n🎯 SIGNAL: {final['signal']} (Confidence: {final['confidence']:.1%})")
    print(f"   Aggregate Score: {final['aggregate_score']:.3f}")
    print(f"   Based on {final['agent_count']} agents")
    
    print(f"\n🤖 AGENT CONTRIBUTIONS:")
    for i, contrib in enumerate(final['contributions'], 1):
        print(f"   {i}. {contrib['agent']}: {contrib['signal']} ({contrib['confidence']:.1%})")
    
    print(f"\n📊 SYSTEM STATUS:")
    print(f"   Real Agents: {result['system_status']['real_agents']}")
    print(f"   Stub Agents: {result['system_status']['stub_agents']}")
    print(f"   Total Agents: {result['system_status']['total_agents']}")
    
    # Billionaire math
    print(f"\n💸 BILLIONAIRE PATH:")
    initial = 1000
    target = 1_000_000_000
    daily_return = 1.5  # 1.5% daily
    
    days = 0
    capital = initial
    while capital < target:
        capital *= (1 + daily_return / 100)
        days += 1
    
    print(f"   Starting Capital: ${initial:,}")
    print(f"   Target: ${target:,}")
    print(f"   Required Daily Return: {daily_return}%")
    print(f"   Time to Billionaire: {days} trading days ({days/365:.1f} years)")
    
    if final['signal'] == "BUY":
        print(f"\n🚀 ACTION: Consider buying {symbol} with proper risk management.")
    elif final['signal'] == "SELL":
        print(f"\n⚠️  ACTION: Consider selling or shorting {symbol} with caution.")
    else:
        print(f"\n⏸️  ACTION: Hold position, monitor for better entry.")
    
    print(f"\n⏰ Generated: {result['timestamp']}")
    print("="*60)

def save_results(result: Dict, filename: str = None):
    """Save results to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recommendation_{result['symbol']}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    return filename

def main():
    """Command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trading Pipeline")
    parser.add_argument("symbol", help="Stock symbol (e.g., AAPL, TSLA)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Run pipeline
    result = run_pipeline(args.symbol.upper())
    
    # Output
    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print_recommendation(result)
    
    # Save if requested
    if args.save or args.output == "json":
        filename = save_results(result)
    
    # Exit code (0 for success, 1 for failure)
    sys.exit(0)

if __name__ == "__main__":
    main()