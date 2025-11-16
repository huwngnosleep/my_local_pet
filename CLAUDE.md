# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Ollama-based chatbot with DuckDuckGo web search integration. It provides both command-line and interactive chat interfaces using local LLM models via Ollama's API.

# Important notes from owner for Claude Code
- If you want to write any Markdown docs, write under ./docs folder
- If you want to write any script for testing purpose, write under ./tests folder. using ./tests/bash for .sh files, ./test/python for python files

## Running the Application

**Interactive mode:**
```bash
python start.py
```

**Single query mode:**
```bash
python start.py "Your question here"
```

The application automatically connects to Ollama at `http://localhost:11434` and will use the first available model if `phi3:mini` is not found.

## Architecture

### Module Structure

The codebase follows a clean, modular architecture:

```
├── config.py              # Configuration management (dataclasses)
├── ui.py                  # Terminal UI components
├── search_processor.py    # Search result processing strategies
├── tool_registry.py       # Tool management and registry
├── ollama_client.py       # Ollama API client
├── chatbot.py             # Main chatbot orchestration
└── start.py               # Entry point (minimal)
```

### Core Components

1. **Configuration (`config.py`)**
   - Uses dataclasses for type-safe configuration
   - `Config.from_defaults()` creates default configuration
   - No global variables - all config passed via dependency injection
   - Enums for constants (e.g., `SearchProcessingMethod`)

2. **Ollama Client (`ollama_client.py`)**
   - Handles all Ollama HTTP API communication with connection pooling
   - Supports both streaming and non-streaming responses
   - Returns structured `ModelResponse` and `StreamChunk` objects
   - HTTP session reuse for improved performance (10x faster sequential requests)
   - Automatic retry logic for transient failures
   - Includes health checks and model management
   - Clean error handling with detailed messages
   - Context manager support for resource cleanup

3. **Tool System (`tool_registry.py`)**
   - Registry pattern for dynamic tool management
   - Tools defined as dataclasses with name, description, parameters, function
   - `ToolRegistry.parse_tool_call()` extracts JSON from model responses
   - Two-stage execution: (1) Model decides tool use, (2) Model processes results

4. **Search Processing (`search_processor.py`)**
   - Strategy pattern with three implementations:
     - `ExtractionProcessor`: Keyword-based relevance extraction
     - `SmallModelProcessor`: AI-powered summarization
     - `SimpleProcessor`: Basic truncation
   - `SearchProcessorFactory.create_processor()` creates appropriate processor
   - Abstract base class `SearchResultProcessor` defines interface

5. **ChatBot (`chatbot.py`)**
   - Orchestrates all components
   - Supports both streaming and non-streaming responses
   - Real-time streaming for interactive chat (configurable via `config.ui.use_streaming`)
   - Implements two-stage tool calling logic
   - Graceful keyboard interrupt handling (Ctrl+C during generation)
   - Tracks timing information via `ChatTiming` dataclass
   - Dependency injection: receives `Config` and `ToolRegistry`
   - Methods: `chat()` (non-streaming), `chat_stream()` (streaming), `interactive_chat()`

6. **UI Components (`ui.py`)**
   - `LoadingIndicator`: Animated terminal spinner
   - `TerminalFormatter`: Consistent message formatting
   - Windows-compatible ASCII characters

### Tool Calling Flow

1. User prompt + tool descriptions → Model (first call)
2. Model responds with JSON tool call (if needed)
3. `ToolRegistry.parse_tool_call()` extracts tool name and parameters
4. `ToolRegistry.execute()` runs the tool function
5. Tool result + original prompt → Model (second call)
6. Model generates final answer using tool results

### Windows Compatibility

- Loading spinner uses ASCII characters (`|`, `/`, `-`, `\`) instead of Unicode
- Status indicators use `[OK]` and `[!]` instead of checkmarks/crosses

## Coding Conventions/Standards

This codebase follows strict Python industry standards. All new code must adhere to these conventions.

### Python Style Guidelines

**PEP 8 Compliance**
- Line length: Maximum 100 characters (prefer 80-90)
- Indentation: 4 spaces (no tabs)
- Imports: Grouped (stdlib, third-party, local) with blank lines between groups
- Naming:
  - Classes: `PascalCase` (e.g., `SearchResultProcessor`)
  - Functions/methods: `snake_case` (e.g., `create_processor`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RESULTS`)
  - Private members: Leading underscore (e.g., `_internal_method`)
- Blank lines: 2 between top-level definitions, 1 between methods

**PEP 257 Docstrings**
- All modules, classes, and public functions must have docstrings
- Use Google-style docstring format:
  ```python
  def function_name(param1: str, param2: int) -> bool:
      """Brief description (one line).

      Detailed description if needed (after blank line).

      Args:
          param1: Description of param1.
          param2: Description of param2.

      Returns:
          Description of return value.

      Raises:
          ValueError: When and why this is raised.
      """
  ```

**Type Hints (PEP 484)**
- All function signatures must include type hints
- Use `typing` module for complex types (`Optional`, `List`, `Dict`, etc.)
- Use Python 3.10+ syntax where possible (`list[str]` instead of `List[str]`)
- Example:
  ```python
  from typing import Optional, Dict, Any

  def process_data(
      text: str,
      config: Optional[Dict[str, Any]] = None
  ) -> str:
      ...
  ```

### Architecture Patterns

**SOLID Principles**
- **Single Responsibility**: Each class has one clear purpose
  - ✅ `OllamaClient` only handles API communication
  - ✅ `SearchProcessor` only processes search results
  - ✅ `ToolRegistry` only manages tools

- **Open/Closed**: Extend functionality without modifying existing code
  - ✅ Add new search processors by implementing `SearchResultProcessor`
  - ✅ Add new tools via `ToolRegistry.register()`

- **Liskov Substitution**: Subtypes must be substitutable
  - ✅ All `SearchResultProcessor` implementations are interchangeable

- **Interface Segregation**: Small, focused interfaces
  - ✅ `SearchResultProcessor` has single `process()` method

- **Dependency Inversion**: Depend on abstractions, not concrete classes
  - ✅ `ChatBot` receives `Config`, not hardcoded values
  - ✅ Uses abstract base classes (`SearchResultProcessor`)

**Design Patterns Used**
- **Strategy Pattern**: `search_processor.py` - Interchangeable algorithms
- **Registry Pattern**: `tool_registry.py` - Dynamic tool management
- **Factory Pattern**: `SearchProcessorFactory`, `create_default_registry()`
- **Dependency Injection**: Pass dependencies via constructors
- **Dataclass Pattern**: Use `@dataclass` for data structures

### Code Organization

**Module Guidelines**
- One module per major component
- Maximum ~250 lines per module (prefer smaller)
- Each module has a clear, single purpose
- Import order: stdlib → third-party → local modules

**Class Design**
- Use dataclasses for simple data containers:
  ```python
  from dataclasses import dataclass

  @dataclass
  class ModelResponse:
      text: str
      success: bool
      error: Optional[str] = None
  ```

- Use regular classes for behavior:
  ```python
  class OllamaClient:
      def __init__(self, config: OllamaConfig):
          self.config = config

      def generate(self, prompt: str) -> ModelResponse:
          ...
  ```

- Prefer composition over inheritance
- Keep classes focused (< 200 lines)

**Configuration Management**
- **Never use global variables** for configuration
- Use `config.py` with dataclasses:
  ```python
  @dataclass
  class OllamaConfig:
      url: str = "http://localhost:11434/api/generate"
      model_name: str = "phi3:mini"
  ```
- Pass config via dependency injection
- Use enums for constants:
  ```python
  class SearchProcessingMethod(Enum):
      EXTRACTION = "extraction"
      SIMPLE = "simple"
  ```

### Error Handling

**Structured Error Responses**
- Return structured objects, not raw exceptions:
  ```python
  @dataclass
  class ModelResponse:
      success: bool
      text: str
      error: Optional[str] = None
  ```

**Exception Handling**
- Catch specific exceptions, not bare `except:`
- Provide helpful error messages
- Log errors when appropriate
- Use try/except at module boundaries

### Testing Standards

**Test Structure**
- Place tests in `tests/python/` directory
- Name test files `test_*.py`
- Each test module tests one main module
- Use descriptive test function names:
  ```python
  def test_extraction_processor_with_short_text():
      ...
  ```

**Test Organization**
```python
def test_function_name():
    """Test description."""
    # Arrange
    config = Config.from_defaults()
    bot = ChatBot(config=config)

    # Act
    result = bot.chat("test query")

    # Assert
    assert result is not None
```

**Test Independence**
- Each test should be independent
- Don't rely on global state
- Use dependency injection for easier testing
- Create fresh config/objects per test

### Documentation Standards

**Module Docstrings**
Every module must start with a docstring:
```python
"""Module name and purpose.

Detailed description of what this module provides,
its main classes/functions, and usage examples.
"""
```

**README and Guides**
- User-facing docs go in `docs/` folder
- Use Markdown format
- Include code examples
- Keep guides concise and practical

### Import Conventions

**Import Style**
```python
# Standard library (alphabetical)
import json
import sys
import time
from typing import Optional, List

# Third-party (alphabetical)
import requests
from ddgs import DDGS

# Local modules (alphabetical)
from config import Config, SearchProcessingMethod
from ollama_client import OllamaClient
```

**Avoid Star Imports**
- ❌ `from module import *`
- ✅ `from module import SpecificClass`

### File Structure Template

New Python files should follow this structure:

```python
#!/usr/bin/env python3
"""Module name and brief description.

Detailed description of module purpose and contents.
"""

# Standard library imports
import sys
from typing import Optional

# Third-party imports
import requests

# Local imports
from config import Config


class MyClass:
    """Class description.

    Detailed explanation of class purpose.

    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.
    """

    def __init__(self, config: Config):
        """Initialize MyClass.

        Args:
            config: Configuration object.
        """
        self.config = config

    def my_method(self, param: str) -> str:
        """Method description.

        Args:
            param: Parameter description.

        Returns:
            Return value description.
        """
        pass


def standalone_function(arg: str) -> bool:
    """Function description.

    Args:
        arg: Argument description.

    Returns:
        Return value description.
    """
    pass


if __name__ == "__main__":
    # Example usage or tests
    pass
```

### Code Quality Checklist

Before committing code, verify:
- ✅ PEP 8 compliant (use `flake8` or `black`)
- ✅ All functions have docstrings
- ✅ All functions have type hints
- ✅ No global variables (except module-level constants)
- ✅ Classes follow single responsibility principle
- ✅ Dependencies injected via constructors
- ✅ Error handling is structured and informative
- ✅ Tests written for new functionality
- ✅ Import statements organized correctly
- ✅ Code is readable and self-documenting

### Anti-Patterns to Avoid

**Don't:**
- ❌ Use global variables for state
- ❌ Create god classes (> 300 lines)
- ❌ Use bare `except:` clauses
- ❌ Mix business logic with UI code
- ❌ Hardcode configuration values
- ❌ Use star imports
- ❌ Create circular dependencies
- ❌ Ignore type hints
- ❌ Skip docstrings

**Do:**
- ✅ Use dependency injection
- ✅ Create small, focused classes
- ✅ Catch specific exceptions
- ✅ Separate concerns (UI, logic, data)
- ✅ Use configuration objects
- ✅ Explicit imports
- ✅ Design for testability
- ✅ Provide complete type hints
- ✅ Document all public APIs

### Example: Adding a New Feature

When adding a new tool:

```python
# 1. Create tool implementation
class MyNewTool:
    """Tool description."""

    def __init__(self, config: Config):
        """Initialize tool.

        Args:
            config: Application configuration.
        """
        self.config = config

    def execute(self, param: str) -> str:
        """Execute the tool.

        Args:
            param: Tool parameter.

        Returns:
            Tool result.
        """
        # Implementation
        pass

# 2. Register in tool_registry.py
def create_default_registry(config: Config) -> ToolRegistry:
    registry = ToolRegistry()

    # Existing tools...

    # Add new tool
    new_tool = MyNewTool(config)
    tool = Tool(
        name="my_new_tool",
        description="What this tool does",
        parameters={"param": "Description"},
        function=new_tool.execute
    )
    registry.register(tool)

    return registry
```

### References

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

## Ollama Setup

Models are pulled via:
```bash
ollama pull phi3:mini     # Default model
ollama pull gemma:2b      # Alternative
```

Check Ollama status:
```bash
systemctl status ollama    # Linux
ollama list               # List installed models
```

## Dependencies

- `requests` - Ollama HTTP API
- `ddgs` - DuckDuckGo search
- Running Ollama instance on localhost:11434

Install with:
```bash
pip install requests ddgs
```
