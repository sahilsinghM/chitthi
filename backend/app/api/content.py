from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from app.agents.content_agent import ContentAgent
from app.db.embeddings import create_content_with_embedding

router = APIRouter()
content_agent = ContentAgent()

class IngestContentRequest(BaseModel):
    url: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None

@router.post("/ingest")
async def ingest_content(
    url: Optional[str] = None,
    tags: List[str] = [],
    notes: Optional[str] = None,
    file: Optional[UploadFile] = File(None)
):
    """Ingest content from URL or file upload using Agno agent"""
    try:
        if url:
            # Use Agno ContentAgent to extract content
            result = await content_agent.ingest_url(url, notes)
            
            # Ask clarifying questions
            questions = await content_agent.ask_clarifying_questions(url)
            
            # Store in Supabase with embedding
            try:
                db_item = await create_content_with_embedding(
                    url=url,
                    extracted_text=result.get("summary", ""),
                    summary=result.get("summary"),
                    tags=tags if tags else [],
                )
                content_id = db_item.get("id")
                embedding_status = db_item.get("embedding_status", "unknown")
            except Exception as db_error:
                # Continue even if DB fails (for testing)
                content_id = None
                embedding_status = "failed"
                print(f"Database storage failed: {db_error}")
            
            return {
                "status": "success",
                "type": "url",
                "url": url,
                "summary": result.get("summary"),
                "clarifying_questions": questions,
                "tags": tags,
                "content_id": content_id,
                "stored_in_db": content_id is not None,
                "embedding_status": embedding_status if 'embedding_status' in locals() else "unknown",
            }
        elif file:
            # Process file upload
            try:
                # Read file content
                file_content = await file.read()
                file_text = file_content.decode('utf-8')
                
                # Use ContentAgent to process file
                result = await content_agent.ingest_url(None, notes)  # Pass file content as notes
                
                # For now, treat file content as extracted text
                extracted_text = file_text[:5000]  # Limit size
                summary = result.get("summary") if result.get("summary") else extracted_text[:500]
                
                # Store in Supabase with embedding
                try:
                    db_item = await create_content_with_embedding(
                        file_path=file.filename,
                        extracted_text=extracted_text,
                        summary=summary,
                        tags=tags if tags else [],
                    )
                    content_id = db_item.get("id")
                    embedding_status = db_item.get("embedding_status", "unknown")
                except Exception as db_error:
                    content_id = None
                    embedding_status = "failed"
                    print(f"Database storage failed: {db_error}")
                
                return {
                    "status": "success",
                    "type": "file",
                    "filename": file.filename,
                    "summary": summary,
                    "content_id": content_id,
                    "stored_in_db": content_id is not None,
                    "embedding_status": embedding_status,
                }
            except Exception as file_error:
                raise HTTPException(status_code=400, detail=f"File processing failed: {str(file_error)}")
        else:
            raise HTTPException(status_code=400, detail="Either URL or file must be provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_content(query: str, limit: int = 10, threshold: float = 0.7):
    """Search content using vector similarity"""
    try:
        from app.db.embeddings import search_similar_content
        
        results = await search_similar_content(
            query_text=query,
            limit=limit,
            threshold=threshold
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "threshold": threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

