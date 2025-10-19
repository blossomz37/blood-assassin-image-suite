#!/usr/bin/env python3
"""
Image Generation Script using OpenRouter and Gemini 2.5 Flash Image
Reads prompts from image-prompts/ folder and generates images
"""

import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
import time
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Configuration
# Load .env from current working directory explicitly as a fallback
load_dotenv(dotenv_path=Path.cwd() / ".env")
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = "google/gemini-2.5-flash-image"  # Gemini 2.5 Flash Image model
PROMPTS_DIR = Path("image-prompts")
OUTPUT_DIR = Path("generated-images")

# Create a dedicated session; disable proxies inherited from env to avoid header stripping
SESSION = requests.Session()
SESSION.trust_env = False

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_image(prompt_text, output_filename):
    """
    Generate an image using OpenRouter API with Gemini 2.5 Flash Image
    
    Args:
        prompt_text: The text prompt for image generation
        output_filename: Name for the output file (without extension)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found in .env file")
        return False
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "HTTP-Referer": "https://github.com/yourusername/blood-assassin",  # Optional
        "X-Title": "Blood Assassin Image Generator"  # Optional
    }
    
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"Generate an image based on this prompt: {prompt_text}"
            }
        ],
        # Request image outputs explicitly per OpenRouter docs
        "modalities": ["image", "text"]
    }
    
    try:
        print(f"Generating image for: {output_filename}...")
        # Use our session and avoid cross-host redirects that may drop Authorization headers
        response = SESSION.post(url, json=payload, headers=headers, timeout=30, allow_redirects=False)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract image data from response per OpenRouter image generation format
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0].get('message', {})

            # Preferred path: images field with base64 data URLs
            images = message.get('images', []) or []
            saved_any = False
            for idx, img in enumerate(images, start=1):
                if isinstance(img, dict) and img.get('type') == 'image_url':
                    url = img.get('image_url', {}).get('url', '')
                else:
                    # Some providers may put the URL directly
                    url = (img.get('url') if isinstance(img, dict) else '') or ''

                if isinstance(url, str) and url.startswith('data:image'):
                    try:
                        header, b64 = url.split(',', 1)
                        image_bytes = base64.b64decode(b64)

                        if 'image/png' in header:
                            ext = 'png'
                        elif 'image/jpeg' in header or 'image/jpg' in header:
                            ext = 'jpg'
                        else:
                            ext = 'png'

                        suffix = f"_{idx}" if len(images) > 1 else ""
                        output_path = OUTPUT_DIR / f"{output_filename}{suffix}.{ext}"
                        with open(output_path, 'wb') as f:
                            f.write(image_bytes)
                        print(f"✓ Successfully saved: {output_path}")
                        saved_any = True
                    except Exception as e:
                        print(f"✗ Failed to decode/save image {idx}: {e}")

            if saved_any:
                return True

            # Fallback: some responses may inline a single data URL in content
            content = message.get('content')
            if isinstance(content, str) and content.startswith('data:image'):
                try:
                    header, b64 = content.split(',', 1)
                    image_bytes = base64.b64decode(b64)
                    if 'image/png' in header:
                        ext = 'png'
                    elif 'image/jpeg' in header or 'image/jpg' in header:
                        ext = 'jpg'
                    else:
                        ext = 'png'
                    output_path = OUTPUT_DIR / f"{output_filename}.{ext}"
                    with open(output_path, 'wb') as f:
                        f.write(image_bytes)
                    print(f"✓ Successfully saved: {output_path}")
                    return True
                except Exception as e:
                    print(f"✗ Failed to decode inline image: {e}")
                    return False

            # If we got here, no images were returned
            preview = (message.get('content') or '')
            print(f"✗ No image data in response. Assistant said: {str(preview)[:120]}")
            return False
        else:
            print(f"✗ No image data in response: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error generating image: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return False
    except (ValueError, KeyError, base64.binascii.Error) as e:
        print(f"✗ Unexpected parse error: {e}")
        return False

def main():
    """Main function to process all prompts"""
    if not OPENROUTER_API_KEY:
        print("Error: Please set OPENROUTER_API_KEY in your .env file")
        return

    # Validate key format (OpenRouter API keys usually start with 'sk-or-v1-')
    if not str(OPENROUTER_API_KEY).startswith("sk-or-v1-"):
        print("Error: The OPENROUTER_API_KEY in .env doesn't look like a standard OpenRouter API key.")
        print("Expected prefix: 'sk-or-v1-'. Current:", mask_key(OPENROUTER_API_KEY))
        print("Action: Visit https://openrouter.ai/keys and create a new API key, then update your .env.")
        return

    # Quick auth check before doing any work
    if not check_auth():
        return
    
    # Get all prompt files
    prompt_files = sorted(PROMPTS_DIR.glob("*.txt"))
    
    if not prompt_files:
        print(f"No prompt files found in {PROMPTS_DIR}")
        return
    
    print(f"Found {len(prompt_files)} prompt files")
    print(f"Model: {MODEL}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("-" * 60)
    
    successful = 0
    failed = 0
    
    for prompt_file in prompt_files:
        # Read prompt
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_text = f.read().strip()
        
        # Generate output filename (remove .txt extension)
        output_filename = prompt_file.stem
        
        # Generate image
        if generate_image(prompt_text, output_filename):
            successful += 1
        else:
            failed += 1
        
        # Rate limiting: wait between requests to avoid API limits
        time.sleep(2)
    
    print("-" * 60)
    print(f"Complete! Success: {successful}, Failed: {failed}")

# Helper functions
# ----------------------
# Helpers
# ----------------------
def mask_key(key: Optional[str]) -> str:
    if not key:
        return "<missing>"
    if len(key) <= 10:
        return key[:3] + "..." + key[-2:]
    return key[:8] + "..." + key[-6:]

def check_auth() -> bool:
    """Validate API auth by calling the models endpoint and printing diagnostics."""
    test_url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Accept": "application/json",
    }
    print("Auth check:",
          f"key={mask_key(OPENROUTER_API_KEY)}",
          f"endpoint={test_url}")
    try:
        resp = SESSION.get(test_url, headers=headers, timeout=15, allow_redirects=False)
        print(f"Auth check status: {resp.status_code}")
        # Show redirect info if any
        if 300 <= resp.status_code < 400:
            print("Auth check redirect:", resp.headers.get("Location"))
        if resp.status_code == 200:
            return True
        else:
            print("Auth check body:", resp.text[:300])
            print("Tip: If you see 401, verify the Authorization header reached the server and proxies aren't stripping it.")
            return False
    except requests.RequestException as e:
        print("Auth check error:", e)
        return False

if __name__ == "__main__":
    main()
