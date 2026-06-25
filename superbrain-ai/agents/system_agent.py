"""
System Agent — Handles file operations and shell commands safely.
"""

import logging
from typing import Dict, List
import subprocess
import os
from pathlib import Path
import shutil

from .base_agent import BaseAgent
from config import SHELL_EXECUTION_TIMEOUT, BLOCKED_SHELL_COMMANDS, ALLOWED_SHELL_PATHS

logger = logging.getLogger("system_agent")


class SystemAgent(BaseAgent):
    """
    System Agent specializes in:
    - Safe file operations (create, read, write, delete)
    - Shell command execution with safety checks
    - Directory navigation and management
    """
    
    def __init__(self, orchestrator):
        super().__init__(orchestrator)
        self.timeout = SHELL_EXECUTION_TIMEOUT
    
    def execute(self, user_input: str, intent: Dict) -> str:
        """Execute a system operation."""
        logger.info(f"System task: {user_input[:100]}...")
        
        # Determine the operation type
        operation = self._classify_operation(user_input)
        
        if operation["type"] == "file":
            return self._handle_file_operation(operation)
        elif operation["type"] == "shell":
            return self._handle_shell_command(operation)
        elif operation["type"] == "directory":
            return self._handle_directory_operation(operation)
        else:
            return f"Unclear operation. Please be more specific."
    
    def _classify_operation(self, user_input: str) -> Dict:
        """Classify what type of operation the user wants."""
        input_lower = user_input.lower()
        
        # File operations
        if any(word in input_lower for word in ["create file", "write to", "save to"]):
            return {"type": "file", "operation": "write", "input": user_input}
        elif any(word in input_lower for word in ["read file", "show file", "open file"]):
            return {"type": "file", "operation": "read", "input": user_input}
        elif any(word in input_lower for word in ["delete file", "remove file"]):
            return {"type": "file", "operation": "delete", "input": user_input}
        
        # Directory operations
        elif any(word in input_lower for word in ["list files", "show directory", "ls"]):
            return {"type": "directory", "operation": "list", "input": user_input}
        elif "create folder" in input_lower or "create directory" in input_lower:
            return {"type": "directory", "operation": "create", "input": user_input}
        
        # Shell commands
        else:
            return {"type": "shell", "command": user_input, "input": user_input}
    
    def _handle_file_operation(self, operation: Dict) -> str:
        """Handle file operations safely."""
        op_type = operation.get("operation")
        input_text = operation.get("input", "")
        
        try:
            if op_type == "read":
                # Extract filename
                filename = self._extract_filename(input_text)
                if not filename:
                    return "Please specify a filename."
                
                if not os.path.exists(filename):
                    return f"File not found: {filename}"
                
                with open(filename, 'r') as f:
                    content = f.read()
                
                self._mark_success()
                return f"Contents of {filename}:\n\n{content}"
            
            elif op_type == "write":
                # Ask LLM to extract filename and content
                extracted = self._extract_write_params(input_text)
                filename = extracted.get("filename")
                content = extracted.get("content")
                
                if not filename or not content:
                    return "Could not determine filename or content."
                
                # Validate path
                if not self._is_safe_path(filename):
                    return f"Error: Cannot write to {filename} (outside allowed paths)"
                
                with open(filename, 'w') as f:
                    f.write(content)
                
                self._mark_success()
                return f"Successfully wrote to {filename}"
            
            elif op_type == "delete":
                filename = self._extract_filename(input_text)
                if not filename:
                    return "Please specify a filename."
                
                if not self._is_safe_path(filename):
                    return f"Error: Cannot delete {filename} (outside allowed paths)"
                
                if os.path.exists(filename):
                    os.remove(filename)
                    self._mark_success()
                    return f"Deleted {filename}"
                else:
                    return f"File not found: {filename}"
        
        except Exception as e:
            self._mark_error()
            return f"Error: {str(e)}"
    
    def _handle_shell_command(self, operation: Dict) -> str:
        """Execute shell command with safety checks."""
        command = operation.get("command", "")
        
        # Safety check
        if not self._is_safe_command(command):
            return f"Error: Command '{command}' is blocked for safety reasons."
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            
            self._mark_success()
            return f"Command output:\n{output}" if output else "Command executed successfully"
        
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout}s"
        except Exception as e:
            self._mark_error()
            return f"Error executing command: {str(e)}"
    
    def _handle_directory_operation(self, operation: Dict) -> str:
        """Handle directory operations."""
        op_type = operation.get("operation")
        input_text = operation.get("input", "")
        
        try:
            if op_type == "list":
                # Extract path or use current directory
                path = self._extract_path(input_text) or "."
                
                if not os.path.isdir(path):
                    return f"Not a directory: {path}"
                
                items = os.listdir(path)
                formatted = "\n".join(f"  {item}" for item in sorted(items))
                
                self._mark_success()
                return f"Contents of {path}:\n\n{formatted}"
            
            elif op_type == "create":
                dirname = self._extract_dirname(input_text)
                if not dirname:
                    return "Please specify a directory name."
                
                os.makedirs(dirname, exist_ok=True)
                self._mark_success()
                return f"Created directory: {dirname}"
        
        except Exception as e:
            self._mark_error()
            return f"Error: {str(e)}"
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute."""
        command_lower = command.lower()
        
        # Check against blocked commands
        for blocked in BLOCKED_SHELL_COMMANDS:
            if blocked in command_lower:
                logger.warning(f"Blocked dangerous command: {command}")
                return False
        
        return True
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if path is within allowed directories."""
        try:
            abs_path = os.path.abspath(path)
            
            for allowed in ALLOWED_SHELL_PATHS:
                if abs_path.startswith(allowed):
                    return True
            
            return False
        except:
            return False
    
    def _extract_filename(self, text: str) -> str:
        """Extract filename from text."""
        import re
        # Look for quoted filenames or common patterns
        match = re.search(r'["\']([^"\']+\.?\w*)["\']', text)
        if match:
            return match.group(1)
        
        # Try to find word after "file"
        match = re.search(r'file\s+(\S+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_path(self, text: str) -> str:
        """Extract path from text."""
        import re
        match = re.search(r'in\s+([^\s,]+)', text)
        if match:
            return match.group(1)
        return None
    
    def _extract_dirname(self, text: str) -> str:
        """Extract directory name from text."""
        import re
        match = re.search(r'(?:called|named)\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_write_params(self, text: str) -> Dict:
        """Extract filename and content for write operation."""
        # Ask LLM to parse
        prompt = f"""Extract the filename and content from this request:

{text}

Respond with JSON: {{"filename": "...", "content": "..."}}"""
        
        try:
            response = self.brain.ask(prompt, temperature=0.2)
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {}
    
    def execute_step(self, step: Dict) -> str:
        """Execute a system step from a plan."""
        description = step.get("description", "")
        return self.execute(description, {"type": "system"})
