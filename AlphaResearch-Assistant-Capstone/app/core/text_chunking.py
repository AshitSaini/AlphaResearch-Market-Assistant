"""Text chunking service with semantic awareness"""
import re
from typing import List, Dict, Optional
import logging

try:
    import tiktoken
except Exception:  # pragma: no cover - optional dependency fallback
    tiktoken = None

try:
    import nltk
except Exception:  # pragma: no cover - optional dependency fallback
    nltk = None

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    if nltk is None:
        raise LookupError()
    nltk.data.find('tokenizers/punkt')
except LookupError:
    if nltk is not None:
        nltk.download('punkt', quiet=True)

class SemanticChunker:
    """Intelligently chunk text with semantic boundaries and overlap"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target tokens per chunk
            overlap: Tokens to overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.encoding_for_model("gpt-4") if tiktoken else None
        logger.info(f"SemanticChunker initialized: size={chunk_size}, overlap={overlap}")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        if self.encoding:
            return len(self.encoding.encode(text))
        return max(1, len(text.split()))
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using NLTK"""
        try:
            if nltk is None:
                raise RuntimeError("nltk unavailable")
            return nltk.sent_tokenize(text)
        except Exception as e:
            logger.warning(f"NLTK tokenization failed: {e}, falling back to period split")
            return [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]
    
    def _split_on_semantic_boundaries(self, text: str) -> List[str]:
        """Intelligently split on semantic boundaries (paragraphs, sections)"""
        # Try paragraph split first
        if '\n\n' in text:
            return text.split('\n\n')
        
        # Try section split
        if '#' in text[:200]:  # Markdown headers
            sections = text.split('#')
            return [s.strip() for s in sections if s.strip()]
        
        # Fall back to sentence split
        return self._split_into_sentences(text)
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        semantic_boundaries: bool = True
    ) -> List[Dict]:
        """
        Split text into chunks with specified size and overlap
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            semantic_boundaries: Whether to respect semantic boundaries
            
        Returns:
            List of chunk dictionaries with id, text, token_count, metadata
        """
        if not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        metadata = metadata or {}
        chunks = []
        chunk_id = 0
        source = str(metadata.get("source", "document"))
        source_slug = re.sub(r"[^a-zA-Z0-9]+", "_", source).strip("_").lower()[:80] or "document"
        
        # Get sentences
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        current_tokens = 0
        overlap_buffer = ""
        overlap_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            # If adding this sentence exceeds chunk_size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Save chunk
                chunks.append({
                    "id": f"{source_slug}_chunk_{chunk_id}",
                    "text": current_chunk.strip(),
                    "token_count": current_tokens,
                    "sentence_count": len(current_chunk.split('.')),
                    "metadata": {**metadata, "chunk_id": f"{source_slug}_chunk_{chunk_id}"}
                })
                
                # Create overlap buffer from end of current chunk
                if self.overlap > 0:
                    overlap_sentences = []
                    overlap_text = ""
                    overlap_count = 0
                    
                    # Get last N sentences for overlap
                    for s in reversed(current_chunk.split('.')):
                        s_tokens = self._count_tokens(s)
                        if overlap_count + s_tokens <= self.overlap:
                            overlap_sentences.insert(0, s)
                            overlap_count += s_tokens
                        else:
                            break
                    
                    overlap_buffer = '. '.join(overlap_sentences)
                
                # Start new chunk with overlap
                current_chunk = overlap_buffer + ". " if overlap_buffer else ""
                current_tokens = overlap_tokens
                chunk_id += 1
            
            current_chunk += sentence + " "
            current_tokens += sentence_tokens
            overlap_tokens = min(overlap_tokens + sentence_tokens, self.overlap)
        
        # Add last chunk
        if current_chunk.strip():
            chunks.append({
                "id": f"{source_slug}_chunk_{chunk_id}",
                "text": current_chunk.strip(),
                "token_count": current_tokens,
                "sentence_count": len(current_chunk.split('.')),
                "metadata": {**metadata, "chunk_id": f"{source_slug}_chunk_{chunk_id}"}
            })
        
        logger.info(f"Chunked text into {len(chunks)} chunks (avg tokens: {sum(c['token_count'] for c in chunks) / len(chunks) if chunks else 0:.1f})")
        return chunks
    
    def get_statistics(self, chunks: List[Dict]) -> Dict:
        """Get statistics about chunked text"""
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_tokens_per_chunk": 0,
                "min_tokens": 0,
                "max_tokens": 0
            }
        
        token_counts = [c['token_count'] for c in chunks]
        return {
            "total_chunks": len(chunks),
            "total_tokens": sum(token_counts),
            "avg_tokens_per_chunk": sum(token_counts) / len(chunks),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts)
        }
