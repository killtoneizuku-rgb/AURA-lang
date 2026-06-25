"""
Vector Database — ChromaDB interface for semantic search.
"""

import logging
from typing import List, Dict, Optional
from config import CHROMA_DIR, CHROMA_COLLECTION_NAME

logger = logging.getLogger("vector_db")


class VectorDatabase:
    """
    ChromaDB-based vector storage for semantic memory.
    """
    
    def __init__(self):
        self.collection_name = CHROMA_COLLECTION_NAME
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Initialize persistent client
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "SuperBrain knowledge base"}
            )
            
            logger.info(f"Vector database initialized: {self.collection_name}")
        
        except ImportError:
            logger.warning("ChromaDB not installed. Memory features disabled.")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
    
    def add(self, id: str, text: str, embedding: List[float], metadata: Optional[Dict] = None):
        """Add a document to the vector database."""
        if not self.collection:
            return
        
        try:
            self.collection.add(
                ids=[id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )
            logger.debug(f"Added document {id} to vector DB")
        except Exception as e:
            logger.error(f"Error adding document: {e}")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar documents."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted = []
            if results and results['ids'] and results['ids'][0]:
                for i, id in enumerate(results['ids'][0]):
                    formatted.append({
                        "id": id,
                        "content": results['documents'][0][i] if results['documents'] else "",
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "score": 1 - results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted
        
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def delete(self, id: str):
        """Delete a document by ID."""
        if not self.collection:
            return
        
        try:
            self.collection.delete(ids=[id])
            logger.debug(f"Deleted document {id}")
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
    
    def count(self) -> int:
        """Get total document count."""
        if not self.collection:
            return 0
        
        try:
            return self.collection.count()
        except:
            return 0
    
    def clear(self):
        """Clear all documents."""
        if not self.collection:
            return
        
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(self.collection_name)
            logger.info("Vector database cleared")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
