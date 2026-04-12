#!/usr/bin/env python3
"""
Complete Trading Pipeline - Runs ALL 10 agents on ALL stocks
Generates final buy recommendation for today
"""

import os
import json
import sys
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import concurrent.futures
from stock_scanner import StockScanner
from trading_leader import TradingLeader

# Import all agents
try:
    from technical_analyst import analyze_symbol as technical_analyze
    TECHNICAL_AVAILABLE = True
except ImportError:
    print("⚠️  Technical analyst not found")
    TECHNICAL_AVAILABLE = False

try:
    from fundamental_analyst import analyze_symbol as fundamental_analyze
    FUNDAMENTAL_AVAILABLE = True
except ImportError:
    print("⚠️  Fundamental analyst not found")
    FUNDAMENTAL_AVAILABLE = False

try:
    from sentiment_analyst import analyze_symbol as sentiment_analyze
    SENTIMENT_AVAILABLE = True
except ImportError:
    print("⚠️  Sentiment analyst not found")
    SENTIMENT_AVAILABLE = False

try:
    from macro_analyst import analyze_symbol as macro_analyze
    MACRO_AVAILABLE = True
except ImportError:
    print("⚠️  Macro analyst not found")
    MACRO_AVAILABLE = False

try:
    from crypto_analyst import analyze_symbol as crypto_analyze
    CRYPTO_AVAILABLE = True
except ImportError:
    print("⚠️  Crypto analyst not found")
    CRYPTO_AVAILABLE = False

try:
    from options_analyst import analyze_symbol as options_analyze
    OPTIONS_AVAILABLE = True
except ImportError:
    print("⚠️  Options analyst not found")
    OPTIONS_AVAILABLE = False

try:
    from risk_analyst import analyze_symbol as risk_analyze
    RISK_AVAILABLE = True
except ImportError:
    print("⚠️  Risk analyst not found")
    RISK_AVAILABLE = False

try:
    from quant_analyst import analyze_symbol as quant_analyze
    QUANT_AVAILABLE = True
except ImportError:
    print("⚠️  Quant analyst not found")
    QUANT_AVAILABLE = False

try:
    from sector_analyst import analyze_symbol as sector_analyze
    SECTOR_AVAILABLE = True
except ImportError:
    print("⚠️  Sector analyst not found")
    SECTOR_AVAILABLE = False

try:
    from compliance_analyst import analyze_symbol as compliance_analyze
    COMPLIANCE_AVAILABLE = True
except ImportError:
    print("⚠️  Compliance analyst not found")
    COMPLIANCE_AVAILABLE = False

class CompleteTradingPipeline:
    """Complete pipeline with all 10 agents"""
    
    def __init__(self):
        self.scanner = StockScanner()
        self.leader = TradingLeader()
        self.agent_config = self._load_agent_config()
        
    def _load_agent_config(self) -> Dict[str, Any]:
        """Load agent configuration"""
        return {
            "technical": {
                "enabled": TECHNICAL_AVAILABLE,
                "function": technical_analyze if TECHNICAL_AVAILABLE else None,
                "weight": 0.30,
                "description": "Technical analysis (RSI, MACD, trends)"
            },
            "fundamental": {
                "enabled": FUNDAMENTAL_AVAILABLE,
                "function": fundamental_analyze if FUNDAMENTAL_AVAILABLE else None,
                "weight": 0.25,
                "description": "Fundamental analysis (P/E, margins, valuation)"
            },
            "sentiment": {
                "enabled": SENTIMENT_AVAILABLE,
                "function": sentiment_analyze if SENTIMENT_AVAILABLE else None,
                "weight": 0.15,
                "description": "News and social media sentiment"
            },
            "macro": {
                "enabled": MACRO_AVAILABLE,
                "function": macro_analyze if MACRO_AVAILABLE else None,
                "weight": 0.10,
                "description": "Macroeconomic factors"
            },
            "crypto": {
                "enabled": CRYPTO_AVAILABLE,
                "function": crypto_analyze if CRYPTO_AVAILABLE else None,
                "weight": 0.05,
                "description": "Cryptocurrency analysis"
            },
            "options": {
                "enabled": OPTIONS_AVAILABLE,
                "function": options_analyze if OPTIONS_AVAILABLE else None,
                "weight": 0.05,
                "description": "Options flow analysis"
            },
            "risk": {
                "enabled": RISK_AVAILABLE,
                "function": risk_analyze if RISK_AVAILABLE else None,
                "weight": 0.05,
                "description": "Risk assessment"
            },
            "quant": {
                "enabled": QUANT_AVAILABLE,
                "function": quant_analyze if QUANT_AVAILABLE else None,
                "weight": 0.03,
                "description": "Quantitative models"
            },
            "sector": {
                "enabled": SECTOR_AVAILABLE,
                "function": sector_analyze if SECTOR_AVAILABLE else None,
                "weight": 0.01,
                "description": "Sector rotation analysis"
            },
            "compliance": {
                "enabled": COMPLIANCE_AVAILABLE,
                "function": compliance_analyze if COMPLIANCE_AVAILABLE else None,
                "weight": 0.01,
                "description": "Regulatory compliance"
            }
        }
    
    def analyze_with_agent(self, symbol: str, agent_name: str, agent_func) -> Dict[str, Any]:
        """Analyze a symbol with a specific agent"""
        try:
            result = agent_func(symbol)
            result["agent_type"] = agent_name
            result["symbol"] = symbol
            return result
        except Exception as e:
            return {
                "symbol": symbol,
                "agent_type": agent_name,
                "final_signal": "HOLD",
                "confidence": 0.3,
                "reasoning": f"Agent error: {str(e)}",
                "error": True
            }
    
    def analyze_symbol_all_agents(self, symbol: str) -> List[Dict[str, Any]]:
        """Analyze a symbol with ALL 10 agents"""
        results = []
        
        for agent_name, config in self.agent_config.items():
            if config["enabled"] and config["function"]:
                result = self.analyze_with_agent(symbol, agent_name, config["function"])
                results.append(result)
        
        return results
    
    def run_parallel_analysis(self, symbols: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
        """Run analysis on multiple symbols in parallel"""
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all analysis tasks
            future_to_symbol = {}
            for symbol in symbols:
                future = executor.submit(self.analyze_symbol_all_agents, symbol)
                future_to_symbol[future] = symbol
            
            # Collect results
            completed = 0
            total = len(symbols)
            
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                completed += 1
                
                try:
                    results = future.result()
                    all_results.extend(results)
                    
                    print(f"  Analyzed {completed}/{total}: {symbol} "
                          f"({len(results)} agents)")
                    
                except Exception as e:
                    print(f"  Error analyzing {symbol}: {e}")
        
        return all_results
    
    def run_daily_pipeline(self, max_stocks: int = 50) -> Dict[str, Any]:
        """Run complete daily pipeline"""
        print("=" * 70)
        print("COMPLETE TRADING PIPELINE - Daily Analysis")
        print("=" * 70)
        
        # Step 1: Get ALL stocks
        print("\n📊 STEP 1: Scanning ALL stocks...")
        stocks = self.scanner.get_all_stocks()
        
        if len(stocks) > max_stocks:
            stocks = stocks[:max_stocks]
        
        symbols = [stock["symbol"] for stock in stocks]
        print(f"  Selected {len(symbols)} stocks for analysis")
        
        # Step 2: Run ALL 10 agents on ALL stocks
        print(f"\n🤖 STEP 2: Running ALL 10 agents...")
        
        enabled_agents = [name for name, config in self.agent_config.items() 
                         if config["enabled"]]
        print(f"  Enabled agents: {', '.join(enabled_agents)}")
        
        agent_results = self.run_parallel_analysis(symbols, max_workers=10)
        
        print(f"\n✅ Agent analysis complete:")
        print(f"  Total analyses: {len(agent_results)}")
        print(f"  Unique symbols: {len(set(r['symbol'] for r in agent_results))}")
        
        # Step 3: Aggregate signals
        print(f"\n🤝 STEP 3: Aggregating signals...")
        aggregated = self.leader.aggregate_signals(agent_results)
        
        print(f"  BUY recommendations: {len(aggregated['buy_recommendations'])}")
        print(f"  SELL recommendations: {len(aggregated['sell_recommendations'])}")
        print(f"  HOLD recommendations: {len(aggregated['hold_recommendations'])}")
        
        # Step 4: Make final decision
        print(f"\n🎯 STEP 4: Making final decision...")
        final_decision = self.leader.make_final_decision(aggregated)
        
        # Step 5: Generate report
        print(f"\n📋 STEP 5: Generating report...")
        report = self.generate_daily_report(aggregated, final_decision, agent_results)
        
        # Save results
        self.save_results(report, final_decision, agent_results)
        
        return {
            "report": report,
            "final_decision": final_decision,
            "agent_results": len(agent_results),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_daily_report(self, aggregated: Dict[str, Any], 
                             final_decision: Dict[str, Any],
                             agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive daily report"""
        
        # Agent performance summary
        agent_summary = {}
        for result in agent_results:
            agent = result.get("agent_type", "unknown")
            if agent not in agent_summary:
                agent_summary[agent] = {
                    "count": 0,
                    "buy_signals": 0,
                    "sell_signals": 0,
                    "hold_signals": 0,
                    "avg_confidence": 0.0
                }
            
            agent_summary[agent]["count"] += 1
            signal = result.get("final_signal", "HOLD")
            if signal == "BUY":
                agent_summary[agent]["buy_signals"] += 1
            elif signal == "SELL":
                agent_summary[agent]["sell_signals"] += 1
            else:
                agent_summary[agent]["hold_signals"] += 1
            
            agent_summary[agent]["avg_confidence"] += result.get("confidence", 0.5)
        
        # Calculate averages
        for agent in agent_summary:
            if agent_summary[agent]["count"] > 0:
                agent_summary[agent]["avg_confidence"] /= agent_summary[agent]["count"]
        
        # Top BUY recommendations
        top_buys = aggregated.get("buy_recommendations", [])[:5]
        
        # Top SELL recommendations
        top_sells = aggregated.get("sell_recommendations", [])[:5]
        
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "analysis_summary": {
                "total_stocks_analyzed": aggregated.get("total_analyzed", 0),
                "total_agent_analyses": len(agent_results),
                "enabled_agents": len([a for a in self.agent_config.values() if a["enabled"]]),
                "processing_time": datetime.now().isoformat()
            },
            "agent_summary": agent_summary,
            "top_buy_recommendations": [
                {
                    "symbol": rec["symbol"],
                    "confidence": rec["confidence"],
                    "expected_return": rec.get("expected_return", 0),
                    "aggregate_score": rec.get("aggregate_score", 0),
                    "agent_count": rec.get("agent_count", 0)
                }
                for rec in top_buys
            ],
            "top_sell_recommendations": [
                {
                    "symbol": rec["symbol"],
                    "confidence": rec["confidence"],
                    "expected_return": rec.get("expected_return", 0),
                    "aggregate_score": rec.get("aggregate_score", 0),
                    "agent_count": rec.get("agent_count", 0)
                }
                for rec in top_sells
            ],
            "final_decision_summary": {
                "decision": final_decision.get("decision"),
                "symbol": final_decision.get("symbol"),
                "confidence": final_decision.get("confidence"),
                "expected_return": final_decision.get("expected_return"),
                "reasoning": final_decision.get("reasoning", "")[:200]
            },
            "market_conditions": {
                "timestamp": datetime.now().isoformat(),
                "agents_operational": len(enabled_agents)
            }
        }
        
        return report
    
    def save_results(self, report: Dict[str, Any], 
                    final_decision: Dict[str, Any],
                    agent_results: List[Dict[str, Any]]):
        """Save all results to files"""
        os.makedirs("data/daily_reports", exist_ok=True)
        os.makedirs("data/agent_results", exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Save report
        report_file = f"data/daily_reports/report_{date_str}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Save final decision
        decision_file = f"data/daily_reports/decision_{date_str}.json"
        with open(decision_file, "w") as f:
            json.dump(final_decision, f, indent=2)
        
        # Save agent results (sampled)
        if agent_results:
            sample_results = agent_results[:100]  # Save first 100
            results_file = f"data/agent_results/results_{date_str}.json"
            with open(results_file, "w") as f:
                json.dump(sample_results, f, indent=2)
        
        print(f"\n💾 Results saved:")
        print(f"  Report: {report_file}")
        print(f"  Decision: {decision_file}")
        print(f"  Agent results: {results_file if agent_results else 'Not saved'}")
    
    def print_final_report(self, pipeline_result: Dict[str, Any]):
        """Print final report to console"""
        report = pipeline_result.get("report", {})
        final_decision = pipeline_result.get("final_decision", {})
        
        print("\n" + "=" * 70)
        print("DAILY TRADING REPORT")
        print("=" * 70)
        
        print(f"\n📅 Date: {report.get('date', 'Unknown')}")
        print(f"📊 Analysis Summary:")
        print(f"  Stocks Analyzed: {report.get('analysis_summary', {}).get('total_stocks_analyzed', 0)}")
        print(f"  Agent Analyses: {report.get('analysis_summary', {}).get('total_agent_analyses', 0)}")
        print(f"  Enabled Agents: {report.get('analysis_summary', {}).get('enabled_agents', 0)}")
        
        print(f"\n🤖 Agent Summary:")
        agent_summary = report.get("agent_summary", {})
        for agent, stats in agent_summary.items():
            print(f"  {agent}: {stats['count']} analyses, "
                  f"{stats['buy_signals']} BUY, {stats['sell_signals']} SELL, "
                  f"{stats['hold_signals']} HOLD, "
                  f"avg confidence: {stats['avg_confidence']:.2f}")
        
        print(f"\n✅ Top BUY Recommendations:")
        top_buys = report.get("top_buy_recommendations", [])
        for i, rec in enumerate(top_buys, 1):
            print(f"  {i}. {rec['symbol']}: "
                  f"{rec['confidence']:.1%} confidence, "
                  f"expected return: {rec['expected_return']:.2%}, "
                  f"agents: {rec['agent_count']}")
        
        print(f"\n❌ Top SELL Recommendations:")
        top_sells = report.get("top_sell_recommendations", [])
        for i, rec in enumerate(top_sells, 1):
            print(f"  {i}. {rec['symbol']}: "
                  f"{rec['confidence']:.1%} confidence, "
                  f"expected return: {rec['expected_return']:.2%}, "
                  f"agents: {rec['agent_count']}")
        
        print(f"\n🎯 FINAL DECISION:")
        decision_summary = report.get("final_decision_summary", {})
        if decision_summary.get("decision") == "BUY":
            print(f"  ✅ BUY: {decision_summary['symbol']}")
            print(f"     Confidence: {decision_summary['confidence']:.1%}")
            print(f"     Expected Return: {decision_summary['expected_return']:.2%}")
            print(f"     Reasoning: {decision_summary['reasoning']}")
        else:
            print(f"  ⏸️  {decision_summary.get('decision', 'NO_BUY')}")
            print(f"     {decision_summary.get('reasoning', 'No strong