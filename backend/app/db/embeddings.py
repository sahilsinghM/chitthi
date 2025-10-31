"""Embedding generation and storage operations"""
import os
from typing import List, Optional
from openai import AsyncOpenAI
import httpx
from app.db.client import get_supabase
from app.db.content import create_content_item, get_content_item
from app.db.analytics import track_api_usage
from uuid import UUID

# OpenAI client for embeddings
_embedding_client: Optional[AsyncOpenAI] = None

def get_embedding_client() -> AsyncOpenAI:
    """Get or create OpenAI client for embeddings"""
    global _embedding_client
    if _embedding_client is None:
        # Try OpenAI API key first, then OpenRouter
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Can't use OpenRouter directly for embeddings, need OpenAI
            raise ValueError("OPENAI_API_KEY required for embeddings")
        _embedding_client = AsyncOpenAI(api_key=api_key)
    return _embedding_client

async def generate_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Generate embedding for text using OpenAI"""
    client = get_embedding_client()
    
    # Clean and prepare text
    text = text.replace("\n", " ").strip()
    if len(text) == 0:
        raise ValueError("Text cannot be empty")
    
    # Limit text length (OpenAI embedding limit)
    max_chars = 8000  # Safe limit for text-embedding-3-small
    if len(text) > max_chars:
        text = text[:max_chars]
    
    response = await client.embeddings.create(
        model=model,
        input=text
    )
    
    # Track API usage (synchronous function)
    try:
        track_api_usage(
            provider="openai",
            model=model,
            operation_type="embedding",
            input_tokens=response.usage.total_tokens,
            output_tokens=0,
            cost_estimated=(response.usage.total_tokens / 1000) * 0.00002  # $0.02 per 1M tokens
        )
    except Exception:
        pass  # Don't fail if tracking fails
    
    return response.data[0].embedding

async def create_content_with_embedding(
    url: Optional[str] = None,
    extracted_text: Optional[str] = None,
    summary: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> dict:
    """Create content item and generate/store embedding"""
    # Create content item first
    content_item = create_content_item(
        url=url,
        extracted_text=extracted_text,
        summary=summary,
        tags=tags or [],
    )
    
    content_id = UUID(content_item["id"])
    
    # Generate embedding from summary or extracted text
    text_for_embedding = summary or extracted_text
    if not text_for_embedding:
        return {
            **content_item,
            "embedding_status": "skipped",
            "reason": "No text available for embedding"
        }
    
    try:
        # Generate embedding
        embedding = await generate_embedding(text_for_embedding)
        
        # Store embedding in Supabase
        supabase = get_supabase()
        embedding_data = {
            "content_id": str(content_id),
            "embedding": embedding,
            "model_used": "text-embedding-3-small",
        }
        
        result = supabase.table("content_embeddings").upsert(
            embedding_data,
            on_conflict="content_id,model_used"
        ).execute()
        
        return {
            **content_item,
            "embedding_status": "created",
            "embedding_id": result.data[0]["id"] if result.data else None,
        }
    except Exception as e:
        return {
            **content_item,
            "embedding_status": "failed",
            "error": str(e)
        }

async def search_similar_content(
    query_text: str,
    limit: int = 10,
    threshold: float = 0.7,
) -> List[dict]:
    """Search for similar content using vector similarity"""
    try:
        # Generate embedding for query
        query_embedding = await generate_embedding(query_text)
        
        # Use Supabase RPC function if available
        supabase = get_supabase()
        
        try:
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
        except Exception:
            # RPC function not available, use fallback method
            pass
        
        # Fallback: Get all embeddings and compute similarity (not efficient, but works)
        # For production, use the RPC function
        all_embeddings = supabase.table("content_embeddings").select(
            "*, content_items(*)"
        ).execute()
        
        if not all_embeddings.data:
            return []
        
        # Compute similarities (simple cosine similarity)
        import numpy as np
        
        results = []
        query_vec = np.array(query_embedding)
        
        for item in all_embeddings.data:
            if not item.get("embedding"):
                continue
            
            item_vec = np.array(item["embedding"])
            similarity = float(np.dot(query_vec, item_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(item_vec)))
            
            if similarity > threshold:
                results.append({
                    **item,
                    "similarity": similarity,
                })
        
        # Sort by similarity and limit
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
        
    except Exception as e:
        print(f"Vector search error: {e}")
        return []

