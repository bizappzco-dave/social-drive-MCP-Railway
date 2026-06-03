#!/usr/bin/env python3
"""
Simple HTTP image analyzer for SocialDrive
Uses existing ollama_client module
Minimal dependencies - only requests + pillow (already installed)
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

# Configure
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = int(os.getenv('PORT', '8765'))
# Use Railway env var directly (don't fallback to localhost)
OLLAMA_URL = os.getenv('OLLAMA_BASE_URL') or 'http://localhost:11434'
MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')


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
    """Decode base64 string to image bytes"""
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


def generate_captions(image_source, template_match, industry, count=15, is_base64=False):
    """Generate multiple caption variations using Ollama
    
    Args:
        image_source: File path or base64 string
        template_match: Template analysis result from /template/match
        industry: Industry name (e.g., 'barber')
        count: Number of caption variations to generate
        is_base64: Whether image_source is base64 encoded
    
    Returns:
        {"success": True, "captions": [...], "hashtags": [...]}
    """
    try:
        # Check Ollama health
        try:
            resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if resp.status_code != 200:
                return {"success": False, "error": "Ollama service not available"}
        except Exception as e:
            return {"success": False, "error": f"Ollama connection failed: {e}"}
        
        # Encode image
        if is_base64:
            image_data = decode_base64_image(image_source)
        else:
            image_data = encode_image(image_source)
            
        if not image_data:
            return {"success": False, "error": "Failed to encode image"}
        
        # Build caption generation prompt
        scene_type = template_match.get('scene_type', 'general')
        key_elements = template_match.get('key_elements', [])
        suggested_templates = template_match.get('suggested_templates', [])
        
        if industry == 'barber':
            industry_context = """You are writing social media captions for No Label Academy, a barber training academy.
Style: Professional yet approachable, educational, inspiring.
Audience: Aspiring barbers, current students, haircut enthusiasts.
Hashtags: Use barber-specific tags like #BarberAcademy #BarberTraining #BarberLife #FadeGame #BarberSchool #BarberSkills #HaircutEducation"""
        else:
            industry_context = f"""You are writing social media captions for a {industry} business.
Style: Professional, engaging, on-brand.
Hashtags: Use industry-specific relevant tags."""
        
        prompt = f"""{industry_context}

Generate {count} UNIQUE social media caption variations. Each should:
1. Be 2-4 sentences (Instagram/Facebook length)
2. Include a hook/opening line
3. Reference the image content naturally
4. End with a call-to-action or question
5. Include 5-8 relevant hashtags

Respond ONLY with valid JSON in this exact format:
{{"captions": [{{"text": "caption here", "hashtags": ["#tag1", "#tag2"]}}]}}

Do NOT include any other text, explanations, or markdown formatting.
Make each caption distinct - vary the tone, hooks, and CTAs."""

        # Call Ollama
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.8,  # Higher creativity for variety
                "top_p": 0.9,
            }
        }
        
        logger.info(f"Generating {count} captions with {MODEL}...")
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        
        if response.status_code != 200:
            return {"success": False, "error": f"Ollama API error: {response.status_code}"}
        
        result = response.json()
        response_text = result.get('response', '')
        
        # Parse JSON from response
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
                        text = cap.get('text', cap.get('caption', ''))
                        tags = cap.get('hashtags', [])
                        if text:
                            formatted_captions.append({
                                "caption": text.strip(),
                                "hashtags": tags if tags else []
                            })
                            all_hashtags.update(tags)
                    elif isinstance(cap, str):
                        # Caption without separate hashtags
                        formatted_captions.append({
                            "caption": cap.strip(),
                            "hashtags": []
                        })
                
                logger.info(f"✓ Generated {len(formatted_captions)} captions")
                
                return {
                    "success": True,
                    "captions": formatted_captions,
                    "hashtags": list(all_hashtags),
                    "model": MODEL
                }
            else:
                logger.error("No JSON found in response")
                return {"success": False, "error": "Invalid response format"}
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return {"success": False, "error": f"Failed to parse response: {e}"}
            
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")
        return {"success": False, "error": str(e)}


def analyze_image(image_source, prompt="Describe this image in detail", is_base64=False):
    """Analyze image using Ollama
    
    Args:
        image_source: File path (if is_base64=False) or base64 string (if is_base64=True)
        prompt: Analysis prompt
        is_base64: Whether image_source is base64 encoded
    """
    try:
        # Check Ollama health
        try:
            resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if resp.status_code != 200:
                return {"success": False, "error": "Ollama service not available"}
        except Exception as e:
            return {"success": False, "error": f"Ollama connection failed: {e}"}
        
        # Encode image
        if is_base64:
            image_data = decode_base64_image(image_source)
        else:
            image_data = encode_image(image_source)
            
        if not image_data:
            return {"success": False, "error": "Failed to encode image"}
        
        # Call Ollama
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }
        
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        if resp.status_code == 200:
            result = resp.json()
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": MODEL
            }
        else:
            return {"success": False, "error": f"Ollama error: {resp.status_code} - {resp.text[:200]}"}
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return {"success": False, "error": str(e)}


class ImageAnalyzerHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/health':
            try:
                resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
                self.send_json({
                    "status": "healthy" if resp.status_code == 200 else "unhealthy",
                    "ollama_url": OLLAMA_URL,
                    "model": MODEL
                })
            except Exception as e:
                self.send_json({"status": "unhealthy", "error": str(e)}, 503)
        
        elif parsed.path == '/ollama/status':
            try:
                resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
                models = resp.json().get("models", []) if resp.status_code == 200 else []
                self.send_json({
                    "ollama_healthy": resp.status_code == 200,
                    "base_url": OLLAMA_URL,
                    "current_model": MODEL,
                    "available_models": [{"name": m["name"], "size": m.get("size", 0)} for m in models]
                })
            except Exception as e:
                self.send_json({"error": str(e)}, 503)
        
        else:
            self.send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except:
            self.send_json({"error": "Invalid JSON"}, 400)
            return
        
        if parsed.path == '/analyze':
            image_path = data.get('image_path')
            prompt = data.get('prompt', 'Describe this image in detail for social media content creation')
            
            if not image_path:
                self.send_json({"error": "image_path required"}, 400)
                return
            
            logger.info(f"Analyzing image: {image_path}")
            result = analyze_image(image_path, prompt)
            self.send_json(result)
        
        elif parsed.path == '/analyze-base64':
            image_base64 = data.get('image_base64')
            prompt = data.get('prompt', 'Describe this image in detail for social media content creation')
            
            if not image_base64:
                self.send_json({"error": "image_base64 required"}, 400)
                return
            
            logger.info(f"Analyzing base64 image (length: {len(image_base64)})")
            result = analyze_image(image_base64, prompt, is_base64=True)
            self.send_json(result)
        
        elif parsed.path == '/template/match':
            image_path = data.get('image_path')
            image_base64 = data.get('image_base64')
            industry = data.get('industry', 'barber')
            
            if not image_path and not image_base64:
                self.send_json({"error": "image_path or image_base64 required"}, 400)
                return
            
            # Industry-specific prompt
            if industry == 'barber':
                prompt = """Analyze this image for a barber academy. Identify:
1. What type of scene is this? (training, haircut, equipment, team, storefront, before/after)
2. What key elements are visible? (barber chairs, clippers, mirrors, students, instructors)
3. What is the main subject?
4. Suggest 2-3 relevant social media post templates for this image type.

Respond in JSON format:
{
  "scene_type": "...",
  "key_elements": ["...", "..."],
  "main_subject": "...",
  "suggested_templates": ["template1", "template2"]
}"""
            else:
                prompt = "Analyze this image and suggest social media templates. What type of scene is this?"
            
            logger.info(f"Matching template for {industry} industry")
            
            # Use base64 if provided, otherwise file path
            if image_base64:
                logger.info(f"Using base64 image (length: {len(image_base64)})")
                result = analyze_image(image_base64, prompt, is_base64=True)
            else:
                logger.info(f"Using file path: {image_path}")
                result = analyze_image(image_path, prompt)
            
            self.send_json(result)
        
        elif parsed.path == '/generate-captions':
            image_path = data.get('image_path')
            image_base64 = data.get('image_base64')
            template_match = data.get('template_match')
            industry = data.get('industry', 'barber')
            count = data.get('count', 15)

            # template_match may be a raw string (from /template/match response field) or a dict
            if isinstance(template_match, str):
                try:
                    import re
                    json_match = re.search(r'\{.*\}', template_match, re.DOTALL)
                    if json_match:
                        template_match = json.loads(json_match.group())
                    else:
                        template_match = {"scene_type": "general", "key_elements": [], "main_subject": template_match, "suggested_templates": []}
                except Exception:
                    template_match = {"scene_type": "general", "key_elements": [], "main_subject": str(template_match), "suggested_templates": []}
            
            if not image_path and not image_base64:
                self.send_json({"error": "image_path or image_base64 required"}, 400)
                return
            
            if not template_match:
                self.send_json({"error": "template_match required (from /template/match)"}, 400)
                return
            
            logger.info(f"Generating {count} captions for {industry} industry")
            
            # Use base64 if provided, otherwise file path
            if image_base64:
                logger.info(f"Using base64 image (length: {len(image_base64)})")
                result = generate_captions(image_base64, template_match, industry, count, is_base64=True)
            else:
                logger.info(f"Using file path: {image_path}")
                result = generate_captions(image_path, template_match, industry, count)
            
            self.send_json(result)
        
        else:
            self.send_json({"error": "Not found"}, 404)


def run_server():
    """Start HTTP server"""
    server = HTTPServer(('0.0.0.0', PORT), ImageAnalyzerHandler)
    logger.info("=" * 60)
    logger.info("Image Analyzer HTTP Server")
    logger.info("=" * 60)
    logger.info(f"Port: {PORT}")
    logger.info(f"Ollama URL: {OLLAMA_URL}")
    logger.info(f"Model: {MODEL}")
    logger.info("=" * 60)
    logger.info(f"Server starting on http://0.0.0.0:{PORT}")
    logger.info("Endpoints:")
    logger.info("  GET  /health          - Health check")
    logger.info("  GET  /ollama/status   - Ollama service status")
    logger.info("  POST /analyze         - Analyze single image (file path)")
    logger.info("  POST /analyze-base64  - Analyze single image (base64)")
    logger.info("  POST /template/match  - Match image to template (supports both)")
    logger.info("  POST /generate-captions - Generate 15 captions with hashtags")
    logger.info("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    run_server()
