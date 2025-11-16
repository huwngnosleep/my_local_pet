# Troubleshooting Ollama 404 Error

## What Does 404 Error Mean?

A 404 error when chatting with Ollama means the **model name doesn't exist** in your Ollama installation.

## Quick Fix

### Step 1: Check What Models You Have Installed

On your Ubuntu Server, run:
```bash
ollama list
```

This will show you all installed models. Example output:
```
NAME              ID              SIZE      MODIFIED
phi3:mini         abc123def       2.3 GB    2 days ago
gemma:2b          xyz789ghi       1.7 GB    1 day ago
```

### Step 2: Match the Model Name

The model name in your Python script (line 13) must **exactly match** a model from `ollama list`.

Common mismatches:
- Script says `phi3:mini` but you installed `phi3` ❌
- Script says `phi3` but you installed `phi3:mini` ❌
- Script says `llama3.2:3b` but you installed `llama3.2` ❌

### Step 3: Fix It (Choose ONE option)

**Option A: Pull the Model the Script Expects**
```bash
# If script uses phi3:mini, run:
ollama pull phi3:mini
```

**Option B: Update the Script to Match Your Model**

Edit `ollama_api_example.py` line 13:
```python
# Change this line to match your installed model
MODEL_NAME = "your-actual-model-name"  # e.g., "gemma:2b"
```

**Option C: Use the Updated Script (Already Fixed!)**

The script I just updated will:
1. Check what models you have
2. Automatically use the first available model if `phi3:mini` isn't found
3. Show a clear error message if the model is missing

## Common Issues and Solutions

### Issue 1: No Models Installed

**Symptom:**
```bash
ollama list
# Shows empty list or "No models found"
```

**Solution:**
```bash
# Pull a model first
ollama pull phi3:mini
# or
ollama pull gemma:2b
```

### Issue 2: Model Name Has Extra Characters

**Symptom:**
- You see `phi3:mini:latest` in `ollama list`
- Script uses `phi3:mini`

**Solution:**
Try using the full name:
```python
MODEL_NAME = "phi3:mini:latest"
```

Or try without the tag:
```python
MODEL_NAME = "phi3"
```

### Issue 3: Ollama Service Not Running

**Symptom:**
```
Cannot connect to Ollama
```

**Solution:**
```bash
# Check if Ollama is running
systemctl status ollama

# If not running, start it
sudo systemctl start ollama

# Or run manually
ollama serve
```

## Testing Your Setup

### Test 1: List Models via API
```bash
curl http://localhost:11434/api/tags
```

Should return JSON with your models.

### Test 2: Test a Model via API
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Hello",
  "stream": false
}'
```

If this returns 404, the model name is wrong.

### Test 3: Run Python Script
```bash
python3 ollama_api_example.py
```

The script will now:
- Show you all installed models
- Automatically pick an available model
- Give clear error messages

## Still Getting 404?

Run these diagnostic commands on your Ubuntu Server:

```bash
# 1. Check Ollama version
ollama --version

# 2. List all models with full details
ollama list

# 3. Try to run a model directly
ollama run phi3:mini "test"

# 4. Check API is responding
curl http://localhost:11434/api/tags | jq .

# 5. Check service logs
journalctl -u ollama -n 50
```

Send me the output and I can help diagnose further!

## Summary Checklist

- [ ] Ollama is installed and running (`systemctl status ollama`)
- [ ] At least one model is pulled (`ollama list`)
- [ ] Model name in script matches exactly (`ollama list` vs `MODEL_NAME`)
- [ ] Ollama API is accessible (`curl http://localhost:11434/api/tags`)
- [ ] Python script is using the updated version

## Quick Reference Commands

```bash
# See what models you have
ollama list

# Pull a new model
ollama pull phi3:mini

# Test a model
ollama run phi3:mini

# Check service
systemctl status ollama

# Restart service
sudo systemctl restart ollama
```
