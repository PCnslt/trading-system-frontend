#!/usr/bin/env python3
"""
Quant Analyst Agent - Quantitative analysis using statistical models and machine learning
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

def fetch_quant_data(symbol="AAPL"):
    """Fetch quant data."""
    # Mock data
    return {
        "symbol": symbol,
        "metric1": 0.67,
        "metric2": 0.89,
        "metric3": 0.12,
        "trend": "neutral",
        "confidence": random.uniform(0, 1)
    }

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, data: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze quant data."""
    prompt = f"""You are a Quant analyst. Analyze the following quant data for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Data:
- Metric1: {data.get('metric1', 'N/A')}
- Metric2: {data.get('metric2', 'N/A')}
- Metric3: {data.get('metric3', 'N/A')}
- Trend: {data.get('trend', 'N/A')}
- Confidence: {data.get('confidence', 'N/A')}

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
    if conf > 0.7:
        signal = "BUY"
    elif conf < 0.3:
        signal = "SELL"
    else:
        signal = "HOLD"
    return {
        "signal": signal,
        "confidence": int(conf * 100),
        "reasoning": f"Rule-based: confidence {conf:.2f}",
        "summary": f"Quant outlook: {signal}"
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
        data = fetch_quant_data(symbol)
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
        print(f"\nQuant Analysis for {symbol}:")
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")
        print(f"Confidence: {result.get('analysis', {}).get('confidence', 'N/A')}%")
        print(f"Reasoning: {result.get('analysis', {}).get('reasoning', 'N/A')}")
