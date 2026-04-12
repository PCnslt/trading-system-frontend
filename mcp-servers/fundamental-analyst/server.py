#!/usr/bin/env python3
"""
MCP Server for Fundamental analysis tools (P/E, EPS, valuation) using real data and HuggingFace AI models
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from datetime import datetime
import requests
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize server
server = Server("fundamental-analyst")

# Load API keys from environment
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def fetch_fmp_data(endpoint: str, symbol: str) -> Dict:
    """Fetch data from Financial Modeling Prep API."""
    base_url = f"https://financialmodelingprep.com/api/v3/{endpoint}/{symbol}"
    params = {"apikey": FMP_API_KEY}
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]  # Return most recent
        elif isinstance(data, dict):
            return data
        else:
            return {}
    except Exception as e:
        raise Exception(f"Failed to fetch FMP data: {e}")

def get_fundamental_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch key fundamental metrics for a symbol."""
    metrics = {}
    
    # Fetch ratios
    ratios = fetch_fmp_data("ratios", symbol)
    if ratios:
        metrics["pe_ratio"] = ratios.get("priceEarningsRatio")
        metrics["peg_ratio"] = ratios.get("pegRatio")
        metrics["debt_to_equity"] = ratios.get("debtEquityRatio")
        metrics["return_on_equity"] = ratios.get("returnOnEquity")
        metrics["profit_margin"] = ratios.get("netProfitMargin")
    
    # Fetch key metrics
    key_metrics = fetch_fmp_data("key-metrics", symbol)
    if key_metrics:
        metrics["market_cap"] = key_metrics.get("marketCap")
        metrics["enterprise_value"] = key_metrics.get("enterpriseValue")
        metrics["ev_to_ebitda"] = key_metrics.get("evToEbitda")
        metrics["price_to_book"] = key_metrics.get("pbRatio")
        metrics["dividend_yield"] = key_metrics.get("dividendYield")
    
    # Fetch income statement (latest)
    income = fetch_fmp_data("income-statement", symbol)
    if income:
        metrics["revenue"] = income.get("revenue")
        metrics["gross_profit"] = income.get("grossProfit")
        metrics["net_income"] = income.get("netIncome")
        metrics["eps"] = income.get("eps")
    
    # Fetch balance sheet (latest)
    balance = fetch_fmp_data("balance-sheet-statement", symbol)
    if balance:
        metrics["total_assets"] = balance.get("totalAssets")
        metrics["total_liabilities"] = balance.get("totalLiabilities")
        metrics["shareholder_equity"] = balance.get("totalShareholderEquity")
        metrics["cash"] = balance.get("cashAndCashEquivalents")
    
    # Fetch cash flow (latest)
    cashflow = fetch_fmp_data("cash-flow-statement", symbol)
    if cashflow:
        metrics["operating_cash_flow"] = cashflow.get("operatingCashFlow")
        metrics["free_cash_flow"] = cashflow.get("freeCashFlow")
    
    return metrics

def call_huggingface(prompt: str) -> str:
    """Call HuggingFace Inference API with prompt."""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.2,
            "top_p": 0.95,
            "return_full_text": False
        }
    }
    try:
        response = requests.post(HF_INFERENCE_URL, headers=HF_HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "No output generated")
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        else:
            return str(result)
    except Exception as e:
        return f"Error calling HuggingFace model: {e}"

def analyze_with_ai(symbol: str, metrics: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze fundamental metrics and produce signal."""
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
    
    response = call_huggingface(prompt)
    # Try to extract JSON from response
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            ai_result = json.loads(json_match.group())
        else:
            ai_result = {"signal": "HOLD", "confidence": 50, "reasoning": response[:200], "summary": "AI analysis failed to produce structured output."}
    except Exception:
        ai_result = {"signal": "HOLD", "confidence": 50, "reasoning": "Failed to parse AI response.", "summary": "AI analysis error."}
    
    return ai_result

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for fundamental-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Fundamental analysis tools (P/E, EPS, valuation) using real data and AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock or asset symbol (e.g., AAPL, TSLA)"
                    },
                    "use_ai": {
                        "type": "boolean",
                        "description": "Use HuggingFace AI model for analysis (default: true)",
                        "default": True
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="health_check",
            description="Check fundamental-analyst health and API availability",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool execution requests"""
    
    symbol = arguments.get("symbol", "UNKNOWN").upper()
    
    if name == "analyze":
        use_ai = arguments.get("use_ai", True)
        
        try:
            # Fetch real fundamental metrics
            metrics = get_fundamental_metrics(symbol)
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(symbol, metrics)
                signal = ai_result.get("signal", "HOLD")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                summary = ai_result.get("summary", "")
            else:
                # Fallback rule-based analysis
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
                reasoning = "Rule-based analysis using P/E ratio"
                summary = f"Fundamental metrics: P/E={pe}, Debt/Equity={metrics.get('debt_to_equity', 'N/A')}, ROE={metrics.get('return_on_equity', 'N/A')}"
            
            # Format response
            response_text = f"Fundamental Analysis for {symbol}\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Signal: {signal} (Confidence: {confidence:.1%})\n"
            if metrics.get('pe_ratio'):
                response_text += f"P/E Ratio: {metrics['pe_ratio']:.2f}\n"
            if metrics.get('peg_ratio'):
                response_text += f"PEG Ratio: {metrics['peg_ratio']:.2f}\n"
            if metrics.get('debt_to_equity'):
                response_text += f"Debt-to-Equity: {metrics['debt_to_equity']:.2f}\n"
            if metrics.get('return_on_equity'):
                response_text += f"Return on Equity: {metrics['return_on_equity']:.2%}\n"
            if metrics.get('profit_margin'):
                response_text += f"Profit Margin: {metrics['profit_margin']:.2%}\n"
            if metrics.get('market_cap'):
                response_text += f"Market Cap: ${metrics['market_cap']:,.0f}\n"
            if metrics.get('dividend_yield'):
                response_text += f"Dividend Yield: {metrics['dividend_yield']:.2%}\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Summary: {summary}\n"
            
            # Add API status
            response_text += f"\nAPI Status: FMP {'✅' if FMP_API_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing fundamental analysis for {symbol}: {str(e)}\n"
            response_text += "Please check API keys and symbol validity."
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    elif name == "health_check":
        # Test API connectivity
        status = {
            "fmp": bool(FMP_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Fundamental Analyst Health Check\n\n"
        response_text += f"✅ FMP API: {'Configured' if status['fmp'] else 'Missing key'}\n"
        response_text += f"✅ HuggingFace Token: {'Configured' if status['huggingface'] else 'Missing token'}\n"
        response_text += f"🕒 Timestamp: {status['timestamp']}\n"
        
        if status['fmp'] and status['huggingface']:
            response_text += "\nStatus: ✅ FULLY OPERATIONAL\n"
        else:
            response_text += "\nStatus: ⚠️ PARTIALLY CONFIGURED\n"
            response_text += "Some functionality may be limited."
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    else:
        return [
            types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )
        ]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fundamental-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())