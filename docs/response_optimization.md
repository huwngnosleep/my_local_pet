# Response Length Optimization Guide

This guide explains how to control the length and verbosity of chatbot responses.

## Problem

LLM models tend to be verbose, providing long, detailed answers even for simple questions. For example:

**Question:** "Which city is Vietnam's capital?"

**Verbose Response:** "Hanoi is indeed still recognized today as the capital city of Vietnam. According to Wikipedia and other reputable sources, Hanoi has been an important center for more than a thousand years..." (300+ words)

**Desired Response:** "Ha Noi"

## Solutions

The chatbot now provides **four complementary approaches** to control response length:

### 1. Response Style (Recommended)

The most effective method is using **response styles** which change how the model generates answers through system prompt instructions.

#### Available Styles

- **CONCISE**: Brief, direct answers with minimal elaboration
- **NORMAL**: Balanced responses with moderate detail (default)
- **DETAILED**: Comprehensive answers with full explanations

#### Usage

**Method 1: Configure at startup**

```python
from config import Config, ResponseStyle
from chatbot import ChatBot

# Create config with concise responses
config = Config.from_defaults()
config.set_response_style(ResponseStyle.CONCISE)

# Initialize chatbot
bot = ChatBot(config=config)

# Ask questions
response = bot.chat("Which city is Vietnam's capital?")
print(response)  # Output: "Ha Noi"
```

**Method 2: Direct configuration**

```python
from config import Config, ResponseStyle, OllamaConfig
from chatbot import ChatBot

# Configure Ollama with concise style
ollama_config = OllamaConfig(
    response_style=ResponseStyle.CONCISE,
    temperature=0.3
)

config = Config(ollama_config=ollama_config)
bot = ChatBot(config=config)
```

### 2. Generation Parameters

Fine-tune the model's generation behavior using these parameters:

#### Temperature

Controls randomness and creativity. Lower values produce more focused, deterministic outputs.

- **Range:** 0.0 - 2.0
- **Default:** 0.3
- **Recommendation for conciseness:** 0.1 - 0.5

```python
config = Config.from_defaults()
config.set_temperature(0.2)  # Very focused, less verbose
```

#### Max Tokens (num_predict)

Limits the maximum number of tokens the model can generate.

- **Default:** -1 (unlimited)
- **Recommendation:** 50-100 for very short answers, 200-300 for normal

**Warning:** This truncates responses, which can cut off mid-sentence. Use response styles instead for natural brevity.

```python
config = Config.from_defaults()
config.set_max_tokens(50)  # Limit to 50 tokens
```

#### Top P (Nucleus Sampling)

Controls diversity of word selection.

- **Range:** 0.0 - 1.0
- **Default:** 0.9
- **Lower values** = less diverse, more predictable (slightly shorter)

```python
from config import Config, OllamaConfig

ollama_config = OllamaConfig(
    top_p=0.8,
    temperature=0.3
)

config = Config(ollama_config=ollama_config)
```

### 3. Combined Approach (Best Results)

For maximum conciseness, combine multiple techniques:

```python
from config import Config, ResponseStyle, OllamaConfig
from chatbot import ChatBot

# Create optimized config for concise responses
ollama_config = OllamaConfig(
    response_style=ResponseStyle.CONCISE,
    temperature=0.2,        # Low temperature = focused
    num_predict=100,        # Limit response length
    top_p=0.8              # Less diverse vocabulary
)

config = Config(ollama_config=ollama_config)
bot = ChatBot(config=config)

# Test with factual questions
response = bot.chat("Which city is Vietnam's capital?")
print(response)  # Expected: "Ha Noi" or "Hanoi"
```

### 4. Prompt Engineering

You can also specify output format in your questions:

```python
# Be explicit about desired format
bot.chat("Which city is Vietnam's capital? Answer with just the city name.")

# Request specific format
bot.chat("List the top 3 programming languages. Format: bullet points, one line each.")

# Set constraints
bot.chat("Explain Python in one sentence.")
```

## Complete Example

Here's a complete script demonstrating all approaches:

```python
#!/usr/bin/env python3
"""Example: Optimizing response length for concise answers."""

from config import Config, ResponseStyle, OllamaConfig
from chatbot import ChatBot


def example_concise_responses():
    """Demonstrate concise response configuration."""

    # Configure for maximum conciseness
    ollama_config = OllamaConfig(
        model_name="phi3:mini",
        response_style=ResponseStyle.CONCISE,
        temperature=0.2,
        num_predict=80,
        top_p=0.8
    )

    config = Config(ollama_config=ollama_config)
    bot = ChatBot(config=config)

    # Test questions
    questions = [
        "Which city is Vietnam's capital?",
        "What is 15 + 27?",
        "Who wrote Romeo and Juliet?",
        "What is the chemical symbol for gold?"
    ]

    print("=== Concise Response Mode ===\n")
    for question in questions:
        response = bot.chat(question, show_loading=False, show_timing=False)
        print(f"Q: {question}")
        print(f"A: {response}\n")


def example_detailed_responses():
    """Demonstrate detailed response configuration."""

    # Configure for detailed explanations
    config = Config.from_defaults()
    config.set_response_style(ResponseStyle.DETAILED)
    config.set_temperature(0.7)

    bot = ChatBot(config=config)

    print("=== Detailed Response Mode ===\n")
    response = bot.chat(
        "Which city is Vietnam's capital?",
        show_loading=False,
        show_timing=False
    )
    print(f"Q: Which city is Vietnam's capital?")
    print(f"A: {response}\n")


def example_dynamic_switching():
    """Demonstrate switching response styles dynamically."""

    config = Config.from_defaults()
    bot = ChatBot(config=config)

    question = "What is Python?"

    # Test all three styles
    for style in [ResponseStyle.CONCISE, ResponseStyle.NORMAL, ResponseStyle.DETAILED]:
        config.set_response_style(style)
        print(f"=== {style.value.upper()} Style ===")
        response = bot.chat(question, show_loading=False, show_timing=False)
        print(f"A: {response}\n")


if __name__ == "__main__":
    # Run examples
    example_concise_responses()
    print("\n" + "="*60 + "\n")
    example_detailed_responses()
    print("\n" + "="*60 + "\n")
    example_dynamic_switching()
```

## Recommendations by Use Case

### For Factual Q&A (e.g., trivia, definitions)

```python
ollama_config = OllamaConfig(
    response_style=ResponseStyle.CONCISE,
    temperature=0.1,
    num_predict=50
)
```

### For Conversational Chat

```python
ollama_config = OllamaConfig(
    response_style=ResponseStyle.NORMAL,
    temperature=0.5
)
```

### For Educational/Explanatory Content

```python
ollama_config = OllamaConfig(
    response_style=ResponseStyle.DETAILED,
    temperature=0.7,
    num_predict=-1  # No limit
)
```

### For Code Generation

```python
ollama_config = OllamaConfig(
    response_style=ResponseStyle.CONCISE,
    temperature=0.3,
    num_predict=500  # Allow longer for code
)
```

## Testing Your Configuration

Create a test script to verify your settings:

```python
from config import Config, ResponseStyle
from chatbot import ChatBot

# Your configuration
config = Config.from_defaults()
config.set_response_style(ResponseStyle.CONCISE)
config.set_temperature(0.2)

bot = ChatBot(config=config)

# Test questions
test_cases = [
    ("Which city is Vietnam's capital?", "Ha Noi"),
    ("What is 2+2?", "4"),
    ("Who invented Python?", "Guido van Rossum")
]

for question, expected in test_cases:
    response = bot.chat(question, show_loading=False, show_timing=False)
    print(f"Q: {question}")
    print(f"Expected: ~{expected}")
    print(f"Got: {response}")
    print(f"Length: {len(response)} chars\n")
```

## Troubleshooting

### Responses still too long?

1. **Lower temperature further:** Try 0.1 or even 0.0
2. **Use stricter num_predict:** Set to 30-50 for very short answers
3. **Be explicit in prompts:** "Answer in 3 words or less"
4. **Try a different model:** Some models are naturally more concise

### Responses too short/incomplete?

1. **Increase num_predict or set to -1**
2. **Switch to NORMAL or DETAILED style**
3. **Raise temperature to 0.5-0.7**
4. **Avoid overly restrictive prompts**

### Responses cut off mid-sentence?

- **Problem:** num_predict is too low
- **Solution:** Increase num_predict or use response_style instead of token limits

## Summary

**Best Practice:** Use `ResponseStyle.CONCISE` with low temperature (0.2-0.3) for brief answers. Only use `num_predict` if you need hard limits, as it can truncate unnaturally.

**Key Takeaway:** Response styles use intelligent prompt engineering to guide the model toward natural brevity, while token limits forcefully truncate output.
