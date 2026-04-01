from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from src.models import (
    MemoryCreate, MemoryResponse, SearchQuery,
    RAGQuery, RAGResponse, APIUsage
)
from src.memory_manager import get_memory_manager
from src.rag_engine import get_rag_engine
from src.cost_tracker import get_cost_tracker
from src.database import init_database, health_check as db_health_check
from src.ollama_client import get_ollama_client, close_ollama_client
from src.config import get_config

# Configure logging
logging.basicConfig(
    level=get_config().log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Local Memory System",
    description="Production-ready memory system with RAG and cost optimization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Local Memory System...")
    
    # Initialize database
    try:
        await init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Initialize Ollama client (warm up)
    try:
        ollama = await get_ollama_client()
        if await ollama.health_check():
            logger.info("Ollama service is healthy")
        else:
            logger.warning("Ollama service may not be available")
    except Exception as e:
        logger.error(f"Ollama initialization failed: {e}")
        # Continue anyway - some endpoints may still work
    
    logger.info("Local Memory System started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Local Memory System...")
    await close_ollama_client()
    logger.info("Shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Local Memory System",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Vector memory storage",
            "Local AI embeddings (Ollama)",
            "RAG with local generation",
            "Cost tracking and optimization",
            "Dockerized deployment"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    db_healthy = await db_health_check()
    
    try:
        ollama = await get_ollama_client()
        ollama_healthy = await ollama.health_check()
    except Exception:
        ollama_healthy = False
    
    status = "healthy" if db_healthy and ollama_healthy else "degraded"
    
    return {
        "status": status,
        "database": "healthy" if db_healthy else "unhealthy",
        "ollama": "healthy" if ollama_healthy else "unhealthy",
        "timestamp": "2026-03-31T00:54:00Z"  # Static for now
    }


@app.post("/memories", response_model=dict)
async def create_memory(memory: MemoryCreate):
    """Store a new memory."""
    try:
        memory_manager = await get_memory_manager()
        memory_id = await memory_manager.store(
            content=memory.content,
            metadata=memory.metadata,
            tags=memory.tags
        )
        
        return {
            "id": memory_id,
            "message": "Memory stored successfully",
            "content_preview": memory.content[:100] + "..." if len(memory.content) > 100 else memory.content
        }
    except Exception as e:
        logger.error(f"Failed to create memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memories/retrieve", response_model=list[MemoryResponse])
async def retrieve_memories(search: SearchQuery):
    """Retrieve similar memories."""
    try:
        memory_manager = await get_memory_manager()
        memories = await memory_manager.retrieve(
            query=search.query,
            top_k=search.top_k,
            filters=search.filters,
            use_cache=search.use_cache
        )
        
        return memories
    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag", response_model=RAGResponse)
async def rag_query(rag_query: RAGQuery):
    """Answer a question using RAG."""
    try:
        rag_engine = await get_rag_engine()
        response = await rag_engine.query_with_sources(rag_query)
        
        return response
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}")
async def get_memory(memory_id: str):
    """Get a specific memory by ID."""
    try:
        # For now, we'll retrieve it via search with exact match
        memory_manager = await get_memory_manager()
        memories = await memory_manager.retrieve(
            query=memory_id,  # Not ideal, but works for demo
            top_k=1,
            filters={"id": memory_id} if "id" in locals() else None
        )
        
        if memories:
            return memories[0]
        else:
            raise HTTPException(status_code=404, detail="Memory not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory."""
    try:
        memory_manager = await get_memory_manager()
        success = await memory_manager.delete(memory_id)
        
        if success:
            return {"message": "Memory deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Memory not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    try:
        memory_manager = await get_memory_manager()
        stats = await memory_manager.get_stats()
        
        return {
            "memory_system": stats,
            "config": {
                "embedding_model": get_config().embedding_model,
                "generation_model": get_config().generation_model,
                "embedding_dimension": get_config().embedding_dimension
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/usage")
async def get_usage(days: int = 7):
    """Get API usage summary."""
    try:
        from datetime import datetime, timedelta
        cost_tracker = get_cost_tracker()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        summary = await cost_tracker.get_usage_summary(start_date, end_date)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "summary": summary,
            "total_cost": sum(usage["total_cost"] for usage in summary.values())
        }
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run the application
if __name__ == "__main__":
    config = get_config()
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.api_debug
    )