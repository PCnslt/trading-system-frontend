#!/usr/bin/env python3
"""
Lightweight MCP Gateway for Trading Agents
Exposes HTTP endpoints and SSE for VS Code MCP client
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, AsyncGenerator, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator


def ensure_string(value: Any) -> str:
    """Convert any value to string, handling dict -> JSON conversion."""
    if value is None:
        return ""
    elif isinstance(value, dict):
        try:
            return json.dumps(value, indent=2)
        except Exception:
            return str(value)
    elif isinstance(value, list):
        try:
            return json.dumps(value, indent=2)
        except Exception:
            return str(value)
    else:
        return str(value)

# Import agent functions
try:
    from technical_analyst import analyze_symbol as technical_analyze
    TECHNICAL_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Technical analyst not available: {e}")
    TECHNICAL_AVAILABLE = False
    technical_analyze = None

try:
    from fundamental_analyst import analyze_symbol as fundamental_analyze
    FUNDAMENTAL_AVAILABLE = True
except ImportError:
    FUNDAMENTAL_AVAILABLE = False
    fundamental_analyze = None

try:
    from sentiment_analyst import analyze_symbol as sentiment_analyze
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    sentiment_analyze = None

try:
    from macro_analyst import analyze_symbol as macro_analyze
    MACRO_AVAILABLE = True
except ImportError:
    MACRO_AVAILABLE = False
    macro_analyze = None

try:
    from crypto_analyst import analyze_symbol as crypto_analyze
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    crypto_analyze = None

try:
    from options_analyst import analyze_symbol as options_analyze
    OPTIONS_AVAILABLE = True
except ImportError:
    OPTIONS_AVAILABLE = False
    options_analyze = None

try:
    from risk_analyst import analyze_symbol as risk_analyze
    RISK_AVAILABLE = True
except ImportError:
    RISK_AVAILABLE = False
    risk_analyze = None

try:
    from quant_analyst import analyze_symbol as quant_analyze
    QUANT_AVAILABLE = True
except ImportError:
    QUANT_AVAILABLE = False
    quant_analyze = None

try:
    from sector_analyst import analyze_symbol as sector_analyze
    SECTOR_AVAILABLE = True
except ImportError:
    SECTOR_AVAILABLE = False
    sector_analyze = None

try:
    from compliance_analyst import analyze_symbol as compliance_analyze
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    compliance_analyze = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Trading Agent Gateway", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AgentRequest(BaseModel):
    symbol: str
    use_ai: bool = True

class AgentResponse(BaseModel):
    symbol: str
    agent: str
    signal: str
    confidence: float
    reasoning: str
    timestamp: str
    success: bool
    error: Optional[str] = None
    
    @validator('reasoning', pre=True)
    def ensure_reasoning_string(cls, v):
        """Ensure reasoning is always a string, converting dict/list to JSON."""
        if v is None:
            return ""
        elif isinstance(v, dict) or isinstance(v, list):
            try:
                return json.dumps(v, indent=2)
            except Exception:
                return str(v)
        else:
            return str(v)

class MCPMessage(BaseModel):
    jsonrpc: str = "2.0"
    id: int = None
    method: str = None
    params: Dict[str, Any] = None
    result: Any = None
    error: Dict[str, Any] = None

# Health endpoint
@app.get("/")
async def root():
    return {
        "service": "Trading Agent Gateway",
        "version": "1.0.0",
        "agents": {
            "technical": TECHNICAL_AVAILABLE,
            "fundamental": FUNDAMENTAL_AVAILABLE,
            "sentiment": SENTIMENT_AVAILABLE,
            "macro": MACRO_AVAILABLE,
            "crypto": CRYPTO_AVAILABLE,
            "options": OPTIONS_AVAILABLE,
            "risk": RISK_AVAILABLE,
            "quant": QUANT_AVAILABLE,
            "sector": SECTOR_AVAILABLE,
            "compliance": COMPLIANCE_AVAILABLE
        },
        "endpoints": {
            "health": "/health",
            "agents": "/agents/{agent}/{symbol}",
            "mcp_sse": "/sse"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Agent endpoints
@app.get("/agents/technical/{symbol}")
async def technical_agent(symbol: str, use_ai: bool = True):
    """Call technical analyst agent."""
    if not TECHNICAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Technical analyst not available")
    
    try:
        result = technical_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="technical-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="technical-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Technical analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/fundamental/{symbol}")
async def fundamental_agent(symbol: str, use_ai: bool = True):
    """Call fundamental analyst agent."""
    if not FUNDAMENTAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Fundamental analyst not available")
    
    try:
        result = fundamental_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="fundamental-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="fundamental-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Fundamental analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/sentiment/{symbol}")
async def sentiment_agent(symbol: str, use_ai: bool = True):
    """Call sentiment analyst agent."""
    if not SENTIMENT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sentiment analyst not available")
    
    try:
        result = sentiment_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="sentiment-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="sentiment-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/macro/{symbol}")
async def macro_agent(symbol: str, use_ai: bool = True):
    """Call macro analyst agent."""
    if not MACRO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Macro analyst not available")
    
    try:
        result = macro_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="macro-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="macro-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Macro analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/crypto/{symbol}")
async def crypto_agent(symbol: str, use_ai: bool = True):
    """Call crypto analyst agent."""
    if not CRYPTO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Crypto analyst not available")
    
    try:
        result = crypto_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="crypto-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="crypto-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Crypto analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/options/{symbol}")
async def options_agent(symbol: str, use_ai: bool = True):
    """Call options analyst agent."""
    if not OPTIONS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Options analyst not available")
    
    try:
        result = options_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="options-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="options-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Options analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/risk/{symbol}")
async def risk_agent(symbol: str, use_ai: bool = True):
    """Call risk analyst agent."""
    if not RISK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Risk analyst not available")
    
    try:
        result = risk_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="risk-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="risk-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/quant/{symbol}")
async def quant_agent(symbol: str, use_ai: bool = True):
    """Call quant analyst agent."""
    if not QUANT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Quant analyst not available")
    
    try:
        result = quant_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="quant-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="quant-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Quant analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/sector/{symbol}")
async def sector_agent(symbol: str, use_ai: bool = True):
    """Call sector analyst agent."""
    if not SECTOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Sector analyst not available")
    
    try:
        result = sector_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="sector-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="sector-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Sector analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/compliance/{symbol}")
async def compliance_agent(symbol: str, use_ai: bool = True):
    """Call compliance analyst agent."""
    if not COMPLIANCE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Compliance analyst not available")
    
    try:
        result = compliance_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="compliance-analyst",
                signal=result.get("analysis", {}).get("signal", "HOLD"),
                confidence=result.get("analysis", {}).get("confidence", 0.5),
                reasoning=result.get("analysis", {}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="compliance-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {result.get('error', 'Unknown error')}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"Compliance analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MCP SSE endpoint (simplified)
@app.get("/sse")
async def mcp_sse():
    """SSE endpoint for MCP protocol (simplified)."""
    async def event_stream():
        # Send initial connection event
        yield f"event: connected\ndata: {json.dumps({'message': 'MCP SSE Gateway Connected'})}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"event: ping\ndata: {json.dumps({'timestamp': datetime.now().isoformat()})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

# Tool invocation endpoint (for MCP tools)
@app.post("/tools/{tool_name}")
async def invoke_tool(tool_name: str, params: Dict[str, Any]):
    """Invoke a specific tool by name."""
    agent_map = {
        "technical_analyze": technical_analyze,
        "fundamental_analyze": fundamental_analyze,
        "sentiment_analyze": sentiment_analyze,
        "macro_analyze": macro_analyze,
        "crypto_analyze": crypto_analyze,
        "options_analyze": options_analyze,
        "risk_analyze": risk_analyze,
        "quant_analyze": quant_analyze,
        "sector_analyze": sector_analyze,
        "compliance_analyze": compliance_analyze
    }
    
    if tool_name not in agent_map:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    agent_func = agent_map[tool_name]
    if agent_func is None:
        raise HTTPException(status_code=503, detail=f"Agent for {tool_name} not available")
    
    symbol = params.get("symbol", "").upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol parameter required")
    
    try:
        result = agent_func(symbol, use_ai=params.get("use_ai", True))
        return result
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Start server
    port = int(os.getenv("GATEWAY_PORT", 8081))
    logger.info(f"Starting Trading Agent Gateway on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )