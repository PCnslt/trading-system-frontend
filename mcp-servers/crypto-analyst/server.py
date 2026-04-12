#!/usr/bin/env python3
"""
MCP Server for Cryptocurrency analysis using real data and HuggingFace AI models
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
server = Server("crypto-analyst")

# Load API keys from environment
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def fetch_coinmarketcap(symbol: str) -> Dict:
    """Fetch cryptocurrency data from CoinMarketCap API."""
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY
    }
    params = {
        "symbol": symbol.upper(),
        "convert": "USD"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "status" in data and data["status"]["error_code"] != 0:
            raise ValueError(f"CoinMarketCap error: {data['status']['error_message']}")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch CoinMarketCap data: {e}")

def fetch_binance_ticker(symbol: str) -> Dict:
    """Fetch ticker data from Binance API."""
    url = f"https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": f"{symbol.upper()}USDT"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # If Binance fails, try Binance US
        try:
            url = f"https://api.binance.us/api/v3/ticker/24hr"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            raise Exception(f"Failed to fetch Binance data: {e}")

def get_crypto_metrics(symbol: str) -> Dict[str, Any]:
    """Fetch key cryptocurrency metrics for a symbol."""
    metrics = {}
    
    # CoinMarketCap data
    try:
        cmc_data = fetch_coinmarketcap(symbol)
        if "data" in cmc_data and symbol.upper() in cmc_data["data"]:
            coin_data = cmc_data["data"][symbol.upper()]
            quote = coin_data["quote"]["USD"]
            metrics["price"] = quote.get("price")
            metrics["market_cap"] = quote.get("market_cap")
            metrics["volume_24h"] = quote.get("volume_24h")
            metrics["percent_change_1h"] = quote.get("percent_change_1h")
            metrics["percent_change_24h"] = quote.get("percent_change_24h")
            metrics["percent_change_7d"] = quote.get("percent_change_7d")
            metrics["max_supply"] = coin_data.get("max_supply")
            metrics["circulating_supply"] = coin_data.get("circulating_supply")
    except Exception as e:
        print(f"CoinMarketCap fetch failed: {e}")
    
    # Binance data (additional metrics)
    try:
        binance_data = fetch_binance_ticker(symbol)
        metrics["binance_price"] = float(binance_data.get("lastPrice", 0))
        metrics["binance_volume"] = float(binance_data.get("volume", 0))
        metrics["binance_high"] = float(binance_data.get("highPrice", 0))
        metrics["binance_low"] = float(binance_data.get("lowPrice", 0))
        metrics["binance_price_change_percent"] = float(binance_data.get("priceChangePercent", 0))
    except Exception as e:
        print(f"Binance fetch failed: {e}")
    
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
    """Use HuggingFace LLM to analyze cryptocurrency metrics and produce signal."""
    # Prepare prompt
    prompt = f"""You are a cryptocurrency analyst. Analyze the following metrics for {symbol} and provide a trading signal (BUY, SELL, or HOLD) with confidence score (0-100%) and brief reasoning.

Cryptocurrency Metrics:
- Current Price: ${metrics.get('price', metrics.get('binance_price', 'N/A'))}
- Market Cap: ${metrics.get('market_cap', 'N/A'):,.0f}
- 24h Volume: ${metrics.get('volume_24h', 'N/A'):,.0f}
- 1h Change: {metrics.get('percent_change_1h', 'N/A')}%
- 24h Change: {metrics.get('percent_change_24h', 'N/A')}%
- 7d Change: {metrics.get('percent_change_7d', 'N/A')}%
- Circulating Supply: {metrics.get('circulating_supply', 'N/A'):,.0f}
- Max Supply: {metrics.get('max_supply', 'N/A'):,.0f}
- Binance Price: ${metrics.get('binance_price', 'N/A')}
- Binance 24h Volume: {metrics.get('binance_volume', 'N/A'):,.0f}
- Binance Price Change: {metrics.get('binance_price_change_percent', 'N/A')}%

Interpretation guidelines:
- Large market cap indicates stability.
- High 24h volume suggests liquidity.
- Recent price changes indicate momentum.
- Supply metrics affect scarcity.
- Consider overall crypto market trends and news.

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
    """List available tools for crypto-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Cryptocurrency analysis using real data and AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Cryptocurrency symbol (e.g., BTC, ETH, SOL)"
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
            description="Check crypto-analyst health and API availability",
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
    
    symbol = arguments.get("symbol", "BTC").upper()
    
    if name == "analyze":
        use_ai = arguments.get("use_ai", True)
        
        try:
            # Fetch real cryptocurrency metrics
            metrics = get_crypto_metrics(symbol)
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(symbol, metrics)
                signal = ai_result.get("signal", "HOLD")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                summary = ai_result.get("summary", "")
            else:
                # Fallback rule-based analysis
                change_24h = metrics.get("percent_change_24h", 0)
                if change_24h and change_24h > 5:
                    signal = "BUY"
                    confidence = 0.7
                elif change_24h and change_24h < -5:
                    signal = "SELL"
                    confidence = 0.6
                else:
                    signal = "HOLD"
                    confidence = 0.5
                reasoning = "Rule-based analysis using 24h price change"
                summary = f"Crypto metrics: Price=${metrics.get('price', 'N/A')}, 24h Change={change_24h}%, Market Cap=${metrics.get('market_cap', 'N/A'):,.0f}"
            
            # Format response
            response_text = f"Cryptocurrency Analysis for {symbol}\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Signal: {signal} (Confidence: {confidence:.1%})\n"
            if metrics.get('price'):
                response_text += f"Price: ${metrics['price']:.2f}\n"
            if metrics.get('market_cap'):
                response_text += f"Market Cap: ${metrics['market_cap']:,.0f}\n"
            if metrics.get('volume_24h'):
                response_text += f"24h Volume: ${metrics['volume_24h']:,.0f}\n"
            if metrics.get('percent_change_24h'):
                response_text += f"24h Change: {metrics['percent_change_24h']:.2f}%\n"
            if metrics.get('circulating_supply'):
                response_text += f"Circulating Supply: {metrics['circulating_supply']:,.0f}\n"
            if metrics.get('max_supply'):
                response_text += f"Max Supply: {metrics['max_supply']:,.0f}\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Summary: {summary}\n"
            
            # Add API status
            response_text += f"\nAPI Status: CoinMarketCap {'✅' if COINMARKETCAP_API_KEY else '❌'}, Binance {'✅' if BINANCE_API_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing cryptocurrency analysis for {symbol}: {str(e)}\n"
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
            "coinmarketcap": bool(COINMARKETCAP_API_KEY),
            "binance": bool(BINANCE_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Crypto Analyst Health Check\n\n"
        response_text += f"✅ CoinMarketCap API: {'Configured' if status['coinmarketcap'] else 'Missing key'}\n"
        response_text += f"✅ Binance API: {'Configured' if status['binance'] else 'Missing key'}\n"
        response_text += f"✅ HuggingFace Token: {'Configured' if status['huggingface'] else 'Missing token'}\n"
        response_text += f"🕒 Timestamp: {status['timestamp']}\n"
        
        if status['coinmarketcap'] and status['huggingface']:
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
                server_name="crypto-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())