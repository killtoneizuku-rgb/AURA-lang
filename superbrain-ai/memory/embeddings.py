"""
Embedding Model — Local embedding generation using sentence-transformers.
"""

import logging
from typing import List
from config import EMBEDDING_MODEL

logger = logging.getLogger("embeddings")


class EmbeddingModel:
    """
    Generates embeddings using local sentence-transformers model.
    """
    
    def __init__(self):
        self.model_name = EMBEDDING_MODEL
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Load the embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Using fallback embeddings.")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
    
    def encode(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not self.model:
            return self._fallback_encode(text)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return self._fallback_encode(text)
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self.model:
            return [self._fallback_encode(t) for t in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error batch encoding: {e}")
            return [self._fallback_encode(t) for t in texts]
    
    def _fallback_encode(self, text: str) -> List[float]:
        """Simple fallback embedding (hash-based)."""
        # Create a simple hash-based embedding (not semantic, but works as fallback)
        import hashlib
        
        h = hashlib.md5(text.encode()).hexdigest()
        # Convert hex to float vector (384 dimensions to match all-MiniLM-L6-v2)
        embedding = [(int(h[i:i+2], 16) - 128) / 128.0 for i in range(0, min(len(h), 384*2), 2)]
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        return embedding[:384]
