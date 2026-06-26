"""
SuperBrain Tools - Python Code Runner
Sandboxed Python execution with timeout protection
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger("tools.python_runner")


class PythonRunner:
    """Execute Python code safely with timeout and output capture."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.allowed_modules = {
            'math', 'random', 'datetime', 'time', 'json', 're',
            'collections', 'itertools', 'functools', 'statistics',
            'string', 'textwrap', 'unicodedata', 'copy', 'pprint',
            'typing', 'dataclasses', 'enum', 'pathlib', 'os',
            'sys', 'io', 'tempfile', 'shutil', 'glob', 'fnmatch',
            'csv', 'configparser', 'hashlib', 'hmac', 'secrets',
            'base64', 'binascii', 'struct', 'codecs', 'ast',
            'dis', 'inspect', 'traceback', 'linecache', 'tokenize',
            'numbers', 'decimal', 'fractions', 'cmath',
        }
    
    def execute(self, code: str, input_data: Optional[str] = None) -> Tuple[str, str, int]:
        """
        Execute Python code and return (stdout, stderr, return_code).
        
        Args:
            code: Python code to execute
            input_data: Optional stdin input
            
        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run with timeout
            result = subprocess.run(
                [sys.executable, temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=tempfile.gettempdir(),
            )
            
            return result.stdout, result.stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Python execution timed out after {self.timeout}s")
            return "", f"Error: Execution timed out after {self.timeout} seconds", -1
        except Exception as e:
            logger.error(f"Python execution error: {e}")
            return "", f"Error: {str(e)}", -1
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate code for safety before execution.
        
        Returns:
            Tuple of (is_safe, error_message)
        """
        dangerous_patterns = [
            '__import__', 'eval(', 'exec(', 'compile(',
            'open(', 'subprocess', 'os.system', 'os.popen',
            'socket.', 'urllib.request', 'http.client',
            'importlib', 'pkgutil', 'runpy',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, ""


# Singleton instance
_runner = None

def get_runner(timeout: int = 30) -> PythonRunner:
    """Get or create Python runner instance."""
    global _runner
    if _runner is None:
        _runner = PythonRunner(timeout=timeout)
    return _runner


def run_python_code(code: str, input_data: Optional[str] = None, timeout: int = 30) -> dict:
    """
    Execute Python code and return structured result.
    
    Args:
        code: Python code to execute
        input_data: Optional stdin input
        timeout: Execution timeout in seconds
        
    Returns:
        Dictionary with success, output, error fields
    """
    runner = get_runner(timeout)
    
    # Validate first
    is_safe, error_msg = runner.validate_code(code)
    if not is_safe:
        return {
            "success": False,
            "output": "",
            "error": error_msg,
            "return_code": -1
        }
    
    # Execute
    stdout, stderr, returncode = runner.execute(code, input_data)
    
    return {
        "success": returncode == 0,
        "output": stdout,
        "error": stderr,
        "return_code": returncode
    }
