#!/usr/bin/env python3
"""
SocialDrive MCP Server - Production Ready
Uses Claude API for reliable caption generation
"""

import os
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests
from PIL import Image
import base64
import io
from anthropic import Anthropic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = int(os.getenv('PORT', '8765'))

# Initialize Claude client (API key from Railway env)
ANTHROPIC_API_KEY=os.getenv('ANTHROPIC_API_KEY', '')
if not ANTHROPIC_API_KEY:
    logger.error("❌ ANTHROPIC_API_KEY not set in environment variables!")
    sys.exit(1)

# Debug: Show key details (not the full key!)
logger.info(f"🔑 API Key length: {len(ANTHROPIC_API_KEY)} chars")
logger.info(f"🔑 API Key stripped: {len(ANTHROPIC_API_KEY.strip())} chars")
logger.info(f"🔑 Has whitespace: {ANTHROPIC_API_KEY != ANTHROPIC_API_KEY.strip()}")
logger.info(f"🔑 First 8 chars: {ANTHROPIC_API_KEY[:8]}")
logger.info(f"🔑 Last 8 chars: ...{ANTHROPIC_API_KEY[-8:]}")

# Strip any whitespace/newlines
ANTHROPIC_API_KEY=ANTHROPIC_API_KEY.strip()

client = Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL = "claude-sonnet-4-5-20250929"  # Latest Claude Sonnet

logger.info(f"✅ MCP Server starting on port {PORT}")
logger.info(f"✅ Using Claude model: {MODEL}")
logger.info(f"🔑 API Key configured: {bool(ANTHROPIC_API_KEY)}")
logger.info(f"🔑 API Key starts with: {ANTHROPIC_API_KEY[:10] if ANTHROPIC_API_KEY else 'None'}...")

# Test Claude API connectivity on startup
try:
    test_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    test_response = test_client.messages.create(
        model=MODEL,
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}],
        timeout=10.0
    )
    logger.info(f"✅ Claude API connectivity test PASSED")
except Exception as e:
    logger.error(f"❌ Claude API connectivity test FAILED: {e}")
    logger.error("⚠️ Server will start but Claude calls will fail!")


def encode_image(image_path):
    """Encode image to base64 from file path"""
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            max_size = 1024
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logger.error(f"Image encoding failed: {e}")
        return None


def decode_base64_image(base64_string):
    """Decode base64 string to image bytes for Claude API"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        
        # Validate and resize
        img = Image.open(io.BytesIO(image_data))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        max_size = 1024
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logger.error(f"Base64 decode failed: {e}")
        return None


def generate_captions(image_base64, template_match, industry, count=3, brief_text=None):
    """Generate caption variations using Claude API
    
    Args:
        image_base64: Base64 encoded image
        template_match: Template analysis result
        industry: Industry name (e.g., 'barber')
        count: Number of caption variations (default 3)
        brief_text: Optional brief/promo text to include (e.g., "Free places for first 10")
    
    Returns:
        {"success": True, "captions": [...], "hashtags": [...]}
    """
    try:
        logger.info(f"📸 Generating {count} captions with Claude...")
        if brief_text:
            logger.info(f"📝 Including brief text: {brief_text}")
        
        # Strip data URL prefix if present
        if image_base64 and ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
            logger.info("📷 Stripped data URL prefix from caption generation")
        
        # Determine media type
        media_type = "image/jpeg"
        if image_base64 and image_base64.startswith('data:'):
            if 'png' in image_base64.split(',')[0]:
                media_type = "image/png"
            elif 'gif' in image_base64.split(',')[0]:
                media_type = "image/gif"
        
        # Build industry-specific context
        if industry == 'barber':
            industry_context = """You are writing social media captions for No Label Academy, a barber training academy.
Style: Professional yet approachable, educational, inspiring.
Audience: Aspiring barbers, current students, haircut enthusiasts.
Hashtags: Use barber-specific tags like #BarberAcademy #BarberTraining #BarberLife #FadeGame #BarberSchool #BarberSkills #HaircutEducation"""
        else:
            industry_context = f"""You are writing social media captions for a {industry} business.
Style: Professional, engaging, on-brand.
Hashtags: Use industry-specific relevant tags."""
        
        # Extract scene info
        scene_type = template_match.get('scene_type', 'general')
        key_elements = template_match.get('key_elements', [])
        
        # Build prompt
        brief_instruction = f"\n\nIMPORTANT PROMOTION TO INCLUDE: {brief_text}\nMake sure to naturally incorporate this offer into each caption." if brief_text else ""
        
        prompt = f"""{industry_context}

Analyze this image and generate {count} UNIQUE social media caption variations.

Image context:
- Scene type: {scene_type}
- Key elements: {', '.join(key_elements) if key_elements else 'Various elements visible'}{brief_instruction}

Each caption should:
1. Be 2-4 sentences (Instagram/Facebook length)
2. Include a hook/opening line
3. Reference the image content naturally
4. End with a call-to-action or question
5. Include 5-8 relevant hashtags
6. {f'NATURALLY incorporate the promotion: "{brief_text}"' if brief_text else 'Be engaging and shareable'}

Respond ONLY with valid JSON in this exact format:
{{
  "captions": [
    {{"caption": "caption text here", "hashtags": ["#tag1", "#tag2", "#tag3"]}},
    {{"caption": "another caption", "hashtags": ["#tag4", "#tag5"]}}
  ]
}}

Do NOT include any other text, explanations, or markdown formatting.
Make each caption distinct - vary the tone, hooks, and CTAs."""
        
        # Call Claude API with image
        logger.info(f"🤖 Calling Claude API...")
        
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            timeout=30.0,  # 30 second timeout
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Parse response
        response_text = response.content[0].text
        logger.info(f"📝 Claude response received ({len(response_text)} chars)")
        
        # Extract JSON from response
        try:
            # Find JSON in response (may have markdown formatting)
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                parsed = json.loads(json_match.group())
                captions = parsed.get('captions', [])
                
                # Validate and format
                formatted_captions = []
                all_hashtags = set()
                
                for cap in captions[:count]:
                    if isinstance(cap, dict):
                        text = cap.get('caption', cap.get('text', ''))
                        tags = cap.get('hashtags', [])
                        if text:
                            formatted_captions.append({
                                "caption": text.strip(),
                                "hashtags": tags if tags else []
                            })
                            all_hashtags.update(tags)
                    elif isinstance(cap, str):
                        formatted_captions.append({
                            "caption": cap.strip(),
                            "hashtags": []
                        })
                
                logger.info(f"✅ Generated {len(formatted_captions)} captions")
                
                return {
                    "success": True,
                    "captions": formatted_captions,
                    "hashtags": list(all_hashtags),
                    "model": f"Claude 3.5 Sonnet"
                }
            else:
                logger.error("No JSON found in response")
                return {"success": False, "error": "Invalid response format"}
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return {"success": False, "error": f"JSON parse error: {e}"}
            
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")
        return {"success": False, "error": str(e)}


def template_match(image_base64, industry='barber'):
    """Analyze image and match to template using Claude"""
    try:
        logger.info("🔍 Analyzing image for template matching...")
        
        # Strip data URL prefix if present
        if image_base64 and ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
            logger.info("📷 Stripped data URL prefix")
        
        # Determine media type
        media_type = "image/jpeg"
        if image_base64 and image_base64.startswith('data:'):
            if 'png' in image_base64.split(',')[0]:
                media_type = "image/png"
            elif 'gif' in image_base64.split(',')[0]:
                media_type = "image/gif"
        
        prompt = f"""Analyze this {industry} business image and identify:
1. Scene type (e.g., 'training', 'before/after', 'product showcase')
2. Key elements visible
3. Main subject/focus
4. Suggested social media templates

Respond ONLY with valid JSON:
{{
  "scene_type": "type here",
  "key_elements": ["element1", "element2"],
  "main_subject": "subject description",
  "suggested_templates": ["template1", "template2"]
}}

No other text or markdown."""
        
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            timeout=30.0,  # 30 second timeout
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        response_text = response.content[0].text
        logger.info(f"📝 Template analysis complete")
        
        # Parse JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            template = json.loads(json_match.group())
            return {
                "success": True,
                "template_match": template,
                "model": MODEL
            }
        else:
            return {"success": False, "error": "Invalid template response"}
            
    except Exception as e:
        logger.error(f"Template matching failed: {e}")
        return {"success": False, "error": str(e)}


class MCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            logger.info(f"📥 POST {self.path} - {len(body)} bytes")
            
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                logger.error("❌ Invalid JSON in request")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            
            # Route requests
            if self.path == '/generate-captions':
                logger.info("🎨 Generating captions...")
                result = generate_captions(
                    image_base64=data.get('image_base64'),
                    template_match=data.get('template_match', {}),
                    industry=data.get('industry', 'barber'),
                    count=data.get('count', 3),
                    brief_text=data.get('brief_text')  # Pass brief text
                )
            elif self.path == '/template/match':
                logger.info("🔍 Matching template...")
                result = template_match(
                    image_base64=data.get('image_base64'),
                    industry=data.get('industry', 'barber')
                )
            else:
                logger.error(f"❌ Unknown endpoint: {self.path}")
                result = {"error": "Unknown endpoint"}
            
            logger.info(f"📤 Response: success={result.get('success', False)}")
            
            self.send_response(200 if result.get('success', False) else 400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"❌ POST handler error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        if self.path == '/health':
            result = {
                "status": "healthy",
                "llm_provider": "Claude API",
                "model": MODEL,
                "api_key_configured": bool(ANTHROPIC_API_KEY)
            }
            self.send_response(200)
        else:
            result = {"error": "Not found"}
            self.send_response(404)
        
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), MCPHandler)
    logger.info(f"🚀 MCP Server running on port {PORT}")
    server.serve_forever()
