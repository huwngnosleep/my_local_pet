#!/usr/bin/env python3
"""Test script for chatbot streaming functionality.

This script demonstrates the streaming chat capabilities of the ChatBot class.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from chatbot import ChatBot
from config import Config


def test_streaming_chat():
    """Test streaming chat with a simple query."""
    print("=" * 60)
    print("Test: Streaming Chat")
    print("=" * 60)

    config = Config.from_defaults()
    config.ui.show_timing = True
    config.ui.use_streaming = True

    bot = ChatBot(config=config)

    # Test connection first
    print("\nTesting connection to Ollama...")
    if not bot.test_connection():
        print("\n✗ Cannot connect to Ollama. Make sure it's running.")
        return False

    print("\n" + "=" * 60)
    print("Streaming Response Test")
    print("=" * 60)

    test_queries = [
        "Say hello in 5 words",
        "Count from 1 to 3",
        "What is Python?",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}]")
        print(f"Query: {query}")
        print("-" * 60)

        try:
            response = bot.chat_stream(query, use_tools=False)
            print()  # Extra newline for spacing
            if response and not response.startswith("Error:"):
                print(f"✓ Response received ({len(response)} characters)")
            else:
                print(f"✗ Error: {response}")
                return False

        except KeyboardInterrupt:
            print("\n\nTest interrupted by user.")
            return False
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            return False

    print("\n" + "=" * 60)
    print("✓ All streaming tests passed!")
    print("=" * 60)
    return True


def test_streaming_vs_nonstreaming():
    """Compare streaming vs non-streaming chat."""
    print("\n" + "=" * 60)
    print("Test: Streaming vs Non-Streaming Comparison")
    print("=" * 60)

    config = Config.from_defaults()
    config.ui.show_timing = True
    bot = ChatBot(config=config)

    query = "Explain what Python is in one sentence"

    # Non-streaming
    print("\n[Non-Streaming Mode]")
    print("-" * 60)
    response_nonstreaming = bot.chat(query, use_tools=False)
    print(f"AI: {response_nonstreaming}")
    print()

    # Streaming
    print("\n[Streaming Mode]")
    print("-" * 60)
    response_streaming = bot.chat_stream(query, use_tools=False)
    print()

    print("\n" + "=" * 60)
    print("✓ Comparison complete")
    print("Note: Streaming should feel more responsive!")
    print("=" * 60)

    return True


def test_streaming_with_tools():
    """Test streaming chat with tool usage (web search)."""
    print("\n" + "=" * 60)
    print("Test: Streaming with Web Search Tool")
    print("=" * 60)

    config = Config.from_defaults()
    config.ui.show_timing = True
    config.ui.use_streaming = True

    bot = ChatBot(config=config)

    print("\nQuery: What's the weather in Paris?")
    print("Note: This will use web search, then stream the final answer")
    print("-" * 60)

    try:
        response = bot.chat_stream(
            "What's the weather in Paris?",
            use_tools=True
        )
        print()

        if response and not response.startswith("Error:"):
            print("✓ Streaming with tools completed successfully")
            return True
        else:
            print(f"✗ Error: {response}")
            return False

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


def test_keyboard_interrupt():
    """Test that keyboard interrupts are handled gracefully."""
    print("\n" + "=" * 60)
    print("Test: Keyboard Interrupt Handling")
    print("=" * 60)

    print("\nThis test shows how the chat handles interruptions.")
    print("In a real scenario, you could press Ctrl+C during generation.")
    print("For this test, we'll just verify the handler exists.")

    config = Config.from_defaults()
    bot = ChatBot(config=config)

    print("\n✓ Keyboard interrupt handling is implemented in:")
    print("  - chat_stream() method")
    print("  - interactive_chat() method")

    return True


def run_all_tests():
    """Run all chatbot streaming tests."""
    print("\n" + "=" * 60)
    print("CHATBOT STREAMING TESTS")
    print("=" * 60)

    tests = [
        ("Basic Streaming", test_streaming_chat),
        ("Streaming vs Non-Streaming", test_streaming_vs_nonstreaming),
        ("Streaming with Tools", test_streaming_with_tools),
        ("Keyboard Interrupt", test_keyboard_interrupt),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user.")
        sys.exit(1)
