# GTX 1650 Setup Guide for Ollama

## Your GPU Specs
- **Model:** NVIDIA GTX 1650
- **VRAM:** 4GB GDDR6
- **CUDA Cores:** 896
- **Expected Speed:** 5-10x faster than CPU!

## Installation Steps (Ubuntu Server)

### Step 1: Install NVIDIA Drivers

```bash
# Update package list
sudo apt update

# Check if NVIDIA GPU is detected
lspci | grep -i nvidia
# You should see your GTX 1650 listed

# Install recommended NVIDIA driver
sudo apt install nvidia-driver-535

# Alternatively, let Ubuntu choose the best driver
sudo ubuntu-drivers autoinstall
```

### Step 2: Install CUDA Toolkit (Optional but Recommended)

```bash
# Install CUDA toolkit for better performance
sudo apt install nvidia-cuda-toolkit

# Or install specific CUDA version
sudo apt install nvidia-cuda-toolkit-11-8
```

### Step 3: Reboot

```bash
sudo reboot
```

### Step 4: Verify GPU Installation

After reboot:

```bash
# Check NVIDIA driver is loaded
nvidia-smi
```

You should see output like:
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.x   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce GTX 1650  Off | 00000000:01:00.0 Off |                  N/A |
| 45%   30C    P8    2W /  75W |      0MiB /  4096MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### Step 5: Reinstall Ollama (to enable GPU support)

```bash
# Ollama will automatically detect GPU on installation
# If Ollama is already installed, restart the service
sudo systemctl restart ollama

# Or reinstall to ensure GPU support
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 6: Test GPU with Ollama

```bash
# Pull a model
ollama pull phi3:mini

# Run and test
ollama run phi3:mini "Write a haiku about speed"

# While it's running, in another terminal:
watch -n 1 nvidia-smi
# This shows real-time GPU usage
```

## Verifying GPU is Being Used

### Method 1: Check Ollama Logs
```bash
# Check Ollama is using GPU
journalctl -u ollama -f

# Look for messages like:
# "GPU detected: NVIDIA GeForce GTX 1650"
# "Using CUDA"
```

### Method 2: Monitor GPU Usage
```bash
# Open two terminals:

# Terminal 1: Run nvidia-smi in watch mode
watch -n 0.5 nvidia-smi

# Terminal 2: Ask a question
ollama run phi3:mini "Explain quantum computing"
```

You should see:
- GPU Utilization spike to 80-100%
- Memory usage increase (1-3GB for phi3:mini)
- Temperature increase

### Method 3: Speed Test
```bash
# Time a response
time echo "Write a 200 word essay about AI" | ollama run phi3:mini

# Should complete in 2-5 seconds with GPU
# vs 10-30 seconds on CPU
```

## Best Models for GTX 1650 (4GB VRAM)

### Super Fast (< 1 second/response)
```bash
ollama pull tinyllama           # 637MB - Lightning fast
ollama pull qwen2:1.5b          # 934MB - Very fast, good quality
```

### Fast (1-2 seconds/response) - RECOMMENDED
```bash
ollama pull gemma:2b            # 1.7GB - Best balance
ollama pull phi:2               # 1.7GB - Great for code
ollama pull phi3:mini           # 2.3GB - Best quality for size
```

### Medium (2-4 seconds/response)
```bash
ollama pull llama3.2:3b         # 2.0GB - Good all-rounder
ollama pull mistral:7b-instruct-q4_0  # ~3.8GB - Tight fit but works
```

## Troubleshooting

### GPU Not Detected by Ollama

**Check 1: Verify driver is loaded**
```bash
nvidia-smi
# If this fails, drivers aren't installed properly
```

**Check 2: Restart Ollama**
```bash
sudo systemctl restart ollama
```

**Check 3: Check Ollama logs**
```bash
journalctl -u ollama -n 50
```

### Out of Memory Errors

If you get CUDA out of memory errors:

**Solution 1: Use smaller models**
```bash
# Switch from phi3:mini to gemma:2b
ollama pull gemma:2b
```

**Solution 2: Use more quantized models**
```bash
# Use 4-bit quantization instead of 8-bit
ollama pull mistral:7b-q4_0
```

**Solution 3: Close other GPU applications**
```bash
# Check what's using GPU
nvidia-smi

# Kill GPU processes
sudo fuser -v /dev/nvidia*
```

### Slow Performance (not using GPU)

**Check if GPU is being used:**
```bash
# Run this while asking Ollama a question
nvidia-smi dmon

# You should see activity in the GPU columns
```

**Force GPU usage:**
```bash
# Set environment variable
export CUDA_VISIBLE_DEVICES=0
sudo systemctl restart ollama
```

## Performance Benchmarks (Expected)

### Phi3:mini (3.8B) - RECOMMENDED
- **CPU (Pentium):** 8-12 seconds per response
- **GPU (GTX 1650):** 1.5-2.5 seconds per response
- **Speedup:** ~5-6x faster

### Gemma:2b (2B)
- **CPU (Pentium):** 5-8 seconds per response
- **GPU (GTX 1650):** 0.7-1.5 seconds per response
- **Speedup:** ~6-8x faster

### TinyLlama (1.1B)
- **CPU (Pentium):** 3-5 seconds per response
- **GPU (GTX 1650):** 0.3-0.8 seconds per response
- **Speedup:** ~8-10x faster

## Monitoring GPU

### Real-time Monitoring
```bash
# Install monitoring tools
sudo apt install nvtop

# Run nvtop (better than nvidia-smi)
nvtop

# Or use watch with nvidia-smi
watch -n 0.5 nvidia-smi
```

### Check Temperature
```bash
# Make sure GPU isn't overheating
nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader

# Should stay under 80°C during inference
```

## Power Consumption

GTX 1650 TDP: 75W
- Idle: ~10W
- Running LLM: 40-60W
- Much more efficient than high-end GPUs!

## Tips for Best Performance

1. **Use the right model size**
   - Don't try to run 7B+ models on 4GB VRAM
   - Stick with 3B and smaller for best experience

2. **Monitor VRAM usage**
   ```bash
   watch -n 1 "nvidia-smi --query-gpu=memory.used,memory.total --format=csv"
   ```

3. **Keep drivers updated**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

4. **Clean GPU (physical)**
   - Dust buildup reduces cooling
   - Check temperatures regularly

5. **Use 4-bit quantization for larger models**
   - Saves VRAM
   - Minimal quality loss

## Next Steps

After GPU setup:
1. Install drivers (Step 1-3)
2. Verify with `nvidia-smi` (Step 4)
3. Restart Ollama (Step 5)
4. Test with `phi3:mini` (Step 6)
5. Try the Python script with GPU speedup!

Your responses should be **5-10x faster**! 🚀
