"""
Agent Registry — Manages agent discovery and registration.
"""

import logging
from typing import Dict, List, Optional, Type
from .base_agent import BaseAgent

logger = logging.getLogger("agent_registry")


class AgentRegistry:
    """
    Registry for discovering and managing agents.
    Allows dynamic agent registration and lookup.
    """
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
    
    def register(self, name: str, agent: BaseAgent):
        """Register an agent instance."""
        self._agents[name] = agent
        logger.info(f"Registered agent: {name}")
    
    def register_class(self, name: str, agent_class: Type[BaseAgent]):
        """Register an agent class for later instantiation."""
        self._agent_classes[name] = agent_class
        logger.info(f"Registered agent class: {name}")
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self._agents.get(name)
    
    def get_all(self) -> Dict[str, BaseAgent]:
        """Get all registered agents."""
        return self._agents.copy()
    
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
    
    def create_agent(self, name: str, orchestrator) -> Optional[BaseAgent]:
        """Create an agent instance from a registered class."""
        agent_class = self._agent_classes.get(name)
        if agent_class:
            agent = agent_class(orchestrator)
            self.register(name, agent)
            return agent
        return None
    
    def unregister(self, name: str) -> bool:
        """Unregister an agent."""
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered agent: {name}")
            return True
        return False
    
    def has_agent(self, name: str) -> bool:
        """Check if an agent is registered."""
        return name in self._agents
    
    def get_status(self) -> Dict[str, Dict]:
        """Get status of all agents."""
        status = {}
        for name, agent in self._agents.items():
            status[name] = agent.get_status()
        return status
