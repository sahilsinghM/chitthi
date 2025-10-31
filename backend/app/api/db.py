from fastapi import APIRouter, HTTPException
from app.db.client import get_supabase
from app.db.schema import init_database

router = APIRouter()

@router.get("/test")
async def test_connection():
    """Test Supabase connection"""
    try:
        supabase = get_supabase()
        # Try a simple query
        result = supabase.table("content_items").select("id").limit(1).execute()
        return {
            "status": "connected",
            "message": "Supabase connection successful",
            "tables_accessible": True
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "tables_accessible": False
        }

@router.post("/init")
async def initialize_database():
    """Initialize database schema (verify only, actual migration should be run in Supabase SQL editor)"""
    try:
        result = init_database()
        if result:
            return {
                "status": "success",
                "message": "Database schema verified",
                "note": "If tables don't exist, run supabase/migrations/001_init_schema.sql in Supabase SQL Editor"
            }
        else:
            return {
                "status": "warning",
                "message": "Schema verification failed. Please run migration SQL manually.",
                "migration_file": "supabase/migrations/001_init_schema.sql"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify-rpc")
async def verify_rpc_function():
    """Verify that match_content_embeddings RPC function is available"""
    try:
        from app.db.embeddings import generate_embedding
        from app.db.client import get_supabase
        
        # Generate a test embedding
        test_text = "test query for vector search"
        test_embedding = await generate_embedding(test_text)
        
        supabase = get_supabase()
        
        try:
            # Try to call the RPC function
            result = supabase.rpc(
                "match_content_embeddings",
                {
                    "query_embedding": test_embedding,
                    "match_threshold": 0.0,
                    "match_count": 1,
                }
            ).execute()
            
            return {
                "status": "success",
                "rpc_function": "match_content_embeddings",
                "available": True,
                "message": "RPC function is deployed and working",
                "note": "This confirms the vector search function is properly set up"
            }
        except Exception as rpc_error:
            return {
                "status": "warning",
                "rpc_function": "match_content_embeddings",
                "available": False,
                "message": f"RPC function not available: {str(rpc_error)}",
                "action_required": "Run supabase/functions/match_content_embeddings.sql in Supabase SQL Editor"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "available": False
        }



