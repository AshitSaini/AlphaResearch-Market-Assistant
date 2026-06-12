"""RAG Pipeline - Orchestrates retrieval and generation"""
from app.core.embeddings import EmbeddingsGenerator
from app.core.vector_store import ChromaVectorStore
from app.core.text_chunking import SemanticChunker
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.document_service import DocumentService
from app.config import settings
from typing import Dict, List, Optional
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class RAGPipeline:
    """End-to-end RAG pipeline: Retrieve → Rank → Generate"""
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.embeddings_gen = EmbeddingsGenerator()
        self.retrieval = RetrievalService()
        self.llm = LLMService()
        self.chunker = SemanticChunker(
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        logger.info("RAGPipeline initialized")
    
    def ingest_documents(
        self,
        documents: List[Dict],
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest documents into vector store
        
        Args:
            documents: List of documents with 'id' and 'text'
            metadata: Common metadata for all documents
            
        Returns:
            Ingestion statistics
        """
        start_time = time.time()
        
        try:
            all_chunks = []
            all_embeddings = []
            
            normalized_documents = []
            failed_count = 0
            for doc in documents:
                if isinstance(doc, (str, Path)):
                    try:
                        path = Path(doc)
                        normalized_documents.append({
                            "id": path.name,
                            "text": DocumentService.ingest(str(path)),
                            "metadata": {"source": path.name, "path": str(path)}
                        })
                    except Exception as exc:
                        failed_count += 1
                        logger.error(f"Failed to ingest {doc}: {exc}")
                else:
                    normalized_documents.append(doc)

            # Process each document
            for doc in normalized_documents:
                doc_id = doc.get('id', 'unknown')
                text = doc.get('text', '')
                doc_metadata = {
                    "source": doc_id,
                    **(metadata or {}),
                    **(doc.get('metadata', {}))
                }
                
                # Chunk the document
                chunks = self.chunker.chunk_text(text, metadata=doc_metadata)
                all_chunks.extend(chunks)
                logger.info(f"Document {doc_id}: created {len(chunks)} chunks")
            
            # Generate embeddings for all chunks
            chunk_texts = [chunk['text'] for chunk in all_chunks]
            if not chunk_texts:
                return {
                    "total_documents": len(normalized_documents),
                    "failed_count": failed_count,
                    "total_chunks": 0,
                    "total_embeddings": 0,
                    "documents_added": 0,
                    "elapsed_seconds": time.time() - start_time,
                    "chunks_per_second": 0,
                }
            all_embeddings = self.embeddings_gen.batch_generate(chunk_texts)
            
            # Add to vector store
            added_count = self.retrieval.vector_store.add_documents(
                all_chunks,
                all_embeddings
            )
            
            elapsed = time.time() - start_time
            stats = {
                "total_documents": len(normalized_documents),
                "failed_count": failed_count,
                "total_chunks": len(all_chunks),
                "total_embeddings": len(all_embeddings),
                "documents_added": added_count,
                "elapsed_seconds": elapsed,
                "chunks_per_second": len(all_chunks) / elapsed if elapsed > 0 else 0
            }
            
            logger.info(f"Ingestion complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error during document ingestion: {str(e)}")
            raise
    
    def execute(
        self,
        question: str,
        top_k: int = None,
        include_reasoning: bool = False
    ) -> Dict:
        """
        Execute full RAG pipeline for a question
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            include_reasoning: Include reasoning/explanation
            
        Returns:
            RAG response with answer, sources, and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Retrieving for question: {question[:100]}")
            retrieval_results = self.retrieval.search(question, top_k=top_k)
            
            # Step 2: Format context
            context = self._format_context(retrieval_results)
            logger.info(f"Formatted context: {len(context)} characters")
            
            # Step 3: Generate answer with LLM
            logger.info("Generating response with LLM")
            answer = self.llm.generate_with_context(
                question,
                context,
                temperature=0.35,
                max_tokens=950
            )
            
            # Step 4: Extract sources
            sources = self._extract_sources(retrieval_results)
            
            # Step 5: Calculate confidence
            similarities = retrieval_results.get('similarities', [])
            confidence = similarities[0] if similarities else 0
            
            elapsed = time.time() - start_time
            
            response = {
                "question": question,
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "num_documents_retrieved": len(sources),
                "response_time_ms": int(elapsed * 1000),
                "similarities": similarities[:3],  # Top 3 similarities
                "status": "success"
            }
            
            if include_reasoning:
                response["reasoning"] = {
                    "retrieval_time": retrieval_results.get('retrieval_time', 0),
                    "context_length": len(context),
                    "model": self.llm.model
                }
            
            logger.info(f"RAG pipeline complete: confidence={confidence:.2f}, time={elapsed:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error during RAG pipeline: {str(e)}")
            return {
                "question": question,
                "answer": None,
                "error": str(e),
                "status": "failed",
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _format_context(self, retrieval_results: Dict) -> str:
        """Format search results as context for LLM"""
        documents = retrieval_results.get('documents', [[]])[0] if retrieval_results.get('documents') else []
        metadatas = retrieval_results.get('metadatas', [[]])[0] if retrieval_results.get('metadatas') else []
        similarities = retrieval_results.get('similarities', [])
        
        context_parts = []
        
        for i, (doc, meta, sim) in enumerate(zip(documents, metadatas, similarities)):
            source = self._format_source(meta)
            context_parts.append(f"[Document {i+1} - {source} (confidence: {sim:.2f})]")
            context_parts.append(doc)
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _extract_sources(self, retrieval_results: Dict) -> List[str]:
        """Extract unique source references"""
        metadatas = retrieval_results.get('metadatas', [[]])[0] if retrieval_results.get('metadatas') else []
        
        sources = []
        for meta in metadatas:
            source = self._format_source(meta)
            if source and source not in sources:
                sources.append(source)
        
        return sources

    def _format_source(self, metadata: Dict) -> str:
        """Format local or official provenance for user-facing citations."""
        if metadata.get("source_url") or metadata.get("circular_no") or metadata.get("exchange"):
            parts = [
                metadata.get("exchange", "").strip(),
                metadata.get("circular_no", "").strip(),
                metadata.get("date", "").strip(),
                metadata.get("section", "").strip(),
            ]
            label = " | ".join(part for part in parts if part)
            title = metadata.get("source", "").strip()
            url = metadata.get("source_url", "").strip()
            if title and label:
                label = f"{title} ({label})"
            else:
                label = title or label
            return f"{label} - {url}" if url else label

        return metadata.get("source", "")
    
    def get_pipeline_stats(self) -> Dict:
        """Get pipeline statistics"""
        return {
            "embeddings_model": settings.OPENAI_EMBEDDING_MODEL,
            "llm_model": settings.OPENAI_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "top_k": settings.TOP_K_RESULTS,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
            "vector_store": self.retrieval.vector_store.get_collection_stats()
        }
