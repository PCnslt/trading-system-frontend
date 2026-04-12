import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    print("ERROR: HUGGINGFACE_TOKEN not found in .env")
    exit(1)

print(f"Token present: {HF_TOKEN[:10]}...")

# Test Inference API with a simple model
url = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
payload = {"inputs": "Hello, how are you?"}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# List available models (requires different endpoint)
url_models = "https://api-inference.huggingface.co/models"
try:
    response = requests.get(url_models, headers=headers, timeout=30)
    print(f"Models status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"Total models: {len(models)}")
        # Show first 5
        for model in models[:5]:
            print(f"  - {model.get('id', 'N/A')}")
    else:
        print(f"Models error: {response.text}")
except Exception as e:
    print(f"Models exception: {e}")