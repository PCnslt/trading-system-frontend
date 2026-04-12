#!/usr/bin/env python3
"""
Standalone Technical Analyst Agent
Performs RSI, MACD, SMA analysis using yfinance and HuggingFace Llama 3.3 70B
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
import numpy as np
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")

# HuggingFace Router API (replaces deprecated Inference API)
from hf_router import analyze_with_llm

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator."""
    if len(prices) < period + 1:
        return None
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 1
    rsi = 100 - 100 / (1 + rs)
    
    for i in range(period, len(deltas)):
        delta = deltas[i]
        if delta > 0:
            up_val = delta
            down_val = 0
        else:
            up_val = 0
            down_val = -delta
        
        up = (up * (period - 1) + up_val) / period
        down = (down * (period - 1) + down_val) / period
        rs = up / down if down != 0 else 1
        rsi = 100 - 100 / (1 + rs)
    
    return rsi

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average."""
    return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]

def calculate_macd(prices):
    """Calculate MACD (12,26,9)."""
    ema12 = calculate_ema(prices, 12)
    ema26 = calculate_ema(prices, 26)
    macd_line = ema12 - ema26
    # For signal line, we need MACD history; simplified
    signal_line = calculate_ema(prices[-9:] if len(prices) >= 9 else prices, 9)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_sma(prices, period):
    """Calculate Simple Moving Average."""
    if len(prices) >= period:
        return sum(prices[-period:]) / period
    return None

def get_technical_indicators(symbol: str) -> Dict[str, Any]:
    """Calculate RSI, MACD, and SMA for a symbol using yfinance."""
    indicators = {}
    
    try:
        # Download historical data (90 days enough for indicators)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="90d")
        if hist.empty:
            raise ValueError(f"No historical data for {symbol}")
        
        # Get latest close price and date
        latest_close = hist['Close'].iloc[-1]
        latest_date = hist.index[-1].strftime('%Y-%m-%d')
        indicators["latest_close"] = round(latest_close, 2)
        indicators["latest_date"] = latest_date
        
        # Calculate RSI (14-day)
        prices = hist['Close'].values
        rsi = calculate_rsi(prices, period=14)
        if rsi is not None:
            indicators["rsi"] = round(rsi, 2)
        
        # Calculate MACD (12,26,9)
        macd_line, macd_signal, macd_hist = calculate_macd(prices)
        indicators["macd"] = round(macd_line, 4)
        indicators["macd_signal"] = round(macd_signal, 4)
        indicators["macd_hist"] = round(macd_hist, 4)
        
        # Calculate SMA 50 and 200
        sma_50 = calculate_sma(prices, 50)
        sma_200 = calculate_sma(prices, 200)
        if sma_50 is not None:
            indicators["sma_50"] = round(sma_50, 2)
        if sma_200 is not None:
            indicators["sma_200"] = round(sma_200, 2)
        
        # Additional info
        indicators["volume"] = int(hist['Volume'].iloc[-1])
        indicators["high"] = round(hist['High'].iloc[-1], 2)
        indicators["low"] = round(hist['Low'].iloc[-1], 2)
        indicators["source"] = "yfinance"
        
        return indicators
        
    except Exception as e:
        raise Exception(f"Failed to calculate technical indicators: {e}")

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, indicators: Dict) -> Dict[str, Any]:
    """Use HuggingFace Router LLM to analyze technical indicators and produce signal."""
    # Prepare prompt
    prompt = f"""You are a financial technical analyst. Analyze the following technical indicators for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Technical Indicators:
- Latest Close Price: ${indicators.get('latest_close', 'N/A')} on {indicators.get('latest_date', 'N/A')}
- RSI (14-day): {indicators.get('rsi', 'N/A')} (oversold <30, overbought >70)
- MACD: {indicators.get('macd', 'N/A')}
- MACD Signal: {indicators.get('macd_signal', 'N/A')}
- MACD Histogram: {indicators.get('macd_hist', 'N/A')}
- SMA 50-day: {indicators.get('sma_50', 'N/A')}
- SMA 200-day: {indicators.get('sma_200', 'N/A')}

Interpretation guidelines:
- RSI above 70 suggests overbought (potential SELL), below 30 oversold (potential BUY).
- MACD above signal line suggests bullish momentum.
- Price above SMA 50 and SMA 200 suggests uptrend.
- Consider convergence/divergence of indicators.

Provide your analysis in JSON format with keys: signal, confidence, reasoning, summary.
"""
    try:
        ai_result = analyze_with_llm(prompt, json_output=True, max_tokens=300, temperature=0.2)
        # Ensure required keys exist
        if not isinstance(ai_result, dict):
            ai_result = {"signal": "HOLD", "confidence": 50, "reasoning": "AI returned non-dict", "summary": "AI analysis error."}
        # Validate signal
        signal = ai_result.get("signal", "").upper()
        if signal not in ["BUY", "SELL", "HOLD"]:
            ai_result["signal"] = "HOLD"
        # Ensure confidence is float
        if "confidence" in ai_result:
            try:
                ai_result["confidence"] = float(ai_result["confidence"])
            except:
                ai_result["confidence"] = 50
        return ai_result
    except Exception as e:
        return {"signal": "HOLD", "confidence": 50, "reasoning": f"AI analysis failed: {e}", "summary": "AI analysis error."}

def rule_based_analysis(indicators: Dict) -> Dict[str, Any]:
    """Fallback rule-based analysis if AI fails."""
    rsi = indicators.get("rsi")
    if rsi:
        if rsi < 30:
            signal = "BUY"
            confidence = (30 - rsi) / 30 * 0.5 + 0.5
        elif rsi > 70:
            signal = "SELL"
            confidence = (rsi - 70) / 30 * 0.5 + 0.5
        else:
            signal = "HOLD"
            confidence = 0.5
    else:
        signal = "HOLD"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Rule-based analysis using RSI ({rsi if rsi else 'N/A'})",
        "summary": f"Technical indicators: RSI={indicators.get('rsi', 'N/A')}, MACD={indicators.get('macd', 'N/A')}"
    }

def analyze_symbol(symbol: str, use_ai: bool = True) -> Dict[str, Any]:
    """Main analysis function for a symbol."""
    symbol = symbol.upper()
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "indicators": {},
        "analysis": {}
    }
    
    try:
        # Fetch technical indicators
        indicators = get_technical_indicators(symbol)
        result["indicators"] = indicators
        
        # Perform analysis
        if use_ai and HUGGINGFACE_TOKEN:
            analysis = analyze_with_ai(symbol, indicators)
        else:
            analysis = rule_based_analysis(indicators)
        
        result["analysis"] = analysis
        result["success"] = True
        
        # Calculate potential trade parameters
        if analysis["signal"] == "BUY":
            price_target = indicators["latest_close"] * 1.05  # 5% target
            stop_loss = indicators["latest_close"] * 0.96    # 4% stop loss
        elif analysis["signal"] == "SELL":
            price_target = indicators["latest_close"] * 0.97  # 3% target
            stop_loss = indicators["latest_close"] * 1.02    # 2% stop loss
        else:  # HOLD
            price_target = indicators["latest_close"] * 1.02
            stop_loss = indicators["latest_close"] * 0.98
        
        result["trade"] = {
            "current_price": indicators["latest_close"],
            "price_target": round(price_target, 2),
            "stop_loss": round(stop_loss, 2),
            "potential_return_pct": round(((price_target - indicators["latest_close"]) / indicators["latest_close"]) * 100, 2),
            "risk_reward_ratio": round(abs((price_target - indicators["latest_close"]) / (indicators["latest_close"] - stop_loss)), 2) if analysis["signal"] != "HOLD" else 1.0
        }
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def print_result(result: Dict):
    """Print analysis result in readable format."""
    if not result["success"]:
        print(f"❌ Analysis failed for {result['symbol']}: {result['error']}")
        return
    
    symbol = result["symbol"]
    indicators = result["indicators"]
    analysis = result["analysis"]
    trade = result.get("trade", {})
    
    print("\n" + "="*60)
    print(f"💰 TECHNICAL ANALYSIS: {symbol}")
    print("="*60)
    
    print(f"\n📊 INDICATORS:")
    print(f"   Price: ${indicators.get('latest_close', 'N/A'):.2f} ({indicators.get('latest_date', 'N/A')})")
    if 'rsi' in indicators:
        print(f"   RSI (14-day): {indicators['rsi']:.2f}")
    if 'macd' in indicators:
        print(f"   MACD: {indicators['macd']:.4f} (Signal: {indicators.get('macd_signal', 'N/A'):.4f})")
    if 'sma_50' in indicators:
        print(f"   SMA 50-day: ${indicators['sma_50']:.2f}")
    if 'sma_200' in indicators:
        print(f"   SMA 200-day: ${indicators['sma_200']:.2f}")
    
    print(f"\n🤖 ANALYSIS:")
    print(f"   Signal: {analysis.get('signal', 'HOLD')}")
    print(f"   Confidence: {analysis.get('confidence', 0.5):.1%}")
    print(f"   Reasoning: {analysis.get('reasoning', '')}")
    
    if trade:
        print(f"\n💸 TRADE PARAMETERS:")
        print(f"   Current Price: ${trade.get('current_price', 0):.2f}")
        print(f"   Price Target: ${trade.get('price_target', 0):.2f}")
        print(f"   Stop Loss: ${trade.get('stop_loss', 0):.2f}")
        print(f"   Potential Return: {trade.get('potential_return_pct', 0):+.2f}%")
        print(f"   Risk/Reward Ratio: {trade.get('risk_reward_ratio', 0):.2f}:1")
    
    print(f"\n⏰ Timestamp: {result['timestamp']}")
    print("="*60)

def main():
    """Command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Technical Analyst Agent")
    parser.add_argument("symbol", help="Stock symbol (e.g., AAPL, TSLA)")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI analysis (use rule-based)")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--save", help="Save result to JSON file")
    
    args = parser.parse_args()
    
    # Perform analysis
    result = analyze_symbol(args.symbol, use_ai=not args.no_ai)
    
    # Output
    if args.output == "json":
        output = json.dumps(result, indent=2)
        print(output)
    else:
        print_result(result)
    
    # Save to file if requested
    if args.save:
        with open(args.save, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved to: {args.save}")
    
    # Exit code
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()