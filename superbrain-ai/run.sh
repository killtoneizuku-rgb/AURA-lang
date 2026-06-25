#!/bin/bash
# SuperBrain JARVIS Launcher (Linux/Mac)

echo "🧠 SuperBrain JARVIS - Starting..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama doesn't appear to be running."
    echo "   Start it with: ollama serve"
    echo ""
fi

# Run the application
echo "🚀 Launching SuperBrain JARVIS..."
python main.py "$@"
