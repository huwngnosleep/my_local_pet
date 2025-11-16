#!/usr/bin/env python3
"""Interactive streaming demo.

A simple interactive chat interface demonstrating real-time streaming responses.
"""

import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ollama_client import OllamaClient
from config import Config


def main():
    """Run interactive streaming chat demo."""
    print("=" * 60)
    print("OLLAMA STREAMING CHAT DEMO")
    print("=" * 60)
    print("\nThis demo shows real-time streaming responses.")
    print("Watch as tokens appear one by one!\n")
    print("Commands:")
    print("  - Type your question and press Enter")
    print("  - Type 'exit' or 'quit' to end")
    print("  - Press Ctrl+C to interrupt generation")
    print("=" * 60)

    config = Config.from_defaults()

    # Show configuration
    print(f"\nConfiguration:")
    print(f"  Model: {config.ollama.model_name}")
    print(f"  Temperature: {config.ollama.temperature}")
    print(f"  Ollama URL: {config.ollama.url}")

    # Test connection
    print("\nTesting connection to Ollama...")
    with OllamaClient(config.ollama) as client:
        if not client.health_check():
            print("✗ Cannot connect to Ollama!")
            print("  Make sure Ollama is running: systemctl status ollama")
            sys.exit(1)

        models = client.get_model_names()
        if not models:
            print("✗ No models installed!")
            print("  Pull a model first: ollama pull phi3:mini")
            sys.exit(1)

        print(f"✓ Connected! Available models: {', '.join(models)}")

    print("\n" + "=" * 60)
    print("Chat started! (streaming mode)")
    print("=" * 60 + "\n")

    # Main chat loop
    with OllamaClient(config.ollama) as client:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye!")
                    break

                # Stream response
                print("Assistant: ", end='', flush=True)

                full_response = ""
                chunk_count = 0

                try:
                    for chunk in client.generate_stream(user_input):
                        if chunk.error:
                            print(f"\n\n✗ Error: {chunk.error}")
                            break

                        print(chunk.text, end='', flush=True)
                        full_response += chunk.text
                        chunk_count += 1

                        if chunk.done:
                            print()  # Newline after response
                            break

                except KeyboardInterrupt:
                    print("\n\n[Generation interrupted by user]")
                    continue

                # Show stats for this response
                if full_response:
                    print(f"  (Received {chunk_count} chunks, "
                          f"{len(full_response)} characters)\n")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}\n")
                continue


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
        sys.exit(0)
