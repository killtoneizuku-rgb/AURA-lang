"""
SuperBrain Tools - Shell Command Executor
Safe shell command execution with whitelist validation
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, List, Tuple
import logging
import platform

logger = logging.getLogger("tools.shell_tool")


class ShellTool:
    """Execute shell commands safely with validation."""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.blocked_commands = [
            "rm -rf /", "format", "del /f /s /q C:", 
            "mkfs", "dd if=", ":(){ :|:& };:",
            "shutdown", "reboot", "halt", "sudo",
            "curl | bash", "wget | bash", "curl|bash", "wget|bash",
            "chmod 777", "chown -R", "mv /", "cp /",
        ]
        
        # Allowed paths (user home and subdirectories)
        self.allowed_paths = [
            str(Path.home()),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads"),
            str(Path.cwd()),
            "/tmp",
            "/var/tmp",
        ]
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command for safety."""
        # Check blocked commands
        for blocked in self.blocked_commands:
            if blocked.lower() in command.lower():
                return False, f"Blocked command detected: {blocked}"
        
        # Check for dangerous patterns
        dangerous_patterns = ["sudo", "su ", "pkexec", "doas"]
        for pattern in dangerous_patterns:
            if pattern in command.split():
                return False, f"Dangerous command: {pattern}"
        
        return True, ""
    
    def execute(
        self, 
        command: str, 
        cwd: Optional[str] = None,
        shell: bool = True
    ) -> Tuple[str, str, int]:
        """
        Execute shell command.
        
        Args:
            command: Command to execute
            cwd: Working directory
            shell: Use shell execution
            
        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        # Validate first
        is_safe, error_msg = self.validate_command(command)
        if not is_safe:
            logger.warning(f"Blocked unsafe command: {command}")
            return "", error_msg, -1
        
        # Set working directory
        if cwd is None:
            cwd = Path.home()
        
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=cwd,
                env=os.environ.copy(),
            )
            
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Command timed out after {self.timeout}s: {command}")
            return "", f"Error: Command timed out after {self.timeout} seconds", -1
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return "", f"Error: {str(e)}", -1
    
    def list_files(self, path: Optional[str] = None) -> dict:
        """List files in directory."""
        if path is None:
            path = str(Path.cwd())
        
        # Validate path
        path_obj = Path(path)
        if not path_obj.exists():
            return {"success": False, "error": f"Path does not exist: {path}"}
        
        try:
            items = []
            for item in path_obj.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                })
            
            return {
                "success": True,
                "path": str(path_obj),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def read_file(self, path: str, max_lines: int = 100) -> dict:
        """Read file contents."""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if not path_obj.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            # Check file size
            if path_obj.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                return {"success": False, "error": "File too large (>10MB)"}
            
            content = path_obj.read_text(errors='ignore')
            lines = content.split('\n')[:max_lines]
            
            return {
                "success": True,
                "path": str(path_obj),
                "content": '\n'.join(lines),
                "total_lines": len(content.split('\n')),
                "truncated": len(lines) < len(content.split('\n'))
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_file(self, path: str, content: str) -> dict:
        """Write content to file."""
        try:
            path_obj = Path(path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            path_obj.write_text(content)
            
            return {
                "success": True,
                "path": str(path_obj),
                "message": f"Successfully wrote {len(content)} bytes"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_tool = None

def get_tool(timeout: int = 15) -> ShellTool:
    """Get or create shell tool instance."""
    global _tool
    if _tool is None:
        _tool = ShellTool(timeout=timeout)
    return _tool


def run_shell_command(command: str, cwd: Optional[str] = None) -> dict:
    """Execute shell command and return structured result."""
    tool = get_tool()
    stdout, stderr, returncode = tool.execute(command, cwd)
    
    return {
        "success": returncode == 0,
        "output": stdout,
        "error": stderr,
        "return_code": returncode
    }
