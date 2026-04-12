#!/usr/bin/env python3
"""Test Hugging Face Inference API"""
import os
import requests
import json

# Load API key from environment
API_KEY = os.getenv("HUGGINGFACE_TOKEN")
if not API_KEY:
    print("HUGGINGFACE_TOKEN environment variable not set")
    exit(1)

print(f"Hugging Face API Key: {API_KEY[:10]}...")

# Test with a simple model
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Try a small, fast model first
models_to_test = [
    "microsoft/phi-2",  # Small, fast
    "google/flan-t5-small",  # Very small
    "distilbert/distilbert-base-uncased"  # Embedding model
]

for model in models_to_test:
    print(f"\nTesting model: {model}")
    
    if "embedding" in model or "bert" in model:
        # Test embedding
        data = {
            "inputs": "Test sentence for embedding"
        }
    else:
        # Test generation
        data = {
            "inputs": "What is 2+2? Answer:",
            "parameters": {
                "max_new_tokens": 10,
                "temperature": 0.1
            }
        }
    
    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json=data,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response type: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    print(f"Generated: {result[0]['generated_text'][:50]}...")
                else:
                    print(f"Result: {str(result)[:100]}...")
            else:
                print(f"Result: {str(result)[:100]}...")
        elif response.status_code == 503:
            print("Model is loading (normal for first request)")
        else:
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")