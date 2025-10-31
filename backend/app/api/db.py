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



