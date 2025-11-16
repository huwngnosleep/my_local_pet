#!/usr/bin/env python3
"""Test timing feature.

Shows how long each step takes in the chatbot pipeline.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from chatbot import ChatBot


def test_simple_query(bot: ChatBot):
    """Test timing for simple query (no tools).

    Args:
        bot: ChatBot instance to use.
    """
    print("=" * 60)
    print("Test 1: Simple Query (No Tools)")
    print("=" * 60)

    response = bot.chat("What is Python?", use_tools=False, show_timing=True)
    print(f"\nResponse: {response[:100]}...")
    print()


def test_web_search_query(bot: ChatBot):
    """Test timing for web search query.

    Args:
        bot: ChatBot instance to use.
    """
    print("=" * 60)
    print("Test 2: Web Search Query (With Tools)")
    print("=" * 60)

    response = bot.chat("What are the latest Python releases?", use_tools=True, show_timing=True)
    print(f"\nResponse: {response[:200]}...")
    print()


def test_without_timing(bot: ChatBot):
    """Test with timing disabled.

    Args:
        bot: ChatBot instance to use.
    """
    print("=" * 60)
    print("Test 3: Without Timing Display")
    print("=" * 60)

    response = bot.chat("Hello!", use_tools=False, show_timing=False)
    print(f"\nResponse: {response}")
    print()

def main():
    """Main test function."""
    print("\nTiming Feature Test")
    print("=" * 60)
    print("This will show timing information for different scenarios")
    print("=" * 60)
    print()

    # Initialize chatbot
    config = Config.from_defaults()
    bot = ChatBot(config=config)

    # Test connection
    print("Testing connection to Ollama...")
    if not bot.test_connection():
        print("Error: Cannot connect to Ollama")
        sys.exit(1)

    try:
        # Test 1: Simple query
        test_simple_query(bot)

        # Test 2: Web search (if user wants)
        if len(sys.argv) > 1 and sys.argv[1] == "--full":
            test_web_search_query(bot)
        else:
            print("Skipping web search test (use --full to include)")
            print()

        # Test 3: No timing
        test_without_timing(bot)

        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
