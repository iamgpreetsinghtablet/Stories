import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")
BASE_URL = "https://integrate.api.nvidia.com/v1"

# Selected models for variety
MODELS = [
    "meta/llama-3.2-3b-instruct",
    "google/gemma-3-4b-it",
    "meta/llama-3.1-8b-instruct",
    "nvidia/llama-3.1-nemotron-70b-instruct",
    "mistralai/mixtral-8x7b-instruct-v0.1"
]

STORY_PROMPT = "Write a short, engaging children's story (about 300-500 words) about a small blue robot named Pip who finds a lost kitten in a futuristic city. The story should have a happy ending and a gentle moral."

def generate_story(model_id):
    output_dir = "Gemini/Story_generator/stories"
    filename = model_id.replace("/", "_").replace(".", "_") + ".txt"
    filepath = os.path.join(output_dir, filename)
    
    if os.path.exists(filepath):
        print(f"Skipping {model_id}, already exists.")
        return None

    print(f"Generating story with model: {model_id}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Combined prompt to avoid "System role not supported" errors
    combined_prompt = f"System: You are a creative children's book author.\n\nUser: {STORY_PROMPT}"
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": combined_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        # Added timeout to avoid hanging
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            story = result['choices'][0]['message']['content']
            print(f"Successfully generated story with {model_id}")
            return story
        else:
            print(f"Error with model {model_id}: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.Timeout:
        print(f"Timeout reached for model {model_id}")
        return None
    except Exception as e:
        print(f"Exception with model {model_id}: {e}")
        return None

def main():
    if not API_KEY:
        print("Error: NVIDIA_API_KEY not found in .env file.")
        return

    output_dir = "Gemini/Story_generator/stories"
    os.makedirs(output_dir, exist_ok=True)

    for model in MODELS:
        story = generate_story(model)
        if story:
            filename = model.replace("/", "_").replace(".", "_") + ".txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Model: {model}\n")
                f.write("="*40 + "\n\n")
                f.write(story)
            print(f"Saved story to {filepath}")
        else:
            print(f"Failed to generate story with {model}")

if __name__ == "__main__":
    main()
