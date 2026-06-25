"""
Memory Agent — Handles storage and retrieval of knowledge.
"""

import logging
from typing import Dict, Optional
from .base_agent import BaseAgent

logger = logging.getLogger("memory_agent")


class MemoryAgent(BaseAgent):
    """
    Memory Agent specializes in:
    - Storing information in long-term memory
    - Retrieving relevant memories
    - Managing user profile and preferences
    """
    
    def __init__(self, orchestrator):
        super().__init__(orchestrator)
    
    def execute(self, user_input: str, intent: Dict) -> str:
        """Execute a memory operation."""
        logger.info(f"Memory task: {user_input[:100]}...")
        
        if not self.orchestrator.memory:
            return "Memory system not initialized."
        
        # Determine operation type
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["remember", "save", "store"]):
            return self._store_memory(user_input)
        elif any(word in input_lower for word in ["recall", "what did", "my notes", "search memory"]):
            return self._retrieve_memory(user_input)
        elif "forget" in input_lower:
            return self._forget_memory(user_input)
        else:
            return self._retrieve_memory(user_input)
    
    def _store_memory(self, user_input: str) -> str:
        """Store information in memory."""
        try:
            # Ask LLM to extract the key information to store
            prompt = f"""Extract the key fact or information to remember from this request:

{user_input}

Respond with ONLY the fact to remember, nothing else."""
            
            fact = self.brain.ask(prompt).strip()
            
            if not fact or len(fact) < 5:
                return "I couldn't determine what to remember. Please be more specific."
            
            # Store in memory
            self.orchestrator.memory.store(fact, metadata={"source": "user_request"})
            
            self._mark_success()
            return f"I've remembered: {fact}"
        
        except Exception as e:
            self._mark_error()
            return f"Error storing memory: {str(e)}"
    
    def _retrieve_memory(self, query: str) -> str:
        """Retrieve relevant memories."""
        try:
            # Search memory
            results = self.orchestrator.memory.search(query, top_k=5)
            
            if not results:
                return "No relevant memories found."
            
            # Format results
            formatted = []
            for i, r in enumerate(results, 1):
                content = r.get("content", "No content")
                score = r.get("score", 0)
                formatted.append(f"{i}. {content} (relevance: {score:.2f})")
            
            self._mark_success()
            return f"Found {len(results)} relevant memories:\n\n" + "\n".join(formatted)
        
        except Exception as e:
            self._mark_error()
            return f"Error retrieving memory: {str(e)}"
    
    def _forget_memory(self, user_input: str) -> str:
        """Delete memories matching criteria."""
        try:
            # Ask LLM what to delete
            prompt = f"""What should be deleted from memory based on this request?

{user_input}

Respond with search terms to find the memories to delete."""
            
            search_terms = self.brain.ask(prompt).strip()
            
            # Find matching memories
            results = self.orchestrator.memory.search(search_terms, top_k=10)
            
            if not results:
                return "No matching memories found to delete."
            
            # Delete them
            count = 0
            for r in results:
                doc_id = r.get("id")
                if doc_id:
                    self.orchestrator.memory.delete(doc_id)
                    count += 1
            
            self._mark_success()
            return f"Deleted {count} memories matching '{search_terms}'"
        
        except Exception as e:
            self._mark_error()
            return f"Error deleting memories: {str(e)}"
    
    def execute_step(self, step: Dict) -> str:
        """Execute a memory step from a plan."""
        description = step.get("description", "")
        return self.execute(description, {"type": "memory"})
