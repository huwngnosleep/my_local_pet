#!/bin/bash
# GTX 1650 GPU Setup Script for Ollama
# Run with: sudo bash setup_gpu.sh

set -e

echo "========================================"
echo "GTX 1650 GPU Setup for Ollama"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo bash setup_gpu.sh"
    exit 1
fi

# Step 1: Check if NVIDIA GPU is detected
echo "[Step 1/5] Checking for NVIDIA GPU..."
if lspci | grep -i nvidia | grep -i "GTX 1650" > /dev/null; then
    echo "✓ GTX 1650 detected!"
else
    echo "⚠ GTX 1650 not found. Make sure it's properly installed."
    lspci | grep -i nvidia
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Install NVIDIA drivers
echo ""
echo "[Step 2/5] Installing NVIDIA drivers..."
apt update
apt install -y ubuntu-drivers-common

# Let Ubuntu choose the best driver
echo "Installing recommended NVIDIA driver..."
ubuntu-drivers autoinstall

# Step 3: Install CUDA toolkit (optional)
echo ""
echo "[Step 3/5] Installing CUDA toolkit..."
read -p "Install CUDA toolkit? (Recommended for best performance) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    apt install -y nvidia-cuda-toolkit
    echo "✓ CUDA toolkit installed"
else
    echo "Skipping CUDA toolkit installation"
fi

# Step 4: Check if Ollama is installed
echo ""
echo "[Step 4/5] Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    echo "Restarting Ollama service to detect GPU..."
    systemctl restart ollama
else
    echo "Ollama not found. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "⚠ IMPORTANT: You must REBOOT for changes to take effect!"
echo ""
echo "After reboot, verify GPU is working:"
echo "  1. Run: nvidia-smi"
echo "  2. Pull a model: ollama pull phi3:mini"
echo "  3. Test: ollama run phi3:mini"
echo "  4. Monitor GPU: watch -n 1 nvidia-smi"
echo ""
read -p "Reboot now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebooting in 5 seconds..."
    sleep 5
    reboot
else
    echo "Please reboot manually: sudo reboot"
fi
