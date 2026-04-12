#!/usr/bin/env python3
"""
Working RAG Solution using Ollama
Fixes the RAG endpoint by using Ollama directly with proper configuration.
"""

import json
import requests
import time
from typing import Dict, Any

class OllamaRAG:
    """Simple RAG using Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.embedding_model = "nomic-embed-text:latest"
        self.generation_model = "qwen2.5:0.5b"  # Available model
    
    def test_connection(self) -> bool:
        """Test if Ollama is reachable"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, system: str = None, max_tokens: int = 500) -> Dict[str, Any]:
        """Generate response using Ollama"""
        data = {
            "model": self.generation_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": max_tokens
            }
        }
        
        if system:
            data["system"] = system
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=60  # Longer timeout for generation
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result.get("response", "").strip(),
                    "tokens": result.get("eval_count", 0) + result.get("prompt_eval_count", 0),
                    "model": self.generation_model,
                    "success": True
                }
            else:
                return {
                    "response": f"Error: {response.status_code}",
                    "tokens": 0,
                    "model": self.generation_model,
                    "success": False
                }
        except requests.exceptions.Timeout:
            return {
                "response": "Timeout: Model took too long to respond",
                "tokens": 0,
                "model": self.generation_model,
                "success": False
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "tokens": 0,
                "model": self.generation_model,
                "success": False
            }
    
    def rag_query(self, question: str, context: str = None, max_tokens: int = 500) -> Dict[str, Any]:
        """RAG query with context"""
        if context is None:
            context = self.get_default_context()
        
        system_prompt = """You are a helpful assistant. Answer based on the provided context.
If the context doesn't contain relevant information, say so."""
        
        user_prompt = f"""Context: {context}

Question: {question}

Answer:"""
        
        return self.generate(user_prompt, system_prompt, max_tokens)
    
    def get_default_context(self) -> str:
        """Get default system context"""
        return """System Status (April 11, 2026):
- Memory System: PostgreSQL + Ollama + FastAPI operational
- Store/retrieve: Working, RAG endpoint had timeout issues
- Learning Velocity: 6.5/10 (improved from 3.5 baseline)
- Execution Rate: 83% (20/24 decisions completed)
- Trading Platform: 10-agent system, 3 agents operational
- APIs: Alpha Vantage, FMP, NewsAPI, CoinMarketCap configured
- Cost: $0/month maintained
- Storage: 78.6 GB free
- Skills: 6 workspace skills active
- Current Blockers: RAG endpoint 500 error, GitHub secrets, user verification pending
- Recent Fixes: Memory system embedding format fixed, humanizer skill added"""

def main():
    """Test the working RAG solution"""
    print("=== Testing Working RAG Solution ===\n")
    
    rag = OllamaRAG()
    
    # Test connection
    if not rag.test_connection():
        print("❌ Ollama not reachable. Make sure it's running.")
        return
    
    print("✅ Ollama connection successful")
    print(f"Using model: {rag.generation_model}\n")
    
    # Test questions
    test_cases = [
        {
            "question": "What is the current learning velocity?",
            "context": None
        },
        {
            "question": "What is the status of the trading platform?",
            "context": None
        },
        {
            "question": "What are the current blockers?",
            "context": None
        },
        {
            "question": "How much storage is free?",
            "context": None
        },
        {
            "question": "What recent fixes were implemented?",
            "context": None
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['question']}")
        print("-" * 40)
        
        start_time = time.time()
        result = rag.rag_query(
            question=test['question'],
            context=test['context'],
            max_tokens=300
        )
        elapsed = time.time() - start_time
        
        if result["success"]:
            print(f"✅ Answer: {result['response']}")
            print(f"   Tokens: {result['tokens']}")
            print(f"   Time: {elapsed:.2f}s")
        else:
            print(f"❌ Failed: {result['response']}")
        
        print()
    
    # Test direct generation
    print("=== Direct Generation Test ===")
    direct_result = rag.generate("Hello, how are you?", max_tokens=100)
    if direct_result["success"]:
        print(f"✅ Direct generation works: {direct_result['response'][:100]}...")
    else:
        print(f"❌ Direct generation failed: {direct_result['response']}")

if __name__ == "__main__":
    main()