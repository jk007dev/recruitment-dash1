import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from app.models.schemas import CVUploadRequest, EmbeddingResponse
from app.services import get_embedding_service, get_vector_store_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cv", tags=["cv"])

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    cv_id: str = Form(...)
):
    """Upload and process CV"""
    try:
        content = await file.read()
        text_content = content.decode('utf-8', errors='ignore')
        
        embedding_service = get_embedding_service()
        vector_store = get_vector_store_service()
        
        # Generate embedding
        embedding = embedding_service.embed_text(text_content)
        
        # Store in vector database
        vector_store.upsert_vectors([
            (cv_id, embedding, {
                "filename": file.filename,
                "content": text_content[:500]  # Store first 500 chars as metadata
            })
        ])
        
        return {
            "message": "CV uploaded successfully",
            "cv_id": cv_id,
            "filename": file.filename,
            "embedding_dimension": len(embedding)
        }
    except Exception as e:
        logger.error(f"Error uploading CV: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/embedding", response_model=EmbeddingResponse)
async def get_embedding(text: str):
    """Get embedding for text"""
    try:
        embedding_service = get_embedding_service()
        embedding = embedding_service.embed_text(text)
        
        return EmbeddingResponse(
            embedding=embedding,
            dimension=len(embedding)
        )
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list")
async def list_cvs():
    """List all stored CVs"""
    try:
        vector_store = get_vector_store_service()
        # This is a simplified version - Pinecone doesn't have direct list operation
        return {"message": "CV listing requires Pinecone metadata filtering"}
    except Exception as e:
        logger.error(f"Error listing CVs: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{cv_id}")
async def delete_cv(cv_id: str):
    """Delete a CV"""
    try:
        vector_store = get_vector_store_service()
        vector_store.delete_vector(cv_id)
        
        return {"message": f"CV {cv_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting CV: {e}")
        raise HTTPException(status_code=400, detail=str(e))
