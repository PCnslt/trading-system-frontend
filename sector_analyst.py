#!/usr/bin/env python3
"""
Sector Analyst Agent - Analyzes sector rotation and industry trends
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")
from hf_router import analyze_with_llm

def fetch_sector_data(symbol="AAPL"):
    """Fetch sector data from Finnhub or fallback to mock."""
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
    if FINNHUB_API_KEY and FINNHUB_API_KEY != "your_finnhub_api_key_here":
        try:
            # Fetch sector metrics for S&P 500
            url = "https://finnhub.io/api/v1/sector-metric"
            params = {
                "region": "S&P500",
                "token": FINNHUB_API_KEY
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Find sector for this symbol (simplified)
                # In reality, need to map symbol to sector
                return {
                    "symbol": symbol,
                    "sector_data": data,
                    "source": "finnhub",
                    "trend": "neutral",
                    "confidence": 0.6
                }
        except Exception as e:
            print(f"Finnhub sector fetch failed: {e}")
    
    # Mock data fallback
    sectors = ["Technology", "Healthcare", "Financials", "Consumer Discretionary", "Industrials"]
    return {
        "symbol": symbol,
        "sector": random.choice(sectors),
        "sector_performance": round(random.uniform(-0.05, 0.05), 3),
        "relative_strength": round(random.uniform(0.3, 0.8), 2),
        "trend": random.choice(["bullish", "neutral", "bearish"]),
        "confidence": random.uniform(0.4, 0.9),
        "source": "mock"
    }

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, data: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze sector data."""
    prompt = f"""You are a Sector rotation analyst. Analyze the following sector data for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Sector Data:
- Sector: {data.get('sector', 'N/A')}
- Sector Performance: {data.get('sector_performance', 'N/A')} (positive = outperforming, negative = underperforming)
- Relative Strength: {data.get('relative_strength', 'N/A')} (0-1, higher = stronger)
- Trend: {data.get('trend', 'N/A')}
- Confidence: {data.get('confidence', 'N/A')}
- Data Source: {data.get('source', 'mock')}

Interpretation guidelines:
- Strong sector performance (+>0.02) suggests BUY for stocks in that sector.
- Weak sector performance (<-0.02) suggests SELL.
- Relative strength >0.7 indicates strong momentum.
- Consider overall market conditions and sector rotation trends.

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
    conf = data.get("confidence", 0.5)
    try:
        conf = float(conf)
    except:
        conf = 0.5
    
    sector_perf = data.get("sector_performance", 0)
    try:
        sector_perf = float(sector_perf)
    except:
        sector_perf = 0
    
    if sector_perf > 0.02 and conf > 0.6:
        signal = "BUY"
        confidence = int((sector_perf * 1000 + conf * 100) / 2)
    elif sector_perf < -0.02 and conf > 0.6:
        signal = "SELL"
        confidence = int((abs(sector_perf) * 1000 + conf * 100) / 2)
    else:
        signal = "HOLD"
        confidence = int(conf * 100)
    
    return {
        "signal": signal,
        "confidence": min(max(confidence, 0), 100),
        "reasoning": f"Rule-based: sector performance {sector_perf:.3f}, confidence {conf:.2f}",
        "summary": f"Sector outlook: {signal}"
    }

def analyze_symbol(symbol: str, use_ai: bool = True) -> Dict[str, Any]:
    """Main analysis function for a symbol."""
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
        data = fetch_sector_data(symbol)
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
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    result = analyze_symbol(symbol, use_ai=True)
    if "--output" in sys.argv and sys.argv[sys.argv.index("--output") + 1] == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\nSector Analysis for {symbol}:")
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")
        print(f"Confidence: {result.get('analysis', {}).get('confidence', 'N/A')}%")
        print(f"Reasoning: {result.get('analysis', {}).get('reasoning', 'N/A')}")
