# Audio Chatbot - Voice Interactive Mode

## Overview

The Audio Chatbot provides a **voice-interactive interface** where you can:
1. 🎤 Speak your questions into the microphone
2. 🔄 Speech is automatically converted to text
3. 🤖 AI processes your query with streaming responses
4. 📝 Response appears in real-time as text

## Features

- **Voice Input**: Speak naturally, no typing required
- **Real-time Streaming**: See AI responses as they're generated
- **Web Search Integration**: Full tool support (web search, etc.)
- **Automatic Calibration**: Adjusts for ambient noise
- **Hands-free Operation**: Perfect for accessibility or multitasking
- **Free Speech Recognition**: Uses Google's free API (requires internet)

## Quick Start

### Installation

```bash
# Install audio dependencies
pip install -r requirements_audio.txt

# Or install manually
pip install SpeechRecognition pyaudio
```

#### Platform-Specific Setup

**Windows:**
```bash
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

### Basic Usage

```bash
# Start interactive voice chat
python start_audio.py

# Test microphone
python start_audio.py --test

# Single query mode
python start_audio.py --single
```

## How It Works

### Voice Input Flow

```
Microphone
    ↓
Capture Audio (PyAudio)
    ↓
Speech Recognition (Google API)
    ↓
Convert to Text
    ↓
ChatBot Processing
    ↓
Streaming Text Response
```

### Example Session

```
🎤 Listening... (speak now)
✓ Recognized: "What is Python?"

[Query #1]
You said: What is Python?
------------------------------------------------------------
AI: Python is a high-level, interpreted programming language
    known for its simplicity and readability...

[Timing] Total: 3.2s

🎤 Listening... (speak now)
✓ Recognized: "Tell me about machine learning"

[Query #2]
You said: Tell me about machine learning
------------------------------------------------------------
AI: Machine learning is a subset of artificial intelligence...
```

## API Reference

### AudioChatBot Class

```python
class AudioChatBot:
    """Voice-interactive chatbot using microphone input."""

    def __init__(self, config: Config = None):
        """Initialize audio chatbot."""

    def test_microphone(self) -> bool:
        """Test microphone availability."""

    def calibrate_microphone(self) -> None:
        """Calibrate for ambient noise."""

    def listen_for_speech(self, timeout: int = 10) -> str:
        """Listen and convert speech to text."""

    def interactive_voice_chat(self) -> None:
        """Run interactive voice chat session."""

    def single_voice_query(self, auto_listen: bool = True) -> str:
        """Process a single voice query."""
```

## Usage Examples

### Example 1: Interactive Voice Chat

```python
from start_audio import AudioChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True

bot = AudioChatBot(config=config)
bot.interactive_voice_chat()
```

Console Output:
```
🎤 Listening... (speak now)
✓ Recognized: "What's the weather in Tokyo?"

You said: What's the weather in Tokyo?
------------------------------------------------------------
[Tool: web_search] (Executing...)
[Tool: web_search] (Completed in 1.2s)

AI: [Streaming response with weather information...]
```

### Example 2: Single Voice Query

```python
from start_audio import AudioChatBot

bot = AudioChatBot()
response = bot.single_voice_query()
# Listens for speech, processes, returns response
```

### Example 3: Custom Configuration

```python
from start_audio import AudioChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True
config.ui.show_timing = True
config.ollama.temperature = 0.7

bot = AudioChatBot(config=config)

# Customize recognition settings
bot.recognizer.energy_threshold = 3000  # Lower = more sensitive
bot.recognizer.pause_threshold = 1.0    # Seconds of silence

bot.interactive_voice_chat()
```

### Example 4: Programmatic Control

```python
from start_audio import AudioChatBot
import speech_recognition as sr

bot = AudioChatBot()

# Test microphone first
if bot.test_microphone():
    # Calibrate
    bot.calibrate_microphone()

    # Listen and process
    while True:
        speech = bot.listen_for_speech(timeout=10)

        if speech.lower() in ['exit', 'quit']:
            break

        if speech:
            response = bot.chatbot.chat_stream(speech)
            print(f"Response: {response}")
```

## Configuration

### Speech Recognition Settings

```python
# Energy threshold (higher = less sensitive to background noise)
bot.recognizer.energy_threshold = 4000  # Default: 4000

# Dynamic adjustment (adapts to changing noise levels)
bot.recognizer.dynamic_energy_threshold = True

# Pause threshold (seconds of silence to consider end of speech)
bot.recognizer.pause_threshold = 0.8  # Default: 0.8

# Timeouts
timeout = 10              # Max seconds to wait for speech start
phrase_time_limit = 30    # Max seconds for entire phrase
```

### ChatBot Configuration

All standard chatbot settings apply:

```python
config.ui.use_streaming = True     # Streaming responses
config.ui.show_timing = True       # Show timing
config.ollama.model_name = "phi3:mini"
config.ollama.temperature = 1.0
```

## Command Line Options

### Interactive Mode (Default)

```bash
python start_audio.py
```

Starts continuous voice chat session:
- Listen → Recognize → Process → Respond
- Say "exit" or "quit" to end
- Press Ctrl+C to interrupt

### Test Mode

```bash
python start_audio.py --test
```

Tests microphone and calibration:
- Checks microphone availability
- Tests audio capture
- Calibrates for ambient noise
- Displays settings

### Single Query Mode

```bash
python start_audio.py --single
```

Processes one voice query then exits:
- Listen for single question
- Process and respond
- Exit automatically

## Speech Recognition

### Supported Languages

The default Google Speech Recognition supports multiple languages:

```python
# English (default)
text = bot.recognizer.recognize_google(audio)

# Spanish
text = bot.recognizer.recognize_google(audio, language="es-ES")

# French
text = bot.recognizer.recognize_google(audio, language="fr-FR")

# Japanese
text = bot.recognizer.recognize_google(audio, language="ja-JP")
```

### Recognition Engines

While the default uses Google's free API, you can use alternatives:

```python
import speech_recognition as sr

# Google (default, free, requires internet)
text = recognizer.recognize_google(audio)

# Sphinx (offline, less accurate)
text = recognizer.recognize_sphinx(audio)

# Whisper (requires OpenAI API)
# text = recognizer.recognize_whisper_api(audio, api_key="...")
```

## Troubleshooting

### Issue: Microphone Not Detected

**Symptoms:**
```
[!] Microphone error: No module named '_portaudio'
```

**Solutions:**

**Windows:**
```bash
pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install --upgrade pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install --force-reinstall pyaudio
```

### Issue: Speech Not Recognized

**Symptoms:**
```
❌ Could not understand audio
```

**Solutions:**

1. **Speak clearly and louder**
2. **Reduce background noise**
3. **Adjust sensitivity:**
   ```python
   bot.recognizer.energy_threshold = 2000  # Lower = more sensitive
   ```
4. **Increase pause threshold:**
   ```python
   bot.recognizer.pause_threshold = 1.5  # More time to speak
   ```
5. **Re-calibrate:**
   ```python
   bot.calibrate_microphone()
   ```

### Issue: Timeout Before Speaking

**Symptoms:**
```
⏱️  No speech detected (timeout)
```

**Solution:**
```python
# Increase timeout
speech = bot.listen_for_speech(timeout=20)  # 20 seconds
```

### Issue: Speech Recognition Service Error

**Symptoms:**
```
❌ Speech recognition service error: [...]
```

**Causes:**
- No internet connection (Google API requires internet)
- Too many requests (rate limiting)
- Service temporarily unavailable

**Solutions:**
1. Check internet connection
2. Wait a few seconds and try again
3. Consider using offline recognition (Sphinx)

### Issue: Audio Cutting Off

**Symptoms:**
Last words of speech not captured

**Solution:**
```python
# Increase phrase time limit
bot.recognizer.phrase_time_limit = 45  # 45 seconds max
```

### Issue: Background Noise

**Symptoms:**
False triggers or poor recognition

**Solutions:**

1. **Use a better microphone** (headset recommended)
2. **Reduce ambient noise**
3. **Calibrate in actual usage environment:**
   ```python
   bot.calibrate_microphone()  # Run in noisy environment
   ```
4. **Increase energy threshold:**
   ```python
   bot.recognizer.energy_threshold = 5000  # Less sensitive
   ```

## Best Practices

### ✅ Do

1. **Use a quality microphone**
   - Headset or USB mic recommended
   - Built-in laptop mics work but may need calibration

2. **Calibrate in your environment**
   ```python
   bot.calibrate_microphone()  # Before starting
   ```

3. **Speak clearly and at normal pace**
   - No need to shout
   - Pause briefly between sentences

4. **Use in quiet environment**
   - Reduces false triggers
   - Improves recognition accuracy

5. **Check internet connection**
   - Google Speech Recognition requires internet
   - Test with `--test` mode first

### ❌ Don't

1. **Don't speak while microphone is processing**
   - Wait for "Listening..." prompt

2. **Don't use in very noisy environments**
   - Background conversations
   - Music or TV
   - Mechanical noise

3. **Don't speak too fast or mumble**
   - Recognition accuracy decreases

4. **Don't rely on it offline**
   - Default uses Google API (internet required)

## Performance Tips

### Reduce Latency

1. **Use wired internet** (vs WiFi)
2. **Reduce phrase_time_limit** if possible
3. **Lower pause_threshold** for faster detection
   ```python
   bot.recognizer.pause_threshold = 0.6  # Faster cutoff
   ```

### Improve Accuracy

1. **Use external microphone**
2. **Calibrate properly**
3. **Speak in quiet environment**
4. **Use your natural speaking voice**

## Advanced Usage

### Custom Wake Word

```python
from start_audio import AudioChatBot
import speech_recognition as sr

bot = AudioChatBot()

def wait_for_wake_word():
    """Listen for 'hey assistant' wake word."""
    while True:
        speech = bot.listen_for_speech(timeout=5)
        if "hey assistant" in speech.lower():
            print("🎤 Activated!")
            return True

# Usage
while True:
    if wait_for_wake_word():
        speech = bot.listen_for_speech(timeout=10)
        if speech:
            bot.chatbot.chat_stream(speech)
```

### Continuous Listening

```python
from start_audio import AudioChatBot

bot = AudioChatBot()

# Listen continuously without re-calibration
while True:
    speech = bot.listen_for_speech(timeout=None)  # No timeout
    if speech:
        if "exit" in speech.lower():
            break
        bot.chatbot.chat_stream(speech)
```

### Multi-Language Support

```python
from start_audio import AudioChatBot
import speech_recognition as sr

bot = AudioChatBot()

# Detect language and respond
with sr.Microphone() as source:
    audio = bot.recognizer.listen(source)

    # Try multiple languages
    for lang_code, lang_name in [("en-US", "English"), ("es-ES", "Spanish")]:
        try:
            text = bot.recognizer.recognize_google(audio, language=lang_code)
            print(f"Detected {lang_name}: {text}")
            break
        except:
            continue
```

## Integration Examples

### Voice-Controlled Assistant

```python
from start_audio import AudioChatBot

bot = AudioChatBot()

commands = {
    "what time": lambda: bot.chatbot.chat_stream("What time is it?"),
    "weather": lambda: bot.chatbot.chat_stream("What's the weather?"),
    "news": lambda: bot.chatbot.chat_stream("Latest news"),
}

while True:
    speech = bot.listen_for_speech()

    # Check for commands
    for keyword, action in commands.items():
        if keyword in speech.lower():
            action()
            break
    else:
        # General query
        bot.chatbot.chat_stream(speech)
```

### Log All Queries

```python
from start_audio import AudioChatBot
import json
from datetime import datetime

bot = AudioChatBot()

log_file = "voice_queries.json"
queries = []

try:
    while True:
        speech = bot.listen_for_speech()
        if speech:
            timestamp = datetime.now().isoformat()
            queries.append({
                "timestamp": timestamp,
                "query": speech
            })

            # Save log
            with open(log_file, 'w') as f:
                json.dump(queries, f, indent=2)

            # Process
            bot.chatbot.chat_stream(speech)

except KeyboardInterrupt:
    print(f"\nSaved {len(queries)} queries to {log_file}")
```

## Testing

### Test Microphone

```bash
python start_audio.py --test
```

Expected output:
```
[OK] Microphone detected

[Calibrating microphone for ambient noise...]
Please remain silent for a moment...
[OK] Calibration complete
    Energy threshold: 4238

✓ All tests passed
```

### Test Recognition

```python
from start_audio import AudioChatBot

bot = AudioChatBot()

# Test speech recognition
if bot.test_microphone():
    bot.calibrate_microphone()

    print("\nSay something...")
    text = bot.listen_for_speech(timeout=10)

    if text:
        print(f"✓ Recognized: {text}")
    else:
        print("✗ No speech recognized")
```

## Security & Privacy

### Data Handling

- **Audio data**: Sent to Google Speech Recognition API
- **Text queries**: Processed by local Ollama instance
- **No audio storage**: Audio is not saved locally by default
- **Internet required**: For speech recognition (Google API)

### Privacy Considerations

1. **Audio sent to Google**: Speech is processed by Google's servers
2. **Local AI processing**: Ollama runs locally, queries stay on your machine
3. **No recording**: Audio not saved unless you explicitly implement it
4. **Internet traffic**: Both speech API and web search use internet

### Offline Alternative

For complete privacy, use offline speech recognition:

```python
import speech_recognition as sr

# Use Sphinx (offline, less accurate)
bot.recognizer.recognize_sphinx(audio)
```

## Accessibility

The audio chatbot is particularly useful for:

- **Visual impairments**: Hands-free, voice-only interaction
- **Motor disabilities**: No keyboard/mouse required
- **Multitasking**: Use while doing other tasks
- **Learning disabilities**: Speak naturally instead of typing

## Limitations

1. **Requires internet**: Google Speech Recognition needs connection
2. **Accuracy varies**: Depends on accent, pronunciation, background noise
3. **Language support**: Best for English; other languages vary in accuracy
4. **No speech output**: Responses are text-only (TTS can be added)
5. **Latency**: ~1-3 seconds for speech recognition

## Future Enhancements

Potential improvements:

- [ ] Text-to-speech (TTS) for audio responses
- [ ] Offline speech recognition (Whisper)
- [ ] Wake word detection
- [ ] Voice activity detection (VAD)
- [ ] Multi-language auto-detection
- [ ] Audio recording/playback
- [ ] Speaker identification
- [ ] Emotion detection from voice

## References

- **Implementation**: [start_audio.py](../start_audio.py)
- **Dependencies**: [requirements_audio.txt](../requirements_audio.txt)
- **SpeechRecognition Docs**: https://pypi.org/project/SpeechRecognition/
- **PyAudio Docs**: https://people.csail.mit.edu/hubert/pyaudio/

## Related Documentation

- [ChatBot Streaming](./chatbot_streaming.md) - Text-based streaming
- [Streaming Quick Start](./streaming_quick_start.md) - Quick reference
- [Configuration](../config.py) - Configuration options
