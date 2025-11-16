#!/usr/bin/env python3
"""Quick example: Get concise responses from the chatbot.

This script shows how to configure the chatbot to give brief,
direct answers instead of long, verbose responses.

Run this to see the difference!
"""

from config import Config, ResponseStyle, OllamaConfig
from chatbot import ChatBot


def main():
    """Demonstrate concise response configuration."""

    print("="*60)
    print("CONCISE RESPONSE EXAMPLE")
    print("="*60)
    print()

    # Configure for concise responses
    ollama_config = OllamaConfig(
        response_style=ResponseStyle.CONCISE,  # Use CONCISE style
        temperature=0.2,                       # Low temp = more focused
        num_predict=100,                       # Limit to 100 tokens
        top_p=0.8                              # Less diverse vocabulary
    )

    config = Config(ollama_config=ollama_config)
    bot = ChatBot(config=config)

    # Test with your example question
    print("Configuration: CONCISE mode (brief, direct answers)")
    print()

    question = "Which city is Vietnam's capital?"
    print(f"Question: {question}")
    print()

    response = bot.chat(question, show_loading=True, show_timing=True)

    print()
    print(f"Answer: {response}")
    print()
    print(f"Response length: {len(response)} characters")
    print()

    # Try a few more examples
    print("-" * 60)
    print("More examples:")
    print("-" * 60)
    print()

    examples = [
        "What is 25 + 17?",
        "Who invented the telephone?",
        "What is the capital of France?"
    ]

    for q in examples:
        answer = bot.chat(q, show_loading=False, show_timing=False)
        print(f"Q: {q}")
        print(f"A: {answer}")
        print()

    print("="*60)
    print("\nTIP: To switch back to normal/detailed responses, use:")
    print("  config.set_response_style(ResponseStyle.NORMAL)")
    print("  config.set_response_style(ResponseStyle.DETAILED)")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Ollama is running with a model installed.")
        print("Example: ollama pull phi3:mini")
