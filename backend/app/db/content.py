"""Database operations for content items and embeddings"""
from typing import List, Optional, Dict, Any
from app.db.client import get_supabase
from uuid import UUID
import json

def create_content_item(
    url: Optional[str] = None,
    file_path: Optional[str] = None,
    extracted_text: Optional[str] = None,
    summary: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Create a new content item"""
    supabase = get_supabase()
    
    data = {}
    if url:
        data["url"] = url
    if file_path:
        data["file_path"] = file_path
    if extracted_text:
        data["extracted_text"] = extracted_text
    if summary:
        data["summary"] = summary
    if tags:
        data["tags"] = tags
    
    result = supabase.table("content_items").insert(data).execute()
    return result.data[0] if result.data else {}

def get_content_item(content_id: UUID) -> Optional[Dict[str, Any]]:
    """Get a content item by ID"""
    supabase = get_supabase()
    result = supabase.table("content_items").select("*").eq("id", str(content_id)).execute()
    return result.data[0] if result.data else None

def store_embedding(
    content_id: UUID,
    embedding: List[float],
    model_used: str = "text-embedding-3-small",
) -> Dict[str, Any]:
    """Store embedding for a content item"""
    supabase = get_supabase()
    
    data = {
        "content_id": str(content_id),
        "embedding": embedding,
        "model_used": model_used,
    }
    
    # Use upsert to handle duplicates
    result = supabase.table("content_embeddings").upsert(
        data,
        on_conflict="content_id,model_used"
    ).execute()
    
    return result.data[0] if result.data else {}

def search_similar_content(
    query_embedding: List[float],
    limit: int = 10,
    threshold: float = 0.7,
) -> List[Dict[str, Any]]:
    """Search for similar content using vector similarity"""
    supabase = get_supabase()
    
    # Use Supabase RPC for vector similarity search
    # Note: This requires a custom function in Supabase
    # For now, we'll use a simple approach with the client
    
    # Get all embeddings (this should be optimized with RPC)
    result = supabase.rpc(
        "match_content_embeddings",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        }
    ).execute()
    
    if result.data:
        return result.data
    
    # Fallback: return empty list if RPC doesn't exist
    return []



