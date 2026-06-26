# 🚀 Quick Start Guide

## 1-Minute Setup (if you have Ollama)

```bash
cd superbrain-ai
pip install -r requirements.txt
python launch_ui.py
```

## First-Time Setup (5 minutes)

### Step 1: Install Ollama
Visit https://ollama.ai and download for your OS

### Step 2: Pull AI Model
```bash
ollama pull qwen2.5:7b
```

### Step 3: Install SuperBrain
```bash
cd superbrain-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Launch UI
```bash
python launch_ui.py
```

Your browser will open to `http://localhost:7860`

---

## Try These Commands

**Chat:**
- "Hello! What can you do?"
- "Write a Python function to sort a list"
- "Search for latest AI news"

**System:**
- "List files in my Documents folder"
- "Create a file called test.txt with hello world"

**Memory:**
- "Remember that I work as a developer"
- "What do you remember about me?"

---

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift+Enter` - New line
- `Ctrl+K` - Focus search (coming soon)

---

## Need Help?

- Full docs: `README.md`
- Installation: `INSTALL.md`
- Logs: Check `logs/` folder
