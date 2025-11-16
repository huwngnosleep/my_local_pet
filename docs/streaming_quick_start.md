# Streaming Quick Start Guide

## Basic Usage

### Real-time Streaming (Recommended for Chat)

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

# Stream and display in real-time
for chunk in client.generate_stream("Tell me a joke"):
    if chunk.error:
        print(f"Error: {chunk.error}")
        break

    print(chunk.text, end='', flush=True)

    if chunk.done:
        print()  # Add newline
        break
```

### Streaming with Buffering

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

# Stream internally, return complete text
response = client.generate("Explain Python", stream=True)

if response.success:
    print(response.text)
else:
    print(f"Error: {response.error}")
```

### Traditional Non-Streaming

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

# Wait for complete response
response = client.generate("What is AI?")

if response.success:
    print(response.text)
```

## Interactive Chat Example

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()

with OllamaClient(config.ollama) as client:
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        print("Assistant: ", end='', flush=True)

        for chunk in client.generate_stream(user_input):
            if chunk.error:
                print(f"\nError: {chunk.error}")
                break

            print(chunk.text, end='', flush=True)

            if chunk.done:
                print()
                break
```

## Running Test Scripts

### Test All Streaming Features

```bash
python tests/python/test_streaming.py
```

### Interactive Demo

```bash
python tests/python/interactive_streaming_demo.py
```

## Key Points

1. **Always use `flush=True`** when printing streaming chunks
2. **Check `chunk.error`** for error handling
3. **Check `chunk.done`** to know when streaming is complete
4. **Use context manager** (`with` statement) for automatic cleanup
5. **Handle KeyboardInterrupt** for graceful cancellation

## Performance Benefits

- **10x faster** perceived response time (streaming shows first token immediately)
- Connection pooling reduces latency by ~50-100ms per request
- Automatic retries for server errors (500, 502, 503, 504)

## Further Reading

- [Full Streaming Documentation](./streaming_responses.md)
- [HTTP Connection Pooling](./http_connection_pooling.md)
