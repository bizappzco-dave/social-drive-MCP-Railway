#!/usr/bin/env python3
"""Test Claude API with direct key input"""
import sys
import os
from anthropic import Anthropic

print("=== Claude API Key Test ===\n")

# Get key from command line or environment
if len(sys.argv) > 1:
    API_KEY=sys.argv[1]
elif os.getenv('ANTHROPIC_API_KEY'):
    API_KEY=os.getenv('ANTHROPIC_API_KEY')
else:
    print("Usage: python3 test_api_key.py <your-api-key>")
    print("   or: export ANTHROPIC_API_KEY=sk-ant-... && python3 test_api_key.py")
    sys.exit(1)

print(f"\nKey length: {len(API_KEY)} chars")
print(f"Starts with: {API_KEY[:10]}...")
print(f"Ends with: ...{API_KEY[-10:]}")
print()

try:
    client = Anthropic(api_key=API_KEY)
    
    # Test 1: Simple text call
    print("📝 Test 1: Simple text generation...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'Hello, API is working!'"}]
    )
    print(f"✅ Test 1 PASSED: {response.content[0].text}")
    print()
    
    # Test 2: Image analysis (with tiny test image)
    print("🖼️  Test 2: Image analysis...")
    test_image = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAB//2Q=="
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": test_image}},
                {"type": "text", "text": "What color is this image? One word only."}
            ]
        }]
    )
    print(f"✅ Test 2 PASSED: {response.content[0].text}")
    print()
    
    print("🎉 ALL TESTS PASSED! Your API key is valid and working!")
    print("✅ You can use this key in Railway")
    
except Exception as e:
    print(f"❌ TEST FAILED: {e}")
    print()
    print("Possible issues:")
    print("1. Key is invalid or revoked")
    print("2. Key has spaces or formatting issues")
    print("3. Account has no API access enabled")
    print("4. Rate limit exceeded")
    print()
    print("Go to: https://console.anthropic.com/settings/keys")
    print("Create a NEW key and try again.")
