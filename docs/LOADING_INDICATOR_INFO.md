# Loading Indicator Feature

## What It Does

When you ask the AI a question, you'll now see an animated spinner while it's thinking:

```
⠋ AI is thinking...
```

The spinner rotates through different frames to show that the program is working and hasn't frozen.

## How It Looks

When you chat with the AI:

```
You: What is Python?
⠹ AI is thinking...
AI: Python is a high-level programming language...

You: Tell me a joke
⠼ AI is thinking...
AI: Why did the programmer quit his job? Because...
```

The spinner disappears once the AI finishes responding.

## Customizing the Spinner

You can change the spinner style by editing `ollama_api_example.py` around line 25.

### Available Spinner Styles

**Current style (Braille spinner):**
```python
self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
```
Animation: ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏

**Classic spinner:**
```python
self.spinner = itertools.cycle(['|', '/', '-', '\\'])
```
Animation: | / - \

**Moon phases:**
```python
self.spinner = itertools.cycle(['◐', '◓', '◑', '◒'])
```
Animation: ◐ ◓ ◑ ◒

**Dots spinner:**
```python
self.spinner = itertools.cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
```
Animation: ⣾ ⣽ ⣻ ⢿ ⡿ ⣟ ⣯ ⣷

**Simple dots:**
```python
self.spinner = itertools.cycle(['.  ', '.. ', '...'])
```
Animation: .   ..  ...

**Arrow:**
```python
self.spinner = itertools.cycle(['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'])
```
Animation: ← ↖ ↑ ↗ → ↘ ↓ ↙

**Box bounce:**
```python
self.spinner = itertools.cycle(['▖', '▘', '▝', '▗'])
```
Animation: ▖ ▘ ▝ ▗

### Custom Message

You can also change the message by editing line 76:

```python
# Change "AI is thinking" to whatever you want
loader = LoadingIndicator("AI is thinking")

# Examples:
loader = LoadingIndicator("Processing")
loader = LoadingIndicator("Please wait")
loader = LoadingIndicator("Generating response")
```

## Disabling the Loading Indicator

If you don't want the loading indicator, you can disable it:

### For the entire script:
Change line 76 in `chat()` function:
```python
# From:
if show_loading:
    loader = LoadingIndicator("AI is thinking")
    loader.start()

# To:
show_loading = False  # Add this line
if show_loading:
    loader = LoadingIndicator("AI is thinking")
    loader.start()
```

### For a single call:
```python
# When calling chat() function
response = chat("Your question", show_loading=False)
```

## Technical Details

- Uses threading to run the animation in the background
- Updates every 0.1 seconds (10 frames per second)
- Automatically clears the line when done
- Won't interfere with the AI's response
- Thread-safe and gracefully handles interrupts

## Troubleshooting

**Spinner doesn't show:**
- Your terminal might not support Unicode characters
- Try the classic spinner: `['|', '/', '-', '\\']`

**Spinner leaves artifacts:**
- This can happen in some terminals
- The code clears the line, but some terminals may need adjustment
- Try adding a newline before the response

**Animation is too fast/slow:**
- Edit line 36 to change speed
- `time.sleep(0.1)` - decrease for faster, increase for slower
- Examples:
  - `time.sleep(0.05)` - faster
  - `time.sleep(0.2)` - slower

## Performance Impact

The loading indicator has minimal performance impact:
- Uses a separate thread (doesn't slow down the API call)
- Very low CPU usage (~0.1%)
- No impact on AI response time
