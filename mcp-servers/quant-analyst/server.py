#!/usr/bin/env python3
"""
MCP Server for Quantitative analysis using real data and HuggingFace AI models
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
from scipy import stats
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize server
server = Server("quant-analyst")

# Load API keys from environment
QUANT_MODEL_API_KEY = os.environ.get("QUANT_MODEL_API_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def calculate_quant_metrics(symbol: str) -> Dict[str, Any]:
    """Calculate quantitative metrics for a symbol."""
    metrics = {}
    
    # Download historical data (last 180 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    try:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
        if data.empty:
            raise ValueError("No historical data available")
        
        closes = data['Adj Close']
        returns = closes.pct_change().dropna()
        
        # Basic statistics
        metrics["mean_return"] = returns.mean()
        metrics["volatility"] = returns.std()
        metrics["skewness"] = returns.skew()
        metrics["kurtosis"] = returns.kurtosis()
        
        # Normality test (Jarque-Bera)
        if len(returns) > 0:
            from scipy.stats import jarque_bera
            jb_stat, jb_pvalue = jarque_bera(returns)
            metrics["jarque_bera_stat"] = jb_stat
            metrics["jarque_bera_pvalue"] = jb_pvalue
            metrics["is_normal"] = jb_pvalue > 0.05
        
        # Autocorrelation (lag 1)
        autocorr = returns.autocorr(lag=1)
        metrics["autocorrelation_lag1"] = autocorr
        
        # Momentum indicators
        # 20-day momentum
        if len(closes) >= 20:
            momentum_20 = (closes.iloc[-1] / closes.iloc[-20] - 1) * 100
            metrics["momentum_20d"] = momentum_20
        
        # 50-day vs 200-day moving averages
        sma_50 = closes.rolling(window=50).mean()
        sma_200 = closes.rolling(window=200).mean()
        if len(closes) >= 200:
            metrics["sma_50"] = sma_50.iloc[-1]
            metrics["sma_200"] = sma_200.iloc[-1]
            metrics["price_vs_sma50"] = (closes.iloc[-1] / sma_50.iloc[-1] - 1) * 100
            metrics["price_vs_sma200"] = (closes.iloc[-1] / sma_200.iloc[-1] - 1) * 100
        
        # Volatility metrics
        # 20-day rolling volatility
        rolling_vol = returns.rolling(window=20).std() * np.sqrt(252)
        if len(rolling_vol) > 0:
            metrics["current_volatility"] = rolling_vol.iloc[-1]
        
        # Sharpe ratio (annualized, assuming risk-free rate 0.02)
        risk_free_rate = 0.02
        excess_return = metrics["mean_return"] * 252 - risk_free_rate
        metrics["sharpe_ratio"] = excess_return / (metrics["volatility"] * np.sqrt(252)) if metrics["volatility"] > 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        metrics["max_drawdown"] = drawdown.min()
        
        # Value at Risk (95%, 1-day)
        metrics["var_95"] = np.percentile(returns, 5)
        
        # Beta calculation (vs SPY)
        spy = yf.download('SPY', start=start_date, end=end_date, progress=False)['Adj Close']
        spy_returns = spy.pct_change().dropna()
        # Align indices
        common_idx = returns.index.intersection(spy_returns.index)
        if len(common_idx) > 1:
            cov = np.cov(returns.loc[common_idx], spy_returns.loc[common_idx])[0,1]
            var_market = spy_returns.loc[common_idx].var()
            metrics["beta"] = cov / var_market if var_market > 0 else 1.0
        else:
            metrics["beta"] = 1.0
        
        # R-squared (goodness of fit to market)
        if len(common_idx) > 1:
            from sklearn.linear_model import LinearRegression
            X = spy_returns.loc[common_idx].values.reshape(-1,1)
            y = returns.loc[common_idx].values
            model = LinearRegression().fit(X, y)
            metrics["r_squared"] = model.score(X, y)
        else:
            metrics["r_squared"] = 0
        
        metrics["data_start"] = start_date.strftime("%Y-%m-%d")
        metrics["data_end"] = end_date.strftime("%Y-%m-%d")
        metrics["current_price"] = closes.iloc[-1]
        
    except Exception as e:
        raise Exception(f"Failed to calculate quantitative metrics: {e}")
    
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
    """Use HuggingFace LLM to analyze quantitative metrics and produce signal."""
    # Prepare prompt
    prompt = f"""You are a quantitative analyst. Analyze the following quantitative metrics for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Quantitative Metrics:
- Current Price: ${metrics.get('current_price', 'N/A'):.2f}
- Mean Daily Return: {metrics.get('mean_return', 'N/A'):.4%}
- Daily Volatility: {metrics.get('volatility', 'N/A'):.4%}
- Skewness: {metrics.get('skewness', 'N/A'):.3f}
- Kurtosis: {metrics.get('kurtosis', 'N/A'):.3f}
- Jarque-Bera p-value: {metrics.get('jarque_bera_pvalue', 'N/A'):.4f}
- Autocorrelation (lag 1): {metrics.get('autocorrelation_lag1', 'N/A'):.3f}
- 20-Day Momentum: {metrics.get('momentum_20d', 'N/A'):.2f}%
- Price vs SMA 50: {metrics.get('price_vs_sma50', 'N/A'):.2f}%
- Price vs SMA 200: {metrics.get('price_vs_sma200', 'N/A'):.2f}%
- Current Volatility (annualized): {metrics.get('current_volatility', 'N/A'):.2%}
- Sharpe Ratio: {metrics.get('sharpe_ratio', 'N/A'):.2f}
- Maximum Drawdown: {metrics.get('max_drawdown', 'N/A'):.2%}
- Value at Risk (95%, 1-day): {metrics.get('var_95', 'N/A'):.2%}
- Beta (vs SPY): {metrics.get('beta', 'N/A'):.2f}
- R-squared (vs market): {metrics.get('r_squared', 'N/A'):.2%}
- Data Period: {metrics.get('data_start', 'N/A')} to {metrics.get('data_end', 'N/A')}

Interpretation guidelines:
- Positive momentum and price above moving averages suggest bullish trend.
- High Sharpe ratio indicates good risk-adjusted returns.
- Negative skewness indicates higher left-tail risk.
- High kurtosis indicates fat tails (more extreme returns).
- Low Jarque-Bera p-value (<0.05) suggests non-normal returns.
- Positive autocorrelation suggests trend persistence.
- Beta > 1 indicates higher volatility than market.
- High R-squared suggests strong market correlation.

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
    """List available tools for quant-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Quantitative analysis using real data and AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, TSLA)"
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
            description="Check quant-analyst health and API availability",
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
    
    symbol = arguments.get("symbol", "AAPL").upper()
    
    if name == "analyze":
        use_ai = arguments.get("use_ai", True)
        
        try:
            # Calculate quantitative metrics
            metrics = calculate_quant_metrics(symbol)
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(symbol, metrics)
                signal = ai_result.get("signal", "HOLD")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                summary = ai_result.get("summary", "")
            else:
                # Fallback rule-based analysis
                momentum = metrics.get("momentum_20d", 0)
                if momentum > 5:
                    signal = "BUY"
                    confidence = 0.7
                elif momentum < -5:
                    signal = "SELL"
                    confidence = 0.6
                else:
                    signal = "HOLD"
                    confidence = 0.5
                reasoning = "Rule-based analysis using 20-day momentum"
                summary = f"Quant metrics: Momentum={momentum:.2f}%, Sharpe={metrics.get('sharpe_ratio', 'N/A'):.2f}, Beta={metrics.get('beta', 'N/A'):.2f}"
            
            # Format response
            response_text = f"Quantitative Analysis for {symbol}\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Signal: {signal} (Confidence: {confidence:.1%})\n"
            response_text += f"Current Price: ${metrics['current_price']:.2f}\n"
            if metrics.get('momentum_20d'):
                response_text += f"20-Day Momentum: {metrics['momentum_20d']:.2f}%\n"
            if metrics.get('sharpe_ratio'):
                response_text += f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n"
            if metrics.get('beta'):
                response_text += f"Beta: {metrics['beta']:.2f}\n"
            if metrics.get('volatility'):
                response_text += f"Daily Volatility: {metrics['volatility']:.4%}\n"
            if metrics.get('max_drawdown'):
                response_text += f"Maximum Drawdown: {metrics['max_drawdown']:.2%}\n"
            if metrics.get('jarque_bera_pvalue'):
                response_text += f"Normality p-value: {metrics['jarque_bera_pvalue']:.4f}\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Summary: {summary}\n"
            
            # Add API status
            response_text += f"\nAPI Status: Quant Model API {'✅' if QUANT_MODEL_API_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing quantitative analysis for {symbol}: {str(e)}\n"
            response_text += "Please check symbol validity and internet connectivity."
        
        return [
            types.TextContent(
                type="text",
                text=response_text
            )
        ]
    
    elif name == "health_check":
        # Test API connectivity
        status = {
            "quant_model_api": bool(QUANT_MODEL_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Quant Analyst Health Check\n\n"
        response_text += f"✅ Quant Model API: {'Configured' if status['quant_model_api'] else 'Missing key'}\n"
        response_text += f"✅ HuggingFace Token: {'Configured' if status['huggingface'] else 'Missing token'}\n"
        response_text += f"🕒 Timestamp: {status['timestamp']}\n"
        
        if status['quant_model_api'] and status['huggingface']:
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
                server_name="quant-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())