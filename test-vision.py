#!/usr/bin/env python3
"""Quick test for Ollama vision with llama3.2"""

import requests
import base64
from PIL import Image
import io
import sys

def encode_image(image_path):
    """Encode image to base64"""
    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode()

def test_vision(image_path, prompt="Describe this image in detail"):
    """Test Ollama vision with llama3.2"""
    print(f"Testing vision with: {image_path}")
    print(f"Model: llama3.2")
    print(f"Prompt: {prompt}")
    print("-" * 50)
    
    try:
        image_data = encode_image(image_path)
        print(f"✓ Image encoded ({len(image_data)} bytes)")
        
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Analysis complete!")
            print(f"\nResult:\n{result.get('response', 'No response')[:500]}...")
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test-vision.py <image_path>")
        sys.exit(1)
    
    test_vision(sys.argv[1])
