# Documentation Index

## 🚀 Quick Start

- **[Audio Chatbot Quick Start](./AUDIO_QUICK_START.md)** - **NEW!** Voice-interactive chatbot (microphone input)
- **[Streaming Update Summary](./STREAMING_UPDATE_SUMMARY.md)** - Complete overview of streaming features
- **[Streaming Quick Start](./streaming_quick_start.md)** - Get started with text streaming in 5 minutes

## Feature Documentation

### Core Features

1. **[Audio Chatbot](./audio_chatbot.md)** - **NEW!**
   - Voice-interactive chatbot using microphone
   - Speech-to-text conversion (Google API)
   - Hands-free operation
   - Streaming text responses
   - Full tool integration (web search)
   - Accessibility features

2. **[ChatBot Streaming](./chatbot_streaming.md)** - **RECOMMENDED**
   - Complete chatbot streaming guide
   - Interactive chat with real-time responses
   - Tool integration (web search + streaming)
   - Configuration and best practices
   - Examples and troubleshooting

3. **[Streaming Responses](./streaming_responses.md)**
   - OllamaClient streaming implementation
   - Real-time token-by-token streaming
   - Two streaming modes (real-time and buffered)
   - Performance comparisons
   - Advanced usage patterns

4. **[HTTP Connection Pooling](./http_connection_pooling.md)**
   - Connection reuse for 10x performance boost
   - Automatic retry logic
   - Resource management
   - Configuration details

### Changelog

- **[Streaming & Connection Pooling Updates](./CHANGELOG_streaming.md)**
   - What's new
   - API changes
   - Migration guide
   - Performance metrics

## Examples

All examples are in `tests/python/`:

### Test Scripts

```bash
# Run comprehensive streaming tests
python tests/python/test_streaming.py

# Interactive streaming demo
python tests/python/interactive_streaming_demo.py
```

### Code Examples

#### Real-time Streaming

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

for chunk in client.generate_stream("Tell me a story"):
    print(chunk.text, end='', flush=True)
    if chunk.done:
        break
```

#### Interactive Chat

```python
with OllamaClient(config.ollama) as client:
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        print("Assistant: ", end='', flush=True)
        for chunk in client.generate_stream(user_input):
            print(chunk.text, end='', flush=True)
            if chunk.done:
                print()
                break
```

## Architecture

### Module Overview

```
ollama_client.py
├── ModelResponse      # Complete response dataclass
├── StreamChunk        # Streaming chunk dataclass
├── ModelInfo          # Model metadata
└── OllamaClient       # Main client class
    ├── generate()           # Non-streaming or buffered streaming
    ├── generate_stream()    # Real-time streaming generator
    ├── health_check()       # Connection test
    ├── list_models()        # Available models
    ├── get_model_names()    # Model names only
    ├── model_exists()       # Check model availability
    ├── test_connection()    # Detailed connection test
    ├── close()              # Resource cleanup
    ├── __enter__()          # Context manager entry
    └── __exit__()           # Context manager exit
```

### Key Features

- ✅ **Streaming responses** (real-time and buffered)
- ✅ **Connection pooling** (10x performance improvement)
- ✅ **Automatic retries** (transient failure handling)
- ✅ **Context manager** (automatic resource cleanup)
- ✅ **Type-safe** (full type hints with dataclasses)
- ✅ **Error handling** (structured error responses)
- ✅ **Backward compatible** (existing code works unchanged)

## Performance

### Connection Pooling

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| First request | 100ms | 100ms | - |
| Subsequent requests | 100ms | 10ms | **10x faster** |
| 10 requests | 1000ms | 190ms | **5x faster** |

### Streaming

| Metric | Non-Streaming | Streaming |
|--------|---------------|-----------|
| Time to first token | Wait for complete response | ~200ms |
| User experience | Wait and see all at once | See tokens as generated |
| Interactivity | None | Full real-time display |

## Best Practices

### ✅ Do

1. **Use context manager** for automatic cleanup:
   ```python
   with OllamaClient(config.ollama) as client:
       response = client.generate("Hello")
   ```

2. **Use streaming** for interactive applications:
   ```python
   for chunk in client.generate_stream(prompt):
       print(chunk.text, end='', flush=True)
       if chunk.done:
           break
   ```

3. **Check for errors** in streaming:
   ```python
   for chunk in client.generate_stream(prompt):
       if chunk.error:
           print(f"Error: {chunk.error}")
           break
   ```

4. **Reuse client instances** for connection pooling benefits:
   ```python
   with OllamaClient(config.ollama) as client:
       for question in questions:
           response = client.generate(question)
   ```

### ❌ Don't

1. **Don't create new clients** for each request:
   ```python
   # Bad - defeats connection pooling
   for question in questions:
       client = OllamaClient(config.ollama)
       response = client.generate(question)
   ```

2. **Don't forget flush=True** when streaming:
   ```python
   # Bad - output will be buffered
   print(chunk.text, end='')

   # Good - immediate display
   print(chunk.text, end='', flush=True)
   ```

3. **Don't ignore the done flag**:
   ```python
   # Bad - infinite loop risk
   for chunk in client.generate_stream(prompt):
       print(chunk.text, end='', flush=True)

   # Good - proper termination
   for chunk in client.generate_stream(prompt):
       print(chunk.text, end='', flush=True)
       if chunk.done:
           break
   ```

## Troubleshooting

### Connection Issues

```python
# Test connection
with OllamaClient(config.ollama) as client:
    success, message = client.test_connection()
    print(message)
```

### Timeout Issues

```python
# Increase timeout
config = Config.from_defaults()
config.ollama.timeout_first_request = 120  # 2 minutes
client = OllamaClient(config.ollama)
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull phi3:mini
```

## API Reference

### OllamaClient Methods

#### `generate(prompt, model=None, stream=False, timeout=None, options=None)`

Generate response (streaming or non-streaming).

**Parameters:**
- `prompt` (str): Input prompt
- `model` (str, optional): Model name (uses config default if None)
- `stream` (bool): Enable buffered streaming (default: False)
- `timeout` (int, optional): Timeout in seconds
- `options` (dict, optional): Generation options (temperature, top_p, etc.)

**Returns:** `ModelResponse`

#### `generate_stream(prompt, model=None, timeout=None, options=None)`

Generate real-time streaming response.

**Parameters:**
- `prompt` (str): Input prompt
- `model` (str, optional): Model name
- `timeout` (int, optional): Timeout in seconds
- `options` (dict, optional): Generation options

**Yields:** `StreamChunk` objects

#### `health_check()`

Check if Ollama service is accessible.

**Returns:** `bool` - True if accessible

#### `list_models()`

List all available models.

**Returns:** `List[ModelInfo]`

#### `close()`

Close HTTP session and release resources.

## Resources

### External Links

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [requests Documentation](https://requests.readthedocs.io/)
- [Python Generators](https://docs.python.org/3/tutorial/classes.html#generators)

### Project Files

- Main implementation: `ollama_client.py`
- Configuration: `config.py`
- Tests: `tests/python/test_streaming.py`
- Interactive demo: `tests/python/interactive_streaming_demo.py`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review examples in `tests/python/`
3. Read the detailed documentation in this folder

## Version Info

- Python: 3.10+
- Ollama API: v1.0+
- Dependencies: requests, urllib3
