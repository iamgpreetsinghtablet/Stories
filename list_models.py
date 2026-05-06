import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")
BASE_URL = "https://integrate.api.nvidia.com/v1"

def list_models():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }
    response = requests.get(f"{BASE_URL}/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        return [model['id'] for model in models.get('data', [])]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

if __name__ == "__main__":
    models = list_models()
    print("Available Models:")
    for model in models:
        print(f"- {model}")
