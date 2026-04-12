#!/usr/bin/env python3
"""
MCP Server for Options trading analysis using real data and HuggingFace AI models
"""

import asyncio
import json
import os
from typing import Any, Dict, List
from datetime import datetime
import requests
import yfinance as yf
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize server
server = Server("options-analyst")

# Load API keys from environment
OPTIONS_DATA_API_KEY = os.environ.get("OPTIONS_DATA_API_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def get_options_data(symbol: str) -> Dict[str, Any]:
    """Fetch options data for a symbol using yfinance."""
    metrics = {}
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get stock info
        info = ticker.info
        metrics["current_price"] = info.get("regularMarketPrice")
        metrics["bid"] = info.get("bid")
        metrics["ask"] = info.get("ask")
        metrics["volume"] = info.get("volume")
        
        # Get options expiration dates
        expirations = ticker.options
        if expirations:
            # Get nearest expiration
            nearest = expirations[0]
            options_chain = ticker.option_chain(nearest)
            
            # Calls
            calls = options_chain.calls
            if not calls.empty:
                metrics["call_volume"] = calls["volume"].sum()
                metrics["call_open_interest"] = calls["openInterest"].sum()
                metrics["call_implied_volatility"] = calls["impliedVolatility"].mean()
                metrics["call_last_price"] = calls["lastPrice"].mean()
            
            # Puts
            puts = options_chain.puts
            if not puts.empty:
                metrics["put_volume"] = puts["volume"].sum()
                metrics["put_open_interest"] = puts["openInterest"].sum()
                metrics["put_implied_volatility"] = puts["impliedVolatility"].mean()
                metrics["put_last_price"] = puts["lastPrice"].mean()
            
            # Calculate put/call ratio
            if metrics.get("call_volume") and metrics.get("put_volume"):
                metrics["put_call_ratio"] = metrics["put_volume"] / metrics["call_volume"]
            else:
                metrics["put_call_ratio"] = None
            
            metrics["expiration_date"] = nearest
    except Exception as e:
        raise Exception(f"Failed to fetch options data: {e}")
    
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
    """Use HuggingFace LLM to analyze options metrics and produce signal."""
    # Prepare prompt
    prompt = f"""You are an options trading analyst. Analyze the following options metrics for {symbol} and provide a trading signal (BUY_CALL, BUY_PUT, SELL_CALL, SELL_PUT, or HOLD) with confidence score (0-100%) and brief reasoning.

Options Metrics:
- Current Stock Price: ${metrics.get('current_price', 'N/A')}
- Bid/Ask: ${metrics.get('bid', 'N/A')}/${metrics.get('ask', 'N/A')}
- Stock Volume: {metrics.get('volume', 'N/A')}
- Call Volume: {metrics.get('call_volume', 'N/A')}
- Put Volume: {metrics.get('put_volume', 'N/A')}
- Call Open Interest: {metrics.get('call_open_interest', 'N/A')}
- Put Open Interest: {metrics.get('put_open_interest', 'N/A')}
- Call Implied Volatility: {metrics.get('call_implied_volatility', 'N/A'):.2%} average
- Put Implied Volatility: {metrics.get('put_implied_volatility', 'N/A'):.2%} average
- Call Last Price: ${metrics.get('call_last_price', 'N/A')}
- Put Last Price: ${metrics.get('put_last_price', 'N/A')}
- Put/Call Ratio: {metrics.get('put_call_ratio', 'N/A')}
- Nearest Expiration: {metrics.get('expiration_date', 'N/A')}

Interpretation guidelines:
- High put/call ratio (>1) indicates bearish sentiment.
- Low put/call ratio (<0.7) indicates bullish sentiment.
- High implied volatility suggests expensive options (possible selling opportunities).
- Low implied volatility suggests cheap options (possible buying opportunities).
- Volume and open interest indicate liquidity and trader interest.
- Consider stock price trend and overall market conditions.

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
    """List available tools for options-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Options trading analysis using real data and AI",
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
            description="Check options-analyst health and API availability",
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
            # Fetch real options data
            metrics = get_options_data(symbol)
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(symbol, metrics)
                signal = ai_result.get("signal", "HOLD")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                summary = ai_result.get("summary", "")
            else:
                # Fallback rule-based analysis
                put_call_ratio = metrics.get("put_call_ratio")
                if put_call_ratio and put_call_ratio > 1.2:
                    signal = "BUY_PUT"
                    confidence = 0.7
                elif put_call_ratio and put_call_ratio < 0.8:
                    signal = "BUY_CALL"
                    confidence = 0.7
                else:
                    signal = "HOLD"
                    confidence = 0.5
                reasoning = "Rule-based analysis using put/call ratio"
                summary = f"Options metrics: Put/Call Ratio={put_call_ratio}, Call IV={metrics.get('call_implied_volatility', 'N/A'):.2%}"
            
            # Format response
            response_text = f"Options Analysis for {symbol}\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Signal: {signal} (Confidence: {confidence:.1%})\n"
            if metrics.get('current_price'):
                response_text += f"Stock Price: ${metrics['current_price']:.2f}\n"
            if metrics.get('put_call_ratio'):
                response_text += f"Put/Call Ratio: {metrics['put_call_ratio']:.2f}\n"
            if metrics.get('call_implied_volatility'):
                response_text += f"Call Implied Volatility: {metrics['call_implied_volatility']:.2%}\n"
            if metrics.get('put_implied_volatility'):
                response_text += f"Put Implied Volatility: {metrics['put_implied_volatility']:.2%}\n"
            if metrics.get('call_volume'):
                response_text += f"Call Volume: {metrics['call_volume']:,}\n"
            if metrics.get('put_volume'):
                response_text += f"Put Volume: {metrics['put_volume']:,}\n"
            if metrics.get('expiration_date'):
                response_text += f"Nearest Expiration: {metrics['expiration_date']}\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Summary: {summary}\n"
            
            # Add API status
            response_text += f"\nAPI Status: Options Data API {'✅' if OPTIONS_DATA_API_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing options analysis for {symbol}: {str(e)}\n"
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
            "options_api": bool(OPTIONS_DATA_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Options Analyst Health Check\n\n"
        response_text += f"✅ Options Data API: {'Configured' if status['options_api'] else 'Missing key'}\n"
        response_text += f"✅ HuggingFace Token: {'Configured' if status['huggingface'] else 'Missing token'}\n"
        response_text += f"🕒 Timestamp: {status['timestamp']}\n"
        
        if status['options_api'] and status['huggingface']:
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
                server_name="options-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())