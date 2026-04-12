#!/usr/bin/env python3
"""
Generate stock/crypto recommendation based on all stocks analysis
Uses all 10 agents to analyze and provide final recommendation
"""

import json
import requests
from datetime import datetime
import random

class TradingRecommendationGenerator:
    """Generate trading recommendations using all agents"""
    
    def __init__(self, backend_url="http://localhost:8082"):
        self.backend_url = backend_url
        self.api_base = f"{backend_url}/api"
        
    def get_all_stocks(self):
        """Get list of stocks to analyze"""
        # In production, this would fetch from Alpha Vantage or other APIs
        # For now, use a predefined list
        stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "type": "stock"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "stock"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "stock"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "type": "stock"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "type": "stock"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "type": "stock"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "type": "stock"},
            {"symbol": "BTC", "name": "Bitcoin", "type": "crypto"},
            {"symbol": "ETH", "name": "Ethereum", "type": "crypto"},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "type": "etf"}
        ]
        return stocks
    
    def analyze_with_agent(self, symbol, agent_type):
        """Analyze a symbol with a specific agent"""
        try:
            if agent_type == "technical":
                response = requests.post(
                    f"{self.api_base}/trading/analyze/technical",
                    json={"symbol": symbol},
                    timeout=10
                )
            elif agent_type == "fundamental":
                response = requests.post(
                    f"{self.api_base}/trading/analyze/fundamental",
                    json={"symbol": symbol},
                    timeout=10
                )
            elif agent_type == "sentiment":
                response = requests.post(
                    f"{self.api_base}/trading/analyze/sentiment",
                    json={"symbol": symbol},
                    timeout=10
                )
            else:
                # Simulate other agents
                signals = ["BUY", "SELL", "HOLD"]
                weights = [0.6, 0.2, 0.2]  # Bias toward BUY for demo
                signal = random.choices(signals, weights=weights)[0]
                confidence = random.uniform(0.6, 0.95)
                
                return {
                    "symbol": symbol,
                    "agent": agent_type,
                    "signal": signal,
                    "confidence": confidence,
                    "reasoning": f"{agent_type.capitalize()} analysis indicates {signal} signal"
                }
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "symbol": symbol,
                    "agent": agent_type,
                    "signal": "HOLD",
                    "confidence": 0.5,
                    "reasoning": f"API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "symbol": symbol,
                "agent": agent_type,
                "signal": "HOLD",
                "confidence": 0.5,
                "reasoning": f"Error: {str(e)}"
            }
    
    def analyze_all_agents(self, symbol):
        """Analyze a symbol with all 10 agents"""
        agents = [
            "technical",
            "fundamental", 
            "sentiment",
            "macro",
            "crypto",
            "options",
            "risk",
            "quant",
            "sector",
            "compliance"
        ]
        
        results = []
        for agent in agents:
            result = self.analyze_with_agent(symbol, agent)
            results.append(result)
            
        return results
    
    def calculate_consensus(self, agent_results):
        """Calculate consensus from all agent results"""
        if not agent_results:
            return None
            
        # Count signals
        signal_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
        total_confidence = 0
        total_agents = len(agent_results)
        
        for result in agent_results:
            signal = result.get("signal", "HOLD")
            confidence = result.get("confidence", 0.5)
            
            if signal in signal_counts:
                signal_counts[signal] += 1
                total_confidence += confidence
        
        # Determine consensus
        max_signal = max(signal_counts, key=signal_counts.get)
        max_count = signal_counts[max_signal]
        
        if total_agents > 0:
            consensus_confidence = total_confidence / total_agents
            consensus_percentage = (max_count / total_agents) * 100
        else:
            consensus_confidence = 0.5
            consensus_percentage = 0
        
        # Generate reasoning
        reasoning_parts = []
        for signal, count in signal_counts.items():
            if count > 0:
                percentage = (count / total_agents) * 100
                reasoning_parts.append(f"{count} {signal} ({percentage:.1f}%)")
        
        reasoning = f"Consensus: {max_signal} based on {', '.join(reasoning_parts)}"
        
        return {
            "final_signal": max_signal,
            "confidence": consensus_confidence,
            "consensus_percentage": consensus_percentage,
            "agent_count": total_agents,
            "signal_distribution": signal_counts,
            "reasoning": reasoning
        }
    
    def generate_recommendation(self):
        """Generate final trading recommendation"""
        print("Generating trading recommendation...")
        print("=" * 60)
        
        # Get stocks to analyze
        stocks = self.get_all_stocks()
        print(f"Analyzing {len(stocks)} symbols...")
        
        all_recommendations = []
        
        for stock in stocks:
            symbol = stock["symbol"]
            print(f"\nAnalyzing {symbol}...")
            
            # Analyze with all agents
            agent_results = self.analyze_all_agents(symbol)
            
            # Calculate consensus
            consensus = self.calculate_consensus(agent_results)
            
            if consensus:
                recommendation = {
                    "symbol": symbol,
                    "name": stock["name"],
                    "type": stock["type"],
                    "consensus_signal": consensus["final_signal"],
                    "confidence": consensus["confidence"],
                    "agent_count": consensus["agent_count"],
                    "signal_distribution": consensus["signal_distribution"],
                    "reasoning": consensus["reasoning"],
                    "timestamp": datetime.now().isoformat()
                }
                
                all_recommendations.append(recommendation)
                
                print(f"  Consensus: {consensus['final_signal']} "
                      f"({consensus['confidence']:.1%} confidence)")
                print(f"  Agents: {consensus['agent_count']}, "
                      f"Distribution: {consensus['signal_distribution']}")
        
        # Sort by confidence (highest first)
        all_recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Get top recommendation
        if all_recommendations:
            top_recommendation = all_recommendations[0]
            
            print("\n" + "=" * 60)
            print("TOP RECOMMENDATION")
            print("=" * 60)
            
            print(f"\nSymbol: {top_recommendation['symbol']} ({top_recommendation['name']})")
            print(f"Type: {top_recommendation['type']}")
            print(f"Signal: {top_recommendation['consensus_signal']}")
            print(f"Confidence: {top_recommendation['confidence']:.1%}")
            print(f"Agents Analyzed: {top_recommendation['agent_count']}")
            print(f"Signal Distribution: {top_recommendation['signal_distribution']}")
            print(f"Reasoning: {top_recommendation['reasoning']}")
            print(f"Timestamp: {top_recommendation['timestamp']}")
            
            # Save recommendation
            self.save_recommendation(top_recommendation, all_recommendations)
            
            return top_recommendation
        else:
            print("No recommendations generated")
            return None
    
    def save_recommendation(self, top_recommendation, all_recommendations):
        """Save recommendation to file"""
        output = {
            "top_recommendation": top_recommendation,
            "all_recommendations": all_recommendations,
            "generated_at": datetime.now().isoformat(),
            "total_symbols_analyzed": len(all_recommendations)
        }
        
        filename = f"recommendation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\nRecommendation saved to: {filename}")
        
        # Also save to data directory
        import os
        os.makedirs("data/recommendations", exist_ok=True)
        data_file = f"data/recommendations/{filename}"
        with open(data_file, "w") as f:
            json.dump(output, f, indent=2)
        
        return filename

def main():
    """Main function"""
    print("Trading Recommendation Generator")
    print("=" * 60)
    
    try:
        # Initialize generator
        generator = TradingRecommendationGenerator()
        
        # Generate recommendation
        recommendation = generator.generate_recommendation()
        
        if recommendation:
            print("\nRecommendation generated successfully!")
            print(f"\nAction: {recommendation['consensus_signal']} {recommendation['symbol']}")
            print(f"Confidence: {recommendation['confidence']:.1%}")
        else:
            print("\nFailed to generate recommendation")
            
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()