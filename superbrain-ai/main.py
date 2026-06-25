"""
SuperBrain JARVIS — Main Entry Point
Launches the full AI assistant system.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_LEVEL, LOG_FORMAT, LOG_FILES, LOG_DIR
from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from core.model_manager import ModelManager


def setup_logging():
    """Configure multi-file logging system."""
    for log_file in LOG_FILES.values():
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILES["activity"]),
        ]
    )


def check_prerequisites():
    """Verify Ollama is running and models are available."""
    import requests
    from config import OLLAMA_BASE_URL, PRIMARY_MODEL
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = [m["name"] for m in response.json().get("models", [])]
            logging.info(f"✅ Ollama connected. Available models: {models}")
            
            if not any(PRIMARY_MODEL in m for m in models):
                logging.warning(f"⚠️ Primary model '{PRIMARY_MODEL}' not found.")
                print(f"\n⚠️ Model '{PRIMARY_MODEL}' not found. Install with:")
                print(f"   ollama pull {PRIMARY_MODEL}\n")
            
            return True
    except requests.exceptions.ConnectionError:
        logging.error("❌ Ollama is not running!")
        print("\n" + "="*60)
        print("❌ ERROR: Ollama is not running!")
        print("Start it with: ollama serve")
        print("="*60 + "\n")
        return False
    except Exception as e:
        logging.warning(f"Could not check Ollama: {e}")
        return True  # Continue anyway


def initialize_system():
    """Initialize all system components."""
    logging.info("🔧 Initializing SuperBrain JARVIS...")
    
    memory = MemoryManager()
    logging.info("✅ Memory system initialized")
    
    model_mgr = ModelManager()
    logging.info("✅ Model manager initialized")
    
    orchestrator = Orchestrator(memory=memory, model_manager=model_mgr)
    logging.info("✅ Orchestrator initialized")
    
    return orchestrator, memory, model_mgr


def run_cli_mode(orchestrator):
    """Run in command-line interface mode."""
    print("\n" + "🧠" * 20)
    print("   SUPERBRAIN JARVIS — AI Operating System")
    print("   Type 'exit' to quit, 'help' for commands")
    print("🧠" * 20 + "\n")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye! SuperBrain shutting down...")
                break
            
            if user_input.lower() == "help":
                print("""
📋 Available Commands:
  /memory   — Browse your memory/knowledge base
  /agents   — Show agent status
  /models   — List available models
  /clear    — Clear conversation history
  /export   — Export conversation
  /help     — Show this help
  exit      — Shut down SuperBrain
""")
                continue
            
            if user_input.startswith("/"):
                handle_command(user_input, orchestrator)
                continue
            
            print("\n🧠 Thinking...", end="", flush=True)
            response = orchestrator.process(user_input)
            print(f"\n🤖 JARVIS: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Interrupted. Type 'exit' to quit.")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            print(f"\n❌ Error: {e}")


def handle_command(command, orchestrator):
    """Handle slash commands."""
    cmd = command.lower().strip("/")
    
    if cmd == "clear":
        orchestrator.clear_conversation()
        print("✅ Conversation cleared")
    elif cmd == "agents":
        status = orchestrator.get_agent_status()
        for name, info in status.items():
            print(f"  {name}: {info['status']}")
    elif cmd == "models":
        models = orchestrator.model_manager.list_models()
        for m in models:
            print(f"  - {m}")
    elif cmd == "memory":
        stats = orchestrator.memory.get_stats()
        print(f"  📊 Memory Stats: {stats}")
    else:
        print(f"Unknown command: /{cmd}")


if __name__ == "__main__":
    setup_logging()
    
    if not check_prerequisites():
        sys.exit(1)
    
    orchestrator, memory, model_mgr = initialize_system()
    
    # Check for CLI flag
    if "--cli" in sys.argv:
        run_cli_mode(orchestrator)
    else:
        # For now, default to CLI (UI implementation follows)
        print("\n🌐 Starting web UI would go here...")
        print("   For now, use --cli for command-line mode\n")
        run_cli_mode(orchestrator)
