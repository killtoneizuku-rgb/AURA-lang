"""
Context Manager — Manages conversation history and state.
"""

import logging
from typing import Dict, List, Optional
from collections import deque
from config import MAX_CONVERSATION_HISTORY

logger = logging.getLogger("context_manager")


class ContextManager:
    """
    Manages conversation context including:
    - Short-term conversation history
    - Current task state
    - User preferences for current session
    """
    
    def __init__(self):
        self.history = deque(maxlen=MAX_CONVERSATION_HISTORY)
        self.current_intent = None
        self.current_task = None
        self.variables = {}  # Temporary variables for task execution
    
    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.history.append({"role": role, "content": content})
        logger.debug(f"Added {role} message to history")
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation messages."""
        return list(self.history)[-limit:]
    
    def get_all_messages(self) -> List[Dict]:
        """Get full conversation history."""
        return list(self.history)
    
    def clear(self):
        """Clear conversation history."""
        self.history.clear()
        self.current_intent = None
        self.current_task = None
        self.variables = {}
        logger.info("Conversation context cleared")
    
    def set_current_intent(self, intent: Dict):
        """Set the current detected intent."""
        self.current_intent = intent
    
    def get_current_intent(self) -> Optional[Dict]:
        """Get the current intent."""
        return self.current_intent
    
    def set_variable(self, key: str, value):
        """Set a temporary variable for task execution."""
        self.variables[key] = value
        logger.debug(f"Set variable {key}")
    
    def get_variable(self, key: str, default=None):
        """Get a temporary variable."""
        return self.variables.get(key, default)
    
    def clear_variables(self):
        """Clear temporary variables."""
        self.variables = {}
    
    def get_context_summary(self) -> str:
        """Generate a summary of current context for prompts."""
        if not self.history:
            return "No conversation history."
        
        recent = self.get_recent_messages(5)
        summary_lines = []
        for msg in recent:
            summary_lines.append(f"{msg['role']}: {msg['content'][:100]}...")
        
        return "\n".join(summary_lines)
