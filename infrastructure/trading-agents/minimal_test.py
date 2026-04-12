#!/usr/bin/env python3
"""Minimal DeepSeek test"""
import os
import requests
import json

# Use the API key we know works
API_KEY = "sk-8102ecc99c74c4a8e8c1e5d5a3aef02"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": "Say 'TEST OK' if you receive this."}
    ],
    "max_tokens": 10,
    "temperature": 0
}

try:
    print("Testing DeepSeek API...")
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"Response: {result['choices'][0]['message']['content']}")
        print("✅ DeepSeek API working")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")