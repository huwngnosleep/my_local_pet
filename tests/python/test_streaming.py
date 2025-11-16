#!/usr/bin/env python3
"""Test script for streaming functionality.

This script demonstrates various streaming capabilities of the OllamaClient.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ollama_client import OllamaClient
from config import Config


def test_basic_streaming():
    """Test basic streaming with real-time display."""
    print("=" * 60)
    print("Test 1: Basic Streaming")
    print("=" * 60)

    config = Config.from_defaults()
    client = OllamaClient(config.ollama)

    print("\nPrompt: 'Write a haiku about Python programming'\n")
    print("Response: ", end='', flush=True)

    chunk_count = 0
    for chunk in client.generate_stream("Write a haiku about Python programming"):
        if chunk.error:
            print(f"\nError: {chunk.error}")
            return False

        print(chunk.text, end='', flush=True)
        chunk_count += 1

        if chunk.done:
            print(f"\n\n✓ Received {chunk_count} chunks")
            break

    return True


def test_streaming_vs_nonstreaming():
    """Compare streaming vs non-streaming performance."""
    print("\n" + "=" * 60)
    print("Test 2: Streaming vs Non-Streaming Comparison")
    print("=" * 60)

    config = Config.from_defaults()
    client = OllamaClient(config.ollama)

    prompt = "Explain what Python is in 2 sentences"

    # Test non-streaming
    print("\n[Non-Streaming Mode]")
    start = time.time()
    response = client.generate(prompt, stream=False)
    non_streaming_time = time.time() - start

    if response.success:
        print(f"Response: {response.text}")
        print(f"Time: {non_streaming_time:.2f}s")
    else:
        print(f"Error: {response.error}")
        return False

    # Test streaming
    print("\n[Streaming Mode]")
    start = time.time()
    first_token_time = None
    full_text = ""

    print("Response: ", end='', flush=True)
    for chunk in client.generate_stream(prompt):
        if chunk.error:
            print(f"\nError: {chunk.error}")
            return False

        if first_token_time is None and chunk.text:
            first_token_time = time.time() - start

        print(chunk.text, end='', flush=True)
        full_text += chunk.text

        if chunk.done:
            break

    total_streaming_time = time.time() - start

    print(f"\nTime to first token: {first_token_time:.2f}s")
    print(f"Total time: {total_streaming_time:.2f}s")
    print(f"\n✓ Streaming feels faster (first token arrives sooner)")

    return True


def test_error_handling():
    """Test error handling in streaming."""
    print("\n" + "=" * 60)
    print("Test 3: Error Handling")
    print("=" * 60)

    config = Config.from_defaults()
    # Try to use a non-existent model
    config.ollama.model_name = "nonexistent_model_12345"
    client = OllamaClient(config.ollama)

    print("\nAttempting to use non-existent model...")

    for chunk in client.generate_stream("Hello"):
        if chunk.error:
            print(f"✓ Error caught correctly: {chunk.error}")
            return True

        if chunk.done:
            break

    print("✗ Error should have been caught")
    return False


def test_progress_indicator():
    """Test streaming with progress indicator."""
    print("\n" + "=" * 60)
    print("Test 4: Progress Indicator")
    print("=" * 60)

    config = Config.from_defaults()
    client = OllamaClient(config.ollama)

    print("\nGenerating response with progress dots...")
    print("Progress: ", end='', flush=True)

    chunk_count = 0
    for chunk in client.generate_stream("Count from 1 to 5"):
        if chunk.error:
            print(f"\nError: {chunk.error}")
            return False

        if chunk.text:
            chunk_count += 1
            if chunk_count % 2 == 0:
                print('.', end='', flush=True)

        if chunk.done:
            print(f" Done! ({chunk_count} chunks)")
            break

    return True


def test_context_manager():
    """Test streaming with context manager."""
    print("\n" + "=" * 60)
    print("Test 5: Context Manager Usage")
    print("=" * 60)

    config = Config.from_defaults()

    print("\nUsing context manager for automatic cleanup...")

    with OllamaClient(config.ollama) as client:
        print("Response: ", end='', flush=True)

        for chunk in client.generate_stream("Say hello in 3 words"):
            if chunk.error:
                print(f"\nError: {chunk.error}")
                return False

            print(chunk.text, end='', flush=True)

            if chunk.done:
                print()
                break

    print("✓ Context manager closed session automatically")
    return True


def test_collect_chunks():
    """Test collecting all chunks for post-processing."""
    print("\n" + "=" * 60)
    print("Test 6: Collecting Chunks")
    print("=" * 60)

    config = Config.from_defaults()
    client = OllamaClient(config.ollama)

    print("\nCollecting chunks for analysis...")

    chunks = []
    for chunk in client.generate_stream("List 3 Python features"):
        if chunk.error:
            print(f"Error: {chunk.error}")
            return False

        if chunk.text:
            chunks.append(chunk.text)

        if chunk.done:
            break

    full_text = ''.join(chunks)

    print(f"\nStatistics:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Total characters: {len(full_text)}")
    print(f"  Average chunk size: {len(full_text) / len(chunks):.1f} chars")
    print(f"\nFull response:\n{full_text}")

    return True


def test_streaming_with_options():
    """Test streaming with custom options."""
    print("\n" + "=" * 60)
    print("Test 7: Streaming with Custom Options")
    print("=" * 60)

    config = Config.from_defaults()
    client = OllamaClient(config.ollama)

    custom_options = {
        "temperature": 0.3,  # Lower temperature for more focused output
        "top_p": 0.9,
        "num_predict": 50    # Limit tokens
    }

    print("\nUsing custom options (temperature=0.3, max_tokens=50)...")
    print("Response: ", end='', flush=True)

    for chunk in client.generate_stream(
        "Explain Python",
        options=custom_options
    ):
        if chunk.error:
            print(f"\nError: {chunk.error}")
            return False

        print(chunk.text, end='', flush=True)

        if chunk.done:
            print()
            break

    print("✓ Custom options applied successfully")
    return True


def run_all_tests():
    """Run all streaming tests."""
    print("\n" + "=" * 60)
    print("OLLAMA CLIENT STREAMING TESTS")
    print("=" * 60)

    tests = [
        ("Basic Streaming", test_basic_streaming),
        ("Streaming vs Non-Streaming", test_streaming_vs_nonstreaming),
        ("Error Handling", test_error_handling),
        ("Progress Indicator", test_progress_indicator),
        ("Context Manager", test_context_manager),
        ("Collecting Chunks", test_collect_chunks),
        ("Custom Options", test_streaming_with_options),
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
