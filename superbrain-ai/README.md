# 🧠 SuperBrain ar0x - Your Personal AI Operating System

<div align="center">

![SuperBrain JARVIS](https://img.shields.io/badge/SuperBrain-JARVIS-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange?style=for-the-badge&logo=ollama)

**A fully autonomous, locally-run multi-agent AI assistant with beautiful animated glassmorphism UI**

🚀 **Zero API Keys** • **100% Local** • **Multi-Agent** • **Beautiful UI** • **Voice Ready**

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [UI Guide](#-ui-guide)
- [Commands](#-commands)
- [Agents](#-agents)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

---

## 🎯 Overview

**SuperBrain JARVIS** is a production-grade, fully autonomous personal AI assistant that runs entirely on your local machine. It uses free local LLM models via Ollama (Qwen2.5, Llama3, DeepSeek, Mistral) - no OpenAI, no paid APIs, no cloud dependencies.

### What Makes It Special?

✨ **Beautiful Animated Glassmorphism UI** - Smooth animations, frosted glass effects, particle backgrounds, and fluid transitions

🧠 **Multi-Agent Architecture** - 5 specialized agents working together like a team of experts

💾 **Persistent Memory** - Vector database + SQLite for long-term knowledge retention

🔒 **100% Private** - Everything runs locally on your machine

🎤 **Voice Ready** - Built-in speech-to-text and text-to-speech support

⚡ **Autonomous Execution** - Can plan, code, search, and execute tasks independently

---

## ✨ Features

### 🎨 Beautiful Animated UI

- **Glassmorphism Design** - Frosted glass panels with blur effects
- **Smooth Animations** - Fade-ins, slide-transitions, hover effects
- **Particle Background** - Floating particles with parallax motion
- **Live Agent Dashboard** - Real-time visualization of agent activities
- **Typing Indicators** - Animated dots while AI is thinking
- **Message Animations** - Messages slide in with elastic bounce
- **Theme Support** - Dark JARVIS, Light Clean, Cyberpunk themes
- **Responsive Layout** - Adapts to any screen size

### 🧠 Multi-Agent System

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| 🧠 **Planner** | Task decomposition | Breaks complex tasks into steps, dependency resolution |
| 👨‍💻 **Coder** | Code generation | Write, execute, debug Python/code |
| ⚙️ **System** | OS operations | File management, shell commands, process control |
| 🌐 **Web** | Internet access | Search, scrape, summarize web content |
| 📂 **Memory** | Knowledge base | Store, retrieve, summarize, forget |

### 💾 Advanced Memory

- **Vector Database** (ChromaDB) - Semantic search across all knowledge
- **Embeddings** (all-MiniLM-L6-v2) - Local embedding generation
- **SQLite Storage** - Structured conversation logs and user profile
- **Auto-Consolidation** - Automatically summarizes old conversations
- **Smart Retrieval** - Context-aware memory recall

### 🛠️ Powerful Tools

- ✅ Python sandbox runner with timeout protection
- ✅ Safe shell command execution with whitelist
- ✅ File CRUD operations (read/write/create/delete/search)
- ✅ Web search via DuckDuckGo (no API key)
- ✅ Web scraping with BeautifulSoup
- ✅ Browser automation with Playwright
- ✅ Screenshot capture
- ✅ Clipboard read/write
- ✅ Desktop notifications
- ✅ Calendar/timer/alarm management

### 🔒 Safety First

- Blocked dangerous commands (`rm -rf /`, `format`, etc.)
- Path validation (only allowed directories)
- Execution timeouts (prevent hanging)
- Command whitelisting
- Sandboxed code execution

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (UI)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │   Chat   │ │Dashboard │ │ Memory   │ │ Settings │       │
│  │  Panel   │ │  Panel   │ │  Panel   │ │  Panel   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR (Brain)                       │
│  Intent Classification → Task Planning → Agent Routing      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LLM CORE (Ollama)                         │
│  qwen2.5:7b → llama3:8b → mistral:7b → deepseek-coder       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                               │
│  Planner │ Coder │ System │ Web │ Memory                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    TOOL LAYER                                │
│  Python │ Shell │ Files │ Web │ Browser │ Clipboard │ ...   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  MEMORY LAYER                                │
│  ChromaDB (Vector) │ SQLite (Structured) │ Embeddings       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running

### Step 1: Install Ollama

**Windows:**
```bash
# Download from https://ollama.ai/download
# Run the installer
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Start Ollama & Pull Models

```bash
# Start Ollama server
ollama serve

# In a new terminal, pull the primary model
ollama pull qwen2.5:7b

# Optional: Pull fallback models
ollama pull llama3:8b
ollama pull mistral:7b
ollama pull deepseek-coder:6.7b

# Optional: Pull embedding model (runs automatically via sentence-transformers)
# No need to pull - it's downloaded automatically by the code
```

### Step 3: Clone & Install SuperBrain

```bash
# Navigate to the project directory
cd superbrain-ai

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for web automation)
playwright install
```

### Step 4: Verify Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# You should see a JSON response with available models
```

---

## 🚀 Quick Start

### Option 1: Launch with UI (Recommended)

```bash
# Windows
run.bat

# macOS/Linux
chmod +x run.sh
./run.sh

# Or directly
python main.py
```

This launches the beautiful animated glassmorphism UI in your browser at `http://localhost:7860`

### Option 2: CLI Mode

```bash
python main.py --cli
```

You'll see:
```
🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠
   SUPERBRAIN JARVIS — AI Operating System
   Type 'exit' to quit, 'help' for commands
🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠🧠

👤 You: 
```

### Example Interactions

**Simple Question:**
```
👤 You: What is quantum computing?

🧠 Thinking...
🤖 JARVIS: Quantum computing is a type of computation that harnesses quantum 
mechanical phenomena such as superposition and entanglement. Unlike classical 
computers that use bits (0 or 1), quantum computers use quantum bits or 
"qubits" which can exist in multiple states simultaneously...
```

**Complex Task:**
```
👤 You: Create a Python script that downloads weather data and saves it to a file

🧠 Thinking...
[Planner Agent decomposes task into 5 steps]
[Coder Agent writes the code]
[System Agent creates the file]
🤖 JARVIS: ✅ Done! I've created `weather_scraper.py` in your Documents folder. 
The script fetches weather data from a public API and saves it to weather_data.json.
Would you like me to run it now?
```

**Web Search:**
```
👤 You: What are the latest news about AI breakthroughs?

🧠 Thinking...
[Web Agent searches DuckDuckGo]
[Web Agent scrapes top 5 results]
[Memory Agent stores the information]
🤖 JARVIS: Here are the top 5 recent AI breakthroughs:
1. New language model achieves 95% accuracy on medical diagnosis...
2. Researchers develop self-improving AI system...
[...with sources and links]
```

---

## 🎨 UI Guide

### The Animated Glassmorphism Interface

When you launch `python main.py`, you'll see a stunning UI with:

#### 🌊 Particle Background Animation
- Hundreds of floating particles drift across the screen
- Parallax effect as you move your mouse
- Soft glow and color transitions
- Configurable speed and density

#### 🪟 Glass Panels
- **Frosted glass effect** with backdrop blur
- **Semi-transparent backgrounds** that adapt to theme
- **Subtle borders** with gradient glow
- **Smooth hover animations** that lift panels

#### 💬 Chat Interface
- **Message bubbles** slide in with elastic bounce
- **Typing indicator** with animated bouncing dots
- **Markdown rendering** for code blocks, tables, lists
- **Auto-scroll** with smooth easing
- **Copy button** on code blocks with feedback animation

#### 📊 Agent Dashboard
- **Live activity indicators** pulsing in real-time
- **Agent status cards** with color-coded states:
  - 🟢 Idle
  - 🔵 Thinking
  - 🟡 Working
  - 🟣 Executing
  - 🔴 Error
- **Progress bars** animate smoothly during tasks
- **Task history** scrolls with fade transitions

#### 🧠 Memory Browser
- **Searchable memory cards** with flip animations
- **Vector similarity visualization**
- **Timeline view** with smooth scrolling
- **Export buttons** with ripple effects

#### ⚙️ Settings Panel
- **Toggle switches** with smooth slide animation
- **Sliders** with glow on interaction
- **Dropdown menus** with fade-in items
- **Theme switcher** with instant preview

### Theme Customization

Access the Settings panel (gear icon) to switch themes:

1. **Dark JARVIS** (Default)
   - Deep blue-black background
   - Cyan accent colors
   - Holographic glows
   - Futuristic feel

2. **Light Clean**
   - White/light gray background
   - Blue accent colors
   - Minimal shadows
   - Professional look

3. **Cyberpunk**
   - Neon purple/pink background
   - Bright yellow/cyan accents
   - Glitch effects
   - Edgy aesthetic

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Send message |
| `Ctrl+K` | Focus search |
| `Ctrl+,` | Open settings |
| `Esc` | Close panels |
| `Ctrl+Shift+M` | Toggle memory panel |
| `Ctrl+Shift+A` | Toggle agent dashboard |
| `F11` | Fullscreen |

---

## 📋 Commands

### Slash Commands (CLI & UI)

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/memory` | Browse your memory/knowledge base |
| `/agents` | Show agent status and activity |
| `/models` | List available LLM models |
| `/clear` | Clear conversation history |
| `/export` | Export conversation to file |
| `/profile` | View/edit your user profile |
| `/voice` | Toggle voice input mode |
| `/theme <name>` | Change UI theme |
| `/config` | View current configuration |

### Voice Commands (if enabled)

Say **"Jarvis"** to wake, then:
- "What's the weather?"
- "Create a new file called test.py"
- "Search for Python tutorials"
- "Remind me to call John at 3 PM"
- "What did we talk about yesterday?"

---

## 🤖 Agents

### How Agents Work

When you give a task, the **Orchestrator**:
1. **Classifies intent** (What do you want?)
2. **Plans steps** (How to achieve it?)
3. **Routes to agents** (Who does what?)
4. **Executes in parallel** (When possible)
5. **Combines results** (Final answer)

### Agent Details

#### 🧠 Planner Agent
**Purpose:** Break down complex tasks into manageable steps

**Example:**
```
Input: "Build a website that shows weather"
Output: 
  Step 1: Research weather APIs
  Step 2: Design HTML structure
  Step 3: Write CSS styling
  Step 4: Implement JavaScript fetch logic
  Step 5: Test and deploy
```

#### 👨‍💻 Coder Agent
**Purpose:** Write, execute, and debug code

**Capabilities:**
- Generate Python, JavaScript, HTML/CSS
- Execute code in sandbox
- Debug errors iteratively
- Optimize performance
- Add comments and documentation

#### ⚙️ System Agent
**Purpose:** Interact with your operating system

**Capabilities:**
- Create/read/update/delete files
- Navigate directories
- Run safe shell commands
- Manage processes
- Take screenshots
- Send notifications

#### 🌐 Web Agent
**Purpose:** Access and process web information

**Capabilities:**
- Search DuckDuckGo (no API key)
- Scrape websites
- Summarize articles
- Extract structured data
- Follow links recursively

#### 📂 Memory Agent
**Purpose:** Store and retrieve knowledge

**Capabilities:**
- Save conversations to vector DB
- Retrieve relevant memories
- Summarize old discussions
- Build user profile
- Forget outdated info

---

## ⚙️ Configuration

### Edit `config.py`

All settings are in one place:

```python
# ─── LLM SETTINGS ───
PRIMARY_MODEL = "qwen2.5:7b"  # Change to any Ollama model
FALLBACK_MODELS = ["llama3:8b", "mistral:7b"]
TEMPERATURE = 0.7              # Higher = more creative
MAX_TOKENS = 4096              # Max response length

# ─── SAFETY SETTINGS ───
BLOCKED_SHELL_COMMANDS = [...]  # Add dangerous commands
ALLOWED_SHELL_PATHS = [...]     # Restrict file access
CODE_EXECUTION_TIMEOUT = 30     # Seconds before kill

# ─── MEMORY SETTINGS ───
MEMORY_RETRIEVAL_TOP_K = 5      # How many memories to recall
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ─── UI SETTINGS ───
UI_THEME = "dark_jarvis"        # dark_jarvis, light_clean, cyberpunk
UI_PORT = 7860                  # Change port if needed
UI_TITLE = "🧠 SuperBrain JARVIS"

# ─── VOICE SETTINGS ───
VOICE_ENABLED = False           # Set True to enable
WAKE_WORD = "jarvis"
TTS_VOICE_RATE = 180            # Words per minute
```

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
OLLAMA_BASE_URL=http://localhost:11434
UI_THEME=dark_jarvis
VOICE_ENABLED=false
LOG_LEVEL=INFO
```

---

## 🔧 Troubleshooting

### ❌ "Ollama is not running"

**Solution:**
```bash
# Start Ollama
ollama serve

# Keep it running in a separate terminal
```

### ❌ "Model not found"

**Solution:**
```bash
# Pull the required model
ollama pull qwen2.5:7b

# Or change PRIMARY_MODEL in config.py to a model you have
```

### ❌ "ModuleNotFoundError: No module named 'chromadb'"

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### ❌ "Playwright browsers not installed"

**Solution:**
```bash
playwright install
```

### ❌ UI doesn't load / Port already in use

**Solution:**
```bash
# Change port in config.py
UI_PORT = 7861  # Use a different port

# Or kill the process using port 7860
# Windows:
netstat -ano | findstr :7860
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:7860 | xargs kill -9
```

### ❌ Slow performance

**Solutions:**
1. Use a smaller model: `ollama pull qwen2.5:3b`
2. Reduce MAX_TOKENS in config.py
3. Close other applications
4. Ensure you have enough RAM (8GB+ recommended)

### ❌ Voice not working

**Solution:**
```bash
# Install system dependencies
# Windows: Visual C++ Redistributable
# macOS: brew install portaudio
# Linux: sudo apt-get install python3-pyaudio

# Then reinstall voice packages
pip install vosk sounddevice pyttsx3 --force-reinstall
```

---

## ❓ FAQ

### Q: Is this really 100% free?
**A:** Yes! No API keys, no subscriptions, no cloud costs. Everything runs locally on your hardware.

### Q: What models can I use?
**A:** Any Ollama model! Recommended: qwen2.5:7b, llama3:8b, mistral:7b, deepseek-coder:6.7b. Change in `config.py`.

### Q: Does it work offline?
**A:** Yes! Once models are downloaded, everything works offline except web search/scraping features.

### Q: Can I customize the agents?
**A:** Absolutely! Edit agent files in `/agents/` to modify behavior, add tools, or create new agents.

### Q: How do I add new tools?
**A:** Create a new file in `/tools/`, inherit from base tool class, register in tool layer. See existing tools for examples.

### Q: Is my data private?
**A:** Yes! All data stays on your machine. Memory is stored locally in `/memory/storage/`.

### Q: Can I run this on a Raspberry Pi?
**A:** Technically yes, but performance will be slow. Recommended: 8GB+ RAM, modern CPU/GPU.

### Q: How do I update?
**A:** Pull latest changes from repo, run `pip install -r requirements.txt --upgrade`, restart.

### Q: Can I use this commercially?
**A:** Yes! MIT license allows commercial use. Just don't claim you built it from scratch 😊

---

## 🛠️ Development

### Project Structure

```
superbrain-ai/
├── main.py                  # Entry point
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── run.sh / run.bat         # Launchers
│
├── core/                    # Core AI logic
│   ├── brain.py             # LLM connector
│   ├── orchestrator.py      # Master controller
│   ├── intent_classifier.py # Intent detection
│   └── ...
│
├── agents/                  # Agent implementations
│   ├── base_agent.py        # Abstract base
│   ├── planner_agent.py     # Task planning
│   └── ...
│
├── tools/                   # Tool implementations
│   ├── python_runner.py     # Code execution
│   ├── shell_tool.py        # Shell commands
│   └── ...
│
├── memory/                  # Memory systems
│   ├── vector_db.py         # ChromaDB interface
│   ├── embeddings.py        # Embedding generation
│   └── ...
│
├── ui/                      # User interface
│   ├── app.py               # Main Gradio app
│   ├── chat_panel.py        # Chat component
│   ├── dashboard_panel.py   # Agent dashboard
│   └── themes/              # CSS themes
│
└── tests/                   # Unit tests
    ├── test_brain.py
    └── ...
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Adding a New Agent

1. Create `agents/my_agent.py`:
```python
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent", "Description")
    
    def execute(self, task, context):
        # Your logic here
        return result
```

2. Register in `agents/agent_registry.py`
3. Update `core/orchestrator.py` to route to your agent

### Building Custom UI

Edit `ui/app.py` to customize the Gradio interface. Themes are in `ui/themes/`.

---

## 📄 License

MIT License - Feel free to use, modify, and distribute!

---

## 🙏 Acknowledgments

- **Ollama** - For making local LLMs accessible
- **Qwen, Llama, Mistral** - Amazing open-source models
- **ChromaDB** - Simple vector database
- **Gradio** - Beautiful UI framework
- **Community** - All open-source contributors

---

## 📞 Support

- **Issues:** Open an issue on GitHub
- **Discussions:** Join our community forum
- **Documentation:** Check the `/docs` folder

---

<div align="center">

**Built with ❤️ by the ar0x**

*Your AI, Your Data, Your Control*

</div>
