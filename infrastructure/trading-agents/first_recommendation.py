#!/usr/bin/env python3
"""
First Billionaire Recommendation - Using HuggingFace Llama 3.3 70B + Alpha Vantage
This script provides a stock recommendation while the full 10-agent system builds.
"""

import os
import sys
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "LNPH1SNZM9C4MT0")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")

# Configuration
SYMBOL = "AAPL"  # Apple Inc. - high liquidity, good for trading
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def fetch_stock_data(symbol: str) -> dict:
    """Fetch daily time series data from Alpha Vantage"""
    print(f"[CHART] Fetching data for {symbol}...")
    
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_KEY,
        "outputsize": "compact"  # Last 100 days
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "Time Series (Daily)" not in data:
            print(f"[WARNING] No data found for {symbol}. Using sample data.")
            # Return sample data if API fails
            return generate_sample_data()
        
        time_series = data["Time Series (Daily)"]
        dates = sorted(time_series.keys())[:20]  # Last 20 days
        
        prices = []
        volumes = []
        
        for date in dates:
            daily = time_series[date]
            prices.append(float(daily["4. close"]))
            volumes.append(int(daily["5. volume"]))
        
        # Calculate metrics
        current_price = prices[-1]
        prev_price = prices[-2] if len(prices) > 1 else current_price
        price_change = ((current_price - prev_price) / prev_price) * 100
        
        avg_volume = np.mean(volumes)
        recent_volume = volumes[-1]
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Simple RSI calculation (14-day)
        if len(prices) >= 15:
            gains = []
            losses = []
            for i in range(1, 15):
                change = prices[-i] - prices[-i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50  # Neutral
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "price_change_pct": price_change,
            "volume_ratio": volume_ratio,
            "rsi": rsi,
            "data_points": len(prices),
            "last_updated": dates[-1],
            "success": True
        }
        
    except Exception as e:
        print(f"[ERROR] Error fetching data: {e}")
        return generate_sample_data()

def generate_sample_data() -> dict:
    """Generate sample data if API fails"""
    return {
        "symbol": SYMBOL,
        "current_price": 255.63,
        "price_change_pct": 1.24,
        "volume_ratio": 1.15,
        "rsi": 58.7,
        "data_points": 20,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "success": False
    }

def analyze_with_ai(stock_data: dict) -> str:
    """Use HuggingFace Llama 3.3 70B for analysis"""
    print("[BRAIN] Analyzing with Llama 3.3 70B...")
    
    prompt = f"""You are a top-tier financial analyst. Analyze this stock data and provide a trading recommendation.

STOCK: {stock_data['symbol']}
CURRENT PRICE: ${stock_data['current_price']:.2f}
PRICE CHANGE: {stock_data['price_change_pct']:+.2f}%
VOLUME RATIO: {stock_data['volume_ratio']:.2f}x average
RSI: {stock_data['rsi']:.1f} (30=oversold, 70=overbought)

Based on this data, provide:
1. TRADING SIGNAL: BUY, SELL, or HOLD
2. CONFIDENCE LEVEL: 0-100%
3. PRIMARY REASON: Brief explanation
4. PRICE TARGET: Next 1-2 weeks
5. STOP LOSS: Risk management level
6. TIMEFRAME: When to enter/exit

Format your response as JSON:
{{
  "signal": "BUY/SELL/HOLD",
  "confidence": 85,
  "reason": "Brief explanation",
  "price_target": 260.50,
  "stop_loss": 245.00,
  "timeframe": "1-2 weeks",
  "risk_level": "Low/Medium/High"
}}"""

    try:
        response = requests.post(
            HF_INFERENCE_URL,
            headers=HF_HEADERS,
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                text = result[0].get("generated_text", str(result))
            else:
                text = str(result)
            
            # Try to parse JSON from response
            try:
                # Extract JSON from markdown if present
                lines = text.strip().split('\n')
                json_start = None
                json_end = None
                for i, line in enumerate(lines):
                    if line.strip().startswith('{'):
                        json_start = i
                        break
                
                if json_start is not None:
                    json_text = '\n'.join(lines[json_start:])
                    # Find matching closing brace
                    brace_count = 0
                    for j, char in enumerate(json_text):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_text = json_text[:j+1]
                                break
                    
                    analysis = json.loads(json_text)
                    return analysis
                else:
                    # Fallback: return text
                    return {"analysis": text, "raw": True}
                    
            except json.JSONDecodeError:
                return {"analysis": text, "raw": True}
        else:
            print(f"[ERROR] HuggingFace API error: {response.status_code}")
            return {"error": "API error", "status_code": response.status_code}
            
    except Exception as e:
        print(f"[ERROR] Error with AI analysis: {e}")
        return {"error": str(e)}

def generate_recommendation():
    """Generate complete recommendation"""
    print("\n" + "="*60)
    print("[MONEY] BILLIONAIRE TRADING RECOMMENDATION")
    print("="*60)
    
    # Fetch stock data
    stock_data = fetch_stock_data(SYMBOL)
    
    print(f"\n[DATA] DATA FOR {stock_data['symbol']}:")
    print(f"   Price: ${stock_data['current_price']:.2f}")
    print(f"   Change: {stock_data['price_change_pct']:+.2f}%")
    print(f"   Volume: {stock_data['volume_ratio']:.2f}x average")
    print(f"   RSI: {stock_data['rsi']:.1f}")
    
    # AI Analysis
    analysis = analyze_with_ai(stock_data)
    
    print("\n[ROBOT] AI RECOMMENDATION:")
    print("-"*40)
    
    if "error" in analysis:
        print(f"[WARNING] Analysis error: {analysis['error']}")
        # Generate fallback recommendation based on multiple factors
        rsi = stock_data['rsi']
        price_change = stock_data['price_change_pct']
        volume_ratio = stock_data['volume_ratio']
        
        # Score each factor
        rsi_score = 0
        if rsi < 30:
            rsi_score = 2  # Strong buy
        elif rsi < 40:
            rsi_score = 1  # Mild buy
        elif rsi > 70:
            rsi_score = -2  # Strong sell
        elif rsi > 60:
            rsi_score = -1  # Mild sell
        
        price_score = 0
        if price_change > 3:
            price_score = 2
        elif price_change > 1:
            price_score = 1
        elif price_change < -3:
            price_score = -2
        elif price_change < -1:
            price_score = -1
        
        volume_score = 1 if volume_ratio > 1.5 else 0
        
        total_score = rsi_score + price_score + volume_score
        
        if total_score >= 3:
            signal = "BUY"
            confidence = min(85, 60 + abs(total_score) * 10)
            reason = "Multiple strong positive indicators"
        elif total_score >= 1:
            signal = "BUY"
            confidence = 65
            reason = "Moderately positive indicators"
        elif total_score <= -3:
            signal = "SELL"
            confidence = min(85, 60 + abs(total_score) * 10)
            reason = "Multiple strong negative indicators"
        elif total_score <= -1:
            signal = "SELL"
            confidence = 65
            reason = "Moderately negative indicators"
        else:
            signal = "HOLD"
            confidence = 60
            reason = "Mixed or neutral indicators"
        
        if signal == "BUY":
            price_target = stock_data['current_price'] * 1.05
            stop_loss = stock_data['current_price'] * 0.96
        elif signal == "SELL":
            price_target = stock_data['current_price'] * 0.97
            stop_loss = stock_data['current_price'] * 1.02
        else:  # HOLD
            price_target = stock_data['current_price'] * 1.02  # small upside
            stop_loss = stock_data['current_price'] * 0.98
        
        print(f"   SIGNAL: {signal}")
        print(f"   CONFIDENCE: {confidence}%")
        print(f"   REASON: {reason}")
        print(f"   PRICE TARGET: ${price_target:.2f}")
        print(f"   STOP LOSS: ${stop_loss:.2f}")
        print(f"   TIMEFRAME: 1-2 weeks")
        
        recommendation = {
            "symbol": SYMBOL,
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "price_target": price_target,
            "stop_loss": stop_loss,
            "current_price": stock_data['current_price'],
            "potential_return_pct": ((price_target - stock_data['current_price']) / stock_data['current_price']) * 100,
            "risk_reward_ratio": abs((price_target - stock_data['current_price']) / (stock_data['current_price'] - stop_loss)) if signal == "BUY" else 1.5,
            "timestamp": datetime.now().isoformat()
        }
        
    elif analysis.get("raw"):
        print(f"   {analysis['analysis']}")
        recommendation = {
            "symbol": SYMBOL,
            "analysis": analysis['analysis'],
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Proper JSON analysis
        signal = analysis.get("signal", "HOLD")
        confidence = analysis.get("confidence", 50)
        reason = analysis.get("reason", "AI analysis")
        price_target = analysis.get("price_target", stock_data['current_price'] * 1.05)
        stop_loss = analysis.get("stop_loss", stock_data['current_price'] * 0.96)
        timeframe = analysis.get("timeframe", "1-2 weeks")
        risk_level = analysis.get("risk_level", "Medium")
        
        print(f"   SIGNAL: {signal}")
        print(f"   CONFIDENCE: {confidence}%")
        print(f"   REASON: {reason}")
        print(f"   PRICE TARGET: ${price_target:.2f}")
        print(f"   STOP LOSS: ${stop_loss:.2f}")
        print(f"   TIMEFRAME: {timeframe}")
        print(f"   RISK LEVEL: {risk_level}")
        
        recommendation = {
            "symbol": SYMBOL,
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "price_target": price_target,
            "stop_loss": stop_loss,
            "current_price": stock_data['current_price'],
            "potential_return_pct": ((price_target - stock_data['current_price']) / stock_data['current_price']) * 100,
            "risk_reward_ratio": abs((price_target - stock_data['current_price']) / (stock_data['current_price'] - stop_loss)) if signal == "BUY" else 1.5,
            "timeframe": timeframe,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat()
        }
    
    print("\n[CHART] POTENTIAL TRADE:")
    if "potential_return_pct" in recommendation:
        print(f"   Potential Return: {recommendation['potential_return_pct']:+.2f}%")
        print(f"   Risk/Reward Ratio: {recommendation['risk_reward_ratio']:.2f}:1")
    
    # Billionaire math
    print("\n[MONEY] BILLIONAIRE PATH:")
    print(f"   Starting Capital: $1,000")
    print(f"   Target: $1,000,000,000")
    
    # Calculate days at different return rates
    for daily_return in [0.5, 1.0, 1.5, 2.0]:
        days = np.log(1_000_000_000 / 1000) / np.log(1 + daily_return/100)
        years = days / 365
        print(f"   At {daily_return}%/day: {years:.1f} years ({int(days)} trading days)")
    
    print("\n" + "="*60)
    print("[SUCCESS] RECOMMENDATION COMPLETE")
    print("="*60)
    
    # Save to file
    with open("first_recommendation.json", "w") as f:
        json.dump(recommendation, f, indent=2)
    
    print(f"\n[SAVE] Saved to: first_recommendation.json")
    
    return recommendation

if __name__ == "__main__":
    try:
        recommendation = generate_recommendation()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        sys.exit(1)