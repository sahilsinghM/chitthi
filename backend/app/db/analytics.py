"""Database operations for API usage tracking and analytics"""
from typing import Dict, Any, Optional
from app.db.client import get_supabase
from uuid import UUID

def track_api_usage(
    provider: str,
    model: str,
    operation_type: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_estimated: float = 0.0,
) -> Dict[str, Any]:
    """Track API usage for cost monitoring (synchronous version)"""
    try:
        supabase = get_supabase()
        
        data = {
            "provider": provider,
            "model": model,
            "operation_type": operation_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_estimated": cost_estimated,
        }
        
        result = supabase.table("api_usage").insert(data).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        # Don't fail if tracking fails
        print(f"API usage tracking failed: {e}")
        return {}

def get_usage_stats(
    provider: Optional[str] = None,
    days: int = 30,
) -> Dict[str, Any]:
    """Get API usage statistics"""
    from datetime import datetime, timedelta
    supabase = get_supabase()
    
    # Calculate date threshold
    threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    query = supabase.table("api_usage").select("*").gte("created_at", threshold_date)
    
    if provider:
        query = query.eq("provider", provider)
    
    result = query.execute()
    
    if not result.data:
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "period_days": days,
        }
    
    total_input = sum(r.get("input_tokens", 0) for r in result.data)
    total_output = sum(r.get("output_tokens", 0) for r in result.data)
    total_cost = sum(r.get("cost_estimated", 0) for r in result.data)
    
    # Group by provider
    by_provider = {}
    by_operation = {}
    
    for r in result.data:
        prov = r.get("provider", "unknown")
        op_type = r.get("operation_type", "unknown")
        
        if prov not in by_provider:
            by_provider[prov] = {"cost": 0.0, "requests": 0, "tokens": 0}
        by_provider[prov]["cost"] += r.get("cost_estimated", 0)
        by_provider[prov]["requests"] += 1
        by_provider[prov]["tokens"] += r.get("input_tokens", 0) + r.get("output_tokens", 0)
        
        if op_type not in by_operation:
            by_operation[op_type] = {"cost": 0.0, "requests": 0}
        by_operation[op_type]["cost"] += r.get("cost_estimated", 0)
        by_operation[op_type]["requests"] += 1
    
    return {
        "total_requests": len(result.data),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_input + total_output,
        "total_cost": round(total_cost, 6),
        "by_provider": {k: {
            "cost": round(v["cost"], 6),
            "requests": v["requests"],
            "tokens": v["tokens"]
        } for k, v in by_provider.items()},
        "by_operation": {k: {
            "cost": round(v["cost"], 6),
            "requests": v["requests"]
        } for k, v in by_operation.items()},
        "period_days": days,
    }

def track_newsletter_analytics(
    draft_id: UUID,
    opens: int = 0,
    read_time: int = 0,
    comments_count: int = 0,
    twitter_likes: int = 0,
    twitter_replies: int = 0,
    twitter_retweets: int = 0,
) -> Dict[str, Any]:
    """Track newsletter engagement metrics"""
    supabase = get_supabase()
    
    data = {
        "draft_id": str(draft_id),
        "opens": opens,
        "read_time": read_time,
        "comments_count": comments_count,
        "twitter_likes": twitter_likes,
        "twitter_replies": twitter_replies,
        "twitter_retweets": twitter_retweets,
    }
    
    result = supabase.table("analytics").insert(data).execute()
    return result.data[0] if result.data else {}

