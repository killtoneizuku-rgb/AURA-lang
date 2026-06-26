# 🧠 SuperBrain JARVIS - Installation Guide

## Quick Start

### 1. Install Ollama (Required)

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

### 2. Start Ollama and Pull Models

```bash
# Start Ollama server
ollama serve

# In a new terminal, pull the primary model
ollama pull qwen2.5:7b

# Optional: Pull additional models for fallback
ollama pull llama3:8b
ollama pull mistral:7b
```

### 3. Install SuperBrain JARVIS

```bash
cd superbrain-ai

# Create virtual environment
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

### 4. Launch the UI

**Windows:**
```bash
run_ui.bat
```

**macOS/Linux:**
```bash
./run_ui.sh
```

**Or directly:**
```bash
python launch_ui.py
```

The UI will open automatically in your browser at `http://localhost:7860`

---

## Features Overview

### 💬 Chat Interface
- Real-time conversation with AI
- Markdown rendering for code and formatting
- Copy responses easily
- Clear and export conversations

### 🤖 Agent Dashboard
- Live status of all 5 agents
- Task completion tracking
- Visual indicators for agent activity

### 🧠 Memory Browser
- View stored memories
- Search through knowledge base
- Memory statistics

### ⚙️ Settings Panel
- Theme selection
- Model configuration
- Voice settings toggle
- Memory management

---

## Glassmorphism UI Features

✨ **Visual Effects:**
- Frosted glass panels with backdrop blur
- Animated aurora background
- Glowing buttons with hover effects
- Smooth transitions and animations
- Pulsing status indicators
- Sliding message animations

🎨 **Theme Colors:**
- Cyan (#00d4ff) - Primary accent
- Purple (#8e2de2) - Secondary accent
- Dark gradient background
- Semi-transparent glass panels

---

## Troubleshooting

### Ollama Not Running
```
Error: Ollama is not running!
Solution: Start with 'ollama serve'
```

### Model Not Found
```
Warning: Model 'qwen2.5:7b' not found
Solution: Run 'ollama pull qwen2.5:7b'
```

### Port Already in Use
```
Error: Address already in use
Solution: Change UI_PORT in config.py or kill the process using port 7860
```

### Dependencies Installation Fails
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Then reinstall
pip install -r requirements.txt --force-reinstall
```

---

## Command Line Mode

For a lightweight experience without the UI:

```bash
python main.py --cli
```

Available CLI commands:
- `/memory` - Browse memories
- `/agents` - Show agent status
- `/models` - List available models
- `/clear` - Clear conversation
- `/export` - Export conversation
- `/help` - Show help

---

## System Requirements

- **OS:** Windows 10+, macOS 10.15+, Linux
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 5GB free space
- **Python:** 3.9 or higher
- **Ollama:** Latest version

---

## First Steps After Installation

1. **Test the connection:**
   - Open the UI
   - Type "Hello, are you there?"
   - You should get a response

2. **Try a coding task:**
   - "Write a Python function to calculate Fibonacci numbers"

3. **Test web search:**
   - "Search for the latest news about AI"

4. **Test memory:**
   - "Remember that my favorite color is blue"
   - Later ask: "What's my favorite color?"

---

## Support

Check logs in the `logs/` directory:
- `activity.log` - General activity
- `agent_decisions.log` - Agent routing
- `errors.log` - Error messages
- `memory_operations.log` - Memory operations

For issues, check the logs and ensure Ollama is running properly.
