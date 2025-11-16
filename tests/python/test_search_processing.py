#!/usr/bin/env python3
"""Test different search processing methods.

Compares speed and output quality of different search result
processing strategies.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config, SearchProcessingMethod
from chatbot import ChatBot


def test_processing_method(bot: ChatBot, method: SearchProcessingMethod, query: str):
    """Test a specific processing method.

    Args:
        bot: ChatBot instance to use for testing.
        method: Search processing method to test.
        query: Search query to execute.

    Returns:
        Tuple of (elapsed_time, result_size).
    """
    print(f"\n{'='*60}")
    print(f"Method: {method.value.upper()}")
    print(f"{'='*60}")

    # Temporarily change the config
    original_method = bot.config.search.processing_method
    bot.config.set_search_processing(method)

    # Disable timing display for cleaner output
    original_timing = bot.config.ui.show_timing
    bot.config.ui.show_timing = False

    start_time = time.time()
    result = bot.chat(query, use_tools=True, show_loading=True)
    elapsed = time.time() - start_time

    # Restore original config
    bot.config.set_search_processing(original_method)
    bot.config.ui.show_timing = original_timing

    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"\nResults:\n{result}")
    print(f"\nContext size: {len(result)} characters")

    return elapsed, len(result)


def main():
    """Main test function."""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "latest Python 3.13 features"

    print(f"Testing search query: '{query}'")
    print("="*60)

    # Initialize chatbot
    config = Config.from_defaults()
    bot = ChatBot(config=config)

    # Test connection
    print("\nTesting connection to Ollama...")
    if not bot.test_connection():
        print("Error: Cannot connect to Ollama")
        sys.exit(1)

    methods = [
        SearchProcessingMethod.SIMPLE,
        SearchProcessingMethod.EXTRACTION,
        SearchProcessingMethod.SMALL_MODEL
    ]
    results = {}

    for method in methods:
        try:
            elapsed, size = test_processing_method(bot, method, query)
            results[method.value] = {"time": elapsed, "size": size}
        except Exception as e:
            print(f"\nError with {method.value}: {e}")

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Method':<15} {'Time (s)':<12} {'Size (chars)':<15} {'Speed'}")
    print("-"*60)

    for method in methods:
        if method.value in results:
            r = results[method.value]
            speed = "★★★" if r['time'] < 5 else "★★" if r['time'] < 10 else "★"
            print(f"{method.value:<15} {r['time']:<12.2f} {r['size']:<15} {speed}")

    print("\nRecommendation:")
    print("- Use 'extraction' for best balance of speed and quality")
    print("- Use 'simple' if you want maximum speed")
    print("- Use 'small_model' if you need smartest extraction (requires tinyllama)")


if __name__ == "__main__":
    main()
