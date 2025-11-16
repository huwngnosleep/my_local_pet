#!/usr/bin/env python3
"""
Test different search processing methods
Compare speed and output quality
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ddgs import DDGS

# Import the processing functions
import start

def test_processing_method(method, query):
    """Test a specific processing method"""
    print(f"\n{'='*60}")
    print(f"Method: {method.upper()}")
    print(f"{'='*60}")

    # Temporarily change the config
    original_method = start.SEARCH_PROCESSING
    start.SEARCH_PROCESSING = method

    start_time = time.time()
    result = start.web_search(query, max_results=3)
    elapsed = time.time() - start_time

    # Restore original config
    start.SEARCH_PROCESSING = original_method

    print(f"Time taken: {elapsed:.2f} seconds")
    print(f"\nResults:\n{result}")
    print(f"\nContext size: {len(result)} characters")

    return elapsed, len(result)

def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "latest Python 3.13 features"

    print(f"Testing search query: '{query}'")
    print("="*60)

    methods = ["simple", "extraction", "small_model"]
    results = {}

    for method in methods:
        try:
            elapsed, size = test_processing_method(method, query)
            results[method] = {"time": elapsed, "size": size}
        except Exception as e:
            print(f"\nError with {method}: {e}")

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Method':<15} {'Time (s)':<12} {'Size (chars)':<15} {'Speed'}")
    print("-"*60)

    for method in methods:
        if method in results:
            r = results[method]
            speed = "★★★" if r['time'] < 5 else "★★" if r['time'] < 10 else "★"
            print(f"{method:<15} {r['time']:<12.2f} {r['size']:<15} {speed}")

    print("\nRecommendation:")
    print("- Use 'extraction' for best balance of speed and quality")
    print("- Use 'simple' if you want maximum speed")
    print("- Use 'small_model' if you need smartest extraction (requires tinyllama)")

if __name__ == "__main__":
    main()
