#!/usr/bin/env python3
"""
MCP Server for Risk management analysis using real data and HuggingFace AI models
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from datetime import datetime, timedelta
import requests
import yfinance as yf
import numpy as np
import pandas as pd
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize server
server = Server("risk-analyst")

# Load API keys from environment
RISK_MODEL_API_KEY = os.environ.get("RISK_MODEL_API_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def calculate_portfolio_risk(symbols: List[str], weights: List[float] = None) -> Dict[str, Any]:
    """Calculate risk metrics for a portfolio."""
    if weights is None:
        weights = [1.0 / len(symbols)] * len(symbols)
    
    # Download historical data (last 90 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    try:
        # Fetch data
        data = yf.download(symbols, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError("No historical data available")
        
        # Calculate daily returns
        closes = data['Adj Close']
        returns = closes.pct_change().dropna()
        
        # Portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Risk metrics
        avg_return = portfolio_returns.mean() * 252  # annualized
        volatility = portfolio_returns.std() * np.sqrt(252)  # annualized
        
        # Sharpe ratio (assuming risk-free rate 0.02)
        risk_free_rate = 0.02
        sharpe = (avg_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Value at Risk (95% confidence, 1-day)
        var_95 = np.percentile(portfolio_returns, 5)
        
        # Maximum drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Beta (if SPY is in symbols, else assume market)
        if 'SPY' in symbols:
            spy_index = symbols.index('SPY')
            market_returns = returns.iloc[:, spy_index]
            covariance = portfolio_returns.cov(market_returns)
            market_variance = market_returns.var()
            beta = covariance / market_variance if market_variance > 0 else 1.0
        else:
            beta = 1.0  # approximation
        
        metrics = {
            "annualized_return": avg_return,
            "annualized_volatility": volatility,
            "sharpe_ratio": sharpe,
            "var_95": var_95,
            "max_drawdown": max_drawdown,
            "beta": beta,
            "num_assets": len(symbols),
            "portfolio_returns_mean": portfolio_returns.mean(),
            "portfolio_returns_std": portfolio_returns.std(),
            "data_start": start_date.strftime("%Y-%m-%d"),
            "data_end": end_date.strftime("%Y-%m-%d")
        }
        return metrics
    except Exception as e:
        raise Exception(f"Failed to calculate portfolio risk: {e}")

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

def analyze_with_ai(metrics: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze risk metrics and produce risk assessment."""
    # Prepare prompt
    prompt = f"""You are a risk management analyst. Analyze the following portfolio risk metrics and provide a risk assessment (LOW, MEDIUM, HIGH) with confidence score (0-100%) and brief reasoning.

Portfolio Risk Metrics:
- Annualized Return: {metrics.get('annualized_return', 'N/A'):.2%}
- Annualized Volatility: {metrics.get('annualized_volatility', 'N/A'):.2%}
- Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A'):.2f}
- Value at Risk (95%, 1-day): {metrics.get('var_95', 'N/A'):.2%}
- Maximum Drawdown: {metrics.get('max_drawdown', 'N/A'):.2%}
- Beta (vs market): {metrics.get('beta', 'N/A'):.2f}
- Number of Assets: {metrics.get('num_assets', 'N/A')}
- Portfolio Returns Mean (daily): {metrics.get('portfolio_returns_mean', 'N/A'):.4%}
- Portfolio Returns Std (daily): {metrics.get('portfolio_returns_std', 'N/A'):.4%}
- Data Period: {metrics.get('data_start', 'N/A')} to {metrics.get('data_end', 'N/A')}

Interpretation guidelines:
- Sharpe Ratio > 1 is good, > 2 is excellent.
- Volatility > 20% annual indicates high risk.
- Maximum drawdown > 20% indicates significant loss potential.
- VaR > 5% daily suggests high downside risk.
- Beta > 1 indicates higher volatility than market.
- Diversification (more assets) reduces unsystematic risk.

Provide your analysis in JSON format with keys: risk_level, confidence, reasoning, recommendations.
"""
    
    response = call_huggingface(prompt)
    # Try to extract JSON from response
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            ai_result = json.loads(json_match.group())
        else:
            ai_result = {"risk_level": "MEDIUM", "confidence": 50, "reasoning": response[:200], "recommendations": "AI analysis failed to produce structured output."}
    except Exception:
        ai_result = {"risk_level": "MEDIUM", "confidence": 50, "reasoning": "Failed to parse AI response.", "recommendations": "AI analysis error."}
    
    return ai_result

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for risk-analyst"""
    return [
        types.Tool(
            name="analyze_portfolio",
            description="Portfolio risk analysis using real data and AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of asset symbols (e.g., ['AAPL', 'TSLA', 'SPY'])"
                    },
                    "weights": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Portfolio weights (optional, defaults to equal weight)"
                    },
                    "use_ai": {
                        "type": "boolean",
                        "description": "Use HuggingFace AI model for analysis (default: true)",
                        "default": True
                    }
                },
                "required": ["symbols"]
            }
        ),
        types.Tool(
            name="health_check",
            description="Check risk-analyst health and API availability",
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
    
    if name == "analyze_portfolio":
        symbols = arguments.get("symbols", ["AAPL", "TSLA", "SPY"])
        weights = arguments.get("weights", None)
        use_ai = arguments.get("use_ai", True)
        
        try:
            # Calculate portfolio risk metrics
            metrics = calculate_portfolio_risk(symbols, weights)
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(metrics)
                risk_level = ai_result.get("risk_level", "MEDIUM")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                recommendations = ai_result.get("recommendations", "")
            else:
                # Fallback rule-based analysis
                volatility = metrics.get("annualized_volatility", 0)
                if volatility < 0.15:
                    risk_level = "LOW"
                    confidence = 0.8
                elif volatility < 0.3:
                    risk_level = "MEDIUM"
                    confidence = 0.7
                else:
                    risk_level = "HIGH"
                    confidence = 0.6
                reasoning = "Rule-based analysis using volatility"
                recommendations = "Consider diversification and hedging if risk is high."
            
            # Format response
            response_text = f"Portfolio Risk Analysis\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Risk Level: {risk_level} (Confidence: {confidence:.1%})\n"
            response_text += f"Portfolio Symbols: {', '.join(symbols)}\n"
            response_text += f"Annualized Return: {metrics['annualized_return']:.2%}\n"
            response_text += f"Annualized Volatility: {metrics['annualized_volatility']:.2%}\n"
            response_text += f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n"
            response_text += f"Value at Risk (95%, 1-day): {metrics['var_95']:.2%}\n"
            response_text += f"Maximum Drawdown: {metrics['max_drawdown']:.2%}\n"
            response_text += f"Beta: {metrics['beta']:.2f}\n"
            response_text += f"Number of Assets: {metrics['num_assets']}\n"
            response_text += f"Data Period: {metrics['data_start']} to {metrics['data_end']}\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Recommendations: {recommendations}\n"
            
            # Add API status
            response_text += f"\nAPI Status: Risk Model API {'✅' if RISK_MODEL_API_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing portfolio risk analysis: {str(e)}\n"
            response_text += "Please check symbols and internet connectivity."
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    elif name == "health_check":
        # Test API connectivity
        status = {
            "risk_model_api": bool(RISK_MODEL_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Risk Analyst Health Check\n\n"
        response_text += f"✅ Risk Model API: {'Configured' if status['risk_model_api'] else 'Missing key'}\n"
        response_text += f"✅ HuggingFace Token: {'Configured' if status['huggingface'] else 'Missing token'}\n"
        response_text += f"🕒 Timestamp: {status['timestamp']}\n"
        
        if status['risk_model_api'] and status['huggingface']:
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
                server_name="risk-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())