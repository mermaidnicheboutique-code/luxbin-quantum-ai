#!/bin/bash
# LUXBIN AI Organism Launcher
# Runs your AI-powered organism with Claude + GPT + Grok

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  LUXBIN AI ORGANISM - Triple AI Power                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /Users/nicholechristie/luxbin-chain/python-implementation

# Install dependencies
echo "📦 Installing AI dependencies..."
pip3 install -q anthropic openai 2>/dev/null

echo ""
echo "🚀 Launching AI Organism..."
echo ""

# Run the AI CLI
python3 ai_organism_cli.py

echo ""
echo "════════════════════════════════════════════════════════════"
echo "AI Organism session ended"
echo "════════════════════════════════════════════════════════════"
