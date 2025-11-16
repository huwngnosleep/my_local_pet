# Streaming Responses

## Overview

The `OllamaClient` now supports streaming responses, allowing real-time token-by-token display as the model generates text. This provides a better user experience by showing progress instead of waiting for the complete response.

## Features

- **Real-time streaming**: Display tokens as they are generated
- **Two modes**: Streaming and non-streaming
- **Error handling**: Graceful error handling for stream interruptions
- **Connection pooling**: Streaming uses the same optimized connection pool
- **Type-safe**: Structured `StreamChunk` dataclass for chunks

## Usage

### Method 1: `generate_stream()` - Real-time Streaming

Use this method when you want to display tokens as they arrive:

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

# Stream response and print in real-time
for chunk in client.generate_stream("Write a short poem about Python"):
    if chunk.error:
        print(f"Error: {chunk.error}")
        break

    print(chunk.text, end='', flush=True)

    if chunk.done:
        print()  # New line at the end
        break
```

### Method 2: `generate()` with `stream=True` - Collect All

Use this method when you want streaming benefits but need the complete text:

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

# Stream internally but return complete response
response = client.generate(
    "Explain Python decorators",
    stream=True
)

if response.success:
    print(response.text)
else:
    print(f"Error: {response.error}")
```

### Method 3: `generate()` - Traditional Non-Streaming

Use this for simple, non-interactive scenarios:

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

# Traditional non-streaming request
response = client.generate("What is Python?")

if response.success:
    print(response.text)
```

## Data Structures

### StreamChunk

Represents a single chunk in a streaming response:

```python
@dataclass
class StreamChunk:
    text: str           # Text content of this chunk
    done: bool          # Whether this is the final chunk
    error: Optional[str] = None  # Error message if any
```

### ModelResponse

Enhanced with streaming support:

```python
@dataclass
class ModelResponse:
    text: str           # Complete generated text
    success: bool       # Request success status
    error: Optional[str] = None
    status_code: Optional[int] = None
    done: bool = True   # Always True for complete responses
```

## Examples

### Example 1: Interactive Chat with Streaming

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

        full_response = ""
        for chunk in client.generate_stream(user_input):
            if chunk.error:
                print(f"\nError: {chunk.error}")
                break

            print(chunk.text, end='', flush=True)
            full_response += chunk.text

            if chunk.done:
                print()  # New line
                break
```

### Example 2: Progress Indicator

```python
import sys
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

print("Generating response", end='', flush=True)

tokens = 0
for chunk in client.generate_stream("Explain quantum computing in simple terms"):
    if chunk.error:
        print(f"\nError: {chunk.error}")
        break

    if chunk.text:
        tokens += 1
        # Show progress dots
        if tokens % 5 == 0:
            print('.', end='', flush=True)

    if chunk.done:
        print("\n\nComplete response received!")
        break
```

### Example 3: Collect and Process Streaming Response

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

chunks = []
for chunk in client.generate_stream("List 5 Python best practices"):
    if chunk.error:
        print(f"Error: {chunk.error}")
        break

    if chunk.text:
        chunks.append(chunk.text)

    if chunk.done:
        break

# Process complete response
full_text = ''.join(chunks)
print(f"Generated {len(chunks)} chunks")
print(f"Total length: {len(full_text)} characters")
print(f"\nResponse:\n{full_text}")
```

### Example 4: Typewriter Effect

```python
import time
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

print("Assistant: ", end='', flush=True)

for chunk in client.generate_stream("Write a haiku about coding"):
    if chunk.error:
        print(f"\nError: {chunk.error}")
        break

    # Print character by character with slight delay
    for char in chunk.text:
        print(char, end='', flush=True)
        time.sleep(0.05)  # 50ms delay per character

    if chunk.done:
        print()
        break
```

### Example 5: Error Handling

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

try:
    for chunk in client.generate_stream("Explain machine learning"):
        if chunk.error:
            print(f"Stream error: {chunk.error}")
            # Handle different error types
            if "not found" in chunk.error.lower():
                print("Model not available. Please install it first.")
            elif "timeout" in chunk.error.lower():
                print("Request took too long. Try a simpler query.")
            else:
                print("An unexpected error occurred.")
            break

        print(chunk.text, end='', flush=True)

        if chunk.done:
            print()
            break

except KeyboardInterrupt:
    print("\n\nStream interrupted by user.")
except Exception as e:
    print(f"\n\nUnexpected error: {e}")
```

## Performance Comparison

### Non-Streaming Mode
- **Latency**: Wait for complete response before displaying
- **User Experience**: Can feel slow for long responses
- **Use Case**: Batch processing, testing, simple queries

### Streaming Mode
- **Latency**: Display starts immediately
- **User Experience**: Feels responsive and interactive
- **Use Case**: Chat interfaces, interactive tools, long responses

### Benchmark Example

```python
import time
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

prompt = "Write a detailed explanation of Python's GIL"

# Measure non-streaming
start = time.time()
response = client.generate(prompt, stream=False)
non_streaming_time = time.time() - start
print(f"Non-streaming: {non_streaming_time:.2f}s total")

# Measure streaming (time to first token)
start = time.time()
first_token_time = None
for chunk in client.generate_stream(prompt):
    if first_token_time is None and chunk.text:
        first_token_time = time.time() - start
        print(f"Streaming: {first_token_time:.2f}s to first token")
    if chunk.done:
        total_streaming_time = time.time() - start
        print(f"Streaming: {total_streaming_time:.2f}s total")
        break
```

## Best Practices

### 1. Always Check for Errors

```python
for chunk in client.generate_stream(prompt):
    if chunk.error:
        # Handle error appropriately
        print(f"Error: {chunk.error}")
        break
    # Process chunk
```

### 2. Use flush=True for Real-time Display

```python
# Good - immediate display
print(chunk.text, end='', flush=True)

# Bad - buffered output
print(chunk.text, end='')
```

### 3. Check for done Flag

```python
for chunk in client.generate_stream(prompt):
    print(chunk.text, end='', flush=True)

    if chunk.done:
        print()  # Add newline
        break  # Exit loop
```

### 4. Use Context Manager for Long-Running Sessions

```python
with OllamaClient(config.ollama) as client:
    for chunk in client.generate_stream(prompt):
        # Process chunks
        pass
# Session automatically closed
```

### 5. Handle Keyboard Interrupts

```python
try:
    for chunk in client.generate_stream(prompt):
        print(chunk.text, end='', flush=True)
        if chunk.done:
            break
except KeyboardInterrupt:
    print("\n\nGeneration cancelled by user.")
```

## Integration with Existing Code

The streaming feature is **backward compatible**. Existing code continues to work without changes:

```python
# Old code - still works
client = OllamaClient(config.ollama)
response = client.generate("Hello")
print(response.text)

# New code - streaming support
for chunk in client.generate_stream("Hello"):
    print(chunk.text, end='', flush=True)
    if chunk.done:
        break
```

## Limitations

1. **Timeout Handling**: Timeout applies to the entire stream, not per chunk
2. **No Partial Recovery**: If stream fails mid-way, partial response is lost
3. **Sequential Processing**: Chunks must be processed in order
4. **No Stream Seeking**: Cannot rewind or skip ahead in the stream

## Advanced Usage

### Custom Streaming Handler

```python
class StreamHandler:
    def __init__(self):
        self.chunks = []
        self.total_chars = 0

    def handle_chunk(self, chunk):
        if chunk.error:
            return False

        self.chunks.append(chunk.text)
        self.total_chars += len(chunk.text)

        print(chunk.text, end='', flush=True)

        return not chunk.done

    def get_full_text(self):
        return ''.join(self.chunks)

# Usage
client = OllamaClient(config.ollama)
handler = StreamHandler()

for chunk in client.generate_stream("Explain Python"):
    if not handler.handle_chunk(chunk):
        break

print(f"\n\nTotal characters: {handler.total_chars}")
```

### Streaming with Token Counting

```python
from ollama_client import OllamaClient
from config import Config

config = Config.from_defaults()
client = OllamaClient(config.ollama)

token_count = 0
for chunk in client.generate_stream("Explain recursion"):
    if chunk.text:
        # Approximate token count (rough estimate)
        token_count += len(chunk.text.split())
        print(chunk.text, end='', flush=True)

    if chunk.done:
        print(f"\n\nApproximate tokens: {token_count}")
        break
```

## Troubleshooting

### Issue: Stream Hangs

**Solution**: Check timeout settings in config

```python
config = Config.from_defaults()
config.ollama.timeout_first_request = 60  # Increase timeout
client = OllamaClient(config.ollama)
```

### Issue: Chunks Arrive Too Fast

**Solution**: Add throttling if needed

```python
import time

for chunk in client.generate_stream(prompt):
    print(chunk.text, end='', flush=True)
    time.sleep(0.01)  # 10ms delay between chunks
    if chunk.done:
        break
```

### Issue: Missing Final Newline

**Solution**: Always print newline after done

```python
for chunk in client.generate_stream(prompt):
    print(chunk.text, end='', flush=True)
    if chunk.done:
        print()  # Ensure newline at end
        break
```

## References

- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Python Generators](https://docs.python.org/3/tutorial/classes.html#generators)
- [HTTP Streaming with Requests](https://requests.readthedocs.io/en/latest/user/advanced/#streaming-requests)
