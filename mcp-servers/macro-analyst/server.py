#!/usr/bin/env python3
"""
MCP Server for Macroeconomic analysis using real data and HuggingFace AI models
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
server = Server("macro-analyst")

# Load API keys from environment
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
OECD_API_KEY = os.environ.get("OECD_API_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def fetch_alpha_vantage_economic(function: str) -> Dict:
    """Fetch economic data from Alpha Vantage API."""
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
        "apikey": ALPHA_VANTAGE_KEY,
        "datatype": "json"
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch Alpha Vantage economic data: {e}")

def get_macro_indicators() -> Dict[str, Any]:
    """Fetch key macroeconomic indicators."""
    indicators = {}
    
    # Real GDP (quarterly)
    try:
        gdp_data = fetch_alpha_vantage_economic("REAL_GDP")
        if "data" in gdp_data and len(gdp_data["data"]) > 0:
            latest_gdp = gdp_data["data"][0]
            indicators["gdp"] = float(latest_gdp["value"])
            indicators["gdp_date"] = latest_gdp["date"]
    except Exception as e:
        print(f"Could not fetch GDP: {e}")
    
    # CPI (monthly)
    try:
        cpi_data = fetch_alpha_vantage_economic("CPI")
        if "data" in cpi_data and len(cpi_data["data"]) > 0:
            latest_cpi = cpi_data["data"][0]
            indicators["cpi"] = float(latest_cpi["value"])
            indicators["cpi_date"] = latest_cpi["date"]
    except Exception as e:
        print(f"Could not fetch CPI: {e}")
    
    # Unemployment rate
    try:
        unemp_data = fetch_alpha_vantage_economic("UNEMPLOYMENT")
        if "data" in unemp_data and len(unemp_data["data"]) > 0:
            latest_unemp = unemp_data["data"][0]
            indicators["unemployment"] = float(latest_unemp["value"])
            indicators["unemployment_date"] = latest_unemp["date"]
    except Exception as e:
        print(f"Could not fetch unemployment: {e}")
    
    # Federal funds rate
    try:
        fedfunds_data = fetch_alpha_vantage_economic("FEDERAL_FUNDS_RATE")
        if "data" in fedfunds_data and len(fedfunds_data["data"]) > 0:
            latest_fed = fedfunds_data["data"][0]
            indicators["fed_funds_rate"] = float(latest_fed["value"])
            indicators["fed_funds_date"] = latest_fed["date"]
    except Exception as e:
        print(f"Could not fetch federal funds rate: {e}")
    
    # Retail sales (optional)
    try:
        retail_data = fetch_alpha_vantage_economic("RETAIL_SALES")
        if "data" in retail_data and len(retail_data["data"]) > 0:
            latest_retail = retail_data["data"][0]
            indicators["retail_sales"] = float(latest_retail["value"])
            indicators["retail_sales_date"] = latest_retail["date"]
    except Exception as e:
        print(f"Could not fetch retail sales: {e}")
    
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

def analyze_with_ai(indicators: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze macroeconomic indicators and produce market outlook."""
    # Prepare prompt
    prompt = f"""You are a macroeconomic analyst. Analyze the following macroeconomic indicators and provide a market outlook (BULLISH, BEARISH, or NEUTRAL) with confidence score (0-100%) and brief reasoning.

Macroeconomic Indicators:
- Real GDP: {indicators.get('gdp', 'N/A')} (Date: {indicators.get('gdp_date', 'N/A')})
- CPI (Inflation): {indicators.get('cpi', 'N/A')}% (Date: {indicators.get('cpi_date', 'N/A')})
- Unemployment Rate: {indicators.get('unemployment', 'N/A')}% (Date: {indicators.get('unemployment_date', 'N/A')})
- Federal Funds Rate: {indicators.get('fed_funds_rate', 'N/A')}% (Date: {indicators.get('fed_funds_date', 'N/A')})
- Retail Sales: {indicators.get('retail_sales', 'N/A')} (Date: {indicators.get('retail_sales_date', 'N/A')})

Interpretation guidelines:
- GDP growth > 2% is positive for equities.
- CPI > 3% indicates inflationary pressure, may lead to rate hikes.
- Unemployment < 5% is healthy labor market.
- Low interest rates support borrowing and investment.
- Retail sales growth indicates consumer strength.

Provide your analysis in JSON format with keys: outlook, confidence, reasoning, summary.
"""
    
    response = call_huggingface(prompt)
    # Try to extract JSON from response
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            ai_result = json.loads(json_match.group())
        else:
            ai_result = {"outlook": "NEUTRAL", "confidence": 50, "reasoning": response[:200], "summary": "AI analysis failed to produce structured output."}
    except Exception:
        ai_result = {"outlook": "NEUTRAL", "confidence": 50, "reasoning": "Failed to parse AI response.", "summary": "AI analysis error."}
    
    return ai_result

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for macro-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Macroeconomic analysis using real data and AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "use_ai": {
                        "type": "boolean",
                        "description": "Use HuggingFace AI model for analysis (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="health_check",
            description="Check macro-analyst health and API availability",
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
    
    if name == "analyze":
        use_ai = arguments.get("use_ai", True)
        
        try:
            # Fetch real macroeconomic indicators
            indicators = get_macro_indicators()
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(indicators)
                outlook = ai_result.get("outlook", "NEUTRAL")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                summary = ai_result.get("summary", "")
            else:
                # Fallback rule-based analysis
                gdp = indicators.get("gdp")
                if gdp and gdp > 2.0:
                    outlook = "BULLISH"
                    confidence = 0.7
                elif gdp and gdp < 0.5:
                    outlook = "BEARISH"
                    confidence = 0.6
                else:
                    outlook = "NEUTRAL"
                    confidence = 0.5
                reasoning = "Rule-based analysis using GDP growth"
                summary = f"Macro indicators: GDP={gdp}, CPI={indicators.get('cpi', 'N/A')}, Unemployment={indicators.get('unemployment', 'N/A')}"
            
            # Format response
            response_text = f"Macroeconomic Analysis\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Market Outlook: {outlook} (Confidence: {confidence:.1%})\n"
            if indicators.get('gdp'):
                response_text += f"Real GDP: ${indicators['gdp']:,.2f}B (Date: {indicators.get('gdp_date', 'N/A')})\n"
            if indicators.get('cpi'):
                response_text += f"CPI (Inflation): {indicators['cpi']}% (Date: {indicators.get('cpi_date', 'N/A')})\n"
            if indicators.get('unemployment'):
                response_text += f"Unemployment Rate: {indicators['unemployment']}% (Date: {indicators.get('unemployment_date', 'N/A')})\n"
            if indicators.get('fed_funds_rate'):
                response_text += f"Federal Funds Rate: {indicators['fed_funds_rate']}% (Date: {indicators.get('fed_funds_date', 'N/A')})\n"
            if indicators.get('retail_sales'):
                response_text += f"Retail Sales: ${indicators['retail_sales']:,.2f}B (Date: {indicators.get('retail_sales_date', 'N/A')})\n"
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Summary: {summary}\n"
            
            # Add API status
            response_text += f"\nAPI Status: Alpha Vantage {'✅' if ALPHA_VANTAGE_KEY else '❌'}, FRED {'✅' if FRED_API_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing macroeconomic analysis: {str(e)}\n"
            response_text += "Please check API keys."
        
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
            "fred": bool(FRED_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Macro Analyst Health Check\n\n"
        response_text += f"✅ Alpha Vantage API: {'Configured' if status['alpha_vantage'] else 'Missing key'}\n"
        response_text += f"✅ FRED API: {'Configured' if status['fred'] else 'Missing key'}\n"
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
                server_name="macro-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())