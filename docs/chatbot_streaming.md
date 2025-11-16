# ChatBot Streaming Responses

## Overview

The `ChatBot` class now supports real-time streaming responses, providing an interactive chat experience where you can see the AI's response being generated token by token.

## Features

- **Real-time streaming**: See responses as they're generated
- **Tool integration**: Streaming works seamlessly with web search and other tools
- **Keyboard interrupts**: Gracefully handle Ctrl+C during generation
- **Backward compatible**: Non-streaming mode still available
- **Configurable**: Enable/disable streaming via configuration

## Quick Start

### Interactive Chat with Streaming (Default)

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
bot = ChatBot(config=config)

# Streaming is enabled by default
bot.interactive_chat()
```

### Disable Streaming

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = False  # Disable streaming

bot = ChatBot(config=config)
bot.interactive_chat()
```

## API Reference

### New Method: `chat_stream()`

```python
def chat_stream(
    self,
    prompt: str,
    model: Optional[str] = None,
    use_tools: bool = True,
    show_loading: bool = None,
    show_timing: bool = None
) -> str:
    """Process a chat message with streaming response.

    Args:
        prompt: User's input message.
        model: Model name to use (uses config default if None).
        use_tools: Whether to enable tool usage.
        show_loading: Whether to show loading animation.
        show_timing: Whether to display timing information.

    Returns:
        Complete model's response text.
    """
```

### Updated Method: `interactive_chat()`

```python
def interactive_chat(
    self,
    model: Optional[str] = None,
    use_streaming: Optional[bool] = None
) -> None:
    """Run an interactive chat session.

    Args:
        model: Model name to use (uses config default if None).
        use_streaming: Whether to use streaming responses (uses config default if None).
    """
```

## Configuration

Add to your `config.py` or modify at runtime:

```python
from config import Config

config = Config.from_defaults()

# Enable streaming (default)
config.ui.use_streaming = True

# Disable streaming
config.ui.use_streaming = False

# Other streaming-related settings
config.ui.show_timing = True  # Show response timing
config.ui.show_loading = True  # Show loading spinner
```

## Usage Examples

### Example 1: Basic Streaming Chat

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True

bot = ChatBot(config=config)

# Single query with streaming
response = bot.chat_stream("Tell me about Python")
# Response is printed in real-time
# Returns complete response text
```

### Example 2: Interactive Session

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
bot = ChatBot(config=config)

# Start interactive chat with streaming
bot.interactive_chat()

# Example interaction:
# You: What is machine learning?
# AI: [Streams response in real-time...]
```

### Example 3: Programmatic Chat

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
bot = ChatBot(config=config)

questions = [
    "What is Python?",
    "Explain functions",
    "What are classes?"
]

for question in questions:
    print(f"\nQ: {question}")
    # Response streams to console automatically
    answer = bot.chat_stream(question, use_tools=False)
    print()  # Extra spacing
```

### Example 4: With Web Search Tool

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True

bot = ChatBot(config=config)

# This will:
# 1. Use web search tool (non-streaming for tool detection)
# 2. Execute the search
# 3. Stream the final answer using search results
response = bot.chat_stream(
    "What's the latest news about AI?",
    use_tools=True
)
```

### Example 5: Comparison Mode

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
bot = ChatBot(config=config)

query = "Explain quantum computing"

print("=== Non-Streaming Mode ===")
response1 = bot.chat(query, use_tools=False)
print(f"AI: {response1}")

print("\n=== Streaming Mode ===")
response2 = bot.chat_stream(query, use_tools=False)
# Streams automatically, returns complete text
```

### Example 6: Custom Timing Display

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
config.ui.show_timing = True  # Show detailed timing

bot = ChatBot(config=config)

# Timing is displayed after the response
response = bot.chat_stream(
    "Explain recursion",
    show_timing=True
)
```

## How It Works

### Without Tools (Direct Streaming)

```
User Input
    ↓
Build Prompt with System Instructions
    ↓
Stream Response from Model
    ↓
Display tokens in real-time
    ↓
Return complete response
```

### With Tools (Two-Stage)

```
User Input
    ↓
Build Prompt with Tool Descriptions
    ↓
First Call: Detect Tool Usage (non-streaming)
    ↓
Tool Detected?
    ├─ No → Stream Response Directly
    │       ↓
    │   Display in real-time
    │
    └─ Yes → Execute Tool
            ↓
        Second Call: Stream Final Answer with Tool Results
            ↓
        Display in real-time
```

## Performance

### Perceived Latency

| Mode | Time to First Token | Total Time | User Experience |
|------|---------------------|------------|-----------------|
| Non-Streaming | Wait for complete response | Same | Wait then see all |
| Streaming | ~200ms | Same | See immediately |

### Streaming Benefits

1. **Immediate Feedback**: First token appears in ~200ms
2. **Better UX**: Users see progress instead of waiting
3. **Interruptible**: Can cancel with Ctrl+C mid-generation
4. **Engaging**: Feels more like a conversation

## Keyboard Interrupts

Streaming responses can be interrupted gracefully:

```python
from chatbot import ChatBot

bot = ChatBot()

try:
    # User can press Ctrl+C during generation
    response = bot.chat_stream("Write a long essay")
except KeyboardInterrupt:
    print("\nGeneration interrupted by user")
```

The chatbot handles interrupts in two ways:

1. **During response generation**: Partial response is returned
2. **During interactive chat**: Chat session continues or exits

## Tool Integration

### Web Search Example

```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True

bot = ChatBot(config=config)

# Tool execution flow:
# 1. [Non-streaming] Model decides to use web_search
# 2. [Tool execution] DuckDuckGo search runs
# 3. [Streaming] Final answer is streamed using search results

response = bot.chat_stream("What's the weather in Tokyo?")
```

Console output:
```
[Tool: web_search] (Executing...)
[Tool: web_search] (Completed in 1.2s)

AI: [Streams response based on search results...]
```

## Configuration Options

### UIConfig Settings

```python
@dataclass
class UIConfig:
    show_timing: bool = True        # Display timing info
    show_loading: bool = True       # Show loading spinner
    use_streaming: bool = True      # Enable streaming
    spinner_chars: tuple = ('|', '/', '-', '\\')
```

### OllamaConfig Settings

```python
@dataclass
class OllamaConfig:
    timeout_first_request: int = 120   # Timeout for initial request
    timeout_tool_request: int = 150    # Timeout after tool execution
    temperature: float = 1.0           # Generation temperature
    num_predict: int = 100             # Max tokens (streaming respects this)
    top_p: float = 0.5                 # Nucleus sampling
```

## Best Practices

### ✅ Do

1. **Use streaming for interactive chat**:
   ```python
   bot.interactive_chat()  # Streaming enabled by default
   ```

2. **Handle keyboard interrupts**:
   ```python
   try:
       response = bot.chat_stream(query)
   except KeyboardInterrupt:
       print("\nInterrupted")
   ```

3. **Enable timing for performance monitoring**:
   ```python
   config.ui.show_timing = True
   ```

4. **Use non-streaming for batch processing**:
   ```python
   responses = [bot.chat(q, use_tools=False) for q in queries]
   ```

### ❌ Don't

1. **Don't use streaming for silent batch operations**:
   ```python
   # Bad - streaming prints to console
   results = [bot.chat_stream(q) for q in many_queries]

   # Good - use non-streaming for batch
   results = [bot.chat(q) for q in many_queries]
   ```

2. **Don't mix streaming modes unpredictably**:
   ```python
   # Confusing - stick to one mode per session
   bot.chat(q1)         # Non-streaming
   bot.chat_stream(q2)  # Streaming
   bot.chat(q3)         # Non-streaming
   ```

3. **Don't ignore return values**:
   ```python
   # Good - capture complete response
   full_response = bot.chat_stream(query)

   # Bad - lose the response
   bot.chat_stream(query)  # Response only printed
   ```

## Testing

### Run Streaming Tests

```bash
# Test chatbot streaming functionality
python tests/python/test_chat_streaming.py
```

### Manual Testing

```bash
# Start interactive chat with streaming
python start.py

# Or in Python:
python -c "from chatbot import ChatBot; ChatBot().interactive_chat()"
```

## Comparison: Streaming vs Non-Streaming

### When to Use Streaming

✅ Interactive chat sessions
✅ Real-time user feedback needed
✅ Long responses (essays, explanations)
✅ Better user experience desired

### When to Use Non-Streaming

✅ Batch processing
✅ Silent background operations
✅ Logging/recording responses
✅ Need complete response before processing

## Example Output

### Streaming Mode

```
You: Tell me about Python

AI: Python is a high-level, interpreted programming language known for its
simplicity and readability. Created by Guido van Rossum in 1991, it emphasizes
code readability with significant use of whitespace...

[Timing] Total: 3.2s
```

*Note: In streaming mode, you see each word appear as it's generated.*

### Non-Streaming Mode

```
You: Tell me about Python

[Loading indicator shows...]

AI: Python is a high-level, interpreted programming language known for its
simplicity and readability. Created by Guido van Rossum in 1991, it emphasizes
code readability with significant use of whitespace...

[Timing] Total: 3.2s
```

*Note: In non-streaming mode, you wait, then see the complete response at once.*

## Troubleshooting

### Issue: Streaming Not Working

**Solution**: Check configuration
```python
config = Config.from_defaults()
print(f"Streaming enabled: {config.ui.use_streaming}")
```

### Issue: Response Cut Off

**Solution**: Increase `num_predict`
```python
config.ollama.num_predict = 500  # Allow more tokens
```

### Issue: Timeout During Streaming

**Solution**: Increase timeout
```python
config.ollama.timeout_first_request = 300  # 5 minutes
```

### Issue: No Streaming Output Visible

**Solution**: Ensure `flush=True` (already implemented)
```python
print(chunk.text, end='', flush=True)  # Correct
```

## Advanced Usage

### Custom Streaming Handler

```python
from chatbot import ChatBot
from config import Config

class CustomChatBot(ChatBot):
    def chat_stream(self, prompt: str, **kwargs):
        """Override to add custom streaming behavior."""
        print(f"[Streaming query: {prompt[:50]}...]")
        result = super().chat_stream(prompt, **kwargs)
        print(f"[Complete - {len(result)} chars]")
        return result

bot = CustomChatBot()
bot.chat_stream("Hello")
```

### Streaming with Logging

```python
import logging
from chatbot import ChatBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = ChatBot()

query = "Explain Python"
logger.info(f"Starting streaming query: {query}")

response = bot.chat_stream(query)

logger.info(f"Completed - {len(response)} characters generated")
```

## References

- Main implementation: [chatbot.py](../chatbot.py)
- Streaming client: [ollama_client.py](../ollama_client.py)
- Configuration: [config.py](../config.py)
- Tests: [tests/python/test_chat_streaming.py](../tests/python/test_chat_streaming.py)

## Related Documentation

- [Streaming Responses](./streaming_responses.md) - OllamaClient streaming
- [HTTP Connection Pooling](./http_connection_pooling.md) - Performance optimization
- [Streaming Quick Start](./streaming_quick_start.md) - Quick reference
