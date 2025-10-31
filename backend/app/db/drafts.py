"""Database operations for drafts"""
from typing import Optional, Dict, Any, List
from app.db.client import get_supabase
from uuid import UUID

def create_draft(
    content: str,
    topic_id: Optional[UUID] = None,
    title: Optional[str] = None,
    model_used: Optional[str] = None,
    prompt_used: Optional[str] = None,
    status: str = "draft",
) -> Dict[str, Any]:
    """Create a new draft"""
    supabase = get_supabase()
    
    data = {
        "content": content,
        "status": status,
        "version": 1,
    }
    
    if topic_id:
        data["topic_id"] = str(topic_id)
    if title:
        data["title"] = title
    if model_used:
        data["model_used"] = model_used
    if prompt_used:
        data["prompt_used"] = prompt_used
    
    result = supabase.table("drafts").insert(data).execute()
    return result.data[0] if result.data else {}

def get_draft(draft_id: UUID) -> Optional[Dict[str, Any]]:
    """Get a draft by ID"""
    supabase = get_supabase()
    result = supabase.table("drafts").select("*").eq("id", str(draft_id)).execute()
    return result.data[0] if result.data else None

def create_draft_version(
    draft_id: UUID,
    content: str,
    changes_summary: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new version of a draft"""
    supabase = get_supabase()
    
    # Get current draft to determine next version number
    draft = get_draft(draft_id)
    if not draft:
        raise ValueError(f"Draft {draft_id} not found")
    
    next_version = draft.get("version", 0) + 1
    
    # Update draft version
    supabase.table("drafts").update({
        "version": next_version,
        "content": content,
    }).eq("id", str(draft_id)).execute()
    
    # Create version record
    version_data = {
        "draft_id": str(draft_id),
        "version_number": next_version,
        "content": content,
    }
    if changes_summary:
        version_data["changes_summary"] = changes_summary
    
    result = supabase.table("draft_versions").insert(version_data).execute()
    return result.data[0] if result.data else {}

def list_drafts(status: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """List drafts, optionally filtered by status"""
    supabase = get_supabase()
    
    query = supabase.table("drafts").select("*").order("created_at", desc=True)
    
    if status:
        query = query.eq("status", status)
    
    result = query.limit(limit).execute()
    return result.data if result.data else []



