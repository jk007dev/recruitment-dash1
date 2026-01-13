from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CVUploadRequest(BaseModel):
    filename: str
    content: str
    cv_id: Optional[str] = None

class JDRequest(BaseModel):
    job_description: str
    job_title: str
    required_skills: Optional[List[str]] = None

class MatchResult(BaseModel):
    cv_id: str
    filename: str
    match_score: float
    reasoning: str
    matched_skills: List[str]
    experience_alignment: str
    overall_assessment: str

class MatchingRequest(BaseModel):
    jd: JDRequest
    cv_ids: List[str]
    llm_provider: str = "openai"
    top_k: int = 5

class MatchingResponse(BaseModel):
    job_title: str
    total_cvs_matched: int
    matches: List[MatchResult]
    timestamp: datetime = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Senior Python Developer",
                "total_cvs_matched": 3,
                "matches": [
                    {
                        "cv_id": "cv_001",
                        "filename": "john_doe.pdf",
                        "match_score": 0.95,
                        "reasoning": "Strong Python background with 8 years of experience",
                        "matched_skills": ["Python", "FastAPI", "Docker"],
                        "experience_alignment": "Excellent",
                        "overall_assessment": "Highly recommended"
                    }
                ]
            }
        }

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    dimension: int
