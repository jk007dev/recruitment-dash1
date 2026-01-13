import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for managing different LLM providers"""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.llm = self._get_llm(provider)
    
    def _get_llm(self, provider: str):
        """Get LLM instance based on provider"""
        provider = provider.lower()
        
        if provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=0.7
            )
        
        elif provider == "claude":
            if not settings.claude_api_key:
                raise ValueError("Claude API key not configured")
            return ChatAnthropic(
                api_key=settings.claude_api_key,
                model=settings.claude_model,
                temperature=0.7
            )
        
        elif provider == "grok":
            # Grok is not directly supported by LangChain
            # Using OpenAI-compatible API for now
            logger.warning("Grok provider using OpenAI compatibility layer")
            return ChatOpenAI(
                api_key=settings.grok_api_key,
                model=settings.grok_model,
                base_url="https://api.x.ai/v1",
                temperature=0.7
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def invoke(self, prompt: str) -> str:
        """Invoke LLM with prompt"""
        try:
            message = self.llm.invoke(prompt)
            return message.content
        except Exception as e:
            logger.error(f"Error invoking {self.provider}: {e}")
            raise
    
    def stream(self, prompt: str):
        """Stream LLM response"""
        try:
            return self.llm.stream(prompt)
        except Exception as e:
            logger.error(f"Error streaming from {self.provider}: {e}")
            raise

def get_llm_service(provider: str = None) -> LLMService:
    """Get LLM service instance"""
    provider = provider or settings.llm_provider
    return LLMService(provider)
