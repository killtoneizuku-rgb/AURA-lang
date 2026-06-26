"""
SuperBrain JARVIS — Configuration
All settings in one place. No API keys needed.
"""

import os
from pathlib import Path

# ─── PATHS ───
BASE_DIR = Path(__file__).parent
MEMORY_DIR = BASE_DIR / "memory" / "storage"
CHROMA_DIR = MEMORY_DIR / "chroma_db"
SQLITE_PATH = MEMORY_DIR / "superbrain.db"
EXPORT_DIR = MEMORY_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
for d in [MEMORY_DIR, CHROMA_DIR, EXPORT_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── LLM SETTINGS ───
OLLAMA_BASE_URL = "http://localhost:11434"
PRIMARY_MODEL = "qwen2.5:7b"
FALLBACK_MODELS = ["llama3:8b", "mistral:7b", "deepseek-coder:6.7b"]
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
TEMPERATURE = 0.7
MAX_TOKENS = 4096

# ─── CONTEXT SETTINGS ───
MAX_CONVERSATION_HISTORY = 50  # messages kept in context
MAX_CONTEXT_TOKENS = 6000      # estimated token budget for context
SYSTEM_PROMPT_TOKENS_BUDGET = 1000

# ─── AGENT SETTINGS ───
INTENT_CONFIDENCE_THRESHOLD = 0.6
MAX_PLANNING_STEPS = 10
MAX_CODE_EXECUTION_RETRIES = 3
CODE_EXECUTION_TIMEOUT = 30  # seconds
SHELL_EXECUTION_TIMEOUT = 15  # seconds

# ─── SAFETY SETTINGS ───
BLOCKED_SHELL_COMMANDS = [
    "rm -rf /", "format", "del /f /s /q C:", 
    "mkfs", "dd if=", ":(){ :|:& };:",
    "shutdown", "reboot", "halt",
    "curl | bash", "wget | bash",
]
ALLOWED_SHELL_PATHS = [
    str(Path.home()),
    str(Path.home() / "Desktop"),
    str(Path.home() / "Documents"),
    str(Path.home() / "Downloads"),
    str(Path.cwd()),
]
MAX_FILE_SIZE_MB = 10

# ─── MEMORY SETTINGS ───
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_COLLECTION_NAME = "superbrain_knowledge"
MEMORY_RETRIEVAL_TOP_K = 5
MEMORY_CONSOLIDATION_AGE_DAYS = 30
SHORT_TERM_MEMORY_LIMIT = 20

# ─── VOICE SETTINGS ───
VOICE_ENABLED = False
WAKE_WORD = "jarvis"
STT_ENGINE = "vosk"  # or "whisper"
TTS_ENGINE = "pyttsx3"
TTS_VOICE_RATE = 180

# ─── UI SETTINGS ───
UI_THEME = "dark_jarvis"
UI_PORT = 7860
UI_WIDTH = "100%"
UI_TITLE = "🧠 SuperBrain JARVIS"
UI_DESCRIPTION = "Your Personal AI Operating System"
UI_SHARE = False
UI_SERVER_NAME = "0.0.0.0"

# ─── WEB SEARCH SETTINGS ───
SEARCH_ENGINE = "duckduckgo"  # no API key needed
MAX_SEARCH_RESULTS = 5
SCRAPE_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ─── LOGGING ───
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
LOG_FILES = {
    "activity": LOG_DIR / "activity.log",
    "decisions": LOG_DIR / "agent_decisions.log",
    "errors": LOG_DIR / "errors.log",
    "memory": LOG_DIR / "memory_operations.log",
}
