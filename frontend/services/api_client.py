import requests
from typing import List, Dict, Optional
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8801")

class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url
    
    def upload_cv(self, cv_id: str, file_path: str) -> Dict:
        """Upload CV file"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'cv_id': cv_id}
                response = requests.post(
                    f"{self.base_url}/api/cv/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def match_cvs(self, jd: Dict, cv_ids: List[str], llm_provider: str = "openai", top_k: int = 5) -> Dict:
        """Match CVs against JD"""
        try:
            payload = {
                "jd": jd,
                "cv_ids": cv_ids,
                "llm_provider": llm_provider,
                "top_k": top_k
            }
            response = requests.post(
                f"{self.base_url}/api/matching/match",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_embedding(self, text: str) -> Dict:
        """Get embedding for text"""
        try:
            response = requests.post(
                f"{self.base_url}/api/cv/embedding",
                params={"text": text},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
