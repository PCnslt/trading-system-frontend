#!/usr/bin/env python3
"""
Generate endpoint functions for new agents.
"""

endpoints = [
    ("macro", "macro", "Macro analyst"),
    ("crypto", "crypto", "Crypto analyst"),
    ("options", "options", "Options analyst"),
    ("risk", "risk", "Risk analyst"),
    ("quant", "quant", "Quant analyst"),
    ("sector", "sector", "Sector analyst"),
    ("compliance", "compliance", "Compliance analyst"),
]

template = '''
@app.get("/agents/{route}/{symbol}")
async def {name}_agent(symbol: str, use_ai: bool = True):
    """Call {description}."""
    if not {uppercase}_AVAILABLE:
        raise HTTPException(status_code=503, detail="{description} not available")
    
    try:
        result = {name}_analyze(symbol.upper(), use_ai=use_ai)
        # Transform result to AgentResponse schema
        if result.get("success"):
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="{name}-analyst",
                signal=result.get("analysis", {{}}).get("signal", "HOLD"),
                confidence=result.get("analysis", {{}}).get("confidence", 0.5),
                reasoning=result.get("analysis", {{}}).get("reasoning", ""),
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=result["success"],
                error=result.get("error")
            )
        else:
            agent_response = AgentResponse(
                symbol=result["symbol"],
                agent="{name}-analyst",
                signal="HOLD",
                confidence=0.0,
                reasoning=f"Analysis failed: {{result.get('error', 'Unknown error')}}",
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                success=False,
                error=result.get("error")
            )
        return agent_response
    except Exception as e:
        logger.error(f"{description} failed: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))
'''

output = []
for route, name, desc in endpoints:
    uppercase = name.upper()
    output.append(template.format(route=route, name=name, uppercase=uppercase, description=desc))

print('\n'.join(output))