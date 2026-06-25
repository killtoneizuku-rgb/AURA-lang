"""
Memory Manager — High-level interface for all memory operations.
"""

import logging
import uuid
from typing import List, Dict, Optional
from config import MEMORY_RETRIEVAL_TOP_K

logger = logging.getLogger("memory_manager")


class MemoryManager:
    """
    Central manager for all memory operations.
    Combines vector DB and SQLite storage.
    """
    
    def __init__(self):
        self.vector_db = None
        self.embeddings = None
        self.sqlite_store = None
        self._initialize()
    
    def _initialize(self):
        """Initialize all memory components."""
        try:
            from .vector_db import VectorDatabase
            from .embeddings import EmbeddingModel
            from .sqlite_store import SQLiteStore
            
            self.vector_db = VectorDatabase()
            self.embeddings = EmbeddingModel()
            self.sqlite_store = SQLiteStore()
            
            logger.info("Memory manager initialized")
        
        except Exception as e:
            logger.error(f"Error initializing memory manager: {e}")
    
    def store(self, text: str, metadata: Optional[Dict] = None) -> str:
        """Store a piece of information in memory."""
        doc_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = self.embeddings.encode(text) if self.embeddings else []
        
        # Store in vector DB
        if self.vector_db and embedding:
            self.vector_db.add(doc_id, text, embedding, metadata or {})
        
        # Log in SQLite
        if self.sqlite_store:
            self.sqlite_store.log_task("memory_store", text[:100], "success")
        
        logger.debug(f"Stored memory: {doc_id}")
        return doc_id
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for relevant memories."""
        if not self.vector_db or not self.embeddings:
            return []
        
        top_k = top_k or MEMORY_RETRIEVAL_TOP_K
        
        # Generate query embedding
        query_embedding = self.embeddings.encode(query)
        
        # Search vector DB
        results = self.vector_db.search(query_embedding, top_k=top_k)
        
        logger.debug(f"Found {len(results)} memories for query: {query[:50]}...")
        return results
    
    def delete(self, doc_id: str):
        """Delete a memory by ID."""
        if self.vector_db:
            self.vector_db.delete(doc_id)
        logger.debug(f"Deleted memory: {doc_id}")
    
    def store_conversation(self, user_input: str, response: str):
        """Store a conversation turn."""
        # Store in SQLite
        if self.sqlite_store:
            self.sqlite_store.store_conversation(user_input, response)
        
        # Also store in vector DB for semantic retrieval
        combined = f"User: {user_input}\nAssistant: {response}"
        self.store(combined, metadata={"type": "conversation"})
    
    def get_user_profile(self) -> Dict:
        """Get user profile information."""
        if not self.sqlite_store:
            return {}
        
        # Get all preferences
        profile = {}
        # Could be extended to fetch specific keys
        return profile
    
    def set_user_preference(self, key: str, value: str):
        """Set a user preference."""
        if self.sqlite_store:
            self.sqlite_store.set_user_preference(key, value)
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        stats = {
            "vector_count": self.vector_db.count() if self.vector_db else 0,
            "status": "active" if self.vector_db else "inactive"
        }
        return stats
    
    def clear(self):
        """Clear all memories."""
        if self.vector_db:
            self.vector_db.clear()
        logger.info("All memories cleared")
