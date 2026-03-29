#!/bin/bash

echo "🧹 Setting up auto-clean environment..."

# Check uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing..."
    pip install uv
fi

# Create virtual environment
echo "→ Creating virtual environment..."
uv venv .venv

# Activate it
echo "→ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies from pyproject.toml
echo "→ Installing dependencies..."
uv pip install -e .

echo ""
echo "✅ Setup complete. Environment is ready."
echo "   To activate later: source .venv/bin/activate"
echo ""