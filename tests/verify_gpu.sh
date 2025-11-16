#!/bin/bash
# GPU Verification Script for Ollama
# Run after installing GPU: bash verify_gpu.sh

echo "========================================"
echo "GPU Setup Verification"
echo "========================================"
echo ""

# Test 1: Check NVIDIA driver
echo "[Test 1/5] Checking NVIDIA driver..."
if command -v nvidia-smi &> /dev/null; then
    echo "✓ nvidia-smi found"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo ""
else
    echo "✗ nvidia-smi not found!"
    echo "  Install drivers: sudo ubuntu-drivers autoinstall"
    exit 1
fi

# Test 2: Check GPU memory
echo "[Test 2/5] Checking GPU memory..."
VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
if [ "$VRAM" -ge 3000 ]; then
    echo "✓ GPU has ${VRAM}MB VRAM"
else
    echo "⚠ GPU only has ${VRAM}MB VRAM"
    echo "  This might be too small for some models"
fi
echo ""

# Test 3: Check Ollama is installed
echo "[Test 3/5] Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    ollama --version
else
    echo "✗ Ollama not found!"
    echo "  Install: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi
echo ""

# Test 4: Check if any models are installed
echo "[Test 4/5] Checking installed models..."
MODELS=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
if [ "$MODELS" -gt 0 ]; then
    echo "✓ Found $MODELS model(s):"
    ollama list
else
    echo "⚠ No models installed"
    echo "  Install a model: ollama pull phi3:mini"
fi
echo ""

# Test 5: Speed test (if model available)
echo "[Test 5/5] Performance test..."
FIRST_MODEL=$(ollama list 2>/dev/null | tail -n +2 | head -1 | awk '{print $1}')

if [ ! -z "$FIRST_MODEL" ]; then
    echo "Testing with model: $FIRST_MODEL"
    echo "Asking a simple question..."
    echo ""

    # Run speed test
    START=$(date +%s.%N)
    RESPONSE=$(echo "Say hello in one sentence" | ollama run $FIRST_MODEL 2>/dev/null)
    END=$(date +%s.%N)

    # Calculate time
    ELAPSED=$(echo "$END - $START" | bc)

    echo "Response: $RESPONSE"
    echo ""
    echo "⏱ Time taken: ${ELAPSED} seconds"
    echo ""

    # Evaluate performance
    if (( $(echo "$ELAPSED < 2" | bc -l) )); then
        echo "✓ Excellent! GPU is working great! 🚀"
    elif (( $(echo "$ELAPSED < 5" | bc -l) )); then
        echo "✓ Good! GPU seems to be working."
    elif (( $(echo "$ELAPSED < 10" | bc -l) )); then
        echo "⚠ Slower than expected. GPU might not be utilized."
        echo "  Check GPU usage: nvidia-smi"
    else
        echo "✗ Very slow! GPU may not be working."
        echo "  Try: sudo systemctl restart ollama"
    fi
else
    echo "⚠ Skipping performance test (no models installed)"
    echo "  Install a model: ollama pull phi3:mini"
fi

echo ""
echo "========================================"
echo "Verification Complete!"
echo "========================================"
echo ""

# GPU monitoring command
echo "To monitor GPU in real-time:"
echo "  watch -n 1 nvidia-smi"
echo ""
echo "To test with your Python script:"
echo "  python3 ollama_api_example.py"
echo ""
