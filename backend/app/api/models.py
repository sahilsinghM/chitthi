from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.registry import ModelRegistry

router = APIRouter()
registry = ModelRegistry()

class TestModelRequest(BaseModel):
    model: Optional[str] = None
    provider: Optional[str] = None

class GenerateRequest(BaseModel):
    prompt: str
    model: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

@router.get("/")
async def list_models():
    """List all available models from all providers"""
    try:
        models = await registry.get_all_models()
        return {
            "models": [model.model_dump() for model in models],
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/costs")
async def get_costs():
    """Get cost estimates for all models"""
    try:
        models = await registry.get_all_models()
        costs = []
        for model in models:
            # Example: estimate cost for 1000 input + 1000 output tokens
            estimated_cost = registry.estimate_cost(1000, 1000, model.id)
            costs.append({
                "model_id": model.id,
                "display_name": model.display_name,
                "provider": model.provider,
                "cost_per_2k_tokens": estimated_cost,
                "cost_per_1k_input": model.cost_per_1k_input,
                "cost_per_1k_output": model.cost_per_1k_output,
            })
        return {"costs": costs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_model(request: TestModelRequest):
    """Test model connection"""
    try:
        if request.provider:
            success = await registry.test_provider(request.provider)
            return {
                "provider": request.provider,
                "status": "success" if success else "failed",
                "accessible": success
            }
        elif request.model:
            # Test specific model
            provider_name = registry._get_provider_from_model(request.model)
            if not provider_name:
                raise HTTPException(status_code=404, detail="Provider not found for model")
            success = await registry.test_provider(provider_name)
            return {
                "model": request.model,
                "provider": provider_name,
                "status": "success" if success else "failed",
                "accessible": success
            }
        else:
            raise HTTPException(status_code=400, detail="Either model or provider must be specified")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_text(request: GenerateRequest):
    """Generate text using specified model (for testing)"""
    try:
        response = await registry.generate(
            prompt=request.prompt,
            model_id=request.model,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
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
            "metadata": response.metadata
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

