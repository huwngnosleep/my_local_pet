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

### Tool Calling System (`start.py`)

The application implements a custom tool-calling system for Ollama models:

1. **Tool Registration** (`TOOLS` dict at line 85): Tools are defined with name, description, parameters, and function reference
2. **Prompt Injection** (`format_tools_for_prompt()` at line 97): Tool descriptions are injected into the system prompt, instructing the model to output JSON when it needs to use a tool
3. **Response Parsing** (`parse_tool_call()` at line 110): Extracts JSON tool calls from model responses, handling both plain JSON and markdown code blocks
4. **Two-Stage Execution** (`chat()` at line 142):
   - First API call: Model receives user prompt + tool descriptions, may output tool call as JSON
   - Tool execution: If JSON detected, execute the corresponding function
   - Second API call: Send tool results back to model for final answer generation

### Web Search Integration

- Uses `ddgs` library (DuckDuckGo Search)
- `web_search()` function returns compact formatted results
- Default limit: 3 results
- Three processing methods for search results:
  - **EXTRACTION** (default): Algorithmic relevance-based sentence extraction
  - **SMALL_MODEL**: Uses tinyllama for intelligent summarization
  - **SIMPLE**: Basic truncation
- Tool can be disabled per-query with `use_tools=False` parameter

### Timing System

- Tracks and displays execution time for each stage
- Shows: Initial thinking time, Tool execution time, Final answer time, Total time
- Configurable via `SHOW_TIMING` global or `show_timing` parameter
- Helps diagnose timeouts and performance bottlenecks

### Windows Compatibility

- Loading spinner uses ASCII characters (`|`, `/`, `-`, `\`) instead of Unicode
- Status indicators use `[OK]` and `[!]` instead of checkmarks/crosses

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
