# Search Result Processing Guide

This guide explains the three methods for processing web search results before feeding them to your main model.

## Why Process Search Results?

Web search results can be very long (500+ characters per result). Processing them:
- Reduces context size for the main model
- Speeds up response time
- Reduces timeout errors
- Extracts only relevant information

## Processing Methods

### 1. Simple Truncation (`"simple"`)

**How it works:**
- Just cuts text at 200 characters
- Breaks at word boundary

**Pros:**
- Fastest (instant)
- No extra processing
- No dependencies

**Cons:**
- May cut off important information
- Not smart about relevance

**Best for:**
- Maximum speed
- Very slow hardware

**Example:**
```
Input: "Python 3.13 has been released with many new features including improved error messages..."
Output: "Python 3.13 has been released with many new features including improved error..."
```

---

### 2. Algorithmic Extraction (`"extraction"`) ⭐ RECOMMENDED

**How it works:**
- Splits text into sentences
- Scores each sentence based on word overlap with your query
- Returns most relevant sentences (up to 150 chars)

**Pros:**
- Fast (< 1 second)
- Smart - extracts relevant info
- No extra model needed
- Good balance

**Cons:**
- Simple word matching (not semantic understanding)

**Best for:**
- Most use cases
- Good hardware balance

**Example:**
```
Query: "Python 3.13 performance"
Input: "Python 3.13 released. New syntax added. Performance improved 20%. Better error messages."
Output: "Performance improved 20%. Python 3.13 released."
```

---

### 3. Small Model Summarization (`"small_model"`)

**How it works:**
- Uses a tiny model (tinyllama) to summarize
- Understands context and semantics
- Generates 1-2 sentence summary

**Pros:**
- Smartest extraction
- Semantic understanding
- Best quality summaries

**Cons:**
- Slower (5-10 seconds per result)
- Requires tinyllama model
- Uses extra resources

**Best for:**
- When you need highest quality
- Good hardware
- Willing to wait longer

**Requirements:**
```bash
ollama pull tinyllama
```

**Example:**
```
Query: "Python 3.13 performance"
Input: "Python 3.13 has been released with various improvements. The JIT compiler has been added experimentally. Performance benchmarks show 20% improvement in some cases. Error messages are clearer."
Output: "Python 3.13 includes a new JIT compiler with performance improvements up to 20% in benchmarks."
```

## How to Switch Methods

Edit `start.py` line 25:

```python
# Choose one:
SEARCH_PROCESSING = "extraction"    # Recommended
SEARCH_PROCESSING = "simple"        # Fastest
SEARCH_PROCESSING = "small_model"   # Smartest (needs tinyllama)
```

## Test Different Methods

Run the comparison script:

```bash
python tests/test_search_processing.py "your search query"
```

This will test all three methods and show:
- Processing time
- Result size
- Speed comparison

## Performance Comparison

| Method       | Speed    | Quality  | Resources | Recommended For |
|-------------|----------|----------|-----------|-----------------|
| simple      | ★★★★★   | ★★       | Minimal   | Slow hardware   |
| extraction  | ★★★★    | ★★★★     | Minimal   | Most users ⭐   |
| small_model | ★★      | ★★★★★   | High      | Best quality    |

## Context Size Reduction

**Without processing:** ~600-900 chars per result
**With extraction:** ~300-450 chars per result
**With small_model:** ~200-300 chars per result

This 40-60% reduction significantly speeds up the main model's response time.
