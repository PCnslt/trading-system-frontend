#!/usr/bin/env python3
"""Test Hugging Face Router API"""
import os
import requests
import json

# Load API key from environment
API_KEY = os.getenv("HUGGINGFACE_TOKEN")
if not API_KEY:
    print("HUGGINGFACE_TOKEN environment variable not set")
    exit(1)

print(f"Hugging Face API Key: {API_KEY[:10]}...")

# Use the new router endpoint
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test the router endpoint
router_url = "https://router.huggingface.co/hf-inference/models"

# First, check available models
try:
    print("Checking available models via router...")
    response = requests.get(
        f"{router_url}",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        models = response.json()
        print(f"Available models: {len(models)}")
        # Show first few
        for i, model in enumerate(models[:5]):
            print(f"  {i+1}. {model.get('id', 'Unknown')}")
    else:
        print(f"Error checking models: {response.status_code} - {response.text[:200]}")
        
except Exception as e:
    print(f"Exception checking models: {e}")

# Try a simple chat completion
print("\nTrying chat completion...")
data = {
    "inputs": "What is 2+2? Answer in one word.",
    "parameters": {
        "max_new_tokens": 10,
        "temperature": 0.1
    }
}

# Try with a known working model
try:
    response = requests.post(
        f"{router_url}/microsoft/phi-2",
        headers=headers,
        json=data,
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Result: {result}")
    elif response.status_code == 503:
        print("Model is loading (normal)")
    else:
        print(f"Error: {response.text[:200]}")
        
except Exception as e:
    print(f"Exception: {e}")

# Try embedding
print("\nTrying embedding...")
embedding_data = {
    "inputs": "Test sentence for embedding"
}

try:
    response = requests.post(
        f"{router_url}/sentence-transformers/all-MiniLM-L6-v2",
        headers=headers,
        json=embedding_data,
        timeout=15
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Embedding shape would be: {len(result)} dimensions")
    else:
        print(f"Error: {response.text[:200]}")
        
except Exception as e:
    print(f"Exception: {e}")