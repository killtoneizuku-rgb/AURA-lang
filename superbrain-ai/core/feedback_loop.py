"""
Feedback Loop — Error detection and recovery for task execution.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("feedback_loop")


class FeedbackLoop:
    """
    Handles error detection, retry logic, and response refinement.
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.max_retries = 3
        self.error_history = []
    
    def should_retry(self, step: Dict) -> bool:
        """Determine if a failed step should be retried."""
        error_count = sum(
            1 for e in self.error_history 
            if e.get("step_desc") == step.get("description")
        )
        return error_count < self.max_retries
    
    def retry_step(self, step: Dict) -> str:
        """Attempt to retry a failed step with modified approach."""
        step_desc = step.get("description", "")
        step_type = step.get("type", "general")
        
        logger.info(f"Retrying step: {step_desc}")
        
        # Record the error
        self.error_history.append({
            "step_desc": step_desc,
            "step_type": step_type,
            "attempt": len([e for e in self.error_history if e.get("step_desc") == step_desc]) + 1
        })
        
        # Ask LLM for alternative approach
        prompt = f"""The following task failed: {step_desc}
Type: {step_type}

Suggest an alternative approach to accomplish this task.
Be specific and practical."""
        
        try:
            response = self.orchestrator.brain.ask(prompt)
            return f"Alternative approach: {response}"
        except Exception as e:
            logger.error(f"Retry failed: {e}")
            return f"Could not complete: {step_desc}. Error: {str(e)}"
    
    def validate_response(self, response: str, expected_type: str) -> bool:
        """Validate that a response meets expectations."""
        if not response or not response.strip():
            return False
        
        # Type-specific validation
        if expected_type == "json":
            import json
            try:
                json.loads(response)
                return True
            except:
                return False
        elif expected_type == "code":
            # Basic check for code-like content
            return any(keyword in response.lower() for keyword in ["def ", "import ", "class ", "="])
        
        return True
    
    def refine_response(self, response: str, feedback: str) -> str:
        """Ask LLM to refine a response based on feedback."""
        prompt = f"""Original response:
{response}

Feedback for improvement:
{feedback}

Please provide an improved version addressing the feedback."""
        
        try:
            refined = self.orchestrator.brain.ask(prompt)
            return refined
        except Exception as e:
            logger.error(f"Refinement failed: {e}")
            return response
    
    def log_error(self, step: Dict, error: str):
        """Log an error for analysis."""
        self.error_history.append({
            "step": step,
            "error": error,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        logger.error(f"Error logged: {error}")
    
    def get_error_patterns(self) -> List[Dict]:
        """Analyze error history for patterns."""
        from collections import Counter
        error_types = Counter(e.get("step_type", "unknown") for e in self.error_history)
        return [{"type": k, "count": v} for k, v in error_types.most_common()]
    
    def clear_error_history(self):
        """Clear error history."""
        self.error_history = []
        logger.info("Error history cleared")
