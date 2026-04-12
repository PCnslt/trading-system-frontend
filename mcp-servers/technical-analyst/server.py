#!/usr/bin/env python3
"""
MCP Server for Technical analysis tools (RSI, MACD, trends) using real data and HuggingFace AI models
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from datetime import datetime
import numpy as np
import requests
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize server
server = Server("technical-analyst")

# Load API keys from environment
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def fetch_alpha_vantage(symbol: str, function: str, **params) -> Dict:
    """Fetch data from Alpha Vantage API."""
    base_url = "https://www.alphavantage.co/query"
    params.update({
        "function": function,
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_KEY,
        "datatype": "json"
    })
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch Alpha Vantage data: {e}")

def get_technical_indicators(symbol: str) -> Dict[str, Any]:
    """Fetch RSI, MACD, and SMA for a symbol."""
    indicators = {}
    
    # Fetch daily time series for recent prices
    daily = fetch_alpha_vantage(symbol, "TIME_SERIES_DAILY_ADJUSTED")
    time_series = daily.get("Time Series (Daily)", {})
    if not time_series:
        raise ValueError("No daily time series data available")
    
    # Get latest close price
    latest_date = list(time_series.keys())[0]
    latest_close = float(time_series[latest_date]["4. close"])
    indicators["latest_close"] = latest_close
    indicators["latest_date"] = latest_date
    
    # Fetch RSI (14-day)
    rsi_data = fetch_alpha_vantage(symbol, "RSI", interval="daily", time_period=14, series_type="close")
    rsi_series = rsi_data.get("Technical Analysis: RSI", {})
    if rsi_series:
        latest_rsi = float(rsi_series[latest_date]["RSI"])
        indicators["rsi"] = latest_rsi
    
    # Fetch MACD
    macd_data = fetch_alpha_vantage(symbol, "MACD", interval="daily", series_type="close")
    macd_series = macd_data.get("Technical Analysis: MACD", {})
    if macd_series:
        latest_macd = float(macd_series[latest_date]["MACD"])
        latest_signal = float(macd_series[latest_date]["MACD_Signal"])
        latest_hist = float(macd_series[latest_date]["MACD_Hist"])
        indicators["macd"] = latest_macd
        indicators["macd_signal"] = latest_signal
        indicators["macd_hist"] = latest_hist
    
    # Fetch SMA (50-day and 200-day)
    for period in [50, 200]:
        sma_data = fetch_alpha_vantage(symbol, "SMA", interval="daily", time_period=period, series_type="close")
        sma_series = sma_data.get(f"Technical Analysis: SMA", {})
        if sma_series and latest_date in sma_series:
            indicators[f"sma_{period}"] = float(sma_series[latest_date]["SMA"])
    
    return indicators

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

def analyze_with_ai(symbol: str, indicators: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze technical indicators and produce signal."""
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
    
    response = call_huggingface(prompt)
    # Try to extract JSON from response
    try:
        # Find JSON block
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
    """List available tools for technical-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Technical analysis tools (RSI, MACD, trends) using real data and AI",
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
            description="Check technical-analyst health and API availability",
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
            # Fetch real technical indicators
            indicators = get_technical_indicators(symbol)
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(symbol, indicators)
                signal = ai_result.get("signal", "HOLD")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                summary = ai_result.get("summary", "")
            else:
                # Fallback rule-based analysis
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
                reasoning = "Rule-based analysis using RSI"
                summary = f"Technical indicators: RSI={indicators.get('rsi', 'N/A')}, MACD={indicators.get('macd', 'N/A')}"
            
            # Format response
            response_text = f"Technical Analysis for {symbol}\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Signal: {signal} (Confidence: {confidence:.1%})\n"
            response_text += f"Latest Price: ${indicators.get('latest_close', 'N/A'):.2f}\n"
            if indicators.get('rsi'):
                response_text += f"RSI (14-day): {indicators['rsi']:.2f}\n"
            if indicators.get('macd'):
                response_text += f"MACD: {indicators['macd']:.4f} (Signal: {indicators.get('macd_signal', 'N/A'):.4f})\n"
            if indicators.get('sma_50'):
                response_text += f"SMA 50-day: ${indicators['sma_50']:.2f}\n"
            if indicators.get('sma_200'):
                response_text += f"SMA 200-day: ${indicators['sma_200']:.2f}\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Summary: {summary}\n"
            
            # Add API status
            response_text += f"\nAPI Status: Alpha Vantage {'✅' if ALPHA_VANTAGE_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing technical analysis for {symbol}: {str(e)}\n"
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
            "alpha_vantage": bool(ALPHA_VANTAGE_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Technical Analyst Health Check\n\n"
        response_text += f"✅ Alpha Vantage API: {'Configured' if status['alpha_vantage'] else 'Missing key'}\n"
        response_text += f"✅ HuggingFace Token: {'Configured' if status['huggingface'] else 'Missing token'}\n"
        response_text += f"🕒 Timestamp: {status['timestamp']}\n"
        
        if status['alpha_vantage'] and status['huggingface']:
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
                server_name="technical-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
