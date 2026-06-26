"""
Planner Agent — Breaks down complex tasks into executable steps.
"""

import logging
import json
from typing import Dict, List, Optional

from .base_agent import BaseAgent

logger = logging.getLogger("planner_agent")


class PlannerAgent(BaseAgent):
    """
    Planner Agent specializes in:
    - Breaking down complex tasks into steps
    - Identifying dependencies between steps
    - Creating execution plans
    """
    
    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.max_steps = 10
    
    def execute(self, user_input: str, intent: Dict) -> str:
        """Create a plan for the complex task."""
        logger.info(f"Planning task: {user_input[:100]}...")
        
        # Ask LLM to create a plan
        plan = self._create_plan(user_input)
        
        if not plan or not isinstance(plan, list):
            return "Failed to create a plan. Please try rephrasing your request."
        
        # Limit steps
        plan = plan[:self.max_steps]
        
        # Execute the plan through orchestrator
        result = self.orchestrator.execute_plan(plan)
        
        self._mark_success()
        return result
    
    def _create_plan(self, user_input: str) -> List[Dict]:
        """Use LLM to create a step-by-step plan."""
        from core.prompt_templates import PromptTemplates
        
        system_prompt = PromptTemplates.PLANNER_AGENT
        
        prompt = f"""Create a step-by-step plan to accomplish this task:

TASK: {user_input}

Output ONLY a valid JSON array of steps. Each step should have:
- "type": one of [code, system, web, memory, general]
- "description": what needs to be done
- "dependencies": array of step numbers this depends on (empty if none)

Example format:
[
  {{"type": "web", "description": "Search for information", "dependencies": []}},
  {{"type": "code", "description": "Process the data", "dependencies": [1]}}
]"""
        
        try:
            response = self.brain.ask(prompt, system_prompt=system_prompt, temperature=0.3)
            
            # Try to parse as JSON
            plan = self._parse_json_response(response)
            
            if plan and isinstance(plan, list):
                logger.info(f"Created plan with {len(plan)} steps")
                return plan
            else:
                logger.warning("LLM did not return valid JSON plan")
                return self._fallback_plan(user_input)
        
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return self._fallback_plan(user_input)
    
    def _parse_json_response(self, response: str) -> Optional[List[Dict]]:
        """Extract and parse JSON from LLM response."""
        import re
        
        # Try to find JSON array in response
        json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try parsing entire response as JSON
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _fallback_plan(self, user_input: str) -> List[Dict]:
        """Create a simple fallback plan when LLM fails."""
        return [
            {
                "type": "general",
                "description": f"Address the user's request: {user_input}",
                "dependencies": []
            }
        ]
    
    def execute_step(self, step: Dict) -> str:
        """Execute a planning-related step."""
        # Planning steps are usually handled by delegating to other agents
        step_type = step.get("type", "general")
        
        if step_type == "code":
            return self.orchestrator.agents["coder"].execute_step(step)
        elif step_type == "system":
            return self.orchestrator.agents["system"].execute_step(step)
        elif step_type == "web":
            return self.orchestrator.agents["web"].execute_step(step)
        elif step_type == "memory":
            return self.orchestrator.agents["memory"].execute_step(step)
        else:
            return super().execute_step(step)
