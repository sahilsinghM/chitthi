from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.models.registry import ModelRegistry
from app.db.drafts import get_draft, list_drafts, create_draft_version

router = APIRouter()
registry = ModelRegistry()

# Lazy load DraftAgent to avoid import errors at startup
def get_draft_agent(model_id: str):
    """Get DraftAgent instance for given model"""
    try:
        from app.agents.draft_agent import DraftAgent
        return DraftAgent(model_id=model_id, registry=registry)
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"DraftAgent not available. Please install phidata: {str(e)}"
        )

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

class CreateVersionRequest(BaseModel):
    content: str
    changes_summary: Optional[str] = None

@router.post("/generate")
async def generate_draft(request: GenerateDraftRequest):
    """Generate newsletter draft using Agno agent"""
    try:
        from app.db.embeddings import search_similar_content
        from app.db.drafts import create_draft
        
        # Use Agno DraftAgent for better orchestration
        draft_agent = get_draft_agent(request.model)
        
        # Build context: use provided context or search knowledge base
        context = request.context
        if not context and request.topic_id:
            # TODO: Get topic details and related content from DB
            context = "Generate a Hinglish newsletter draft on current trends for builders."
        elif not context:
            context = "Generate a Hinglish newsletter draft on current trends for builders."
        else:
            # If context provided, search for related content in knowledge base
            try:
                related_content = await search_similar_content(
                    query_text=context,
                    limit=5,
                    threshold=0.6
                )
                if related_content:
                    # Enhance context with related content
                    summaries = [item.get("content_summary", "") for item in related_content if item.get("content_summary")]
                    if summaries:
                        context += "\n\nRelated insights from knowledge base:\n" + "\n".join(f"- {s}" for s in summaries[:3])
            except Exception:
                # If search fails, continue with original context
                pass
        
        result = await draft_agent.generate(
            context=context,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Save draft to database
        try:
            saved_draft = create_draft(
                content=result["content"],
                topic_id=request.topic_id,
                title="",  # Extract from content later
                model_used=result["model"],
                status="draft"
            )
            draft_id = saved_draft.get("id")
        except Exception as db_error:
            draft_id = None
            print(f"Draft save failed: {db_error}")
        
        return {
            "draft": {
                "id": draft_id,
                "content": result["content"],
                "title": "",  # TODO: Extract from content
                "model": result["model"],
                "agent": result.get("agent", "DraftAgent"),
            },
            "metadata": {
                "model_used": result["model"],
                "agent_framework": "Agno",
                "saved_to_db": draft_id is not None,
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

@router.get("/list")
async def list_all_drafts(status: Optional[str] = None, limit: int = 20):
    """List all drafts, optionally filtered by status"""
    try:
        drafts = list_drafts(status=status, limit=limit)
        return {
            "drafts": drafts,
            "count": len(drafts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{draft_id}")
async def get_draft_by_id(draft_id: str):
    """Get a draft by ID"""
    try:
        draft = get_draft(UUID(draft_id))
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        return {"draft": draft}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid draft ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{draft_id}/versions")
async def get_draft_versions(draft_id: str):
    """Get all versions of a draft"""
    try:
        from app.db.client import get_supabase
        supabase = get_supabase()
        
        result = supabase.table("draft_versions").select("*").eq(
            "draft_id", draft_id
        ).order("version_number", desc=True).execute()
        
        return {
            "draft_id": draft_id,
            "versions": result.data if result.data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{draft_id}/versions")
async def create_new_version(draft_id: str, request: CreateVersionRequest):
    """Create a new version of a draft"""
    try:
        version = create_draft_version(
            draft_id=UUID(draft_id),
            content=request.content,
            changes_summary=request.changes_summary
        )
        return {"version": version}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

