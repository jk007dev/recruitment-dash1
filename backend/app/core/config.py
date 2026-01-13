from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    api_title: str = "CV Matching RAG API"
    api_version: str = "1.0.0"
    debug: bool = True
    
    # Server Configuration
    backend_url: str = "http://localhost:8801"
    frontend_url: str = "http://localhost:3301"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # Claude Configuration
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-3-opus-20240229"
    
    # Grok Configuration (via xAI API)
    grok_api_key: Optional[str] = None
    grok_model: str = "grok-1"
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-east-1-aws"
    pinecone_index_name: str = "cv-matching-index"
    
    # Langfuse Configuration
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # RAG Configuration
    max_cv_results: int = 10
    similarity_threshold: float = 0.5
    llm_provider: str = "openai"  # openai, claude, grok
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
