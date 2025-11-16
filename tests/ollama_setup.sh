#!/bin/bash
# Ollama Setup Script for Ubuntu Server
# Hardware: Intel Pentium, 8GB RAM, No GPU

echo "================================"
echo "Ollama LLM Setup Script"
echo "================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo bash ollama_setup.sh"
    exit 1
fi

# Install Ollama
echo "Step 1: Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Ollama"
    exit 1
fi

echo ""
echo "Ollama installed successfully!"
echo ""

# Start Ollama service
echo "Step 2: Starting Ollama service..."
systemctl enable ollama
systemctl start ollama
sleep 5

# Check if service is running
if systemctl is-active --quiet ollama; then
    echo "Ollama service is running!"
else
    echo "WARNING: Ollama service may not be running properly"
    echo "Check status with: systemctl status ollama"
fi

echo ""
echo "Step 3: Pulling a lightweight model..."
echo "Recommended models for your hardware:"
echo "  1. phi3:mini (3.8B params) - Best balance"
echo "  2. gemma:2b (2B params) - Fast and efficient"
echo "  3. llama3.2:3b (3B params) - Good quality"
echo "  4. tinyllama (1.1B params) - Fastest, lower quality"
echo ""
read -p "Which model would you like to install? (1-4, default=1): " choice

case $choice in
    2)
        MODEL="gemma:2b"
        ;;
    3)
        MODEL="llama3.2:3b"
        ;;
    4)
        MODEL="tinyllama"
        ;;
    *)
        MODEL="phi3:mini"
        ;;
esac

echo "Pulling model: $MODEL"
echo "This may take several minutes depending on your internet connection..."
ollama pull $MODEL

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to pull model $MODEL"
    exit 1
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Model '$MODEL' is ready to use!"
echo ""
echo "Test it with:"
echo "  ollama run $MODEL"
echo ""
echo "Or use it via API:"
echo "  curl http://localhost:11434/api/generate -d '{"
echo "    \"model\": \"$MODEL\","
echo "    \"prompt\": \"Why is the sky blue?\","
echo "    \"stream\": false"
echo "  }'"
echo ""
echo "For interactive chat:"
echo "  ollama run $MODEL"
echo ""
echo "To list all models:"
echo "  ollama list"
echo ""
echo "To check service status:"
echo "  systemctl status ollama"
echo ""
