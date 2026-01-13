import logging
from typing import Optional, List, Dict
from datetime import datetime
from langfuse import Langfuse
from app.core.config import settings

logger = logging.getLogger(__name__)

class ObservabilityService:
    """Service for Langfuse observability"""
    
    def __init__(self):
        try:
            if settings.langfuse_public_key and settings.langfuse_secret_key:
                self.client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
                logger.info("Langfuse client initialized")
            else:
                self.client = None
                logger.warning("Langfuse keys not configured - observability disabled")
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            self.client = None
    
    def log_cv_matching(
        self,
        cv_filename: str,
        job_title: str,
        match_score: float,
        reasoning: str
    ) -> None:
        """Log CV matching event"""
        if not self.client:
            return
        
        try:
            self.client.trace(
                name="cv_matching",
                user_id="system",
                metadata={
                    "cv_filename": cv_filename,
                    "job_title": job_title,
                    "match_score": match_score,
                    "reasoning": reasoning
                }
            )
        except Exception as e:
            logger.error(f"Error logging to Langfuse: {e}")
    
    def log_embedding_generation(self, text_length: int, embedding_dim: int) -> None:
        """Log embedding generation event"""
        if not self.client:
            return
        
        try:
            self.client.trace(
                name="embedding_generation",
                metadata={
                    "text_length": text_length,
                    "embedding_dimension": embedding_dim
                }
            )
        except Exception as e:
            logger.error(f"Error logging to Langfuse: {e}")
    
    def log_llm_call(
        self,
        model: str,
        prompt: str,
        response: str,
        provider: str
    ) -> None:
        """Log LLM call"""
        if not self.client:
            return
        
        try:
            self.client.trace(
                name="llm_call",
                metadata={
                    "model": model,
                    "provider": provider,
                    "prompt_length": len(prompt),
                    "response_length": len(response)
                }
            )
        except Exception as e:
            logger.error(f"Error logging to Langfuse: {e}")
    
    def flush(self) -> None:
        """Flush pending events"""
        if self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Error flushing Langfuse: {e}")

# Global instance
observability_service = None

def get_observability_service() -> ObservabilityService:
    global observability_service
    if observability_service is None:
        observability_service = ObservabilityService()
    return observability_service
