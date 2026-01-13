import logging
from typing import List, Optional
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing Pinecone vector store"""
    
    def __init__(self):
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            self.index_name = settings.pinecone_index_name
            self.index = self._get_or_create_index()
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def _get_or_create_index(self):
        """Get existing index or create a new one"""
        try:
            # List existing indexes
            indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment.split("-")[0] + "-east-1"
                    )
                )
            
            return self.pc.Index(self.index_name)
        except Exception as e:
            logger.error(f"Error creating/getting index: {e}")
            raise
    
    def upsert_vectors(self, vectors: List[tuple]) -> None:
        """
        Upsert vectors to Pinecone
        vectors: List of tuples (id, embedding, metadata)
        """
        try:
            self.index.upsert(vectors=vectors)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise
    
    def query_similar(self, embedding: List[float], top_k: int = 5) -> List[dict]:
        """Query similar vectors"""
        try:
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True
            )
            return results.matches if hasattr(results, 'matches') else []
        except Exception as e:
            logger.error(f"Error querying vectors: {e}")
            raise
    
    def delete_vector(self, vector_id: str) -> None:
        """Delete a vector by ID"""
        try:
            self.index.delete(ids=[vector_id])
            logger.info(f"Deleted vector: {vector_id}")
        except Exception as e:
            logger.error(f"Error deleting vector: {e}")
            raise
    
    def delete_all(self) -> None:
        """Delete all vectors from index"""
        try:
            self.index.delete(delete_all=True)
            logger.info("Deleted all vectors from index")
        except Exception as e:
            logger.error(f"Error deleting all vectors: {e}")
            raise

# Global instance
vector_store_service = None

def get_vector_store_service() -> VectorStoreService:
    global vector_store_service
    if vector_store_service is None:
        vector_store_service = VectorStoreService()
    return vector_store_service
