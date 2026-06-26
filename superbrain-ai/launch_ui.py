#!/usr/bin/env python3
"""
SuperBrain JARVIS - Standalone UI Launcher
Launches the complete AI assistant with glassmorphism UI.
"""

import sys
import os
import webbrowser
import logging
from pathlib import Path
import time
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import LOG_LEVEL, LOG_FORMAT, LOG_FILES, LOG_DIR, UI_PORT
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
            
            # Check if primary model exists
            if not any(PRIMARY_MODEL in m for m in models):
                logging.warning(f"⚠️ Primary model '{PRIMARY_MODEL}' not found.")
                print(f"\n⚠️ Warning: Model '{PRIMARY_MODEL}' not found.")
                print("You can pull it later with: ollama pull qwen2.5:7b\n")
            
            return True
    except requests.exceptions.ConnectionError:
        logging.error("❌ Ollama is not running!")
        print("\n" + "="*60)
        print("❌ ERROR: Ollama is not running!")
        print("="*60)
        print("\nTo fix this:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Pull a model: ollama pull qwen2.5:7b")
        print("="*60 + "\n")
        
        # Offer to run in demo mode
        print("Would you like to run in DEMO MODE? (y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice == 'y':
                print("\n⚠️ Running in DEMO MODE - Limited functionality without Ollama")
                return True  # Continue in demo mode
        except:
            pass
        
        return False
    
    return True


def initialize_system():
    """Initialize all system components."""
    logging.info("🔧 Initializing SuperBrain JARVIS...")
    
    # Initialize memory system
    memory = MemoryManager()
    logging.info("✅ Memory system initialized")
    
    # Initialize model manager
    model_mgr = ModelManager()
    logging.info("✅ Model manager initialized")
    
    # Initialize orchestrator
    orchestrator = Orchestrator(memory=memory, model_manager=model_mgr)
    logging.info("✅ Orchestrator initialized")
    
    # Load user profile from memory
    profile = memory.get_user_profile()
    if profile:
        logging.info(f"✅ User profile loaded: {profile.get('name', 'Unknown')}")
    
    return orchestrator, memory, model_mgr


def open_browser(url):
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open(url)
    logging.info(f"🌐 Opening browser at {url}")


def launch_ui(orchestrator, memory, model_mgr):
    """Launch the Gradio UI application."""
    from ui.app import create_app
    
    app = create_app(orchestrator, memory, model_mgr)
    
    # Get server URL
    url = f"http://localhost:{UI_PORT}"
    
    # Open browser in separate thread
    browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
    browser_thread.start()
    
    print("\n" + "🧠" * 30)
    print("   SUPERBRAIN JARVIS - AI Operating System")
    print("   Glassmorphism UI Edition")
    print("🧠" * 30)
    print(f"\n🌐 Launching UI at: {url}")
    print("📋 Features:")
    print("   • 💬 Chat Interface with streaming responses")
    print("   • 🤖 Agent Dashboard with live status")
    print("   • 🧠 Memory Browser with search")
    print("   • ⚙️ Settings Panel")
    print("\n✨ Glassmorphism design with motion effects!")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Launch the app
    app.launch(
        server_name="0.0.0.0",
        server_port=UI_PORT,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("   🧠 SUPERBRAIN JARVIS - Standalone Launcher")
    print("="*60 + "\n")
    
    setup_logging()
    
    if not check_prerequisites():
        print("\n❌ Cannot start without Ollama. Please install and run Ollama first.")
        sys.exit(1)
    
    try:
        orchestrator, memory, model_mgr = initialize_system()
        launch_ui(orchestrator, memory, model_mgr)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down SuperBrain JARVIS...")
        logging.info("User requested shutdown")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print("\nCheck logs/Activity.log for details")
        sys.exit(1)
