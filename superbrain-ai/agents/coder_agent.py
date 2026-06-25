"""
Coder Agent — Writes, executes, and debugs code.
"""

import logging
from typing import Dict, Optional
import subprocess
import sys
import tempfile
import os
from pathlib import Path

from .base_agent import BaseAgent
from config import CODE_EXECUTION_TIMEOUT, MAX_CODE_EXECUTION_RETRIES

logger = logging.getLogger("coder_agent")


class CoderAgent(BaseAgent):
    """
    Coder Agent specializes in:
    - Writing Python code
    - Executing code safely
    - Debugging and fixing errors
    """
    
    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.execution_timeout = CODE_EXECUTION_TIMEOUT
        self.max_retries = MAX_CODE_EXECUTION_RETRIES
    
    def execute(self, user_input: str, intent: Dict) -> str:
        """Write and optionally execute code."""
        logger.info(f"Coding task: {user_input[:100]}...")
        
        # Generate code using LLM
        code = self._generate_code(user_input)
        
        if not code:
            return "Failed to generate code."
        
        # Check if user wants execution
        should_execute = any(word in user_input.lower() for word in 
                           ["run", "execute", "test", "try"])
        
        if should_execute:
            result = self._execute_code(code)
            return f"Generated and executed code:\n\n```python\n{code}\n```\n\nResult:\n{result}"
        else:
            return f"Here's the code you requested:\n\n```python\n{code}\n```"
    
    def _generate_code(self, requirement: str) -> str:
        """Generate Python code based on requirements."""
        from core.prompt_templates import PromptTemplates
        
        system_prompt = PromptTemplates.CODER_AGENT
        
        prompt = f"""Write Python code to accomplish this task:

{requirement}

Provide ONLY the code, no explanations. Make it complete and runnable."""
        
        try:
            response = self.brain.ask(prompt, system_prompt=system_prompt, temperature=0.2)
            
            # Extract code from markdown if present
            code = self._extract_code(response)
            return code.strip()
        
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            return ""
    
    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response (may contain markdown)."""
        import re
        
        # Try to extract from markdown code blocks
        code_block = re.search(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
        
        if code_block:
            return code_block.group(1)
        
        # If no code blocks, return the whole response
        return response
    
    def _execute_code(self, code: str) -> str:
        """Execute Python code safely with timeout."""
        for attempt in range(self.max_retries):
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_path = f.name
                
                try:
                    # Execute with timeout
                    result = subprocess.run(
                        [sys.executable, temp_path],
                        capture_output=True,
                        text=True,
                        timeout=self.execution_timeout,
                        cwd=tempfile.gettempdir()
                    )
                    
                    output = result.stdout
                    if result.stderr:
                        output += f"\nErrors:\n{result.stderr}"
                    
                    if result.returncode == 0:
                        self._mark_success()
                        return output if output else "Code executed successfully (no output)"
                    else:
                        # Try to fix the error
                        if attempt < self.max_retries - 1:
                            fixed_code = self._fix_code(code, result.stderr)
                            if fixed_code != code:
                                code = fixed_code
                                continue
                    
                    return output
                
                finally:
                    # Clean up temp file
                    os.unlink(temp_path)
            
            except subprocess.TimeoutExpired:
                return f"Error: Code execution timed out after {self.execution_timeout}s"
            except Exception as e:
                logger.error(f"Execution error: {e}")
                if attempt >= self.max_retries - 1:
                    return f"Error executing code: {str(e)}"
        
        self._mark_error()
        return "Failed to execute code after retries"
    
    def _fix_code(self, code: str, error: str) -> str:
        """Ask LLM to fix code based on error message."""
        prompt = f"""The following Python code has an error:

```python
{code}
```

Error message:
{error}

Fix the code and provide ONLY the corrected code, no explanations."""
        
        try:
            response = self.brain.ask(prompt, temperature=0.2)
            fixed_code = self._extract_code(response)
            return fixed_code
        except Exception as e:
            logger.error(f"Error fixing code: {e}")
            return code
    
    def execute_step(self, step: Dict) -> str:
        """Execute a coding step from a plan."""
        description = step.get("description", "")
        code_requirement = step.get("code_requirement", description)
        
        code = self._generate_code(code_requirement)
        
        if step.get("execute", False):
            result = self._execute_code(code)
            return f"Code executed:\n{result}"
        else:
            return f"Generated code:\n```python\n{code}\n```"
