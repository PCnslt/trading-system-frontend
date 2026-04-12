import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    print("ERROR: HUGGINGFACE_TOKEN not found")
    exit(1)

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# List available models
url = "https://router.huggingface.co/v1/models"
try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"Total models: {len(models)}")
        # Filter for text generation models
        text_models = [m for m in models if m.get('object') == 'model' and 'chat' in m.get('id', '').lower()]
        print(f"Text/chat models: {len(text_models)}")
        for model in text_models[:10]:
            print(f"  - {model.get('id')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test chat completion with a simple model
url = "https://router.huggingface.co/v1/chat/completions"
payload = {
    "model": "deepseek-ai/DeepSeek-R1:fastest",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 50
}
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"\nChat test status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['choices'][0]['message']['content']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Chat exception: {e}")