"""Chroma vector database service"""
import chromadb
from typing import List, Dict, Optional
import logging
import uuid
from app.config import settings

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    """Manage vector embeddings in Chroma vector database"""
    
    def __init__(self, collection_name: str = None):
        """
        Initialize Chroma vector store
        
        Args:
            collection_name: Name of the collection to use
        """
        self.db_path = settings.CHROMA_DB_PATH
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Get or create collection with cosine distance metric
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaVectorStore initialized: path={self.db_path}, collection={self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaVectorStore: {str(e)}")
            raise
    
    def add_documents(
        self,
        chunks: List[Dict],
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> int:
        """
        Add documents with embeddings to vector store
        
        Args:
            chunks: List of chunk dictionaries with text and metadata
            embeddings: List of embedding vectors
            batch_size: Batch size for adding to Chroma
            
        Returns:
            Number of documents added
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch")
        
        if not chunks:
            logger.warning("No chunks to add")
            return 0
        
        added_count = 0
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            try:
                # Prepare data for Chroma
                ids = [chunk.get("id", f"chunk_{uuid.uuid4()}") for chunk in batch_chunks]
                documents = [chunk["text"] for chunk in batch_chunks]
                metadatas = [chunk.get("metadata", {}) for chunk in batch_chunks]
                
                # Upsert keeps repeated ingestion idempotent for demos and tests.
                self.collection.upsert(
                    ids=ids,
                    embeddings=batch_embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
                
                added_count += len(ids)
                logger.info(f"Added {len(ids)} documents to collection (batch {i//batch_size + 1})")
                
            except Exception as e:
                logger.error(f"Error adding batch to collection: {str(e)}")
                raise
        
        logger.info(f"Successfully added {added_count} total documents to vector store")
        return added_count
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Search results with documents, metadatas, distances
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            logger.debug(f"Search returned {len(results['documents'][0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
    
    def delete_collection(self) -> None:
        """Delete the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Error deleting collection: {str(e)}")
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_collection(self) -> None:
        """Clear all documents from collection"""
        try:
            # Get all IDs and delete them
            all_data = self.collection.get()
            if all_data and all_data['ids']:
                self.collection.delete(ids=all_data['ids'])
                logger.info(f"Cleared {len(all_data['ids'])} documents from collection")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")


VectorStore = ChromaVectorStore
