#!/usr/bin/env python3
"""
Enhanced RAG solution with support for multiple providers:
1. DeepSeek API (powerful reasoning)
2. Hugging Face Inference API (free tier)
3. Ollama (local fallback)
4. OpenAI-compatible APIs

This fixes the RAG endpoint issue and provides a more robust solution.
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGProvider:
    """Base class for RAG providers"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
    
    async def generate(self, prompt: str, context: List[str] = None, **kwargs) -> str:
        raise NotImplementedError


class DeepSeekRAG(RAGProvider):
    """DeepSeek API provider (powerful for reasoning)"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key, "https://api.deepseek.com")
    
    async def generate(self, prompt: str, context: List[str] = None, **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("DeepSeek API key required")
        
        # Build context
        full_context = ""
        if context:
            full_context = "\n\n".join([f"Context {i+1}: {c}" for i, c in enumerate(context)])
        
        full_prompt = f"""Based on the following context, answer the question.

{full_context}

Question: {prompt}

Answer:"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": kwargs.get("max_tokens", 1024)
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return {
                "answer": result["choices"][0]["message"]["content"],
                "provider": "deepseek",
                "model": "deepseek-chat",
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise


class HuggingFaceRAG(RAGProvider):
    """Hugging Face Inference API provider (free tier)"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key, "https://api-inference.huggingface.co")
    
    async def generate(self, prompt: str, context: List[str] = None, **kwargs) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Hugging Face API key required")
        
        # Build context
        full_context = ""
        if context:
            full_context = "\n\n".join([f"Context {i+1}: {c}" for i, c in enumerate(context)])
        
        full_prompt = f"""Based on the following context, answer the question.

{full_context}

Question: {prompt}

Answer:"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Try different models (free tier)
        models_to_try = [
            "mistralai/Mistral-7B-Instruct-v0.3",
            "google/flan-t5-xxl",
            "microsoft/phi-2"
        ]
        
        for model in models_to_try:
            try:
                data = {
                    "inputs": full_prompt,
                    "parameters": {
                        "max_new_tokens": kwargs.get("max_tokens", 512),
                        "temperature": 0.1,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/models/{model}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        answer = result[0].get("generated_text", "")
                        return {
                            "answer": answer.strip(),
                            "provider": "huggingface",
                            "model": model,
                            "tokens_used": len(full_prompt) + len(answer)  # Estimate
                        }
            except Exception as e:
                logger.warning(f"Hugging Face model {model} failed: {e}")
                continue
        
        raise Exception("All Hugging Face models failed")


class OllamaRAG(RAGProvider):
    """Ollama local provider (fallback)"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(None, base_url)
    
    async def generate(self, prompt: str, context: List[str] = None, **kwargs) -> Dict[str, Any]:
        # Build context
        full_context = ""
        if context:
            full_context = "\n\n".join([f"Context {i+1}: {c}" for i, c in enumerate(context)])
        
        full_prompt = f"""Based on the following context, answer the question.

{full_context}

Question: {prompt}

Answer:"""
        
        # Try different local models
        models_to_try = ["llama3.2:3b", "qwen2.5:32b"]
        
        for model in models_to_try:
            try:
                data = {
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": kwargs.get("max_tokens", 1024)
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=data,
                    timeout=60  # Longer timeout for local models
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "answer": result.get("response", "").strip(),
                        "provider": "ollama",
                        "model": model,
                        "tokens_used": result.get("eval_count", 0) + result.get("prompt_eval_count", 0)
                    }
            except Exception as e:
                logger.warning(f"Ollama model {model} failed: {e}")
                continue
        
        raise Exception("All Ollama models failed")


class EnhancedRAGEngine:
    """Enhanced RAG engine with multiple provider support"""
    
    def __init__(self):
        self.providers = []
        
        # Load API keys from environment
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        huggingface_key = os.getenv("HUGGINGFACE_TOKEN")
        
        # Initialize providers in order of preference
        if deepseek_key:
            self.providers.append(DeepSeekRAG(deepseek_key))
            logger.info("DeepSeek provider initialized")
        
        if huggingface_key:
            self.providers.append(HuggingFaceRAG(huggingface_key))
            logger.info("Hugging Face provider initialized")
        
        # Always try Ollama as fallback
        self.providers.append(OllamaRAG())
        logger.info("Ollama provider initialized (fallback)")
        
        if not self.providers:
            raise Exception("No RAG providers available")
    
    async def query(self, question: str, context: List[str] = None, max_tokens: int = 1024) -> Dict[str, Any]:
        """Query with multiple provider fallback"""
        
        errors = []
        
        for provider in self.providers:
            try:
                logger.info(f"Trying provider: {provider.__class__.__name__}")
                result = await provider.generate(
                    prompt=question,
                    context=context,
                    max_tokens=max_tokens
                )
                logger.info(f"Success with provider: {provider.__class__.__name__}")
                return result
            except Exception as e:
                error_msg = f"{provider.__class__.__name__}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue
        
        # All providers failed
        raise Exception(f"All RAG providers failed:\n" + "\n".join(errors))


# FastAPI integration
async def create_enhanced_rag_endpoint():
    """Create enhanced RAG endpoint for FastAPI"""
    
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import asyncio
    
    app = FastAPI()
    
    class RAGRequest(BaseModel):
        question: str
        top_k: int = 5
        max_tokens: int = 1024
    
    class RAGResponse(BaseModel):
        answer: str
        provider: str
        model: str
        tokens_used: int
        cost: float = 0.0
    
    # Initialize engine
    engine = EnhancedRAGEngine()
    
    @app.post("/rag")
    async def rag_endpoint(request: RAGRequest) -> RAGResponse:
        """Enhanced RAG endpoint"""
        try:
            # Get context from memory system (simplified - would integrate with actual memory)
            context = [
                "Memory system is operational with PostgreSQL and Ollama.",
                "Trading platform has 10-agent architecture with real-time charts.",
                "Learning velocity is 6.5/10 with execution rate of 83%."
            ]
            
            result = await engine.query(
                question=request.question,
                context=context[:request.top_k],
                max_tokens=request.max_tokens
            )
            
            # Calculate cost (approximate)
            cost = 0.0
            if result["provider"] == "deepseek":
                cost = result["tokens_used"] * 0.0000014  # DeepSeek pricing
            elif result["provider"] == "huggingface":
                cost = 0.0  # Free tier
            
            return RAGResponse(
                answer=result["answer"],
                provider=result["provider"],
                model=result["model"],
                tokens_used=result["tokens_used"],
                cost=cost
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


if __name__ == "__main__":
    # Test the enhanced RAG engine
    import asyncio
    
    async def test():
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        engine = EnhancedRAGEngine()
        
        test_question = "What is the current learning velocity and execution rate?"
        
        try:
            result = await engine.query(test_question)
            print(f"Provider: {result['provider']}")
            print(f"Model: {result['model']}")
            print(f"Tokens used: {result['tokens_used']}")
            print(f"Answer: {result['answer']}")
        except Exception as e:
            print(f"Error: {e}")
    
    asyncio.run(test())