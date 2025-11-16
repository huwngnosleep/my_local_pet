#!/usr/bin/env python3
"""Ollama chatbot with web search capabilities.

A command-line chatbot powered by Ollama with DuckDuckGo web search integration.
Supports both interactive and single-query modes.

Usage:
    Interactive mode:
        python start.py

    Single query mode:
        python start.py "Your question here"

Features:
    - DuckDuckGo web search integration
    - Tool calling system for dynamic information retrieval
    - Multiple search result processing methods
    - Timing information for performance analysis
    - Clean, modular architecture

Author: Generated with Claude Code
"""

import sys
from typing import Optional

from config import Config, SearchProcessingMethod
from chatbot import ChatBot


def main() -> None:
    """Main entry point for the chatbot application."""
    # Create configuration
    config = Config.from_defaults()

    # Optional: Customize configuration here
    # config.set_search_processing(SearchProcessingMethod.SIMPLE)
    # config.ui.show_timing = True

    # Initialize chatbot
    bot = ChatBot(config=config)

    # Test connection to Ollama
    print("\nTesting connection to Ollama...")
    print("-" * 50)

    if not bot.test_connection():
        print("\nPlease install and start Ollama first:")
        print("  1. Run: curl -fsSL https://ollama.com/install.sh | sh")
        print("  2. Pull a model: ollama pull phi3:mini")
        print("  3. Start service: systemctl start ollama")
        sys.exit(1)

    print("-" * 50)

    # Check if default model exists, otherwise use first available
    available_models = bot.get_available_models()
    if config.ollama.model_name not in available_models and available_models:
        print(f"\n[!] Default model '{config.ollama.model_name}' not found.")
        print(f"Using '{available_models[0]}' instead.")
        bot.set_model(available_models[0])

    print()

    # Determine mode: interactive or single query
    if len(sys.argv) > 1:
        # Single query mode
        prompt = " ".join(sys.argv[1:])
        print(f"Question: {prompt}\n")

        answer = bot.chat(prompt)
        print(f"Answer: {answer}")

    else:
        # Interactive mode
        bot.interactive_chat()


if __name__ == "__main__":
    main()
