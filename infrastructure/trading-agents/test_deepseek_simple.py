#!/usr/bin/env python3
"""Test DeepSeek API with correct key"""
import os
import requests
import json

# Use the environment variable
API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-8102ecc06abb44c8a893229c3373ef02")
print(f"Testing DeepSeek API with key: {API_KEY[:10]}...")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2? Answer in one word."}
    ],
    "temperature": 0.1,
    "max_tokens": 10
}

try:
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Response: {result['choices'][0]['message']['content']}")
        print(f"Tokens used: {result['usage']['total_tokens']}")
        print(f"Cost: ${result['usage']['total_tokens'] * 0.0000014:.6f}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")