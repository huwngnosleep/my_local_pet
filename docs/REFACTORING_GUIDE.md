# Code Refactoring Guide

This document explains the refactored architecture of the Ollama chatbot codebase.

## Overview

The codebase has been refactored from a single procedural `start.py` file (498 lines) into a modular, class-based architecture following Python industry standards.

## Architecture

### Module Structure

```
my_local_pet/
├── config.py              # Configuration management
├── ui.py                  # User interface components
├── search_processor.py    # Search result processing
├── tool_registry.py       # Tool management and registry
├── ollama_client.py       # Ollama API client
├── chatbot.py             # Main chatbot orchestration
├── start.py               # Entry point (80 lines)
└── tests/
    └── python/
        ├── test_search_processing.py
        └── test_timing.py
```

### Design Principles

The refactoring follows these industry-standard principles:

1. **SOLID Principles**
   - Single Responsibility: Each class has one clear purpose
   - Open/Closed: Extensible without modifying existing code
   - Liskov Substitution: Processor classes are interchangeable
   - Interface Segregation: Small, focused interfaces
   - Dependency Inversion: Depends on abstractions (Config, not globals)

2. **PEP 8**: Python style guide compliance
3. **PEP 257**: Comprehensive docstrings
4. **Type Hints**: For better IDE support and type checking
5. **Dataclasses**: For clean data structures

## Module Details

### 1. `config.py` - Configuration Management

**Purpose**: Centralized configuration using dataclasses and enums.

**Key Classes**:
- `SearchProcessingMethod`: Enum for processing strategies
- `OllamaConfig`: Ollama API settings
- `SearchConfig`: Search functionality settings
- `UIConfig`: User interface settings
- `Config`: Main configuration container

**Benefits**:
- Type-safe configuration
- No global variables
- Easy to test and modify
- Clear defaults

**Example**:
```python
from config import Config, SearchProcessingMethod

config = Config.from_defaults()
config.set_search_processing(SearchProcessingMethod.SIMPLE)
config.ui.show_timing = False
```

### 2. `ui.py` - User Interface Components

**Purpose**: Terminal UI elements separated from business logic.

**Key Classes**:
- `LoadingIndicator`: Animated spinner for terminal
- `TerminalFormatter`: Consistent message formatting

**Benefits**:
- Reusable UI components
- Easy to modify appearance
- Testable independently

**Example**:
```python
from ui import LoadingIndicator, TerminalFormatter

loader = LoadingIndicator("Processing")
loader.start()
# Do work...
loader.stop()

formatter = TerminalFormatter()
print(formatter.format_timing(total=5.23))
```

### 3. `search_processor.py` - Search Result Processing

**Purpose**: Strategy pattern for different search result processing methods.

**Key Classes**:
- `SearchResultProcessor`: Abstract base class
- `ExtractionProcessor`: Keyword-based extraction
- `SmallModelProcessor`: AI-powered summarization
- `SimpleProcessor`: Basic truncation
- `SearchProcessorFactory`: Creates processors

**Benefits**:
- Easy to add new processing strategies
- Each processor is independently testable
- Clear separation of concerns

**Example**:
```python
from search_processor import SearchProcessorFactory
from config import SearchProcessingMethod

processor = SearchProcessorFactory.create_processor(
    method=SearchProcessingMethod.EXTRACTION,
    max_length=150
)

result = processor.process(text, query)
```

### 4. `tool_registry.py` - Tool Management

**Purpose**: Registry pattern for managing available tools.

**Key Classes**:
- `Tool`: Dataclass representing a tool
- `WebSearchTool`: DuckDuckGo search implementation
- `ToolRegistry`: Manages tool registration and execution
- `create_default_registry()`: Factory function

**Benefits**:
- Easy to add new tools
- Centralized tool management
- Type-safe tool definitions

**Example**:
```python
from tool_registry import ToolRegistry, Tool

registry = ToolRegistry()
registry.register(my_custom_tool)
result = registry.execute("web_search", query="Python 3.13")
```

### 5. `ollama_client.py` - Ollama API Client

**Purpose**: Clean abstraction over Ollama HTTP API.

**Key Classes**:
- `ModelResponse`: Structured response from model
- `ModelInfo`: Model metadata
- `OllamaClient`: HTTP client for Ollama

**Benefits**:
- Single responsibility for API communication
- Structured error handling
- Easy to mock for testing
- Health checks and model management

**Example**:
```python
from ollama_client import OllamaClient
from config import OllamaConfig

client = OllamaClient(OllamaConfig())
response = client.generate("What is Python?")

if response.success:
    print(response.text)
else:
    print(response.error)
```

### 6. `chatbot.py` - Main Chatbot Logic

**Purpose**: Orchestrates all components to provide chat functionality.

**Key Classes**:
- `ChatTiming`: Timing data structure
- `ChatBot`: Main chatbot class

**Benefits**:
- Clear orchestration of components
- Two-stage tool calling logic in one place
- Easy to extend with new features

**Example**:
```python
from chatbot import ChatBot
from config import Config

config = Config.from_defaults()
bot = ChatBot(config=config)

response = bot.chat("What are the latest Python releases?")
print(response)
```

### 7. `start.py` - Entry Point

**Purpose**: Minimal entry point that wires everything together.

**Before**: 498 lines of mixed concerns
**After**: 80 lines of clean orchestration

**Benefits**:
- Easy to understand
- Minimal logic
- Just wiring components together

## Comparison: Before vs After

### Before (Procedural)

```python
# Global variables scattered throughout
OLLAMA_URL = "..."
MODEL_NAME = "..."
TIMEOUT_FIRST_REQUEST = 120
SEARCH_PROCESSING = SearchProcessingMethod.EXTRACTION

# Functions accessing globals
def web_search(query):
    global SEARCH_PROCESSING  # Implicit dependency
    if SEARCH_PROCESSING == ...
```

### After (Object-Oriented)

```python
# Configuration object
config = Config.from_defaults()

# Dependency injection
bot = ChatBot(config=config)
client = OllamaClient(config.ollama)
```

## Testing

### Test Structure

Tests have been updated to use the new modular structure:

```python
from config import Config
from chatbot import ChatBot

def test_something():
    config = Config.from_defaults()
    bot = ChatBot(config=config)

    # Test with custom configuration
    config.ui.show_timing = False
    result = bot.chat("test query")
```

### Running Tests

```bash
# Test search processing methods
python tests/python/test_search_processing.py

# Test timing feature
python tests/python/test_timing.py

# Full test with web search
python tests/python/test_timing.py --full
```

## Migration Guide

### For Users

The CLI interface remains the same:

```bash
# Still works exactly as before
python start.py "Your question"
python start.py  # Interactive mode
```

### For Developers

If you were importing from `start.py`:

**Before**:
```python
from start import chat, web_search

response = chat("question")
results = web_search("query")
```

**After**:
```python
from chatbot import ChatBot
from config import Config

bot = ChatBot(Config.from_defaults())
response = bot.chat("question")
```

## Benefits of Refactoring

1. **Maintainability**
   - Each module has < 250 lines
   - Clear separation of concerns
   - Easy to find and fix bugs

2. **Testability**
   - Each component can be tested independently
   - Easy to mock dependencies
   - Clear test structure

3. **Extensibility**
   - Add new tools without touching existing code
   - Add new search processors easily
   - Swap implementations via configuration

4. **Readability**
   - Industry-standard patterns
   - Comprehensive docstrings
   - Type hints throughout

5. **Professional Quality**
   - Follows Python best practices (PEP 8, PEP 257)
   - Uses modern Python features (dataclasses, type hints)
   - Clean architecture principles

## Next Steps

Potential improvements:

1. **Add Tests**: Unit tests for each module
2. **Add Logging**: Structured logging throughout
3. **Add Caching**: Cache search results
4. **Add Async**: Async/await for better performance
5. **Add CLI Options**: Argparse for command-line configuration

## Files Preserved

The old version is backed up as `start_old.py` for reference.
