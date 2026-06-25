"""
Memory Consolidator — Auto-summarizes old memories.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger("consolidator")


class MemoryConsolidator:
    """
    Periodically consolidates old memories by summarizing them.
    """
    
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.consolidation_age_days = 30
    
    def should_consolidate(self) -> bool:
        """Check if consolidation is needed."""
        # Could check last consolidation time from SQLite
        return True
    
    def consolidate_old_memories(self):
        """Find and summarize old memories."""
        logger.info("Starting memory consolidation...")
        
        # Get all memories older than threshold
        cutoff_date = datetime.now() - timedelta(days=self.consolidation_age_days)
        
        # This would query SQLite for old conversations
        # For now, just a placeholder
        old_memories = []
        
        if not old_memories:
            logger.info("No old memories to consolidate")
            return
        
        # Group by topic and summarize
        summaries = self._generate_summaries(old_memories)
        
        # Store summaries, archive old details
        for summary in summaries:
            self.memory.store(summary, metadata={"type": "consolidated_summary"})
        
        logger.info(f"Consolidated {len(old_memories)} memories into {len(summaries)} summaries")
    
    def _generate_summaries(self, memories: List[Dict]) -> List[str]:
        """Generate summaries of grouped memories."""
        if not self.memory or not hasattr(self.memory, 'orchestrator'):
            return [f"Consolidated {len(memories)} old memories"]
        
        # Ask LLM to summarize
        combined = "\n".join(m.get("content", "") for m in memories[:10])
        
        prompt = f"""Summarize these old memories concisely:

{combined}

Provide a brief summary capturing the key points."""
        
        try:
            summary = self.memory.orchestrator.brain.ask(prompt)
            return [summary]
        except Exception as e:
            logger.error(f"Error generating summaries: {e}")
            return [f"Consolidated {len(memories)} old memories"]
