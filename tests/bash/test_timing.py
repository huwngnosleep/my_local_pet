#!/usr/bin/env python3
"""
Test timing feature
Shows how long each step takes
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import start

def test_simple_query():
    """Test timing for simple query (no tools)"""
    print("=" * 60)
    print("Test 1: Simple Query (No Tools)")
    print("=" * 60)

    response = start.chat("What is Python?", use_tools=False, show_timing=True)
    print(f"\nResponse: {response[:100]}...")
    print()

def test_web_search_query():
    """Test timing for web search query"""
    print("=" * 60)
    print("Test 2: Web Search Query (With Tools)")
    print("=" * 60)

    response = start.chat("What are the latest Python releases?", use_tools=True, show_timing=True)
    print(f"\nResponse: {response[:200]}...")
    print()

def test_without_timing():
    """Test with timing disabled"""
    print("=" * 60)
    print("Test 3: Without Timing Display")
    print("=" * 60)

    response = start.chat("Hello!", use_tools=False, show_timing=False)
    print(f"\nResponse: {response}")
    print()

if __name__ == "__main__":
    print("\nTiming Feature Test")
    print("=" * 60)
    print("This will show timing information for different scenarios")
    print("=" * 60)
    print()

    try:
        # Test 1: Simple query
        test_simple_query()

        # Test 2: Web search (if user wants)
        if len(sys.argv) > 1 and sys.argv[1] == "--full":
            test_web_search_query()
        else:
            print("Skipping web search test (use --full to include)")
            print()

        # Test 3: No timing
        test_without_timing()

        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
