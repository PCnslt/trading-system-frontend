#!/usr/bin/env python3
"""
Risk Analyst Agent - Analyzes portfolio risk metrics (VaR, drawdown, volatility)
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

def fetch_risk_data(symbol="AAPL"):
    """Fetch risk data from yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="60d")
        if hist.empty:
            raise ValueError(f"No historical data for {symbol}")
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        # Risk metrics
        volatility = returns.std() * (252 ** 0.5)  # annualized volatility
        max_drawdown = (hist['Close'] / hist['Close'].cummax() - 1).min()
        var_95 = returns.quantile(0.05)  # 5% VaR (negative)
        sharpe = returns.mean() / returns.std() * (252 ** 0.5) if returns.std() > 0 else 0
        
        return {
            "symbol": symbol,
            "annual_volatility": round(volatility, 4),
            "max_drawdown": round(max_drawdown, 4),
            "var_95": round(var_95, 4),
            "sharpe_ratio": round(sharpe, 3),
            "avg_daily_return": round(returns.mean(), 4),
            "trend": "low_risk" if volatility < 0.2 else "high_risk",
            "confidence": min(0.9, 0.5 + 0.5 * (1 - abs(max_drawdown))),
            "source": "yfinance"
        }
    except Exception as e:
        print(f"Risk data fetch failed: {e}")
        # Mock data fallback
        return {
            "symbol": symbol,
            "annual_volatility": round(random.uniform(0.1, 0.5), 3),
            "max_drawdown": round(random.uniform(-0.3, -0.05), 3),
            "var_95": round(random.uniform(-0.05, -0.02), 3),
            "sharpe_ratio": round(random.uniform(-0.5, 2.0), 2),
            "trend": random.choice(["low_risk", "medium_risk", "high_risk"]),
            "confidence": random.uniform(0.4, 0.8),
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
    """Use HuggingFace LLM to analyze risk data."""
    prompt = f"""You are a Risk analyst. Analyze the following risk metrics for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Risk Metrics:
- Annualized Volatility: {data.get('annual_volatility', 'N/A')} (>0.3 = high risk, <0.2 = low risk)
- Maximum Drawdown: {data.get('max_drawdown', 'N/A')} (negative, closer to 0 = better)
- 95% Value at Risk (VaR): {data.get('var_95', 'N/A')} (negative, expected worst daily loss)
- Sharpe Ratio: {data.get('sharpe_ratio', 'N/A')} (>1 = good risk-adjusted return)
- Average Daily Return: {data.get('avg_daily_return', 'N/A')}
- Risk Trend: {data.get('trend', 'N/A')}
- Data Source: {data.get('source', 'mock')}

Interpretation guidelines:
- High volatility (>0.3) suggests higher risk, may require SELL or reduced position.
- Large drawdown (<-0.2) indicates significant historical losses, caution.
- VaR more negative than -0.03 suggests high potential for losses.
- Sharpe ratio <0 indicates poor risk-adjusted returns.
- Consider overall market conditions and risk tolerance.

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
    volatility = data.get("annual_volatility", 0.3)
    max_drawdown = data.get("max_drawdown", -0.1)
    sharpe = data.get("sharpe_ratio", 0)
    
    try:
        volatility = float(volatility)
        max_drawdown = float(max_drawdown)
        sharpe = float(sharpe)
    except:
        volatility = 0.3
        max_drawdown = -0.1
        sharpe = 0
    
    risk_score = 0
    if volatility > 0.35:
        risk_score += 2
    elif volatility > 0.25:
        risk_score += 1
    
    if max_drawdown < -0.25:
        risk_score += 2
    elif max_drawdown < -0.15:
        risk_score += 1
    
    if sharpe < 0:
        risk_score += 1
    elif sharpe > 1:
        risk_score -= 1
    
    if risk_score >= 3:
        signal = "SELL"
        confidence = min(30 + risk_score * 15, 80)
    elif risk_score <= 1:
        signal = "BUY"
        confidence = 60
    else:
        signal = "HOLD"
        confidence = 50
    
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Rule-based: Volatility {volatility:.3f}, Max Drawdown {max_drawdown:.3f}, Sharpe {sharpe:.2f}",
        "summary": f"Risk outlook: {signal}"
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
        data = fetch_risk_data(symbol)
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
        print(f"\nRisk Analysis for {symbol}:")
        print(f"Signal: {result.get('analysis', {}).get('signal', 'N/A')}")
        print(f"Confidence: {result.get('analysis', {}).get('confidence', 'N/A')}%")
        print(f"Reasoning: {result.get('analysis', {}).get('reasoning', 'N/A')}")
