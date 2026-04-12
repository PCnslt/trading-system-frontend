#!/usr/bin/env python3
"""
Macro Analyst Agent - Analyzes macroeconomic indicators (GDP, inflation, interest rates)
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "LNPH1SNZM9C4MT0")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")
from hf_router import analyze_with_llm

def fetch_macro_indicators():
    """Fetch macroeconomic indicators from Alpha Vantage."""
    # For now, return mock data
    return {
        "gdp_growth": 2.1,  # percent
        "inflation": 2.5,   # percent
        "unemployment": 3.8, # percent
        "interest_rate": 5.25, # federal funds rate
        "consumer_sentiment": 68.5,
        "retail_sales_growth": 0.3,
        "industrial_production": 0.2,
        "housing_starts": 1.42, # million
        "trade_deficit": -68.6, # billion
    }

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, indicators: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze macroeconomic indicators."""
    prompt = f"""You are a macroeconomic analyst. Analyze the following macroeconomic indicators for the US economy and provide a market outlook (BULLISH, BEARISH, or NEUTRAL) with confidence score (0-100%) and brief reasoning.

Macroeconomic Indicators:
- GDP Growth: {indicators.get('gdp_growth', 'N/A')}%
- Inflation Rate: {indicators.get('inflation', 'N/A')}%
- Unemployment Rate: {indicators.get('unemployment', 'N/A')}%
- Federal Funds Rate: {indicators.get('interest_rate', 'N/A')}%
- Consumer Sentiment: {indicators.get('consumer_sentiment', 'N/A')}
- Retail Sales Growth: {indicators.get('retail_sales_growth', 'N/A')}%
- Industrial Production: {indicators.get('industrial_production', 'N/A')}%
- Housing Starts: {indicators.get('housing_starts', 'N/A')} million
- Trade Deficit: {indicators.get('trade_deficit', 'N/A')} billion

Interpretation guidelines:
- GDP growth > 2% is healthy.
- Inflation 2-3% is target; above 3% may cause rate hikes.
- Unemployment < 4% is strong labor market.
- Consumer sentiment > 60 is positive.
- Rising retail sales and industrial production indicate economic expansion.
- Housing starts > 1.5 million strong.

Provide your analysis in JSON format with keys: signal (BULLISH/BEARISH/NEUTRAL), confidence, reasoning, summary.
"""
    try:
        result = analyze_with_llm(prompt, json_output=True, max_tokens=300, temperature=0.2)
        if not isinstance(result, dict):
            result = {"signal": "NEUTRAL", "confidence": 50, "reasoning": "AI returned non-dict", "summary": "Analysis error."}
        # Ensure signal is valid
        signal = result.get("signal", "").upper()
        if signal not in ["BULLISH", "BEARISH", "NEUTRAL"]:
            result["signal"] = "NEUTRAL"
        return result
    except Exception as e:
        return {"signal": "NEUTRAL", "confidence": 50, "reasoning": f"AI analysis failed: {e}", "summary": "AI analysis error."}

def rule_based_analysis(indicators: Dict) -> Dict[str, Any]:
    """Fallback rule-based analysis."""
    gdp = indicators.get("gdp_growth", 0)
    inflation = indicators.get("inflation", 0)
    unemployment = indicators.get("unemployment", 5)
    if gdp > 2.5 and inflation < 3 and unemployment < 4:
        signal = "BULLISH"
        confidence = 70
    elif gdp < 1 or inflation > 5 or unemployment > 6:
        signal = "BEARISH"
        confidence = 60
    else:
        signal = "NEUTRAL"
        confidence = 50
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Rule-based: GDP {gdp}%, inflation {inflation}%, unemployment {unemployment}%",
        "summary": f"Macro outlook: {signal}"
    }

def analyze_symbol(symbol: str, use_ai: bool = True) -> Dict[str, Any]:
    """Main analysis function for a symbol (symbol ignored for macro)."""
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "indicators": {},
        "analysis": {}
    }
    try:
        indicators = fetch_macro_indicators()
        result["indicators"] = indicators
        
        if use_ai and HUGGINGFACE_TOKEN:
            analysis = analyze_with_ai(symbol, indicators)
        else:
            analysis = rule_based_analysis(indicators)
        
        result["analysis"] = analysis
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    result = analyze_symbol(symbol, use_ai=True)
    if "--output" in sys.argv and sys.argv[sys.argv.index("--output") + 1] == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"\nMacro Analysis for {symbol}:")
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")
        print(f"Confidence: {result.get('analysis', {}).get('confidence', 'N/A')}%")
        print(f"Reasoning: {result.get('analysis', {}).get('reasoning', 'N/A')}")