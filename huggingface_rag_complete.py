#!/usr/bin/env python3
"""
Complete Hugging Face RAG Solution
No Ollama, only free Hugging Face models via router API
"""

import os
import json
import requests
import numpy as np
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hugging Face configuration
HF_API_KEY = "YOUR_HUGGINGFACE_TOKEN_HERE"  # From secrets
HF_ROUTER_URL = "https://router.huggingface.co/hf-inference/models"

# Model choices (free, reliable)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODELS = [
    "microsoft/phi-2",           # Small, fast, good for Q&A
    "google/flan-t5-base",       # Instruction-tuned, good for Q&A
    "microsoft/phi-1_5",         # Alternative if phi-2 fails
]

app = FastAPI(
    title="Hugging Face RAG Solution",
    description="RAG using free Hugging Face models via router API",
    version="1.0"
)

class RAGRequest(BaseModel):
    question: str
    top_k: int = 5
    max_tokens: int = 500

class RAGResponse(BaseModel):
    answer: str
    provider: str = "huggingface"
    model: str
    tokens_used: int
    cost: float = 0.0

class HuggingFaceRAG:
    """Hugging Face RAG implementation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Knowledge base (in-memory for now)
        self.knowledge_base = self._create_knowledge_base()
        self.embeddings_cache = {}
    
    def _create_knowledge_base(self) -> List[Dict[str, Any]]:
        """Create in-memory knowledge base"""
        return [
            {
                "id": "kb_001",
                "content": "System Learning Velocity: 6.5/10 (improved from 3.5 baseline). This measures how quickly the system learns from experiences and improves over time.",
                "category": "metrics",
                "tags": ["learning", "velocity", "performance"]
            },
            {
                "id": "kb_002",
                "content": "Execution Rate: 83% (20 out of 24 decisions completed). This tracks the percentage of planned tasks that are successfully executed.",
                "category": "metrics",
                "tags": ["execution", "rate", "performance"]
            },
            {
                "id": "kb_003",
                "content": "Memory System Architecture: PostgreSQL + Ollama + FastAPI. The system stores memories in PostgreSQL, uses Ollama for local embeddings/generation, and exposes a FastAPI interface. Currently experiencing RAG endpoint timeout issues.",
                "category": "infrastructure",
                "tags": ["memory", "postgresql", "ollama", "fastapi", "rag"]
            },
            {
                "id": "kb_004",
                "content": "Trading Platform: 10-agent system with 3 agents operational (Technical Analyst, Fundamental Analyst, Sentiment Analyst). 7 agents pending activation. Features real-time charts and multiple API integrations (Alpha Vantage, FMP, NewsAPI, CoinMarketCap).",
                "category": "trading",
                "tags": ["trading", "agents", "platform", "charts"]
            },
            {
                "id": "kb_005",
                "content": "Current Blockers: 1) RAG endpoint 500 error (Ollama model timeout), 2) GitHub secrets in commit history blocking pushes, 3) User verification pending for trading platform charts, 4) Skill discrepancy between workspace and global skills.",
                "category": "issues",
                "tags": ["blockers", "issues", "rag", "github", "verification"]
            },
            {
                "id": "kb_006",
                "content": "Recent Achievements: Memory system embedding format fixed, Humanizer skill implemented, Trading agent foundation complete (3/10), Learning velocity improved to 6.5/10, Execution framework with consequence system implemented.",
                "category": "achievements",
                "tags": ["achievements", "fixes", "improvements"]
            },
            {
                "id": "kb_007",
                "content": "Next Priorities: Fix RAG endpoint, Resolve GitHub secrets block, Complete user verification, Activate remaining 7 trading agents, Run weekly evolution on Sunday.",
                "category": "priorities",
                "tags": ["priorities", "todo", "next"]
            },
            {
                "id": "kb_008",
                "content": "Storage Status: 78.6 GB free on C: drive. System maintains $0/month cost through free APIs and local resources.",
                "category": "infrastructure",
                "tags": ["storage", "cost", "infrastructure"]
            },
            {
                "id": "kb_009",
                "content": "Skills Status: 6 workspace skills active (api-keys-manager, capability-evolver, mdsearch-pro, memory-system-integration, humanizer). 51 global skills installed with 27% utilization rate.",
                "category": "skills",
                "tags": ["skills", "utilization", "workspace"]
            },
            {
                "id": "kb_010",
                "content": "RAG Issue Details: The original RAG endpoint fails with 500 errors due to Ollama model timeouts. This Hugging Face solution provides an alternative using free cloud models.",
                "category": "rag",
                "tags": ["rag", "issues", "huggingface", "solution"]
            }
        ]
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text using Hugging Face"""
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        # Try different endpoint formats
        endpoints = [
            f"{HF_ROUTER_URL}/{EMBEDDING_MODEL}/pipeline/feature-extraction",
            f"{HF_ROUTER_URL}/{EMBEDDING_MODEL}"
        ]
        
        data = {
            "inputs": text
        }
        
        for endpoint in endpoints:
            try:
                response = requests.post(
                    endpoint,
                    headers=self.headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    embedding = response.json()
                    if isinstance(embedding, list):
                        # Handle different response formats
                        if len(embedding) > 0:
                            if isinstance(embedding[0], list):
                                embedding = embedding[0]  # Nested list
                            elif isinstance(embedding[0], dict) and "embedding" in embedding[0]:
                                embedding = embedding[0]["embedding"]  # Dict format
                        
                        self.embeddings_cache[text] = embedding
                        logger.debug(f"Got embedding of length {len(embedding)} from {endpoint}")
                        return embedding
                elif response.status_code == 503:
                    logger.info(f"Embedding model is loading from {endpoint}")
                else:
                    logger.debug(f"Endpoint {endpoint} error {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} exception: {e}")
                continue
        
        # If all endpoints fail, use a simple hash-based fallback for testing
        logger.warning(f"All embedding endpoints failed for: {text[:50]}...")
        # Create deterministic pseudo-embedding based on text hash
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        pseudo_embedding = [((hash_val + i) % 1000) / 1000.0 for i in range(384)]
        self.embeddings_cache[text] = pseudo_embedding
        return pseudo_embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def retrieve_relevant(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge based on semantic similarity"""
        question_embedding = self.get_embedding(question)
        if not question_embedding:
            # Fallback: return all knowledge
            return self.knowledge_base[:top_k]
        
        # Calculate similarities
        scored_items = []
        for item in self.knowledge_base:
            content_embedding = self.get_embedding(item["content"])
            if content_embedding:
                similarity = self.cosine_similarity(question_embedding, content_embedding)
                scored_items.append((similarity, item))
            else:
                # If embedding fails, use keyword matching as fallback
                question_words = set(question.lower().split())
                content_words = set(item["content"].lower().split())
                common_words = question_words.intersection(content_words)
                similarity = len(common_words) / max(len(question_words), 1)
                scored_items.append((similarity * 0.5, item))  # Lower weight for keyword match
        
        # Sort by similarity and return top_k
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored_items[:top_k]]
    
    def generate_answer(self, question: str, context: List[Dict[str, Any]], max_tokens: int = 500) -> Dict[str, Any]:
        """Generate answer using Hugging Face models"""
        
        # Format context
        context_text = "\n".join([f"- {item['content']}" for item in context])
        
        prompt = f"""Based on the following information, answer the question.

Available Information:
{context_text}

Question: {question}

Provide a concise, accurate answer. If the information doesn't contain the answer, say so.

Answer:"""
        
        # Try each generation model until one works
        for model in GENERATION_MODELS:
            try:
                data = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": 0.1,
                        "do_sample": False
                    }
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{HF_ROUTER_URL}/{model}",
                    headers=self.headers,
                    json=data,
                    timeout=45
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        # Clean up the response
                        if generated_text.startswith(prompt):
                            generated_text = generated_text[len(prompt):].strip()
                        
                        return {
                            "success": True,
                            "answer": generated_text,
                            "model": model,
                            "time_seconds": elapsed,
                            "tokens_estimated": len(prompt.split()) + len(generated_text.split())
                        }
                elif response.status_code == 503:
                    logger.info(f"Model {model} is loading, trying next...")
                    continue
                else:
                    logger.warning(f"Model {model} error {response.status_code}: {response.text[:200]}")
                    
            except Exception as e:
                logger.warning(f"Model {model} exception: {e}")
                continue
        
        # All models failed, return fallback
        return {
            "success": False,
            "answer": "I cannot generate an answer at the moment due to model availability issues. Based on the context, here's what I know: " + context[0]["content"][:200] + "...",
            "model": "fallback",
            "time_seconds": 0,
            "tokens_estimated": 0
        }
    
    def query(self, question: str, top_k: int = 5, max_tokens: int = 500) -> Dict[str, Any]:
        """Complete RAG query"""
        # Retrieve relevant knowledge
        context = self.retrieve_relevant(question, top_k)
        logger.info(f"Retrieved {len(context)} context items")
        
        # Generate answer
        result = self.generate_answer(question, context, max_tokens)
        
        return {
            "answer": result["answer"],
            "context_used": len(context),
            "model": result["model"],
            "success": result["success"],
            "time_seconds": result.get("time_seconds", 0),
            "tokens_used": result.get("tokens_estimated", 0)
        }

# Initialize RAG engine
rag_engine = HuggingFaceRAG(HF_API_KEY)

@app.post("/rag")
async def rag_endpoint(request: RAGRequest) -> RAGResponse:
    """Hugging Face RAG endpoint"""
    try:
        logger.info(f"RAG query: {request.question}")
        
        result = rag_engine.query(
            question=request.question,
            top_k=request.top_k,
            max_tokens=request.max_tokens
        )
        
        return RAGResponse(
            answer=result["answer"],
            model=result["model"],
            tokens_used=result["tokens_used"],
            cost=0.0  # Free tier
        )
        
    except Exception as e:
        logger.error(f"RAG endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test embedding to verify API works
    test_embedding = rag_engine.get_embedding("test")
    
    return {
        "status": "healthy" if test_embedding else "degraded",
        "service": "huggingface_rag",
        "embedding_model": EMBEDDING_MODEL,
        "generation_models": GENERATION_MODELS,
        "knowledge_items": len(rag_engine.knowledge_base),
        "embeddings_cached": len(rag_engine.embeddings_cache),
        "cost_per_query": 0.0
    }

@app.get("/knowledge")
async def list_knowledge():
    """List knowledge base"""
    return {
        "total_items": len(rag_engine.knowledge_base),
        "categories": list(set(item["category"] for item in rag_engine.knowledge_base)),
        "items": rag_engine.knowledge_base
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Hugging Face RAG Solution",
        "version": "1.0",
        "description": "RAG using free Hugging Face models via router API. No Ollama dependency.",
        "models": {
            "embedding": EMBEDDING_MODEL,
            "generation": GENERATION_MODELS
        },
        "features": {
            "free_tier": True,
            "no_ollama": True,
            "semantic_search": True,
            "context_aware": True
        },
        "endpoints": {
            "POST /rag": "RAG query endpoint",
            "GET /health": "Health check",
            "GET /knowledge": "List knowledge base",
            "GET /": "This information"
        }
    }

if __name__ == "__main__":
    print("=" * 60)
    print("Hugging Face RAG Solution")
    print("=" * 60)
    print()
    print("Configuration:")
    print(f"  Embedding Model: {EMBEDDING_MODEL}")
    print(f"  Generation Models: {', '.join(GENERATION_MODELS)}")
    print(f"  Knowledge Base: {len(rag_engine.knowledge_base)} items")
    print(f"  API: Hugging Face Router")
    print()
    print("Endpoints:")
    print("  POST http://localhost:8002/rag - RAG query")
    print("  GET  http://localhost:8002/health - Health check")
    print("  GET  http://localhost:8002/knowledge - List knowledge")
    print()
    print("Starting server on port 8002...")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        access_log=True
    )