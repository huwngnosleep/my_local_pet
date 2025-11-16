#!/usr/bin/env python3
"""Test script for concise response optimization.

This script demonstrates how to configure the chatbot for brief,
direct answers instead of verbose responses.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import Config, ResponseStyle, OllamaConfig
from chatbot import ChatBot


def test_default_verbose():
    """Test default configuration (may be verbose)."""
    print("="*60)
    print("TEST 1: Default Configuration (NORMAL style)")
    print("="*60 + "\n")

    config = Config.from_defaults()
    bot = ChatBot(config=config)

    question = "Which city is Vietnam's capital?"
    print(f"Question: {question}\n")

    response = bot.chat(question, show_loading=False, show_timing=True)
    print(f"\nResponse: {response}")
    print(f"Length: {len(response)} characters\n")


def test_concise_style():
    """Test with CONCISE response style."""
    print("="*60)
    print("TEST 2: CONCISE Response Style")
    print("="*60 + "\n")

    config = Config.from_defaults()
    config.set_response_style(ResponseStyle.CONCISE)

    bot = ChatBot(config=config)

    question = "Which city is Vietnam's capital?"
    print(f"Question: {question}\n")

    response = bot.chat(question, show_loading=False, show_timing=True)
    print(f"\nResponse: {response}")
    print(f"Length: {len(response)} characters\n")


def test_ultra_concise():
    """Test with maximum conciseness settings."""
    print("="*60)
    print("TEST 3: Ultra Concise (CONCISE + low temp + token limit)")
    print("="*60 + "\n")

    ollama_config = OllamaConfig(
        response_style=ResponseStyle.CONCISE,
        temperature=0.1,
        num_predict=50,
        top_p=0.8
    )

    config = Config(ollama_config=ollama_config)
    bot = ChatBot(config=config)

    question = "Which city is Vietnam's capital?"
    print(f"Question: {question}\n")
    print("Configuration:")
    print(f"  - Response Style: CONCISE")
    print(f"  - Temperature: 0.1")
    print(f"  - Max Tokens: 50")
    print(f"  - Top P: 0.8\n")

    response = bot.chat(question, show_loading=False, show_timing=True)
    print(f"\nResponse: {response}")
    print(f"Length: {len(response)} characters\n")


def test_multiple_questions():
    """Test concise mode with multiple factual questions."""
    print("="*60)
    print("TEST 4: Multiple Questions (CONCISE mode)")
    print("="*60 + "\n")

    ollama_config = OllamaConfig(
        response_style=ResponseStyle.CONCISE,
        temperature=0.2,
        num_predict=80
    )

    config = Config(ollama_config=ollama_config)
    bot = ChatBot(config=config)

    questions = [
        "Which city is Vietnam's capital?",
        "What is 15 + 27?",
        "Who wrote Romeo and Juliet?",
        "What is the chemical symbol for gold?",
        "What year did World War 2 end?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"{i}. Q: {question}")
        response = bot.chat(question, show_loading=False, show_timing=False)
        print(f"   A: {response}")
        print(f"   ({len(response)} chars)\n")


def test_style_comparison():
    """Compare all three response styles side by side."""
    print("="*60)
    print("TEST 5: Style Comparison (CONCISE vs NORMAL vs DETAILED)")
    print("="*60 + "\n")

    question = "What is Python programming language?"
    print(f"Question: {question}\n")

    for style in [ResponseStyle.CONCISE, ResponseStyle.NORMAL, ResponseStyle.DETAILED]:
        print(f"\n--- {style.value.upper()} Style ---")

        config = Config.from_defaults()
        config.set_response_style(style)

        bot = ChatBot(config=config)
        response = bot.chat(question, show_loading=False, show_timing=False)

        print(f"Response: {response}")
        print(f"Length: {len(response)} characters")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CONCISE RESPONSE OPTIMIZATION TEST SUITE")
    print("="*60 + "\n")

    try:
        # Test connection first
        bot = ChatBot()
        if not bot.test_connection():
            print("\n[!] Cannot connect to Ollama. Please ensure it's running.")
            print("    Start Ollama and try again.\n")
            return

        print("\n")

        # Run tests
        test_default_verbose()
        print("\n")

        test_concise_style()
        print("\n")

        test_ultra_concise()
        print("\n")

        test_multiple_questions()
        print("\n")

        test_style_comparison()
        print("\n")

        print("="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\nRecommendation:")
        print("  For brief answers to factual questions, use:")
        print("    - ResponseStyle.CONCISE")
        print("    - temperature=0.2")
        print("    - num_predict=80 (optional)\n")

    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n[!] Error during testing: {e}")


if __name__ == "__main__":
    main()
