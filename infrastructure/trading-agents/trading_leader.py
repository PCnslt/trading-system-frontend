#!/usr/bin/env python3
"""
Trading Leader - Makes final decisions based on all agent recommendations
Predicts which stock will go up the most by tomorrow
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import yfinance as yf
from enhanced_technical_analyst import EnhancedTechnicalAnalyst
from stock_scanner import StockScanner

class TradingLeader:
    """Leader agent that makes final trading decisions"""
    
    def __init__(self):
        self.scanner = StockScanner()
        self.technical_analyst = EnhancedTechnicalAnalyst()
        
        # Agent weights (can be adjusted based on historical performance)
        self.agent_weights = {
            "technical": 0.30,
            "fundamental": 0.25,
            "sentiment": 0.15,
            "macro": 0.10,
            "crypto": 0.05,
            "options": 0.05,
            "risk": 0.05,
            "quant": 0.03,
            "sector": 0.01,
            "compliance": 0.01
        }
        
        # Historical performance tracking
        self.performance_file = "data/leader_performance.json"
        
    def aggregate_signals(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate signals from all agents with weighted scoring"""
        
        # Group by symbol
        symbol_data = {}
        
        for result in agent_results:
            symbol = result.get("symbol")
            if not symbol:
                continue
            
            if symbol not in symbol_data:
                symbol_data[symbol] = {
                    "symbol": symbol,
                    "agent_signals": [],
                    "weighted_score": 0.0,
                    "total_weight": 0.0,
                    "current_price": result.get("current_price"),
                    "metadata": result.get("metadata", {})
                }
            
            agent_type = result.get("agent_type", "unknown")
            signal = result.get("final_signal", "HOLD")
            confidence = result.get("confidence", 0.5)
            weight = self.agent_weights.get(agent_type, 0.05)
            
            # Convert signal to numeric score
            if signal == "BUY":
                score = 1.0
            elif signal == "SELL":
                score = -1.0
            else:  # HOLD
                score = 0.0
            
            weighted_contribution = score * confidence * weight
            
            symbol_data[symbol]["agent_signals"].append({
                "agent": agent_type,
                "signal": signal,
                "confidence": confidence,
                "weight": weight,
                "contribution": weighted_contribution,
                "reasoning": result.get("reasoning", "")
            })
            
            symbol_data[symbol]["weighted_score"] += weighted_contribution
            symbol_data[symbol]["total_weight"] += weight
        
        # Calculate final scores
        final_recommendations = []
        
        for symbol, data in symbol_data.items():
            if data["total_weight"] > 0:
                normalized_score = data["weighted_score"] / data["total_weight"]
            else:
                normalized_score = 0.0
            
            # Determine final signal
            if normalized_score > 0.3:
                final_signal = "STRONG_BUY"
                signal_strength = min(0.95, (normalized_score + 1) / 2)
            elif normalized_score > 0.1:
                final_signal = "BUY"
                signal_strength = min(0.85, (normalized_score + 1) / 2)
            elif normalized_score < -0.3:
                final_signal = "STRONG_SELL"
                signal_strength = min(0.95, (-normalized_score + 1) / 2)
            elif normalized_score < -0.1:
                final_signal = "SELL"
                signal_strength = min(0.85, (-normalized_score + 1) / 2)
            else:
                final_signal = "HOLD"
                signal_strength = 0.5
            
            # Calculate expected return (simplified prediction)
            expected_return = self.predict_tomorrow_return(symbol, normalized_score)
            
            final_recommendations.append({
                "symbol": symbol,
                "final_signal": final_signal,
                "confidence": float(signal_strength),
                "aggregate_score": float(normalized_score),
                "expected_return": float(expected_return),
                "current_price": data.get("current_price"),
                "agent_count": len(data["agent_signals"]),
                "agent_contributions": data["agent_signals"],
                "timestamp": datetime.now().isoformat(),
                "reasoning": f"Aggregated from {len(data['agent_signals'])} agents with score {normalized_score:.3f}"
            })
        
        # Sort by expected return (highest first for BUY, lowest first for SELL)
        buy_recommendations = [r for r in final_recommendations if "BUY" in r["final_signal"]]
        sell_recommendations = [r for r in final_recommendations if "SELL" in r["final_signal"]]
        hold_recommendations = [r for r in final_recommendations if r["final_signal"] == "HOLD"]
        
        buy_recommendations.sort(key=lambda x: x["expected_return"], reverse=True)
        sell_recommendations.sort(key=lambda x: x["expected_return"])
        
        return {
            "buy_recommendations": buy_recommendations,
            "sell_recommendations": sell_recommendations,
            "hold_recommendations": hold_recommendations,
            "total_analyzed": len(final_recommendations),
            "timestamp": datetime.now().isoformat()
        }
    
    def predict_tomorrow_return(self, symbol: str, aggregate_score: float) -> float:
        """Predict tomorrow's return based on technicals and sentiment"""
        try:
            # Get recent data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="10d")
            
            if hist.empty or len(hist) < 5:
                return aggregate_score * 0.05  # Base prediction on aggregate score
            
            # Calculate recent volatility
            returns = hist['Close'].pct_change().dropna()
            recent_volatility = returns.std()
            
            # Calculate momentum
            recent_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) if len(hist) >= 5 else 0
            
            # Get RSI
            close_prices = hist['Close'].values
            import talib
            rsi = talib.RSI(close_prices, timeperiod=14)
            latest_rsi = rsi[-1] if len(rsi) > 0 and not np.isnan(rsi[-1]) else 50
            
            # Get volume trend
            volume_trend = hist['Volume'].iloc[-5:].mean() / hist['Volume'].iloc[-10:-5].mean() if len(hist) >= 10 else 1
            
            # Prediction formula
            base_prediction = aggregate_score * 0.03  # Base 3% max
            
            # Adjust based on RSI
            if latest_rsi < 30:  # Oversold
                rsi_adjustment = 0.01
            elif latest_rsi > 70:  # Overbought
                rsi_adjustment = -0.01
            else:
                rsi_adjustment = 0.0
            
            # Adjust based on momentum
            momentum_adjustment = recent_return * 0.5
            
            # Adjust based on volume
            volume_adjustment = 0.005 if volume_trend > 1.2 else -0.002 if volume_trend < 0.8 else 0.0
            
            # Combine predictions
            predicted_return = base_prediction + rsi_adjustment + momentum_adjustment + volume_adjustment
            
            # Cap predictions
            predicted_return = max(-0.10, min(0.10, predicted_return))
            
            return predicted_return
            
        except Exception as e:
            # Fallback prediction
            return aggregate_score * 0.02
    
    def make_final_decision(self, aggregated_results: Dict[str, Any]) -> Dict[str, Any]:
        """Make final decision on which stock to buy today"""
        
        buy_recommendations = aggregated_results.get("buy_recommendations", [])
        
        if not buy_recommendations:
            return {
                "decision": "NO_BUY",
                "reasoning": "No strong BUY recommendations from agents",
                "timestamp": datetime.now().isoformat()
            }
        
        # Select top recommendation
        top_recommendation = buy_recommendations[0]
        
        # Get additional data for final decision
        symbol = top_recommendation["symbol"]
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            decision = {
                "decision": "BUY",
                "symbol": symbol,
                "company_name": info.get("longName", symbol),
                "current_price": top_recommendation.get("current_price"),
                "expected_return": top_recommendation["expected_return"],
                "expected_price_tomorrow": top_recommendation.get("current_price", 0) * (1 + top_recommendation["expected_return"]),
                "confidence": top_recommendation["confidence"],
                "aggregate_score": top_recommendation["aggregate_score"],
                "agent_count": top_recommendation["agent_count"],
                "sector": info.get("sector", "Unknown"),
                "market_cap": info.get("marketCap"),
                "volume": info.get("volume"),
                "reasoning": f"Top recommendation with {top_recommendation['confidence']:.1%} confidence. "
                           f"Expected to rise {top_recommendation['expected_return']:.2%} by tomorrow. "
                           f"Based on analysis from {top_recommendation['agent_count']} agents.",
                "timestamp": datetime.now().isoformat(),
                "agent_breakdown": [
                    {
                        "agent": contrib["agent"],
                        "signal": contrib["signal"],
                        "confidence": contrib["confidence"],
                        "contribution": contrib["contribution"]
                    }
                    for contrib in top_recommendation.get("agent_contributions", [])[:3]
                ]
            }
            
            # Log decision
            self.log_decision(decision)
            
            return decision
            
        except Exception as e:
            return {
                "decision": "BUY",
                "symbol": symbol,
                "current_price": top_recommendation.get("current_price"),
                "expected_return": top_recommendation["expected_return"],
                "confidence": top_recommendation["confidence"],
                "reasoning": f"Fallback decision: {top_recommendation['reasoning']}. Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def log_decision(self, decision: Dict[str, Any]):
        """Log trading decision for performance tracking"""
        os.makedirs("data", exist_ok=True)
        
        log_entry = {
            "timestamp": decision["timestamp"],
            "decision": decision["decision"],
            "symbol": decision.get("symbol"),
            "expected_return": decision.get("expected_return", 0),
            "confidence": decision.get("confidence", 0),
            "actual_return": None,  # Will be updated tomorrow
            "correct": None  # Will be updated tomorrow
        }
        
        # Load existing log
        if os.path.exists(self.performance_file):
            with open(self.performance_file, "r") as f:
                try:
                    log_data = json.load(f)
                except:
                    log_data = {"decisions": []}
        else:
            log_data = {"decisions": []}
        
        # Add new decision
        log_data["decisions"].append(log_entry)
        
        # Keep only last 100 decisions
        if len(log_data["decisions"]) > 100:
            log_data["decisions"] = log_data["decisions"][-100:]
        
        # Save
        with open(self.performance_file, "w") as f:
            json.dump(log_data, f, indent=2)
    
    def update_performance(self):
        """Update performance metrics with actual returns"""
        if not os.path.exists(self.performance_file):
            return
        
        with open(self.performance_file, "r") as f:
            log_data = json.load(f)
        
        updated = False
        for decision in log_data["decisions"]:
            if decision.get("actual_return") is None and decision.get("symbol"):
                symbol = decision["symbol"]
                timestamp = datetime.fromisoformat(decision["timestamp"])
                
                # Check if it's been at least 1 day
                if datetime.now() - timestamp >= timedelta(days=1):
                    try:
                        # Get actual return
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(
                            start=timestamp.date(),
                            end=(timestamp + timedelta(days=2)).date()
                        )
                        
                        if not hist.empty and len(hist) >= 2:
                            buy_price = decision.get("current_price")
                            if not buy_price:
                                buy_price = hist['Close'].iloc[0]
                            
                            sell_price = hist['Close'].iloc[-1]
                            actual_return = (sell_price / buy_price - 1)
                            
                            decision["actual_return"] = float(actual_return)
                            decision["correct"] = (
                                actual_return > 0 and decision.get("decision") == "BUY" or
                                actual_return < 0 and decision.get("decision") == "SELL"
                            )
                            updated = True
                    except:
                        pass
        
        if updated:
            # Calculate performance metrics
            total_decisions = len([d for d in log_data["decisions"] if d.get("correct") is not None])
            correct_decisions = len([d for d in log_data["decisions"] if d.get("correct") == True])
            
            if total_decisions > 0:
                accuracy = correct_decisions / total_decisions
                log_data["performance_metrics"] = {
                    "total_decisions": total_decisions,
                    "correct_decisions": correct_decisions,
                    "accuracy": accuracy,
                    "last_updated": datetime.now().isoformat()
                }
            
            with open(self.performance_file, "w") as f:
                json.dump(log_data, f, indent=2)
    
    def run_daily_analysis(self, max_stocks: int = 100):
        """Run complete daily analysis pipeline"""
        print("=" * 60)
        print("TRADING LEADER - Daily Analysis")
        print("=" * 60)
        
        # Update performance from previous days
        print("\n📊 Updating performance metrics...")
        self.update_performance()
        
        # Get all stocks
        print("\n🔍 Scanning for stocks...")
        scanner = StockScanner()
        stocks = scanner.get_all_stocks()
        
        if len(stocks) > max_stocks:
            stocks = stocks[:max_stocks]
        
        print(f"📈 Analyzing {len(stocks)} stocks...")
        
        # Collect agent results (in production, would run all 10 agents)
        agent_results = []
        
        # Technical analysis
        print("  Running Technical Analyst...")
        technical_results = self.technical_analyst.analyze_all_stocks(max_stocks=len(stocks))
        for result in technical_results:
            result["agent_type"] = "technical"
            agent_results.append(result)
        
        # Note: Other agents would be added here
        # For now, we'll simulate them
        
        print("  Simulating other agents...")
        for stock in stocks[:20]:  # Simulate for first 20 stocks
            symbol = stock["symbol"]
            
            # Simulate fundamental analyst
            agent_results.append({
                "symbol": symbol,
                "agent_type": "fundamental",
                "final_signal": "BUY" if np.random.random() > 0.6 else "HOLD",
                "confidence": np.random.uniform(0.4, 0.9),
                "reasoning": "Simulated fundamental analysis",
                "current_price": stock.get("current_price")
            })
            
            # Simulate sentiment analyst
            agent_results.append({
                "symbol": symbol,
                "agent_type": "sentiment",
                "final_signal": "BUY" if np.random.random() > 0.5 else "HOLD",
                "confidence": np.random.uniform(0.3, 0.8),
                "reasoning": "Simulated sentiment analysis",
                "current_price": stock.get("current_price")
            })
        
        # Aggregate signals
        print("\n🤝 Aggregating agent signals...")
        aggregated = self.aggregate_signals(agent_results)
        
        print(f"  Total analyzed: {aggregated['total_analyzed']}")
        print(f"  BUY recommendations: {len(aggregated['buy_recommendations'])}")
        print(f"  SELL recommendations: {len(aggregated['sell_recommendations'])}")
        
        # Make final decision
        print("\n🎯 Making final decision...")
        final_decision = self.make_final_decision(aggregated)
        
        print("\n" + "=" * 60)
        print("FINAL DECISION")
        print("=" * 60)
        
        if final_decision["decision"] == "BUY":
            print(f"\n✅ BUY: {final_decision['symbol']}")
            print(f"   Company: {final_decision.get('company_name', 'N/A')}")
            print(f"   Current Price: ${final_decision.get('current_price', 0):.2f}")
            print(f"   Expected Return: {final_decision.get('expected_return', 0):.2%}")
            print(f"   Expected Price Tomorrow: ${final_decision.get('expected_price_tomorrow', 0):.2f}")
            print(f"   Confidence: {final_decision.get('confidence', 0):.1%}")
            print(f"   Reasoning: {final_decision.get('reasoning', '')}")
        else:
            print(f"\n⏸️  {final_decision.get('decision', 'NO_BUY')}")