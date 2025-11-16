#!/usr/bin/env python3
"""
Ollama API Example - Simple chat interface
Usage: python3 ollama_api_example.py
"""

import requests
import json
import sys
import threading
import time
import itertools
from ddgs import DDGS

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"  # Change to your installed model
TIMEOUT_FIRST_REQUEST = 120  # Timeout for initial request (seconds)
TIMEOUT_TOOL_REQUEST = 150   # Timeout for tool result processing (seconds) - compact results reduce context size

# Search result processing method (choose one):
# "extraction" - Fast algorithmic extraction (RECOMMENDED - no extra model)
# "small_model" - Use tinyllama to summarize (slower, uses extra model)
# "simple" - Simple truncation (fastest, least smart)
SEARCH_PROCESSING = "extraction"

class LoadingIndicator:
    """Shows a loading animation while AI is thinking"""
    def __init__(self, message="Thinking"):
        self.message = message
        self.is_running = False
        self.thread = None
        # Simple ASCII spinner for Windows compatibility
        self.spinner = itertools.cycle(['|', '/', '-', '\\'])

    def _animate(self):
        """Animation loop"""
        while self.is_running:
            sys.stdout.write(f'\r{next(self.spinner)} {self.message}...')
            sys.stdout.flush()
            time.sleep(0.1)
        # Clear the line when done
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def start(self):
        """Start the loading animation"""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the loading animation"""
        self.is_running = False
        if self.thread:
            self.thread.join()

def extract_relevant_info(text, query, max_length=150):
    """
    Extract most relevant sentences from text using simple algorithm

    Args:
        text (str): Text to extract from
        query (str): User's query for relevance scoring
        max_length (int): Maximum characters to return

    Returns:
        str: Extracted relevant text
    """
    # Split into sentences
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        return text[:max_length]

    # Score sentences based on query word overlap
    query_words = set(query.lower().split())
    scored_sentences = []

    for sentence in sentences:
        sentence_words = set(sentence.lower().split())
        score = len(query_words & sentence_words)  # Count matching words
        scored_sentences.append((score, sentence))

    # Sort by relevance and take top sentences
    scored_sentences.sort(reverse=True, key=lambda x: x[0])

    # Build result within max_length
    result = []
    current_length = 0

    for score, sentence in scored_sentences:
        if current_length + len(sentence) <= max_length:
            result.append(sentence)
            current_length += len(sentence)
        else:
            break

    if not result:
        return sentences[0][:max_length] + '...'

    return '. '.join(result) + '.'

def summarize_with_small_model(text, query, model="tinyllama"):
    """
    Use a small, fast model to summarize search results

    Args:
        text (str): Text to summarize
        query (str): Original query for context
        model (str): Small model name (default: tinyllama)

    Returns:
        str: Summarized text
    """
    try:
        prompt = f"Summarize this in 1-2 sentences relevant to '{query}': {text}"

        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result.get('response', text[:200])
        else:
            # Fallback to simple truncation
            return text[:200] + '...'
    except Exception:
        # Fallback to simple truncation
        return text[:200] + '...'

def web_search(query, max_results=3):
    """
    Search the web using DuckDuckGo

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return (default: 3)

    Returns:
        str: Compact formatted search results
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return "No results found."

            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')

                # Process the description based on config
                if SEARCH_PROCESSING == "small_model":
                    # Option 1: Use small model to summarize
                    body = summarize_with_small_model(body, query)
                elif SEARCH_PROCESSING == "extraction":
                    # Option 2: Use simple extraction algorithm (RECOMMENDED)
                    body = extract_relevant_info(body, query, max_length=150)
                else:  # "simple"
                    # Option 3: Simple truncation
                    if len(body) > 200:
                        body = body[:200].rsplit(' ', 1)[0] + '...'

                formatted_results.append(f"{i}. {title}\n   {body}")

            return "\n".join(formatted_results)
    except Exception as e:
        return f"Search error: {str(e)}"

# Define available tools
TOOLS = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web using DuckDuckGo. Use this when you need current information, facts, or data that you don't have in your knowledge base.",
        "parameters": {
            "query": "The search query string",
            "max_results": "Maximum number of results (default: 3)"
        },
        "function": web_search
    }
}

def format_tools_for_prompt():
    """Format tools description for the system prompt"""
    tools_desc = "You have access to the following tools:\n\n"
    for tool_name, tool_info in TOOLS.items():
        tools_desc += f"- {tool_info['name']}: {tool_info['description']}\n"
        tools_desc += "  Parameters:\n"
        for param, desc in tool_info['parameters'].items():
            tools_desc += f"    - {param}: {desc}\n"
        tools_desc += "\n"

    tools_desc += (
        "To use a tool, respond with a JSON object in this exact format:\n"
        '{"tool": "tool_name", "parameters": {"param1": "value1", "param2": "value2"}}\n\n'
        "After receiving tool results, provide your final answer to the user."
    )
    return tools_desc

def parse_tool_call(response_text):
    """
    Parse tool call from model response

    Returns:
        tuple: (tool_name, parameters) or (None, None) if no tool call
    """
    try:
        # Try to find JSON in the response
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            if json_end != -1:
                response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            if json_end != -1:
                response_text = response_text[json_start:json_end].strip()

        # Check if response contains "tool"
        if '"tool"' in response_text:
            # Extract JSON (handle multi-line)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                tool_call = json.loads(json_str)

                if 'tool' in tool_call:
                    return tool_call['tool'], tool_call.get('parameters', {})

        return None, None
    except Exception:
        return None, None

def chat(prompt, model=MODEL_NAME, stream=False, show_loading=True, use_tools=True):
    """
    Send a prompt to Ollama and get response

    Args:
        prompt (str): Your question or prompt
        model (str): Model name (default: phi3:mini)
        stream (bool): Stream response (default: False)
        show_loading (bool): Show loading indicator (default: True)
        use_tools (bool): Enable tool usage (default: True)

    Returns:
        str: Model's response
    """
    loader = None
    try:
        # Build system prompt with tools if enabled
        if use_tools:
            system_prompt = format_tools_for_prompt()
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = prompt

        data = {
            "model": model,
            "prompt": full_prompt,
            "stream": stream
        }

        # Start loading indicator
        if show_loading:
            loader = LoadingIndicator("AI is thinking")
            loader.start()

        response = requests.post(OLLAMA_URL, json=data, timeout=TIMEOUT_FIRST_REQUEST)

        # Stop loading indicator
        if loader:
            loader.stop()

        if response.status_code == 200:
            result = response.json()
            model_response = result.get('response', 'No response')

            # Check if model wants to use a tool
            if use_tools:
                tool_name, parameters = parse_tool_call(model_response)

                if tool_name and tool_name in TOOLS:
                    print(f"\n[Using tool: {tool_name}]")

                    # Execute the tool
                    tool_func = TOOLS[tool_name]['function']
                    tool_result = tool_func(**parameters)

                    print(f"[Tool result retrieved]\n")

                    # Send tool result back to model for final response
                    follow_up_prompt = (
                        f"{system_prompt}\n\n"
                        f"User: {prompt}\n\n"
                        f"Assistant: {model_response}\n\n"
                        f"Tool Result:\n{tool_result}\n\n"
                        f"Now provide your final answer to the user based on the tool results:"
                    )

                    # Get final response
                    if show_loading:
                        loader = LoadingIndicator("Generating final answer")
                        loader.start()

                    final_data = {
                        "model": model,
                        "prompt": follow_up_prompt,
                        "stream": stream
                    }

                    final_response = requests.post(OLLAMA_URL, json=final_data, timeout=TIMEOUT_TOOL_REQUEST)

                    if loader:
                        loader.stop()

                    if final_response.status_code == 200:
                        final_result = final_response.json()
                        return final_result.get('response', 'No response')

            return model_response

        elif response.status_code == 404:
            return (f"Error: Model '{model}' not found!\n"
                   f"Run 'ollama list' to see installed models.\n"
                   f"Or pull the model with: ollama pull {model}")
        else:
            return f"Error: HTTP {response.status_code} - {response.text}"

    except requests.exceptions.ConnectionError:
        if loader:
            loader.stop()
        return "Error: Cannot connect to Ollama. Is it running? (Check with: systemctl status ollama)"
    except Exception as e:
        if loader:
            loader.stop()
        return f"Error: {str(e)}"

def interactive_chat(model=None):
    """Run an interactive chat session"""
    if model is None:
        model = MODEL_NAME

    print("=" * 50)
    print("Ollama Interactive Chat")
    print(f"Model: {model}")
    print("=" * 50)
    print("Web Search: Enabled (DuckDuckGo)")
    print("Type 'quit' or 'exit' to end the session")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break

            # Get response with loading indicator
            response = chat(user_input, model=model, show_loading=True)
            print(f"AI: {response}")
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break

def get_available_models():
    """Get list of installed models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        return []
    except:
        return []

def test_connection():
    """Test if Ollama is accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"[OK] Connected to Ollama")
            print(f"[OK] Available models: {len(models)}")
            if models:
                for model in models:
                    print(f"  - {model['name']}")
                return True
            else:
                print("[!] No models installed!")
                print("  Pull a model first: ollama pull phi3:mini")
                return False
        else:
            print(f"[!] Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[!] Cannot connect to Ollama at http://localhost:11434")
        print("  Make sure Ollama is running: systemctl status ollama")
        return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    print("\nTesting connection to Ollama...")
    print("-" * 50)

    if test_connection():
        print("-" * 50)

        # Check if the default model exists, otherwise use the first available
        available_models = get_available_models()
        if MODEL_NAME not in available_models and available_models:
            print(f"\n[!] Default model '{MODEL_NAME}' not found.")
            print(f"Using '{available_models[0]}' instead.")
            MODEL_NAME = available_models[0]

        print()

        # Check if user wants interactive mode or single query
        if len(sys.argv) > 1:
            # Single query mode
            prompt = " ".join(sys.argv[1:])
            print(f"Question: {prompt}\n")
            answer = chat(prompt, model=MODEL_NAME, show_loading=True)
            print(f"Answer: {answer}")
        else:
            # Interactive mode
            interactive_chat(model=MODEL_NAME)
    else:
        print("\nPlease install and start Ollama first:")
        print("  1. Run: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Pull a model: ollama pull phi3:mini")
        print("  3. Start service: systemctl start ollama")
        sys.exit(1)
