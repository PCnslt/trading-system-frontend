#!/usr/bin/env python3
"""
Clean additional secrets from files
"""

import os
import re

def clean_file(filepath):
    """Clean secrets from a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Hugging Face tokens
    content = re.sub(
        r'hf_[A-Za-z0-9]{30,}',
        'YOUR_HUGGINGFACE_TOKEN_HERE',
        content
    )
    
    # Replace OpenAI API keys
    content = re.sub(
        r'sk-[A-Za-z0-9]{48}',
        'YOUR_OPENAI_API_KEY_HERE',
        content
    )
    
    # Replace DeepSeek API keys
    content = re.sub(
        r'sk-[a-f0-9]{32}',
        'YOUR_DEEPSEEK_API_KEY_HERE',
        content
    )
    
    # Replace Groq API keys
    content = re.sub(
        r'gsk_[A-Za-z0-9]{48}',
        'YOUR_GROQ_API_KEY_HERE',
        content
    )
    
    # Replace Alpha Vantage API keys
    content = re.sub(
        r'[A-Z0-9]{16}',
        'YOUR_ALPHAVANTAGE_API_KEY_HERE',
        content
    )
    
    # Replace FMP API keys
    content = re.sub(
        r'[A-Za-z0-9]{20,}',
        'YOUR_FMP_API_KEY_HERE',
        content
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Cleaned: {filepath}")

def main():
    """Clean all files with secrets"""
    files_to_clean = [
        "first_recommendation.py",
        "fundamental_analyst.py",
        "generate_agents.py", 
        "macro_analyst.py",
        "options_analyst.py",
        "quant_analyst.py",
        "risk_analyst.py"
    ]
    
    for filepath in files_to_clean:
        if os.path.exists(filepath):
            clean_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()