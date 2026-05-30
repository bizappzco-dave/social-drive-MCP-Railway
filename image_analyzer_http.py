"""
HTTP Server wrapper for Image Analyzer MCP
Allows SocialDrive to call image analysis via HTTP REST API
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from ollama_client import OllamaClient, create_client
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Image Analyzer API", version="1.0.0")

# Global Ollama client
ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance"""
    global ollama_client
    if ollama_client is None:
        ollama_client = create_client()
        logger.info(f"Ollama client created - URL: {ollama_client.base_url}, Model: {ollama_client.model}")
    return ollama_client


class ImageAnalysisRequest(BaseModel):
    image_path: str
    prompt: Optional[str] = "Describe this image in detail for social media content creation"


class BatchAnalysisRequest(BaseModel):
    images: List[Dict[str, str]]  # List of {path: ..., prompt: ...}


class TemplateMatchRequest(BaseModel):
    image_path: str
    industry: Optional[str] = "barber"


@app.get("/health")
async def health_check():
    """Check if service is healthy"""
    try:
        client = get_ollama_client()
        is_healthy = client.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "ollama_url": client.base_url,
            "model": client.model
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/analyze")
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze a single image
    
    Returns:
    - Image description
    - Detected objects/scenes
    - Suggested social media angles
    """
    try:
        client = get_ollama_client()
        result = client.analyze_image(request.image_path, request.prompt)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))
        
        return result
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def batch_analyze(request: BatchAnalysisRequest):
    """
    Analyze multiple images at once
    
    Returns analysis for each image
    """
    results = []
    for img_data in request.images:
        try:
            client = get_ollama_client()
            prompt = img_data.get("prompt", "Describe this image in detail")
            result = client.analyze_image(img_data["path"], prompt)
            results.append({
                "path": img_data["path"],
                "success": result.get("success", False),
                "analysis": result.get("response", ""),
                "error": result.get("error")
            })
        except Exception as e:
            results.append({
                "path": img_data["path"],
                "success": False,
                "error": str(e)
            })
    
    return {"results": results, "total": len(results)}


@app.post("/template/match")
async def match_template(request: TemplateMatchRequest):
    """
    Analyze image and suggest matching template
    
    For barber industry, detects:
    - Before/after shots
    - Training/education scenes
    - Equipment/tools
    - Team/staff photos
    - Storefront/interior
    """
    try:
        client = get_ollama_client()
        
        # Use industry-specific prompt
        if request.industry == "barber":
            prompt = """Analyze this image for a barber academy. Identify:
1. What type of scene is this? (training, haircut, equipment, team, storefront, before/after)
2. What key elements are visible? (barber chairs, clippers, mirrors, students, instructors)
3. What is the main subject? (person getting haircut, student learning, tools, building)
4. Suggest 2-3 relevant social media post templates for this image type.

Respond in JSON format:
{
  "scene_type": "...",
  "key_elements": ["...", "..."],
  "main_subject": "...",
  "suggested_templates": ["template1", "template2"]
}"""
        else:
            prompt = "Analyze this image and suggest social media templates. What type of scene is this and what templates would work best?"
        
        result = client.analyze_image(request.image_path, prompt)
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))
        
        # Try to parse JSON from response
        analysis_text = result.get("response", "")
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {
                    "success": True,
                    "analysis": parsed,
                    "raw_analysis": analysis_text
                }
        except:
            pass
        
        return {
            "success": True,
            "analysis": {"raw": analysis_text},
            "raw_analysis": analysis_text
        }
        
    except Exception as e:
        logger.error(f"Template matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ollama/status")
async def ollama_status():
    """Check Ollama service status and list available models"""
    try:
        client = get_ollama_client()
        models = client.list_models()
        return {
            "ollama_healthy": client.health_check(),
            "base_url": client.base_url,
            "current_model": client.model,
            "available_models": models
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8765"))
    logger.info(f"Starting Image Analyzer HTTP API on port {port}")
    logger.info(f"Ollama URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    logger.info(f"Ollama Model: {os.getenv('OLLAMA_MODEL', 'llama3.2')}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
