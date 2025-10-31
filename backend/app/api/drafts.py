from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.models.registry import ModelRegistry

router = APIRouter()
registry = ModelRegistry()

class GenerateDraftRequest(BaseModel):
    topic_id: Optional[str] = None
    model: str
    context: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = 2000

class CompareModelsRequest(BaseModel):
    models: List[str]  # List of model IDs to compare
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7

@router.post("/generate")
async def generate_draft(request: GenerateDraftRequest):
    """Generate newsletter draft using specified model"""
    try:
        # TODO: Build full prompt from topic context, knowledge base
        # For now, using provided context
        prompt = request.context or "Generate a Hinglish newsletter draft."
        
        # System prompt for Hinglish newsletter
        system_prompt = request.system_prompt or """You are a newsletter writer creating content in Hinglish (English script with Hindi words mixed naturally).
        
Style guidelines:
- English for logic and technical concepts
- Hindi for emotion and cultural context
- Sharp, witty, builder-energy tone
- Target audience: Engineers, designers, founders, builders
- Length: 500-800 words
- Structure: Hook → Context → Insight → Takeaway → Closing

Write naturally, mixing English and Hindi words seamlessly."""
        
        response = await registry.generate(
            prompt=prompt,
            model_id=request.model,
            system_prompt=system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            use_fallback=True
        )
        
        return {
            "draft": {
                "content": response.content,
                "title": "",  # Extract from content or generate separately
                "model": response.model,
                "provider": response.provider,
            },
            "metadata": {
                "tokens": {
                    "input": response.input_tokens,
                    "output": response.output_tokens,
                    "total": response.input_tokens + response.output_tokens
                },
                "estimated_cost": registry.estimate_cost(
                    response.input_tokens,
                    response.output_tokens,
                    response.model
                ),
                "finish_reason": response.finish_reason,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_models(request: CompareModelsRequest):
    """Generate drafts with multiple models for comparison"""
    try:
        if len(request.models) < 2:
            raise HTTPException(status_code=400, detail="At least 2 models required for comparison")
        if len(request.models) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 models for comparison")
        
        results = []
        for model_id in request.models:
            try:
                response = await registry.generate(
                    prompt=request.prompt,
                    model_id=model_id,
                    system_prompt=request.system_prompt,
                    temperature=request.temperature,
                    use_fallback=True
                )
                results.append({
                    "model": model_id,
                    "content": response.content,
                    "tokens": {
                        "input": response.input_tokens,
                        "output": response.output_tokens,
                    },
                    "estimated_cost": registry.estimate_cost(
                        response.input_tokens,
                        response.output_tokens,
                        model_id
                    ),
                    "provider": response.provider,
                })
            except Exception as e:
                results.append({
                    "model": model_id,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "comparison": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

