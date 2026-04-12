#!/usr/bin/env python3
"""
MCP Server for Sector analysis using real data and HuggingFace AI models
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
server = Server("sector-analyst")

# Load API keys from environment
SECTOR_DATA_API_KEY = os.environ.get("SECTOR_DATA_API_KEY", "")
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN", "")

# HuggingFace Inference API endpoint for Llama 3.3 70B Instruct
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct"
HF_HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

def fetch_sector_performance() -> Dict[str, Any]:
    """Fetch sector performance data from Alpha Vantage."""
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "SECTOR",
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
        raise Exception(f"Failed to fetch sector performance data: {e}")

def get_sector_metrics() -> Dict[str, Any]:
    """Extract key sector performance metrics."""
    sector_data = fetch_sector_performance()
    metrics = {}
    
    # Real-time performance (if available)
    if "Real Time Performance" in sector_data:
        rt = sector_data["Real Time Performance"]
        for sector, perf in rt.items():
            metrics[f"realtime_{sector.lower().replace(' ', '_')}"] = perf
    
    # 1-day performance
    if "Rank A: Real-Time Performance" in sector_data:
        rank_a = sector_data["Rank A: Real-Time Performance"]
        for sector, perf in rank_a.items():
            metrics[f"1day_{sector.lower().replace(' ', '_')}"] = perf
    
    # 5-day performance
    if "Rank B: 1 Day Performance" in sector_data:
        rank_b = sector_data["Rank B: 1 Day Performance"]
        for sector, perf in rank_b.items():
            metrics[f"5day_{sector.lower().replace(' ', '_')}"] = perf
    
    # 1-month performance
    if "Rank C: 5 Day Performance" in sector_data:
        rank_c = sector_data["Rank C: 5 Day Performance"]
        for sector, perf in rank_c.items():
            metrics[f"1month_{sector.lower().replace(' ', '_')}"] = perf
    
    # 3-month performance
    if "Rank D: 1 Month Performance" in sector_data:
        rank_d = sector_data["Rank D: 1 Month Performance"]
        for sector, perf in rank_d.items():
            metrics[f"3month_{sector.lower().replace(' ', '_')}"] = perf
    
    # Year-to-date performance
    if "Rank E: 3 Month Performance" in sector_data:
        rank_e = sector_data["Rank E: 3 Month Performance"]
        for sector, perf in rank_e.items():
            metrics[f"ytd_{sector.lower().replace(' ', '_')}"] = perf
    
    # 1-year performance
    if "Rank F: Year-to-Date (YTD) Performance" in sector_data:
        rank_f = sector_data["Rank F: Year-to-Date (YTD) Performance"]
        for sector, perf in rank_f.items():
            metrics[f"1year_{sector.lower().replace(' ', '_')}"] = perf
    
    # 3-year performance
    if "Rank G: 1 Year Performance" in sector_data:
        rank_g = sector_data["Rank G: 1 Year Performance"]
        for sector, perf in rank_g.items():
            metrics[f"3year_{sector.lower().replace(' ', '_')}"] = perf
    
    # 5-year performance
    if "Rank H: 3 Year Performance" in sector_data:
        rank_h = sector_data["Rank H: 3 Year Performance"]
        for sector, perf in rank_h.items():
            metrics[f"5year_{sector.lower().replace(' ', '_')}"] = perf
    
    # 10-year performance
    if "Rank I: 5 Year Performance" in sector_data:
        rank_i = sector_data["Rank I: 5 Year Performance"]
        for sector, perf in rank_i.items():
            metrics[f"10year_{sector.lower().replace(' ', '_')}"] = perf
    
    # Metadata
    if "Meta Data" in sector_data:
        metrics["last_updated"] = sector_data["Meta Data"].get("Last Updated", "")
    
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

def analyze_with_ai(metrics: Dict) -> Dict[str, Any]:
    """Use HuggingFace LLM to analyze sector performance and produce recommendations."""
    # Prepare prompt
    prompt = f"""You are a sector analyst. Analyze the following sector performance metrics and identify the strongest and weakest sectors, provide overall market outlook (BULLISH, BEARISH, or NEUTRAL) with confidence score (0-100%) and brief reasoning.

Sector Performance (Real-Time):
- Communication Services: {metrics.get('realtime_communication_services', 'N/A')}
- Consumer Discretionary: {metrics.get('realtime_consumer_discretionary', 'N/A')}
- Consumer Staples: {metrics.get('realtime_consumer_staples', 'N/A')}
- Energy: {metrics.get('realtime_energy', 'N/A')}
- Financials: {metrics.get('realtime_financials', 'N/A')}
- Health Care: {metrics.get('realtime_health_care', 'N/A')}
- Industrials: {metrics.get('realtime_industrials', 'N/A')}
- Information Technology: {metrics.get('realtime_information_technology', 'N/A')}
- Materials: {metrics.get('realtime_materials', 'N/A')}
- Real Estate: {metrics.get('realtime_real_estate', 'N/A')}
- Utilities: {metrics.get('realtime_utilities', 'N/A')}

Recent Performance (1-day):
- Communication Services: {metrics.get('1day_communication_services', 'N/A')}
- Consumer Discretionary: {metrics.get('1day_consumer_discretionary', 'N/A')}
- Consumer Staples: {metrics.get('1day_consumer_staples', 'N/A')}
- Energy: {metrics.get('1day_energy', 'N/A')}
- Financials: {metrics.get('1day_financials', 'N/A')}
- Health Care: {metrics.get('1day_health_care', 'N/A')}
- Industrials: {metrics.get('1day_industrials', 'N/A')}
- Information Technology: {metrics.get('1day_information_technology', 'N/A')}
- Materials: {metrics.get('1day_materials', 'N/A')}
- Real Estate: {metrics.get('1day_real_estate', 'N/A')}
- Utilities: {metrics.get('1day_utilities', 'N/A')}

Longer-term trends (1-month, 3-month, YTD, 1-year) are also available.

Interpretation guidelines:
- Positive performance across most sectors indicates broad market strength.
- Sector rotation patterns can signal changing economic conditions.
- Defensive sectors (Utilities, Staples) outperform during uncertainty.
- Cyclical sectors (Discretionary, Industrials) lead during expansions.
- Technology sector often drives innovation growth.

Provide your analysis in JSON format with keys: outlook, confidence, reasoning, top_sector, bottom_sector, recommendations.
"""
    
    response = call_huggingface(prompt)
    # Try to extract JSON from response
    try:
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            ai_result = json.loads(json_match.group())
        else:
            ai_result = {"outlook": "NEUTRAL", "confidence": 50, "reasoning": response[:200], "top_sector": "Unknown", "bottom_sector": "Unknown", "recommendations": "AI analysis failed to produce structured output."}
    except Exception:
        ai_result = {"outlook": "NEUTRAL", "confidence": 50, "reasoning": "Failed to parse AI response.", "top_sector": "Unknown", "bottom_sector": "Unknown", "recommendations": "AI analysis error."}
    
    return ai_result

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for sector-analyst"""
    return [
        types.Tool(
            name="analyze",
            description="Sector performance analysis using real data and AI",
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
            description="Check sector-analyst health and API availability",
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
            # Fetch real sector performance metrics
            metrics = get_sector_metrics()
            
            if use_ai and HUGGINGFACE_TOKEN:
                ai_result = analyze_with_ai(metrics)
                outlook = ai_result.get("outlook", "NEUTRAL")
                confidence = ai_result.get("confidence", 50) / 100.0
                reasoning = ai_result.get("reasoning", "")
                top_sector = ai_result.get("top_sector", "Unknown")
                bottom_sector = ai_result.get("bottom_sector", "Unknown")
                recommendations = ai_result.get("recommendations", "")
            else:
                # Fallback rule-based analysis
                # Find sector with highest real-time performance
                top_perf = -999
                bottom_perf = 999
                top_sector = "Unknown"
                bottom_sector = "Unknown"
                for key, val in metrics.items():
                    if key.startswith("realtime_") and isinstance(val, (int, float)):
                        if val > top_perf:
                            top_perf = val
                            top_sector = key.replace("realtime_", "").replace("_", " ").title()
                        if val < bottom_perf:
                            bottom_perf = val
                            bottom_sector = key.replace("realtime_", "").replace("_", " ").title()
                
                if top_perf > 0.5:
                    outlook = "BULLISH"
                    confidence = 0.7
                elif top_perf < -0.5:
                    outlook = "BEARISH"
                    confidence = 0.6
                else:
                    outlook = "NEUTRAL"
                    confidence = 0.5
                reasoning = f"Rule-based analysis: top sector {top_sector} ({top_perf:.2f}%), bottom sector {bottom_sector} ({bottom_perf:.2f}%)"
                recommendations = f"Consider overweighting {top_sector} and underweighting {bottom_sector}."
            
            # Format response
            response_text = f"Sector Performance Analysis\n"
            response_text += f"Timestamp: {datetime.now().isoformat()}\n"
            response_text += f"Market Outlook: {outlook} (Confidence: {confidence:.1%})\n"
            response_text += f"Top Performing Sector: {top_sector}\n"
            response_text += f"Bottom Performing Sector: {bottom_sector}\n\n"
            
            # Real-time sector performance table
            response_text += "Real-Time Sector Performance:\n"
            sectors = [
                ("Communication Services", metrics.get('realtime_communication_services', 'N/A')),
                ("Consumer Discretionary", metrics.get('realtime_consumer_discretionary', 'N/A')),
                ("Consumer Staples", metrics.get('realtime_consumer_staples', 'N/A')),
                ("Energy", metrics.get('realtime_energy', 'N/A')),
                ("Financials", metrics.get('realtime_financials', 'N/A')),
                ("Health Care", metrics.get('realtime_health_care', 'N/A')),
                ("Industrials", metrics.get('realtime_industrials', 'N/A')),
                ("Information Technology", metrics.get('realtime_information_technology', 'N/A')),
                ("Materials", metrics.get('realtime_materials', 'N/A')),
                ("Real Estate", metrics.get('realtime_real_estate', 'N/A')),
                ("Utilities", metrics.get('realtime_utilities', 'N/A'))
            ]
            for sector_name, perf in sectors:
                if isinstance(perf, (int, float)):
                    response_text += f"  • {sector_name}: {perf:.2f}%\n"
                else:
                    response_text += f"  • {sector_name}: {perf}\n"
            
            response_text += f"\nReasoning: {reasoning}\n"
            response_text += f"Recommendations: {recommendations}\n"
            
            # Add API status
            response_text += f"\nAPI Status: Alpha Vantage {'✅' if ALPHA_VANTAGE_KEY else '❌'}, HuggingFace {'✅' if HUGGINGFACE_TOKEN else '❌'}"
            
        except Exception as e:
            response_text = f"Error performing sector analysis: {str(e)}\n"
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
            "sector_api": bool(SECTOR_DATA_API_KEY),
            "huggingface": bool(HUGGINGFACE_TOKEN),
            "timestamp": datetime.now().isoformat()
        }
        
        response_text = "Sector Analyst Health Check\n\n"
        response_text += f"✅ Alpha Vantage API: {'Configured' if status['alpha_vantage'] else 'Missing key'}\n"
        response_text += f"✅ Sector Data API: {'Configured' if status['sector_api'] else 'Missing key'}\n"
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
                server_name="sector-analyst",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())