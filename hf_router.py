#!/usr/bin/env python3
"""
HuggingFace Router API helper for OpenAI-compatible chat completions.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    raise ValueError("HUGGINGFACE_TOKEN not found in environment variables")

ROUTER_BASE_URL = "https://router.huggingface.co/v1"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# Default model: choose a powerful free model
# meta-llama/Llama-3.1-8B-Instruct has low cost (some free credits)
# If that fails, fallback to another model
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
FALLBACK_MODEL = "Qwen/Qwen2.5-7B-Instruct"

def chat_completion(
    messages: list,
    model: Optional[str] = None,
    max_tokens: int = 500,
    temperature: float = 0.2,
    top_p: float = 0.95,
    json_mode: bool = False
) -> Dict[str, Any]:
    """
    Send chat completion request to HuggingFace Router.
    
    Args:
        messages: List of dicts with role and content
        model: Model ID (defaults to DEFAULT_MODEL)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        top_p: Top-p sampling
        json_mode: Whether to request JSON output (if supported)
    
    Returns:
        Dict with 'content' (str) and 'usage' if available
    """
    if model is None:
        model = DEFAULT_MODEL
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    
    url = f"{ROUTER_BASE_URL}/chat/completions"
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            return {
                "content": content,
                "usage": usage,
                "model": result.get("model", model)
            }
        else:
            raise ValueError(f"Unexpected response format: {result}")
    
    except requests.exceptions.HTTPError as e:
        # If 404 or model not found, try fallback
        if response.status_code in [404, 400] and model != FALLBACK_MODEL:
            print(f"Model {model} failed ({response.status_code}), trying fallback {FALLBACK_MODEL}")
            return chat_completion(messages, model=FALLBACK_MODEL, max_tokens=max_tokens,
                                   temperature=temperature, top_p=top_p, json_mode=json_mode)
        else:
            raise Exception(f"Router API error: {e}\nResponse: {response.text}")
    except Exception as e:
        raise Exception(f"Router API request failed: {e}")

def analyze_with_llm(prompt: str, json_output: bool = True, **kwargs) -> Any:
    """
    High-level function to analyze a prompt with LLM.
    
    Args:
        prompt: The prompt text
        json_output: Whether to expect JSON output (will attempt to parse)
        **kwargs: Additional kwargs passed to chat_completion
    
    Returns:
        Parsed JSON if json_output=True and parsing succeeds, else text
    """
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt}
    ]
    
    result = chat_completion(messages, json_mode=json_output, **kwargs)
    content = result["content"]
    
    if json_output:
        try:
            # Try to extract JSON from markdown code block or plain JSON
            import re
            json_match = re.search(r'```json\n?(.*?)\n?```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            elif content.strip().startswith('{'):
                # Already JSON
                pass
            else:
                # Try to find JSON object in text
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    content = match.group(0)
            
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Failed to parse JSON from LLM response: {e}")
            print(f"Raw content: {content[:200]}...")
            # Return raw content as dict
            return {"raw_output": content, "error": "JSON parsing failed"}
    else:
        return content

if __name__ == "__main__":
    # Test the router
    test_prompt = "What is the capital of France? Answer in JSON format with key 'capital'."
    try:
        result = analyze_with_llm(test_prompt, json_output=True, max_tokens=100)
        print("Test successful!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()