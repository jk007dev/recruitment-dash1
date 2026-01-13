import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import JDRequest, MatchingRequest, MatchingResponse, MatchResult
from app.core.rag_orchestrator import get_rag_orchestrator
from app.services import get_vector_store_service
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/matching", tags=["matching"])

@router.post("/match", response_model=MatchingResponse)
async def match_cvs(request: MatchingRequest):
    """Match CVs against job description"""
    try:
        logger.info(f"Starting matching for job: {request.jd.job_title}")
        
        orchestrator = get_rag_orchestrator()
        vector_store = get_vector_store_service()
        
        # Process each CV
        matches = []
        
        for cv_id in request.cv_ids:
            try:
                # Get CV from vector store (this would need actual retrieval implementation)
                # For now, using mock data structure
                cv_text = f"CV content for {cv_id}"  # Placeholder
                
                # Run RAG pipeline
                result = orchestrator.process(
                    job_description=request.jd.job_description,
                    job_title=request.jd.job_title,
                    cv_id=cv_id,
                    cv_text=cv_text
                )
                
                if result.match_result:
                    matches.append(result.match_result)
            except Exception as e:
                logger.error(f"Error processing CV {cv_id}: {e}")
                continue
        
        # Sort by match score and return top K
        matches.sort(key=lambda x: x.match_score, reverse=True)
        top_matches = matches[:request.top_k]
        
        response = MatchingResponse(
            job_title=request.jd.job_title,
            total_cvs_matched=len(top_matches),
            matches=top_matches,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Matching completed. Found {len(top_matches)} matches")
        return response
        
    except Exception as e:
        logger.error(f"Error in matching: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Matching service is running"}
