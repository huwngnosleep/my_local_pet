# Ollama Setup Guide for Ubuntu Server
## Hardware Specs: Intel Pentium, 8GB RAM, No GPU

## Quick Start

### 1. Install Ollama on your Ubuntu Server

```bash
# Run this command on your Ubuntu Server
curl -fsSL https://ollama.com/install.sh | sh
```

This will:
- Download and install Ollama
- Set up the Ollama service
- Start it automatically

### 2. Verify Installation

```bash
# Check if Ollama service is running
systemctl status ollama

# Or simply check the version
ollama --version
```

### 3. Choose and Pull a Model

For your hardware (8GB RAM, Pentium CPU, no GPU), here are the best options:

#### Recommended Models:

**Option 1: Phi-3 Mini (RECOMMENDED)**
- Size: ~2.3GB
- Parameters: 3.8B
- Best balance of quality and speed for your hardware

```bash
ollama pull phi3:mini
```

**Option 2: Gemma 2B**
- Size: ~1.7GB
- Parameters: 2B
- Faster, still good quality

```bash
ollama pull gemma:2b
```

**Option 3: Llama 3.2 3B**
- Size: ~2GB
- Parameters: 3B
- Good general-purpose model

```bash
ollama pull llama3.2:3b
```

**Option 4: TinyLlama (Fastest)**
- Size: ~700MB
- Parameters: 1.1B
- Fastest but lower quality

```bash
ollama pull tinyllama
```

### 4. Test Your Model

#### Interactive Chat Mode:
```bash
# Replace 'phi3:mini' with your chosen model
ollama run phi3:mini
```

Type your questions and press Enter. Type `/bye` to exit.

#### Single Query:
```bash
echo "Why is the sky blue?" | ollama run phi3:mini
```

## Usage Examples

### Command Line Interface

```bash
# Start interactive chat
ollama run phi3:mini

# Ask a single question
ollama run phi3:mini "What is the capital of France?"

# List installed models
ollama list

# Remove a model
ollama rm model-name
```

### API Usage

Ollama runs a REST API on `http://localhost:11434` by default.

#### Generate Response (Streaming):
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Why is the sky blue?"
}'
```

#### Generate Response (Non-streaming):
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

#### Chat Endpoint (with conversation history):
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "phi3:mini",
  "messages": [
    {"role": "user", "content": "Hello! What can you help me with?"}
  ],
  "stream": false
}'
```

### Python Example

```python
import requests
import json

def chat_with_ollama(prompt, model="phi3:mini"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['response']
    else:
        return f"Error: {response.status_code}"

# Usage
answer = chat_with_ollama("What is machine learning?")
print(answer)
```

## Performance Optimization Tips

### 1. Set CPU Threads
```bash
# Limit CPU threads to avoid overload (adjust based on your CPU cores)
OLLAMA_NUM_THREADS=2 ollama run phi3:mini
```

### 2. Reduce Context Size
Smaller context windows use less RAM:
```bash
ollama run phi3:mini --ctx-size 2048
```

### 3. Monitor Resource Usage
```bash
# Monitor while running
htop

# Or
top
```

## Service Management

```bash
# Start Ollama service
sudo systemctl start ollama

# Stop Ollama service
sudo systemctl stop ollama

# Restart Ollama service
sudo systemctl restart ollama

# Enable auto-start on boot
sudo systemctl enable ollama

# Check service status
sudo systemctl status ollama

# View logs
sudo journalctl -u ollama -f
```

## Troubleshooting

### Issue: Out of Memory
- Use a smaller model (gemma:2b or tinyllama)
- Close other applications
- Reduce context size with `--ctx-size 1024`

### Issue: Slow Responses
- Expected on Pentium CPU (2-10 seconds per response)
- Use smaller models for faster inference
- Reduce context window size

### Issue: Service Won't Start
```bash
# Check logs
sudo journalctl -u ollama -n 50

# Manually start Ollama
ollama serve
```

### Issue: Model Download Fails
- Check internet connection
- Try downloading again
- Use a different model

## Expected Performance

With Intel Pentium and 8GB RAM:
- **Response time**: 2-10 seconds depending on model and query complexity
- **Memory usage**: 2-4GB for small models
- **Recommended model**: phi3:mini or gemma:2b

## Next Steps

1. Install Ollama on your Ubuntu Server
2. Pull phi3:mini or gemma:2b model
3. Test with interactive chat
4. Integrate via API if needed

## Additional Resources

- Ollama Documentation: https://github.com/ollama/ollama
- Model Library: https://ollama.com/library
- API Reference: https://github.com/ollama/ollama/blob/main/docs/api.md
