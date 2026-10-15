#!/usr/bin/env bash
# Quick-start script for Unix / macOS

echo "==================================================="
echo "Starting Flappy Bird Hand Gesture Controller..."
echo "==================================================="

# Check for virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment (.venv)..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "Activating virtual environment (venv)..."
    source venv/bin/activate
fi

# Run Python backend
python3 MP.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[Notice] If packages are missing, run: pip install -r requirements.txt"
fi
