#!/bin/bash
# Quick Ollama Installation Script for Ubuntu Server
# Hardware: Intel Pentium, 8GB RAM, No GPU

set -e

echo "=================================="
echo "Ollama Quick Setup"
echo "=================================="
echo ""

# Install Ollama
echo "[1/3] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "[2/3] Starting Ollama service..."
sleep 3

# Check if service is running
if systemctl is-active --quiet ollama 2>/dev/null; then
    echo "✓ Ollama service is running"
else
    echo "Starting Ollama service..."
    sudo systemctl start ollama 2>/dev/null || ollama serve &
    sleep 3
fi

echo ""
echo "[3/3] Pulling recommended model (phi3:mini)..."
echo "This will download ~2.3GB and may take a few minutes..."
echo ""

ollama pull phi3:mini

echo ""
echo "=================================="
echo "✓ Setup Complete!"
echo "=================================="
echo ""
echo "Test your LLM with:"
echo "  ollama run phi3:mini"
echo ""
echo "Or try a quick test:"
echo "  echo 'Hello, who are you?' | ollama run phi3:mini"
echo ""
echo "For API access:"
echo "  curl http://localhost:11434/api/generate -d '{\"model\":\"phi3:mini\",\"prompt\":\"Hello\",\"stream\":false}'"
echo ""
echo "See OLLAMA_SETUP_GUIDE.md for more details!"
echo ""
