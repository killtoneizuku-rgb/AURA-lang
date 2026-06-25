"""
SQLite Store — Structured data storage for conversations and metadata.
"""

import logging
import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from config import SQLITE_PATH

logger = logging.getLogger("sqlite_store")


class SQLiteStore:
    """
    SQLite database for structured storage:
    - Conversation history
    - User profile
    - Task history
    """
    
    def __init__(self):
        self.db_path = SQLITE_PATH
        self._initialize()
    
    def _initialize(self):
        """Create database tables."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT,
                    assistant_response TEXT,
                    intent_type TEXT
                )
            """)
            
            # User profile table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            # Task history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    task_type TEXT,
                    description TEXT,
                    status TEXT,
                    result TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"SQLite database initialized: {self.db_path}")
        
        except Exception as e:
            logger.error(f"Error initializing SQLite: {e}")
    
    def store_conversation(self, user_input: str, response: str, intent_type: str = None):
        """Store a conversation turn."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (user_input, assistant_response, intent_type) VALUES (?, ?, ?)",
                (user_input, response, intent_type)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
    
    def get_conversations(self, limit: int = 50) -> List[Dict]:
        """Get recent conversations."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {"id": r[0], "timestamp": r[1], "user_input": r[2], "response": r[3], "intent": r[4]}
                for r in rows
            ]
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    def set_user_preference(self, key: str, value: str):
        """Store a user preference."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error setting preference: {e}")
    
    def get_user_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get a user preference."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else default
        except Exception as e:
            logger.error(f"Error getting preference: {e}")
            return default
    
    def log_task(self, task_type: str, description: str, status: str, result: str = None):
        """Log a task execution."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO task_history (task_type, description, status, result) VALUES (?, ?, ?, ?)",
                (task_type, description, status, result)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging task: {e}")
