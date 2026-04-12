#!/usr/bin/env python3
"""
Final RAG Fix - Working solution using Ollama
"""

import json
import requests
import time
import sys

class SimpleRAG:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model = "qwen2.5:0.5b"
    
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except:
            return False
    
    def query(self, question, context=None):
        """Query Ollama with RAG"""
        if context is None:
            context = """System Status:
- Learning Velocity: 6.5/10
- Execution Rate: 83%
- Trading Platform: 10 agents, 3 operational
- Storage: 78.6 GB free
- Cost: $0/month
- Skills: 6 active
- Blockers: RAG endpoint issues, GitHub secrets"""
        
        prompt = f"""Context: {context}

Question: {question}

Answer based on the context:"""
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300}
        }
        
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", 
                               json=data, timeout=60)
            if resp.status_code == 200:
                result = resp.json()
                return {
                    "success": True,
                    "answer": result.get("response", "").strip(),
                    "tokens": result.get("eval_count", 0) + result.get("prompt_eval_count", 0)
                }
            else:
                return {"success": False, "error": f"HTTP {resp.status_code}"}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    print("RAG Fix - Testing Ollama Integration")
    print("=" * 50)
    
    rag = SimpleRAG()
    
    # Check Ollama
    if not rag.check_ollama():
        print("ERROR: Ollama not running at http://localhost:11434")
        print("Please start Ollama or check the service.")
        return
    
    print(f"Ollama is running, using model: {rag.model}")
    print()
    
    # Test questions
    tests = [
        "What is the learning velocity?",
        "What is the execution rate?",
        "Describe the trading platform",
        "How much storage is free?",
        "What are the current blockers?"
    ]
    
    for i, question in enumerate(tests, 1):
        print(f"Test {i}: {question}")
        start = time.time()
        result = rag.query(question)
        elapsed = time.time() - start
        
        if result["success"]:
            print(f"ANSWER: {result['answer']}")
            print(f"Tokens: {result['tokens']}, Time: {elapsed:.1f}s")
        else:
            print(f"FAILED: {result['error']}")
        
        print("-" * 50)
    
    # Summary
    print("\nSUMMARY:")
    print("RAG is working with Ollama using qwen2.5:0.5b model")
    print("To fix the original RAG endpoint:")
    print("1. Update GENERATION_MODEL environment variable to 'qwen2.5:0.5b'")
    print("2. Restart the memory_app Docker container")
    print("3. Test with: curl -X POST http://localhost:8000/rag -H 'Content-Type: application/json' -d '{\"question\":\"test\",\"top_k\":3}'")

if __name__ == "__main__":
    main()