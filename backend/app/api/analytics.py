"""API usage tracking and cost analytics"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.analytics import get_usage_stats, track_newsletter_analytics

router = APIRouter()

class UsageStatsRequest(BaseModel):
    provider: Optional[str] = None
    days: int = 30

@router.get("/usage")
async def get_usage(provider: Optional[str] = None, days: int = 30):
    """Get API usage statistics"""
    try:
        stats = get_usage_stats(provider=provider, days=days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/costs")
async def get_costs():
    """Get cost breakdown by provider and model"""
    try:
        from app.db.client import get_supabase
        
        supabase = get_supabase()
        
        # Get costs grouped by provider
        result = supabase.table("api_usage").select("provider, model, cost_estimated, created_at").execute()
        
        if not result.data:
            return {
                "total_cost": 0.0,
                "by_provider": {},
                "by_model": {},
                "period": "all_time"
            }
        
        # Aggregate costs
        by_provider = {}
        by_model = {}
        total_cost = 0.0
        
        for record in result.data:
            provider = record.get("provider", "unknown")
            model = record.get("model", "unknown")
            cost = record.get("cost_estimated", 0.0)
            
            total_cost += cost
            
            if provider not in by_provider:
                by_provider[provider] = {"total": 0.0, "count": 0}
            by_provider[provider]["total"] += cost
            by_provider[provider]["count"] += 1
            
            model_key = f"{provider}:{model}"
            if model_key not in by_model:
                by_model[model_key] = {"total": 0.0, "count": 0}
            by_model[model_key]["total"] += cost
            by_model[model_key]["count"] += 1
        
        return {
            "total_cost": round(total_cost, 6),
            "by_provider": {k: {
                "total": round(v["total"], 6),
                "count": v["count"],
                "avg_per_request": round(v["total"] / v["count"], 6) if v["count"] > 0 else 0
            } for k, v in by_provider.items()},
            "by_model": {k: {
                "total": round(v["total"], 6),
                "count": v["count"]
            } for k, v in by_model.items()},
            "period": "all_time",
            "total_requests": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

