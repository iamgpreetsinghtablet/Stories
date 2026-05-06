import os
import requests
import json
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")
BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "meta/llama-3.1-405b-instruct"

# We will generate 3 different story concepts
CONCEPTS = [
    "A small blue robot named Pip who finds a lost kitten in a futuristic neon city.",
    "A brave little squirrel named Nutmeg who discovers a secret library inside a giant oak tree.",
    "A lonely star named Sparky who falls to Earth and is helped by a kind girl to find its way home."
]

def generate_full_story(concept):
    print(f"Generating story for: {concept[:50]}...")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Write a high-quality children's story based on this concept: {concept}
    
    The output MUST be in the following JSON format:
    {{
        "title": "A creative title",
        "story": "The full story (300-500 words), engaging and heartwarming.",
        "moral": "A gentle moral of the story.",
        "image_prompt": "A highly detailed visual prompt for an image generator to create a beautiful illustration of a key scene. Style: Digital art, soft lighting, children's book style."
    }}
    """
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def download_image(prompt, filename):
    print(f"Generating image for: {filename}...")
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&model=flux"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"Failed to download image: {response.status_code}")
            return False
    except Exception as e:
        print(f"Exception downloading image: {e}")
        return False

def main():
    output_dir = "Gemini/Story_generator/stories"
    os.makedirs(output_dir, exist_ok=True)
    
    for concept in CONCEPTS:
        content_json = generate_full_story(concept)
        if content_json:
            data = json.loads(content_json)
            title = data['title']
            story = data['story']
            moral = data['moral']
            image_prompt = data['image_prompt']
            
            slug = title.lower().replace(" ", "_").replace(":", "").replace("'", "")
            
            # Save Story
            story_path = os.path.join(output_dir, f"{slug}.txt")
            with open(story_path, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\n")
                f.write(f"Moral: {moral}\n")
                f.write("="*40 + "\n\n")
                f.write(story)
            
            # Save Image
            image_path = os.path.join(output_dir, f"{slug}.jpg")
            if download_image(image_prompt, image_path):
                print(f"Saved story and image for: {title}")
            else:
                print(f"Saved story but failed image for: {title}")

if __name__ == "__main__":
    main()
