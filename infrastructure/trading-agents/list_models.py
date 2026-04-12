import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
url = "https://router.huggingface.co/v1/models"

response = requests.get(url, headers=headers, timeout=30)
print(f"Status: {response.status_code}")
print(f"Response type: {type(response.json())}")
data = response.json()
print(f"Raw data: {data}")
if isinstance(data, list):
    for i, item in enumerate(data):
        print(f"{i}: {item}")
elif isinstance(data, dict):
    for k, v in data.items():
        print(f"{k}: {v}")