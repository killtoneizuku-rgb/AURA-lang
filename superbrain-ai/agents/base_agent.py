"""
Base Agent — Abstract base class for all agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("agent")


class BaseAgent(ABC):
    """
    Abstract base class for all agent types.
    
    Each agent is responsible for:
    - Executing tasks of a specific type
    - Reporting status and results
    - Handling errors gracefully
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.brain = orchestrator.brain
        self.last_used = None
        self.tasks_completed = 0
        self.errors_encountered = 0
    
    @abstractmethod
    def execute(self, user_input: str, intent: Dict) -> str:
        """
        Execute a task based on user input and intent.
        
        Args:
            user_input: The original user request
            intent: Classified intent dictionary
        
        Returns:
            Response string describing the result
        """
        pass
    
    def execute_step(self, step: Dict) -> str:
        """
        Execute a single step from a plan.
        
        Args:
            step: Step dictionary with type, description, etc.
        
        Returns:
            Result of executing the step
        """
        # Default implementation - can be overridden
        return self._execute_generic_step(step)
    
    def _execute_generic_step(self, step: Dict) -> str:
        """Generic step execution using LLM."""
        description = step.get("description", "")
        
        prompt = f"""Execute the following task:
{description}

Provide a clear, concise result or explanation of what you did."""
        
        try:
            response = self.brain.ask(prompt)
            self._mark_success()
            return response
        except Exception as e:
            self._mark_error()
            return f"Error executing step: {str(e)}"
    
    def _mark_success(self):
        """Mark the agent as successfully completing a task."""
        self.last_used = datetime.now()
        self.tasks_completed += 1
        logger.debug(f"{self.__class__.__name__} completed task #{self.tasks_completed}")
    
    def _mark_error(self):
        """Mark that an error occurred."""
        self.errors_encountered += 1
        logger.error(f"{self.__class__.__name__} encountered error #{self.errors_encountered}")
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "name": self.__class__.__name__,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "tasks_completed": self.tasks_completed,
            "errors_encountered": self.errors_encountered,
            "status": "active"
        }
    
    def can_handle(self, intent_type: str) -> bool:
        """Check if this agent can handle a specific intent type."""
        # Override in subclasses for specific capability checking
        return True
