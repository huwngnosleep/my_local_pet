# Timing Feature

The chatbot now displays detailed timing information to help you understand performance and diagnose issues.

## What It Shows

### For Simple Queries (No Tools)
```
[Timing] Total: 8.45s
```

### For Web Search Queries (With Tools)
```
[Tool result retrieved in 1.23s]

[Timing] Initial: 12.34s | Tool: 1.23s | Final: 15.67s | Total: 29.24s
```

**Breakdown:**
- **Initial**: Time for model to decide to use web search
- **Tool**: Time to execute web search (DuckDuckGo)
- **Final**: Time for model to process search results and generate answer
- **Total**: Complete end-to-end time

## Why This Is Useful

### 1. Identify Bottlenecks
See which part takes longest:
- If **Initial** is slow: Model is thinking hard about the query
- If **Tool** is slow: Web search or network issues
- If **Final** is slow: Large context from search results (consider using `SEARCH_PROCESSING = "simple"`)

### 2. Debug Timeouts
If you get timeout errors, check which step:
```
[Timing] Initial: 115.23s | Tool: 1.23s | Final: TIMEOUT
```
This tells you to increase `TIMEOUT_TOOL_REQUEST` in start.py

### 3. Compare Methods
Test different search processing methods:
```bash
# Try extraction method
SEARCH_PROCESSING = "extraction"
[Timing] Initial: 12s | Tool: 0.8s | Final: 15s | Total: 28s

# Try simple method
SEARCH_PROCESSING = "simple"
[Timing] Initial: 12s | Tool: 0.5s | Final: 18s | Total: 31s
```

## Configuration

### Enable/Disable Globally

Edit `start.py` line 32:
```python
SHOW_TIMING = True   # Show timing (default)
SHOW_TIMING = False  # Hide timing
```

### Enable/Disable Per Query

In your code:
```python
# Show timing for this query
response = chat("Your question", show_timing=True)

# Hide timing for this query
response = chat("Your question", show_timing=False)

# Use global config
response = chat("Your question")  # Uses SHOW_TIMING setting
```

## Example Output

### Without Web Search
```
$ python start.py "Explain what Python is"

AI: Python is a high-level programming language...

[Timing] Total: 8.45s
```

### With Web Search
```
$ python start.py "What are the latest Python releases?"

[Using tool: web_search]
[Tool result retrieved in 1.23s]

AI: Based on the search results, Python 3.13 was recently released...

[Timing] Initial: 12.34s | Tool: 1.23s | Final: 15.67s | Total: 29.24s
```

## Performance Benchmarks

Typical timing on different hardware:

| Hardware          | Simple Query | Web Search Query |
|------------------|--------------|------------------|
| i5 + 16GB RAM    | 2-5s         | 8-15s            |
| Pentium + 8GB    | 5-10s        | 20-40s           |
| GPU (GTX 1650)   | 1-3s         | 5-12s            |

## Tips for Speed

1. **Use simpler search processing**:
   ```python
   SEARCH_PROCESSING = SearchProcessingMethod.SIMPLE
   ```

2. **Reduce search results**:
   Edit `web_search()` in start.py:
   ```python
   def web_search(query, max_results=2):  # Changed from 3
   ```

3. **Use faster model**:
   ```bash
   ollama pull gemma:2b  # Faster than phi3:mini
   ```
   Edit start.py:
   ```python
   MODEL_NAME = "gemma:2b"
   ```

4. **Disable tools for simple questions**:
   ```python
   response = chat("Hello!", use_tools=False)
   ```

## Testing

Run timing tests:
```bash
# Basic test
python tests/test_timing.py

# Full test including web search
python tests/test_timing.py --full
```

## Troubleshooting

### Slow "Initial" time
- Model is processing complex prompt with tool descriptions
- Try simpler query or disable tools

### Slow "Tool" time
- Web search is slow (network issues)
- Try reducing max_results

### Slow "Final" time
- Large search results context
- Use `SEARCH_PROCESSING = "simple"` or reduce max_results
- Increase `TIMEOUT_TOOL_REQUEST` if timing out

### No timing shown
- Check `SHOW_TIMING = True` in start.py
- Or use `show_timing=True` in chat() call
