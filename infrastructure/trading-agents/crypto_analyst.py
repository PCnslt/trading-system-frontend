#!/usr/bin/env python3
"""
Crypto Analyst Agent - Analyzes cryptocurrency markets using CoinMarketCap data
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

COINMARKETCAP_KEY = os.getenv("COINMARKETCAP_API_KEY", "5031a7c7-2bf3-413a-8f24-1d0800f575c9")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")
from hf_router import analyze_with_llm

def fetch_crypto_data(symbol="BTC"):
    """Fetch cryptocurrency data from CoinMarketCap."""
    # Mock for now; implement real API later
    return {
        "symbol": symbol,
        "price_usd": 45000 + random.randint(-2000, 2000),
        "market_cap": 900000000000,
        "volume_24h": 30000000000,
        "percent_change_24h": random.uniform(-5, 5),
        "percent_change_7d": random.uniform(-10, 10),
        "dominance": 45.2,
        "fear_greed_index": 65,
        "sentiment_score": 0.6,
    }

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, data: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze crypto data."""
    prompt = f"""You are a cryptocurrency analyst. Analyze the following cryptocurrency data for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Cryptocurrency Data:
- Price (USD): ${data.get('price_usd', 'N/A'):,.2f}
- Market Cap: ${data.get('market_cap', 'N/A'):,.0f}
- 24h Volume: ${data.get('volume_24h', 'N/A'):,.0f}
- 24h Change: {data.get('percent_change_24h', 'N/A'):.2f}%
- 7d Change: {data.get('percent_change_7d', 'N/A'):.2f}%
- Bitcoin Dominance: {data.get('dominance', 'N/A'):.1f}%
- Fear & Greed Index: {data.get('fear_greed_index', 'N/A')}/100
- Sentiment Score: {data.get('sentiment_score', 'N/A')}

Interpretation guidelines:
- Price momentum (24h/7d change) indicates short-term trend.
- High volume suggests strong interest.
- Fear & Greed > 70 indicates greed (caution), < 30 fear (opportunity).
- Bitcoin dominance > 50% suggests BTC leading market.
- Consider overall market sentiment and macro conditions.

Provide your analysis in JSON format with keys: signal, confidence, reasoning, summary.
"""
    try:
        result = analyze_with_llm(prompt, json_output=True, max_tokens=300, temperature=0.2)
        if not isinstance(result, dict):
            result = {"signal": "HOLD", "confidence": 50, "reasoning": "AI returned non-dict", "summary": "Analysis error."}
        signal = result.get("signal", "").upper()
        if signal not in ["BUY", "SELL", "HOLD"]:
            result["signal"] = "HOLD"
        return result
    except Exception as e:
        return {"signal": "HOLD", "confidence": 50, "reasoning": f"AI analysis failed: {e}", "summary": "AI analysis error."}

def rule_based_analysis(data: Dict) -> Dict[str, Any]:
    """Fallback rule-based analysis."""
    change_24h = data.get("percent_change_24h", 0)
    fear_greed = data.get("fear_greed_index", 50)
    if change_24h > 5 and fear_greed < 40:
        signal = "BUY"
        confidence = 70
    elif change_24h < -5 and fear_greed > 70:
        signal = "SELL"
        confidence = 65
    else:
        signal = "HOLD"
        confidence = 50
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Rule-based: 24h change {change_24h:.2f}%, Fear & Greed {fear_greed}",
        "summary": f"Crypto outlook: {signal}"
    }

def analyze_symbol(symbol: str, use_ai: bool = True) -> Dict[str, Any]:
    """Main analysis function for a cryptocurrency symbol."""
    symbol = symbol.upper()
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "data": {},
        "analysis": {}
    }
    try:
        data = fetch_crypto_data(symbol)
        result["data"] = data
        
        if use_ai and HUGGINGFACE_TOKEN:
            analysis = analyze_with_ai(symbol, data)
        else:
            analysis = rule_based_analysis(data)
        
        result["analysis"] = analysis
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC"
    result = analyze_symbol(symbol, use_ai=True)
    if "--output" in sys.argv and sys.argv[sys.argv.index("--output") + 1] == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\nCrypto Analysis for {symbol}:")
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")
        print(f"Confidence: {result.get('analysis', {}).get('confidence', 'N/A')}%")
        print(f"Reasoning: {result.get('analysis', {}).get('reasoning', 'N/A')}")