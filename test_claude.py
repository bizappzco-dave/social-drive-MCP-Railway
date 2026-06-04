#!/usr/bin/env python3
"""Test Claude API connection"""
import os
from anthropic import Anthropic

API_KEY = os.getenv('ANTHROPIC_API_KEY')
print(f"API Key present: {bool(API_KEY)}")
print(f"API Key starts with: {API_KEY[:10] if API_KEY else 'None'}...")

try:
    client = Anthropic(api_key=API_KEY)
    print("✅ Claude client initialized")
    
    # Simple test call
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print(f"✅ API call successful: {response.content[0].text}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
