#!/usr/bin/env python3
"""
Standalone Fundamental Analyst Agent
Performs P/E, EPS, valuation analysis using Financial Modeling Prep and HuggingFace AI
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
FMP_API_KEY = os.getenv("FMP_API_KEY", "YOUR_FMP_API_KEY_HERE")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "LNPH1SNZM9C4MT0")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")

# HuggingFace Router API (replaces deprecated Inference API)
from hf_router import analyze_with_llm

def fetch_alpha_vantage(symbol: str) -> Dict:
    """Fetch fundamental overview from Alpha Vantage."""
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_KEY
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch Alpha Vantage data: {e}")

def get_fundamental_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch key fundamental metrics for a symbol using Alpha Vantage."""
    metrics = {}
    
    # Fetch overview from Alpha Vantage
    overview = fetch_alpha_vantage(symbol)
    if not overview:
        return metrics
    
    # Map Alpha Vantage fields to our metric names
    mapping = {
        "YOUR_FMP_API_KEY_HERE": "market_cap",
        "PERatio": "pe_ratio", 
        "PEGRatio": "peg_ratio",
        "DividendYield": "dividend_yield",
        "EPS": "eps",
        "RevenueTTM": "revenue",
        "GrossProfitTTM": "gross_profit",
        "NetIncome": "net_income",
        "ProfitMargin": "profit_margin",
        "OperatingMarginTTM": "operating_margin",
        "ReturnOnEquityTTM": "return_on_equity",
        "ReturnOnAssetsTTM": "return_on_assets",
        "BookValue": "book_value",
        "PriceToBookRatio": "price_to_book",
        "EVToEBITDA": "ev_to_ebitda",
        "EVToRevenue": "ev_to_revenue",
        "Beta": "beta",
        "52WeekHigh": "week_high_52",
        "52WeekLow": "week_low_52",
        "50DayMovingAverage": "sma_50",
        "200DayMovingAverage": "sma_200",
        "SharesOutstanding": "shares_outstanding",
        "AnalystTargetPrice": "target_price"
    }
    
    for av_key, metric_key in mapping.items():
        if av_key in overview and overview[av_key] not in (None, "", "None"):
            try:
                # Convert string to appropriate type
                value = overview[av_key]
                if value == "None":
                    continue
                # Remove commas and convert
                if isinstance(value, str):
                    value = value.replace(",", "")
                # Try to convert to float if looks numeric
                if isinstance(value, str) and value.replace(".", "", 1).isdigit():
                    metrics[metric_key] = float(value)
                else:
                    metrics[metric_key] = value
            except Exception:
                pass
    
    # Calculate debt-to-equity if we have total liabilities and shareholder equity
    # Not directly available in OVERVIEW, maybe we need INCOME_STATEMENT
    # We'll skip for now
    
    # If we have market cap as string with suffix like "1.23B", convert to number
    if "market_cap" in metrics and isinstance(metrics["market_cap"], str):
        market_cap_str = metrics["market_cap"]
        # Parse suffixes B, M, T
        multipliers = {"B": 1e9, "M": 1e6, "T": 1e12}
        suffix = market_cap_str[-1].upper()
        if suffix in multipliers:
            try:
                num = float(market_cap_str[:-1])
                metrics["market_cap"] = num * multipliers[suffix]
            except:
                pass
    
    return metrics

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Router API with prompt."""
    try:
        result = analyze_with_llm(prompt, json_output=False, max_tokens=300, temperature=0.2)
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, metrics: Dict) -> Dict[str, Any]:
    """Use HuggingFace Router LLM to analyze fundamental metrics and produce signal."""
    # Prepare prompt
    prompt = f"""You are a financial fundamental analyst. Analyze the following fundamental metrics for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Fundamental Metrics:
- P/E Ratio: {metrics.get('pe_ratio', 'N/A')}
- PEG Ratio: {metrics.get('peg_ratio', 'N/A')}
- Debt-to-Equity: {metrics.get('debt_to_equity', 'N/A')}
- Return on Equity: {metrics.get('return_on_equity', 'N/A')}
- Profit Margin: {metrics.get('profit_margin', 'N/A')}
- Market Cap: {metrics.get('market_cap', 'N/A')}
- Enterprise Value: {metrics.get('enterprise_value', 'N/A')}
- EV/EBITDA: {metrics.get('ev_to_ebitda', 'N/A')}
- Price-to-Book: {metrics.get('price_to_book', 'N/A')}
- Dividend Yield: {metrics.get('dividend_yield', 'N/A')}
- Revenue: {metrics.get('revenue', 'N/A')}
- Net Income: {metrics.get('net_income', 'N/A')}
- EPS: {metrics.get('eps', 'N/A')}
- Total Assets: {metrics.get('total_assets', 'N/A')}
- Total Liabilities: {metrics.get('total_liabilities', 'N/A')}
- Shareholder Equity: {metrics.get('shareholder_equity', 'N/A')}
- Cash: {metrics.get('cash', 'N/A')}
- Operating Cash Flow: {metrics.get('operating_cash_flow', 'N/A')}
- Free Cash Flow: {metrics.get('free_cash_flow', 'N/A')}

Interpretation guidelines:
- P/E ratio compared to industry average; lower may indicate undervaluation.
- PEG ratio < 1 suggests undervalued growth.
- Debt-to-Equity > 2 indicates high leverage.
- ROE > 15% is strong.
- Profit margin trends.
- Positive free cash flow is healthy.
- Consider overall financial health and growth prospects.

Provide your analysis in JSON format with keys: signal, confidence, reasoning, summary.
"""
    try:
        ai_result = analyze_with_llm(prompt, json_output=True, max_tokens=300, temperature=0.2)
        # Ensure required keys exist and are correct types
        if not isinstance(ai_result, dict):
            ai_result = {"signal": "HOLD", "confidence": 50, "reasoning": "AI returned non-dict", "summary": "AI analysis error."}
        
        # Validate signal
        signal = ai_result.get("signal", "").upper()
        if signal not in ["BUY", "SELL", "HOLD"]:
            ai_result["signal"] = "HOLD"
        
        # Ensure confidence is float between 0-100
        if "confidence" in ai_result:
            try:
                conf = float(ai_result["confidence"])
                # If confidence appears to be between 0-1, scale to 0-100
                if conf <= 1.0:
                    conf = conf * 100
                ai_result["confidence"] = conf
            except (ValueError, TypeError):
                ai_result["confidence"] = 50.0
        else:
            ai_result["confidence"] = 50.0
        
        # Ensure reasoning is string (convert dict to JSON string if needed)
        reasoning = ai_result.get("reasoning", "")
        if isinstance(reasoning, dict):
            ai_result["reasoning"] = json.dumps(reasoning, indent=2)
        elif not isinstance(reasoning, str):
            ai_result["reasoning"] = str(reasoning)
        
        # Ensure summary is string
        summary = ai_result.get("summary", "")
        if isinstance(summary, dict):
            ai_result["summary"] = json.dumps(summary, indent=2)
        elif not isinstance(summary, str):
            ai_result["summary"] = str(summary)
        
        return ai_result
    except Exception as e:
        return {"signal": "HOLD", "confidence": 50.0, "reasoning": f"AI analysis failed: {e}", "summary": "AI analysis error."}

def rule_based_analysis(metrics: Dict) -> Dict[str, Any]:
    """Fallback rule-based analysis if AI fails."""
    pe = metrics.get("pe_ratio")
    if pe and pe < 15:
        signal = "BUY"
        confidence = 0.7
    elif pe and pe > 30:
        signal = "SELL"
        confidence = 0.6
    else:
        signal = "HOLD"
        confidence = 0.5
    
    return {
        "signal": signal,
        "confidence": confidence,
        "reasoning": f"Rule-based analysis using P/E ratio ({pe if pe else 'N/A'})",
        "summary": f"Fundamental metrics: P/E={pe}, Debt/Equity={metrics.get('debt_to_equity', 'N/A')}, ROE={metrics.get('return_on_equity', 'N/A')}"
    }

def analyze_symbol(symbol: str, use_ai: bool = True) -> Dict[str, Any]:
    """Main analysis function for a symbol."""
    symbol = symbol.upper()
    result = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "error": None,
        "metrics": {},
        "analysis": {}
    }
    
    try:
        # Fetch fundamental metrics
        metrics = get_fundamental_metrics(symbol)
        result["metrics"] = metrics
        
        # Perform analysis
        if use_ai and HUGGINGFACE_TOKEN:
            analysis = analyze_with_ai(symbol, metrics)
        else:
            analysis = rule_based_analysis(metrics)
        
        result["analysis"] = analysis
        result["success"] = True
        
        # Calculate potential trade parameters (simplified)
        if analysis["signal"] == "BUY":
            # Use P/E to estimate fair value
            pe = metrics.get("pe_ratio", 20)
            eps = metrics.get("eps", 0)
            if pe and eps:
                fair_value = eps * 15  # Assume target P/E of 15
                price_target = max(fair_value, metrics.get("market_cap", 0) / 1000000)  # rough
            else:
                price_target = metrics.get("market_cap", 0) / 1000000 * 1.05
            stop_loss = price_target * 0.94
        elif analysis["signal"] == "SELL":
            price_target = metrics.get("market_cap", 0) / 1000000 * 0.97
            stop_loss = price_target * 1.03
        else:  # HOLD
            price_target = metrics.get("market_cap", 0) / 1000000 * 1.02
            stop_loss = price_target * 0.98
        
        # If we have market cap, convert to per-share price (very rough)
        # For simplicity, just use placeholder
        current_price = 0  # Not available from FMP directly
        result["trade"] = {
            "current_price": current_price,
            "price_target": round(price_target, 2),
            "stop_loss": round(stop_loss, 2),
            "potential_return_pct": 0,
            "risk_reward_ratio": 1.0
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
    metrics = result["metrics"]
    analysis = result["analysis"]
    trade = result.get("trade", {})
    
    print("\n" + "="*60)
    print(f"💰 FUNDAMENTAL ANALYSIS: {symbol}")
    print("="*60)
    
    print(f"\n📊 METRICS:")
    if metrics.get('pe_ratio'):
        print(f"   P/E Ratio: {metrics['pe_ratio']:.2f}")
    if metrics.get('peg_ratio'):
        print(f"   PEG Ratio: {metrics['peg_ratio']:.2f}")
    if metrics.get('debt_to_equity'):
        print(f"   Debt-to-Equity: {metrics['debt_to_equity']:.2f}")
    if metrics.get('return_on_equity'):
        print(f"   Return on Equity: {metrics['return_on_equity']:.2%}")
    if metrics.get('profit_margin'):
        print(f"   Profit Margin: {metrics['profit_margin']:.2%}")
    if metrics.get('market_cap'):
        print(f"   Market Cap: ${metrics['market_cap']:,.0f}")
    if metrics.get('dividend_yield'):
        print(f"   Dividend Yield: {metrics['dividend_yield']:.2%}")
    if metrics.get('eps'):
        print(f"   EPS: ${metrics['eps']:.2f}")
    
    print(f"\n🤖 ANALYSIS:")
    print(f"   Signal: {analysis.get('signal', 'HOLD')}")
    print(f"   Confidence: {analysis.get('confidence', 0.5):.1%}")
    print(f"   Reasoning: {analysis.get('reasoning', '')}")
    
    if trade and trade.get('current_price'):
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
    
    parser = argparse.ArgumentParser(description="Fundamental Analyst Agent")
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