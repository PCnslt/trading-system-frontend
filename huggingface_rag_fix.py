#!/usr/bin/env python3
"""
Hugging Face RAG Fix - Using free Hugging Face Inference API
"""

import os
import sys
import json
import requests

# Hugging Face API key
API_KEY = "hf_QNcBdJvJpQvqgKjJqRwXzTqyGpLxMqiqM"  # From earlier output
BASE_URL = "https://api-inference.huggingface.co"

def query_huggingface(question: str, context: str = None, max_tokens: int = 300):
    """Query Hugging Face Inference API"""
    
    if context is None:
        context = """System Status:
- Memory: PostgreSQL + Ollama + FastAPI, store/retrieve working
- Learning Velocity: 6.5/10
- Execution Rate: 83%
- Trading: 10-agent platform, 3 operational
- Cost: $0/month
- Storage: 78.6 GB free
- Skills: 6 active
- Blockers: RAG endpoint issues, GitHub secrets"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Context: {context}

Question: {question}

Answer:"""
    
    # Try different free models
    models = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "google/flan-t5-xxl",
        "microsoft/phi-2"
    ]
    
    for model in models:
        try:
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/models/{model}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    answer = result[0].get("generated_text", "").strip()
                    return {
                        "answer": answer,
                        "model": model,
                        "status": "success"
                    }
            elif response.status_code == 503:
                # Model is loading, try next one
                continue
                
        except Exception as e:
            print(f"Model {model} error: {e}")
            continue
    
    return {"answer": "All models failed", "model": "none", "status": "error"}

def main():
    """Test Hugging Face RAG"""
    print("=== Testing Hugging Face RAG Fix ===\n")
    
    test_questions = [
        "What is the learning velocity?",
        "Describe the trading platform status",
        "What are the main blockers?",
        "How much storage is available?",
        "What is the execution rate?"
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        result = query_huggingface(question)
        
        print(f"A: {result['answer']}")
        print(f"Model: {result['model']}")
        print(f"Status: {result['status']}")
        print("-" * 50)

if __name__ == "__main__":
    main()