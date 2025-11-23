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

    if not bot.test_connection():
        sys.exit(1)

    print("-" * 50)
    bot.interactive_chat()

if __name__ == "__main__":
    main()
