"""
SuperBrain Orchestrator — Master controller for all agents.
Handles intent classification, agent routing, task planning, and execution coordination.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .brain import LLMBrain
from .intent_classifier import IntentClassifier
from .context_manager import ContextManager
from .prompt_templates import PromptTemplates
from .feedback_loop import FeedbackLoop
from .model_manager import ModelManager
from agents.base_agent import BaseAgent
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.system_agent import SystemAgent
from agents.web_agent import WebAgent
from agents.memory_agent import MemoryAgent

logger = logging.getLogger("orchestrator")


class Orchestrator:
    """
    The central brain controller that:
    - Classifies user intent
    - Routes tasks to appropriate agents
    - Manages multi-step task execution
    - Coordinates feedback loops
    - Maintains conversation context
    """
    
    def __init__(self, memory=None, model_manager=None):
        self.brain = LLMBrain()
        self.model_manager = model_manager or ModelManager()
        self.memory = memory
        self.context = ContextManager()
        self.prompt_templates = PromptTemplates()
        self.feedback_loop = FeedbackLoop(self)
        
        # Initialize agents
        self.agents: Dict[str, BaseAgent] = {
            "planner": PlannerAgent(self),
            "coder": CoderAgent(self),
            "system": SystemAgent(self),
            "web": WebAgent(self),
            "memory": MemoryAgent(self),
        }
        
        self.intent_classifier = IntentClassifier(self.brain)
        self.current_task = None
        self.task_history = []
        
        logger.info("Orchestrator initialized with %d agents", len(self.agents))
    
    def process(self, user_input: str) -> str:
        """
        Main entry point for processing user input.
        Returns the final response to the user.
        """
        # Add to conversation history
        self.context.add_message("user", user_input)
        
        # Classify intent
        intent = self.intent_classifier.classify(user_input)
        logger.info(f"Classified intent: {intent['type']} (confidence: {intent['confidence']})")
        
        # Update context with intent
        self.context.set_current_intent(intent)
        
        # Route to appropriate agent(s)
        response = self._route_and_execute(user_input, intent)
        
        # Add response to history
        self.context.add_message("assistant", response)
        
        # Store in memory if significant
        if self.memory and self._should_remember(user_input, response):
            self.memory.store_conversation(user_input, response)
        
        return response
    
    def _route_and_execute(self, user_input: str, intent: Dict) -> str:
        """Route task to appropriate agent(s) and execute."""
        intent_type = intent["type"]
        
        # Simple routing based on intent
        if intent_type == "code":
            return self.agents["coder"].execute(user_input, intent)
        elif intent_type == "system":
            return self.agents["system"].execute(user_input, intent)
        elif intent_type == "web_search" or intent_type == "web_scrape":
            return self.agents["web"].execute(user_input, intent)
        elif intent_type == "memory":
            return self.agents["memory"].execute(user_input, intent)
        elif intent_type == "complex_task":
            # Use planner for complex multi-step tasks
            return self.agents["planner"].execute(user_input, intent)
        else:
            # General conversation - use LLM directly
            return self._general_response(user_input)
    
    def _general_response(self, user_input: str) -> str:
        """Handle general conversation using LLM directly."""
        system_prompt = self.prompt_templates.get_template("general_assistant")
        
        # Get conversation history
        messages = self.context.get_recent_messages(limit=10)
        
        try:
            response = self.brain.ask_with_context(
                messages=messages,
                system_prompt=system_prompt,
            )
            return response
        except Exception as e:
            logger.error(f"Error getting general response: {e}")
            return f"I encountered an error: {str(e)}"
    
    def _should_remember(self, user_input: str, response: str) -> bool:
        """Determine if this conversation should be stored in long-term memory."""
        # Simple heuristic: remember if conversation is substantial
        min_length = 50
        return len(user_input) > min_length or len(response) > min_length
    
    def execute_plan(self, plan: List[Dict]) -> str:
        """Execute a multi-step plan created by the Planner Agent."""
        results = []
        
        for i, step in enumerate(plan):
            step_type = step.get("type", "general")
            step_description = step.get("description", "")
            
            logger.info(f"Executing step {i+1}/{len(plan)}: {step_description}")
            
            try:
                if step_type == "code":
                    result = self.agents["coder"].execute_step(step)
                elif step_type == "system":
                    result = self.agents["system"].execute_step(step)
                elif step_type == "web":
                    result = self.agents["web"].execute_step(step)
                elif step_type == "memory":
                    result = self.agents["memory"].execute_step(step)
                else:
                    result = self._general_response(step_description)
                
                results.append({"step": i + 1, "result": result, "status": "success"})
                
            except Exception as e:
                logger.error(f"Step {i+1} failed: {e}")
                results.append({"step": i + 1, "error": str(e), "status": "failed"})
                
                # Try error recovery
                if self.feedback_loop.should_retry(step):
                    retry_result = self.feedback_loop.retry_step(step)
                    results[-1] = {"step": i + 1, "result": retry_result, "status": "recovered"}
        
        # Compile final result
        final_response = self._compile_plan_results(plan, results)
        return final_response
    
    def _compile_plan_results(self, plan: List[Dict], results: List[Dict]) -> str:
        """Compile results from all plan steps into a coherent response."""
        successful_steps = [r for r in results if r["status"] in ["success", "recovered"]]
        failed_steps = [r for r in results if r["status"] == "failed"]
        
        response_parts = []
        response_parts.append(f"✅ Completed {len(successful_steps)}/{len(plan)} steps:")
        
        for result in results:
            status_icon = "✅" if result["status"] == "success" else ("🔄" if result["status"] == "recovered" else "❌")
            step_info = plan[result["step"] - 1]
            response_parts.append(f"{status_icon} Step {result['step']}: {step_info.get('description', 'Unknown')}")
            
            if "result" in result:
                response_parts.append(f"   → {result['result'][:200]}")
        
        if failed_steps:
            response_parts.append(f"\n⚠️ {len(failed_steps)} step(s) failed")
        
        return "\n".join(response_parts)
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.context.clear()
        logger.info("Conversation history cleared")
    
    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents."""
        status = {}
        for name, agent in self.agents.items():
            status[name] = {
                "status": "active",
                "last_used": getattr(agent, "last_used", None),
                "tasks_completed": getattr(agent, "tasks_completed", 0),
            }
        return status
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history."""
        return self.context.get_all_messages()
    
    def export_conversation(self, filepath: Optional[str] = None) -> str:
        """Export conversation to file."""
        import json
        from pathlib import Path
        
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"conversation_{timestamp}.json"
        
        history = self.get_conversation_history()
        
        with open(filepath, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Conversation exported to {filepath}")
        return filepath
