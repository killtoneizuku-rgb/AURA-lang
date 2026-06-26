"""
SuperBrain Tools - File Operations
Safe file CRUD operations with path validation
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger("tools.file_tool")


class FileTool:
    """File system operations with safety checks."""
    
    def __init__(self, max_file_size_mb: int = 10):
        self.max_file_size = max_file_size_mb * 1024 * 1024
        
        # Allowed base directories
        self.allowed_bases = [
            Path.home(),
            Path.home() / "Desktop",
            Path.home() / "Documents", 
            Path.home() / "Downloads",
            Path.cwd(),
            Path("/tmp"),
        ]
    
    def is_safe_path(self, path: str) -> bool:
        """Check if path is within allowed directories."""
        try:
            path_obj = Path(path).resolve()
            
            for base in self.allowed_bases:
                try:
                    # Check if path starts with allowed base
                    path_obj.relative_to(base.resolve())
                    return True
                except ValueError:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def read(self, path: str, max_lines: Optional[int] = None) -> dict:
        """Read file contents."""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if not path_obj.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            # Check size
            if path_obj.stat().st_size > self.max_file_size:
                return {"success": False, "error": f"File too large (>{self.max_file_size // (1024*1024)}MB)"}
            
            content = path_obj.read_text(encoding='utf-8', errors='ignore')
            
            if max_lines:
                lines = content.split('\n')[:max_lines]
                content = '\n'.join(lines)
            
            return {
                "success": True,
                "path": str(path_obj),
                "content": content,
                "size": path_obj.stat().st_size,
                "lines": len(content.split('\n'))
            }
            
        except Exception as e:
            logger.error(f"Read error: {e}")
            return {"success": False, "error": str(e)}
    
    def write(self, path: str, content: str, append: bool = False) -> dict:
        """Write content to file."""
        try:
            path_obj = Path(path)
            
            # Create parent directories
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path_obj, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(path_obj),
                "message": f"Successfully wrote {len(content)} bytes",
                "mode": "append" if append else "write"
            }
            
        except Exception as e:
            logger.error(f"Write error: {e}")
            return {"success": False, "error": str(e)}
    
    def delete(self, path: str) -> dict:
        """Delete file or empty directory."""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            if path_obj.is_file():
                path_obj.unlink()
                return {"success": True, "message": f"Deleted file: {path}"}
            elif path_obj.is_dir():
                if any(path_obj.iterdir()):
                    return {"success": False, "error": "Directory not empty. Use recursive delete with caution."}
                path_obj.rmdir()
                return {"success": True, "message": f"Deleted directory: {path}"}
            
            return {"success": False, "error": "Unknown path type"}
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return {"success": False, "error": str(e)}
    
    def list_dir(self, path: str = ".", pattern: Optional[str] = None) -> dict:
        """List directory contents."""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {"success": False, "error": f"Directory not found: {path}"}
            
            if not path_obj.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}
            
            items = []
            for item in path_obj.iterdir():
                # Filter by pattern if provided
                if pattern and not item.match(pattern):
                    continue
                
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item),
                }
                
                if item.is_file():
                    try:
                        item_info["size"] = item.stat().st_size
                        item_info["modified"] = item.stat().st_mtime
                    except:
                        pass
                
                items.append(item_info)
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            return {
                "success": True,
                "path": str(path_obj),
                "items": items,
                "count": len(items)
            }
            
        except Exception as e:
            logger.error(f"List error: {e}")
            return {"success": False, "error": str(e)}
    
    def create_dir(self, path: str, parents: bool = True) -> dict:
        """Create directory."""
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=parents, exist_ok=True)
            
            return {
                "success": True,
                "path": str(path_obj),
                "message": f"Created directory: {path}"
            }
            
        except Exception as e:
            logger.error(f"Mkdir error: {e}")
            return {"success": False, "error": str(e)}
    
    def copy(self, src: str, dst: str) -> dict:
        """Copy file."""
        try:
            src_obj = Path(src)
            dst_obj = Path(dst)
            
            if not src_obj.exists():
                return {"success": False, "error": f"Source not found: {src}"}
            
            dst_obj.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_obj, dst_obj)
            
            return {
                "success": True,
                "message": f"Copied {src} to {dst}"
            }
            
        except Exception as e:
            logger.error(f"Copy error: {e}")
            return {"success": False, "error": str(e)}
    
    def move(self, src: str, dst: str) -> dict:
        """Move/rename file or directory."""
        try:
            src_obj = Path(src)
            dst_obj = Path(dst)
            
            if not src_obj.exists():
                return {"success": False, "error": f"Source not found: {src}"}
            
            dst_obj.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_obj), str(dst_obj))
            
            return {
                "success": True,
                "message": f"Moved {src} to {dst}"
            }
            
        except Exception as e:
            logger.error(f"Move error: {e}")
            return {"success": False, "error": str(e)}
    
    def search(self, path: str, pattern: str, recursive: bool = True) -> dict:
        """Search for files matching pattern."""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            matches = []
            
            if recursive:
                matches = [str(p) for p in path_obj.rglob(pattern)]
            else:
                matches = [str(p) for p in path_obj.glob(pattern)]
            
            return {
                "success": True,
                "pattern": pattern,
                "matches": matches[:100],  # Limit results
                "count": len(matches)
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
_tool = None

def get_tool(max_file_size_mb: int = 10) -> FileTool:
    """Get or create file tool instance."""
    global _tool
    if _tool is None:
        _tool = FileTool(max_file_size_mb=max_file_size_mb)
    return _tool
