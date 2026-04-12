#!/usr/bin/env python3
"""
Options Analyst Agent - Analyzes options market data (IV, put/call ratio, skew)
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

def fetch_options_data(symbol="AAPL"):
    """Fetch options data from marketdata.app (free for AAPL) or yfinance fallback."""
    symbol = symbol.upper()
    
    # Try marketdata.app (free for AAPL, no API key needed)
    if symbol == "AAPL":
        try:
            url = f"https://api.marketdata.app/v1/options/chain/{symbol}/"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Extract key metrics
                calls = data.get("calls", [])
                puts = data.get("puts", [])
                if calls and puts:
                    # Calculate implied volatility average
                    iv_call = sum(c.get("iv", 0) for c in calls[:5]) / 5 if len(calls) >= 5 else 0.3
                    iv_put = sum(p.get("iv", 0) for p in puts[:5]) / 5 if len(puts) >= 5 else 0.3
                    put_call_ratio = len(puts) / max(len(calls), 1)
                    skew = iv_put - iv_call
                    
                    return {
                        "symbol": symbol,
                        "implied_volatility_call": round(iv_call, 3),
                        "implied_volatility_put": round(iv_put, 3),
                        "put_call_ratio": round(put_call_ratio, 2),
                        "volatility_skew": round(skew, 3),
                        "total_options": len(calls) + len(puts),
                        "source": "marketdata.app",
                        "trend": "bearish" if skew > 0.1 else "bullish" if skew < -0.1 else "neutral",
                        "confidence": 0.7
                    }
        except Exception as e:
            print(f"Marketdata.app fetch failed: {e}")
    
    # Fallback to yfinance options chain
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        # Get options expiration dates
        exps = ticker.options
        if exps:
            # Get nearest expiration
            nearest = exps[0]
            opt_chain = ticker.option_chain(nearest)
            calls = opt_chain.calls
            puts = opt_chain.puts
            
            # Calculate metrics
            iv_call = calls.impliedVolatility.mean() if not calls.empty else 0.3
            iv_put = puts.impliedVolatility.mean() if not puts.empty else 0.3
            put_call_ratio = len(puts) / max(len(calls), 1)
            skew = iv_put - iv_call
            
            return {
                "symbol": symbol,
                "implied_volatility_call": round(iv_call, 3),
                "implied_volatility_put": round(iv_put, 3),
                "put_call_ratio": round(put_call_ratio, 2),
                "volatility_skew": round(skew, 3),
                "total_options": len(calls) + len(puts),
                "expiration": nearest,
                "source": "yfinance",
                "trend": "bearish" if skew > 0.1 else "bullish" if skew < -0.1 else "neutral",
                "confidence": 0.6
            }
    except Exception as e:
        print(f"YFinance options fetch failed: {e}")
    
    # Mock data fallback
    return {
        "symbol": symbol,
        "implied_volatility_call": round(random.uniform(0.2, 0.5), 3),
        "implied_volatility_put": round(random.uniform(0.2, 0.5), 3),
        "put_call_ratio": round(random.uniform(0.8, 1.5), 2),
        "volatility_skew": round(random.uniform(-0.1, 0.1), 3),
        "total_options": random.randint(50, 200),
        "source": "mock",
        "trend": random.choice(["bullish", "neutral", "bearish"]),
        "confidence": random.uniform(0.4, 0.8)
    }

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, data: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze options data."""
    prompt = f"""You are an Options analyst. Analyze the following options data for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Options Data:
- Implied Volatility (Calls): {data.get('implied_volatility_call', 'N/A')}
- Implied Volatility (Puts): {data.get('implied_volatility_put', 'N/A')}
- Put/Call Ratio: {data.get('put_call_ratio', 'N/A')} (>1 = bearish sentiment, <1 = bullish)
- Volatility Skew: {data.get('volatility_skew', 'N/A')} (positive = puts more expensive, bearish; negative = calls more expensive, bullish)
- Total Options Contracts: {data.get('total_options', 'N/A')}
- Trend: {data.get('trend', 'N/A')}
- Data Source: {data.get('source', 'mock')}

Interpretation guidelines:
- High implied volatility (>0.4) suggests uncertainty, potential for large price moves.
- Put/Call ratio >1.2 indicates bearish sentiment, <0.8 bullish.
- Volatility skew positive (>0.05) suggests fear (bearish), negative (<-0.05) suggests greed (bullish).
- Consider overall market conditions and upcoming events.

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
    put_call_ratio = data.get("put_call_ratio", 1.0)
    skew = data.get("volatility_skew", 0.0)
    iv_call = data.get("implied_volatility_call", 0.3)
    iv_put = data.get("implied_volatility_put", 0.3)
    
    # Convert to floats
    try:
        put_call_ratio = float(put_call_ratio)
        skew = float(skew)
        iv_call = float(iv_call)
        iv_put = float(iv_put)
    except:
        put_call_ratio = 1.0
        skew = 0.0
        iv_call = 0.3
        iv_put = 0.3
    
    # Decision logic
    bearish_score = 0
    bullish_score = 0
    
    if put_call_ratio > 1.2:
        bearish_score += 1
    elif put_call_ratio < 0.8:
        bullish_score += 1
    
    if skew > 0.05:
        bearish_score += 1
    elif skew < -0.05:
        bullish_score += 1
    
    if iv_put > iv_call + 0.05:
        bearish_score += 1
    elif iv_call > iv_put + 0.05:
        bullish_score += 1
    
    if bearish_score > bullish_score:
        signal = "SELL"
        confidence = min(30 + bearish_score * 20, 80)
    elif bullish_score > bearish_score:
        signal = "BUY"
        confidence = min(30 + bullish_score * 20, 80)
    else:
        signal = "HOLD"
        confidence = 50
    
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Rule-based: Put/Call {put_call_ratio:.2f}, Skew {skew:.3f}, IV Call {iv_call:.3f}, IV Put {iv_put:.3f}",
        "summary": f"Options outlook: {signal}"
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
        data = fetch_options_data(symbol)
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
        print(f"\nOptions Analysis for {symbol}:")
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")
        print(f"Confidence: {result.get('analysis', {}).get('confidence', 'N/A')}%")
        print(f"Reasoning: {result.get('analysis', {}).get('reasoning', 'N/A')}")
