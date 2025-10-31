from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.agents.topic_agent import TopicAgent
from app.db.client import get_supabase
from app.db.embeddings import search_similar_content

router = APIRouter()
topic_agent = TopicAgent()

class PrioritizeTopicsRequest(BaseModel):
    content_items: Optional[List[Dict]] = None  # Optional: can query from DB
    interest_weights: Optional[Dict[str, float]] = None
    use_database: bool = True  # Whether to query stored content

@router.post("/prioritize")
async def prioritize_topics(request: PrioritizeTopicsRequest):
    """Prioritize topics from content items using Agno agent"""
    try:
        content_items = request.content_items or []
        
        # If use_database is True and no items provided, query from database
        if request.use_database and not content_items:
            supabase = get_supabase()
            result = supabase.table("content_items").select(
                "id, url, summary, extracted_text, tags, created_at"
            ).order("created_at", desc=True).limit(50).execute()
            
            if result.data:
                content_items = [
                    {
                        "id": item.get("id"),
                        "summary": item.get("summary") or item.get("extracted_text", "")[:200],
                        "tags": item.get("tags", []),
                        "url": item.get("url"),
                    }
                    for item in result.data
                ]
        
        # Use vector search to enhance topics with related content
        if content_items:
            # Cluster similar content items using embeddings
            enhanced_items = []
            for item in content_items[:10]:  # Limit for performance
                try:
                    search_query = item.get("summary", item.get("extracted_text", ""))[:100]
                    if search_query:
                        related = await search_similar_content(
                            query_text=search_query,
                            limit=3,
                            threshold=0.7
                        )
                        item["related_content_count"] = len(related)
                except Exception:
                    item["related_content_count"] = 0
                enhanced_items.append(item)
            
            topics = await topic_agent.prioritize_topics(
                content_items=enhanced_items,
                interest_weights=request.interest_weights
            )
        else:
            topics = []
        
        return {
            "topics": topics,
            "count": len(topics),
            "source": "database" if request.use_database and not request.content_items else "provided"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_topics(limit: int = 20):
    """List prioritized topics from database"""
    try:
        supabase = get_supabase()
        result = supabase.table("topics").select(
            "id, title, description, priority_score, tags, created_at, updated_at"
        ).order("priority_score", desc=True).limit(limit).execute()
        
        return {
            "topics": result.data if result.data else [],
            "count": len(result.data) if result.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



