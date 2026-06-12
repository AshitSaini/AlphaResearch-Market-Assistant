"""Retrieval service for semantic search"""
from app.core.embeddings import EmbeddingsGenerator
from app.core.vector_store import ChromaVectorStore
from app.config import settings
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RetrievalService:
    """Retrieve relevant documents for a query"""
    
    def __init__(self):
        """Initialize retrieval service"""
        self.embeddings_gen = EmbeddingsGenerator()
        self.vector_store = ChromaVectorStore()
        logger.info("RetrievalService initialized")
    
    def search(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None,
        threshold: float = None
    ) -> Dict:
        """
        Search for documents relevant to query
        
        Args:
            query: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            Search results with documents and metadata
        """
        top_k = top_k or settings.TOP_K_RESULTS
        if threshold is not None:
            similarity_threshold = threshold
        elif similarity_threshold is None:
            similarity_threshold = 0.0
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings_gen.generate(query)
            logger.debug(f"Generated query embedding for: {query[:100]}")
            
            # Search vector store
            results = self.vector_store.search(query_embedding, top_k=top_k + 5)  # Get extra for filtering
            
            # Filter by similarity threshold and return top_k
            filtered_results = self._filter_by_threshold(
                results,
                similarity_threshold,
                top_k
            )
            
            logger.info(f"Retrieved {filtered_results['filtered_count']} documents with similarity > {similarity_threshold}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            raise
    
    def _filter_by_threshold(
        self,
        results: Dict,
        threshold: float,
        top_k: int
    ) -> Dict:
        """Filter results by similarity threshold"""
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        # Convert distances to similarity scores (1 - distance for cosine)
        similarities = [1 - d for d in distances]
        
        # Filter and sort by similarity
        filtered = [
            (doc, meta, sim) for doc, meta, sim in zip(documents, metadatas, similarities)
            if sim >= threshold
        ]
        
        # Sort by similarity descending and take top_k
        filtered.sort(key=lambda x: x[2], reverse=True)
        filtered = filtered[:top_k]
        
        return {
            "documents": [[item[0] for item in filtered]],
            "metadatas": [[item[1] for item in filtered]],
            "similarities": [item[2] for item in filtered],
            "filtered_count": len(filtered)
        }
    
    def get_stats(self) -> Dict:
        """Get retrieval service statistics"""
        return {
            "embeddings_model": settings.OPENAI_EMBEDDING_MODEL,
            "top_k_default": settings.TOP_K_RESULTS,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
            "vector_store_stats": self.vector_store.get_collection_stats()
        }
