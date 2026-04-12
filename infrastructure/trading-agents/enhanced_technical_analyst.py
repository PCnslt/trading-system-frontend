#!/usr/bin/env python3
"""
Enhanced Technical Analyst - Analyzes ALL stocks with comprehensive technical indicators
"""

import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List
import talib
from stock_scanner import StockScanner

class EnhancedTechnicalAnalyst:
    """Technical analysis for ALL stocks"""
    
    def __init__(self):
        self.scanner = StockScanner()
        
    def calculate_all_indicators(self, symbol: str, period: str = "3mo") -> Dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty or len(hist) < 20:
                return {"error": "Insufficient data"}
            
            # Convert to numpy arrays for TA-Lib
            close_prices = hist['Close'].values
            high_prices = hist['High'].values
            low_prices = hist['Low'].values
            volume = hist['Volume'].values
            
            # Trend indicators
            sma_20 = talib.SMA(close_prices, timeperiod=20)
            sma_50 = talib.SMA(close_prices, timeperiod=50)
            sma_200 = talib.SMA(close_prices, timeperiod=200)
            ema_12 = talib.EMA(close_prices, timeperiod=12)
            ema_26 = talib.EMA(close_prices, timeperiod=26)
            
            # Momentum indicators
            rsi = talib.RSI(close_prices, timeperiod=14)
            macd, macd_signal, macd_hist = talib.MACD(close_prices)
            stoch_k, stoch_d = talib.STOCH(high_prices, low_prices, close_prices)
            williams = talib.WILLR(high_prices, low_prices, close_prices, timeperiod=14)
            
            # Volatility indicators
            bollinger_upper, bollinger_middle, bollinger_lower = talib.BBANDS(
                close_prices, timeperiod=20, nbdevup=2, nbdevdn=2
            )
            atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)
            
            # Volume indicators
            obv = talib.OBV(close_prices, volume)
            ad = talib.AD(high_prices, low_prices, close_prices, volume)
            
            # Get latest values
            latest_close = close_prices[-1]
            latest_sma_20 = sma_20[-1] if not np.isnan(sma_20[-1]) else None
            latest_sma_50 = sma_50[-1] if not np.isnan(sma_50[-1]) else None
            latest_sma_200 = sma_200[-1] if not np.isnan(sma_200[-1]) else None
            latest_rsi = rsi[-1] if not np.isnan(rsi[-1]) else None
            latest_macd = macd[-1] if not np.isnan(macd[-1]) else None
            latest_macd_signal = macd_signal[-1] if not np.isnan(macd_signal[-1]) else None
            
            # Generate signals
            signals = []
            confidence = 0.5
            
            # RSI signal
            if latest_rsi:
                if latest_rsi < 30:
                    signals.append(("RSI Oversold", "BUY", 0.7))
                    confidence += 0.15
                elif latest_rsi > 70:
                    signals.append(("RSI Overbought", "SELL", 0.7))
                    confidence -= 0.15
                else:
                    signals.append(("RSI Neutral", "HOLD", 0.5))
            
            # MACD signal
            if latest_macd and latest_macd_signal:
                if latest_macd > latest_macd_signal:
                    signals.append(("MACD Bullish", "BUY", 0.6))
                    confidence += 0.1
                else:
                    signals.append(("MACD Bearish", "SELL", 0.6))
                    confidence -= 0.1
            
            # Moving average signals
            if latest_sma_20 and latest_sma_50:
                if latest_close > latest_sma_20 > latest_sma_50:
                    signals.append(("Strong Uptrend", "BUY", 0.8))
                    confidence += 0.2
                elif latest_close < latest_sma_20 < latest_sma_50:
                    signals.append(("Strong Downtrend", "SELL", 0.8))
                    confidence -= 0.2
            
            # Bollinger Bands
            if bollinger_lower[-1] and bollinger_upper[-1]:
                if latest_close <= bollinger_lower[-1]:
                    signals.append(("BB Lower Band", "BUY", 0.6))
                    confidence += 0.1
                elif latest_close >= bollinger_upper[-1]:
                    signals.append(("BB Upper Band", "SELL", 0.6))
                    confidence -= 0.1
            
            # Determine final signal
            buy_signals = sum(1 for s in signals if s[1] == "BUY")
            sell_signals = sum(1 for s in signals if s[1] == "SELL")
            
            if buy_signals > sell_signals:
                final_signal = "BUY"
                confidence = min(0.95, confidence)
            elif sell_signals > buy_signals:
                final_signal = "SELL"
                confidence = min(0.95, abs(confidence))
            else:
                final_signal = "HOLD"
                confidence = 0.5
            
            return {
                "symbol": symbol,
                "current_price": float(latest_close),
                "indicators": {
                    "sma_20": float(latest_sma_20) if latest_sma_20 else None,
                    "sma_50": float(latest_sma_50) if latest_sma_50 else None,
                    "sma_200": float(latest_sma_200) if latest_sma_200 else None,
                    "rsi": float(latest_rsi) if latest_rsi else None,
                    "macd": float(latest_macd) if latest_macd else None,
                    "macd_signal": float(latest_macd_signal) if latest_macd_signal else None,
                    "bollinger_upper": float(bollinger_upper[-1]) if not np.isnan(bollinger_upper[-1]) else None,
                    "bollinger_lower": float(bollinger_lower[-1]) if not np.isnan(bollinger_lower[-1]) else None,
                    "atr": float(atr[-1]) if not np.isnan(atr[-1]) else None,
                    "obv": float(obv[-1]) if not np.isnan(obv[-1]) else None
                },
                "signals": [
                    {
                        "indicator": s[0],
                        "signal": s[1],
                        "strength": s[2]
                    } for s in signals
                ],
                "final_signal": final_signal,
                "confidence": float(confidence),
                "reasoning": f"Technical analysis: {buy_signals} buy vs {sell_signals} sell signals",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "final_signal": "HOLD",
                "confidence": 0.3,
                "reasoning": f"Technical analysis failed: {e}"
            }
    
    def analyze_all_stocks(self, max_stocks: int = 50) -> List[Dict[str, Any]]:
        """Analyze ALL stocks with technical indicators"""
        print(f"🔍 Technical Analyst: Scanning {max_stocks} stocks...")
        
        # Get all stocks
        stocks = self.scanner.get_all_stocks()
        if len(stocks) > max_stocks:
            stocks = stocks[:max_stocks]
        
        results = []
        for i, stock in enumerate(stocks):
            symbol = stock["symbol"]
            print(f"  Analyzing {i+1}/{len(stocks)}: {symbol}")
            
            result = self.calculate_all_indicators(symbol)
            results.append(result)
        
        # Sort by confidence (highest first)
        results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        print(f"✅ Technical analysis complete: {len(results)} stocks analyzed")
        return results
    
    def get_top_recommendations(self, results: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top BUY recommendations"""
        buy_recommendations = [
            r for r in results 
            if r.get("final_signal") == "BUY" and r.get("confidence", 0) > 0.6
        ]
        
        # Sort by confidence
        buy_recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return buy_recommendations[:top_n]

def main():
    """Test the enhanced technical analyst"""
    analyst = EnhancedTechnicalAnalyst()
    
    print("=" * 60)
    print("ENHANCED TECHNICAL ANALYST - Testing")
    print("=" * 60)
    
    # Analyze a sample stock
    print("\n🔍 Analyzing sample stock (AAPL)...")
    result = analyst.calculate_all_indicators("AAPL")
    
    if "error" not in result:
        print(f"\n📊 Results for {result['symbol']}:")
        print(f"  Current Price: ${result['current_price']:.2f}")
        print(f"  Final Signal: {result['final_signal']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Reasoning: {result['reasoning']}")
        
        print(f"\n📈 Indicators:")
        for key, value in result['indicators'].items():
            if value is not None:
                print(f"  {key}: {value:.4f}")
        
        print(f"\n🚦 Signals:")
        for signal in result['signals'][:5]:  # Show first 5
            print(f"  {signal['indicator']}: {signal['signal']} (strength: {signal['strength']})")
    
    # Test batch analysis
    print("\n" + "=" * 60)
    print("Testing batch analysis of 10 stocks...")
    results = analyst.analyze_all_stocks(max_stocks=10)
    
    print(f"\n📊 Top BUY recommendations:")
    top_buys = analyst.get_top_recommendations(results, top_n=5)
    
    for i, rec in enumerate(top_buys, 1):
        print(f"  {i}. {rec['symbol']}: {rec['final_signal']} "
              f"(confidence: {rec['confidence']:.2%}, "
              f"price: ${rec.get('current_price', 0):.2f})")

if __name__ == "__main__":
    main()