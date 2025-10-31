from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

# Optional: Setup Phoenix tracing if enabled
try:
    from app.evaluation.phoenix_setup import setup_phoenix_tracing
    setup_phoenix_tracing()
except ImportError:
    pass  # Phoenix is optional

app = FastAPI(
    title="Newsletter Engine API",
    description="AI-powered Hinglish Newsletter Engine",
    version="0.1.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers (lazy load those with agents)
from app.api import models, db, analytics

# Import routers that may have agent dependencies
try:
    from app.api import content, drafts, topics
except ImportError as e:
    # If agents fail to import, create placeholder routers
    print(f"Warning: Some routers failed to load: {e}")
    from fastapi import APIRouter
    content = APIRouter()
    drafts = APIRouter()
    topics = APIRouter()

app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(drafts.router, prefix="/api/drafts", tags=["drafts"])
app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(db.router, prefix="/api/db", tags=["database"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Newsletter Engine API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

