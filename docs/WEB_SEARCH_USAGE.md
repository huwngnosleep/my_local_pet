# Web Search Tool for Ollama

Your Ollama chat interface now has DuckDuckGo web search capabilities!

## Features

- Automatic web search when the model needs current information
- DuckDuckGo integration for privacy-focused searching
- Simple JSON-based tool calling interface
- Works with any Ollama model that supports tool use

## Usage

### Command Line Mode
```bash
python start.py "What are the latest SpaceX launches?"
```

### Interactive Mode
```bash
python start.py
```

Then ask questions that require web search:
- "What's the current news about Python 3.13?"
- "Search for the latest AI developments"
- "What's happening with cryptocurrency today?"

## How It Works

1. The model receives your question along with tool descriptions
2. If the model determines it needs current information, it outputs a JSON tool call
3. The system executes the web_search function using DuckDuckGo
4. Search results are sent back to the model
5. The model generates a final answer based on the search results

## Tool Call Format

When the model wants to search, it responds with:
```json
{
  "tool": "web_search",
  "parameters": {
    "query": "search query here",
    "max_results": 5
  }
}
```

## Dependencies

- `ddgs` - DuckDuckGo search library
- `requests` - HTTP library for Ollama API
- `ollama` - Running Ollama instance

## Disable Web Search

To disable web search for a specific query:
```python
from start import chat
response = chat("Your question", use_tools=False)
```

## Tips

- The model will only use web search when it determines current information is needed
- Not all models are equally good at using tools - experiment with different models
- The search results are limited to 5 by default to keep context manageable
- Results include title, URL, and description for each search result
