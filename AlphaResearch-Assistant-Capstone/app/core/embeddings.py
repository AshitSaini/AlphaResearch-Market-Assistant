"""OpenAI embeddings service"""
import hashlib
import math
import re
from collections import Counter
from typing import List, Optional
import logging
import time
from app.config import settings

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency fallback
    OpenAI = None

logger = logging.getLogger(__name__)

class EmbeddingsGenerator:
    """Generate embeddings using OpenAI's API"""
    
    def __init__(self, model: str = None):
        """Initialize embeddings generator"""
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self.use_openai = bool(
            OpenAI
            and self.api_key
            and not self.api_key.startswith("your-")
        )
        self.client = OpenAI(api_key=self.api_key) if self.use_openai else None
        
        mode = "OpenAI" if self.use_openai else "local hashing"
        logger.info(f"EmbeddingsGenerator initialized with model: {self.model} ({mode})")
    
    def generate(self, text: str, retry_count: int = 3) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            retry_count: Number of retries on failure
            
        Returns:
            Embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Empty text cannot be embedded")

        if not self.use_openai:
            return self._local_embedding(text)
        
        for attempt in range(retry_count):
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model
                )
                embedding = response.data[0].embedding
                logger.debug(f"Generated embedding of dimension {len(embedding)}")
                return embedding
            except Exception as e:
                logger.warning(f"Embedding generation attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to generate embedding after {retry_count} attempts")
                    raise
    
    def batch_generate(
        self,
        texts: List[str],
        batch_size: int = 100,
        retry_count: int = 3
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call (max 100 for OpenAI)
            retry_count: Number of retries on failure
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        if not self.use_openai:
            embeddings = [self._local_embedding(text) for text in texts]
            logger.info(f"Generated {len(embeddings)} local embeddings")
            return embeddings
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for attempt in range(retry_count):
                try:
                    response = self.client.embeddings.create(
                        input=batch,
                        model=self.model
                    )
                    
                    # Sort by index to maintain order
                    sorted_embeddings = sorted(response.data, key=lambda x: x.index)
                    batch_embeddings = [item.embedding for item in sorted_embeddings]
                    all_embeddings.extend(batch_embeddings)
                    
                    logger.info(f"Generated {len(batch_embeddings)} embeddings (batch {i//batch_size + 1})")
                    break
                    
                except Exception as e:
                    logger.warning(f"Batch embedding attempt {attempt + 1} failed: {str(e)}")
                    if attempt < retry_count - 1:
                        time.sleep(2 ** attempt)
                    else:
                        logger.error(f"Failed to generate batch embeddings after {retry_count} attempts")
                        raise
        
        logger.info(f"Generated {len(all_embeddings)} total embeddings")
        return all_embeddings

    def _local_embedding(self, text: str, dimensions: int = 384) -> List[float]:
        """Create a deterministic bag-of-words hashing embedding for offline demos."""
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        counts = Counter(tokens)
        vector = [0.0] * dimensions

        for token, count in counts.items():
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign * (1.0 + math.log(count))

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
    
    def get_model_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            "model": self.model,
            "dimension": 1536 if self.use_openai else 384,
            "mode": "openai" if self.use_openai else "local",
            "max_tokens_per_minute": 1000000 if "3-small" in self.model else 500000
        }
