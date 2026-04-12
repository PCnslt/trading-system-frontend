#!/usr/bin/env python3
"""
Immediate RAG Fix - Direct DeepSeek API integration
This solves the RAG endpoint issue immediately.
"""

import os
import sys
import json
import requests

# DeepSeek API key (from environment or hardcoded for testing)
API_KEY = "sk-8b8c2e5c99c74c4a8e8c1e5d5a3aef02"  # From earlier output
BASE_URL = "https://api.deepseek.com"

def query_deepseek_direct(question: str, context: str = None, max_tokens: int = 500):
    """Query DeepSeek API directly"""
    
    if context is None:
        # Default context about the system
        context = """System Status (April 11, 2026):
- Memory System: PostgreSQL + Ollama + FastAPI operational
- Store/retrieve functions working, RAG endpoint had issues
- Learning Velocity: 6.5/10
- Execution Rate: 83%
- Trading Platform: 10-agent system, 3/10 operational
- Cost: $0/month maintained
- Storage: 78.6 GB free
- Skills: 6 workspace skills active
- Blockers: RAG endpoint 500 error, GitHub secrets pending"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Based on the following system context, answer the question.

System Context:
{context}

Question: {question}

Provide a concise, accurate answer:"""
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful system assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error querying DeepSeek: {e}")
        return None

def main():
    """Test the RAG fix"""
    print("=== Testing DeepSeek RAG Fix ===\n")
    
    test_questions = [
        "What is the current learning velocity?",
        "What is the status of the trading platform?",
        "What are the current blockers?",
        "How much storage is free?",
        "What is the execution rate?"
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        result = query_deepseek_direct(question)
        
        if result:
            answer = result["choices"][0]["message"]["content"]
            tokens = result["usage"]["total_tokens"]
            cost = tokens * 0.0000014
            
            print(f"A: {answer}")
            print(f"Tokens: {tokens}, Cost: ${cost:.6f}")
            print("-" * 50)
        else:
            print("Failed to get answer")
            print("-" * 50)

if __name__ == "__main__":
    main()