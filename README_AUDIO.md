# 🎤 Audio Chatbot - Voice Interactive AI

> Talk to your AI assistant using your microphone!

## Overview

The **Audio Chatbot** adds voice interaction to the Ollama chatbot, allowing you to:
- 🎤 **Speak** your questions instead of typing
- 🔄 **Automatic** speech-to-text conversion
- 🤖 **Real-time** AI responses with streaming
- 🔍 **Full integration** with web search and tools
- 🆓 **Free** using Google Speech Recognition

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_audio.txt
```

**Platform-specific:**

- **Windows**: `pip install pyaudio`
- **macOS**: `brew install portaudio && pip install pyaudio`
- **Linux**: `sudo apt-get install python3-pyaudio portaudio19-dev && pip install pyaudio`

### 2. Run Voice Chat

```bash
python start_audio.py
```

### 3. Talk to Your AI!

```
🎤 Listening... (speak now)
✓ Recognized: "What is Python?"

You said: What is Python?
------------------------------------------------------------
AI: Python is a high-level, interpreted programming language
    known for its simplicity and readability...
```

## Features

| Feature | Description |
|---------|-------------|
| 🎤 Voice Input | Speak naturally, no typing required |
| 🔄 Speech-to-Text | Automatic conversion using Google API |
| 📝 Streaming Responses | See AI responses in real-time |
| 🔍 Web Search | Full tool integration (web search, etc.) |
| 🌐 Multi-Language | Support for multiple languages |
| ♿ Accessibility | Perfect for hands-free operation |
| 🆓 Free API | Uses Google's free speech recognition |

## Usage Modes

### Interactive Mode (Default)

```bash
python start_audio.py
```

Continuous voice chat:
- Speak → AI responds → Repeat
- Say "exit" or "quit" to end
- Press Ctrl+C to interrupt

### Test Mode

```bash
python start_audio.py --test
```

Test your microphone and calibration

### Single Query Mode

```bash
python start_audio.py --single
```

Ask one question, get answer, exit

## Example Session

```
🎤 VOICE-INTERACTIVE CHATBOT
============================================================
Model: tinyllama
Streaming: Enabled
Web Search: Enabled

Controls:
  - Speak your question into the microphone
  - Say 'exit', 'quit', or 'goodbye' to end
  - Press Ctrl+C to interrupt
============================================================

🎤 Listening... (speak now)
✓ Recognized: "What's the weather in Tokyo?"

[Query #1]
You said: What's the weather in Tokyo?
------------------------------------------------------------
[Tool: web_search] (Executing...)
[Tool: web_search] (Completed in 1.2s)

AI: Based on the latest information, Tokyo is currently experiencing
    partly cloudy weather with temperatures around 18°C (64°F)...

[Timing] Total: 4.5s

🎤 Listening... (speak now)
```

## Configuration

```python
from start_audio import AudioChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True
config.ui.show_timing = True

bot = AudioChatBot(config=config)

# Adjust microphone sensitivity
bot.recognizer.energy_threshold = 3000  # Lower = more sensitive
bot.recognizer.pause_threshold = 1.0    # Seconds of silence

bot.interactive_voice_chat()
```

## Python API

```python
from start_audio import AudioChatBot

# Create audio chatbot
bot = AudioChatBot()

# Test microphone
if bot.test_microphone():
    # Calibrate for ambient noise
    bot.calibrate_microphone()

    # Interactive voice chat
    bot.interactive_voice_chat()

    # Or single query
    response = bot.single_voice_query()
```

## Requirements

### Core Dependencies

- Python 3.10+
- `SpeechRecognition` >= 3.10.0
- `PyAudio` >= 0.2.13

### System Requirements

- **Microphone** (built-in or external)
- **Internet connection** (for Google Speech API)
- **Ollama** running locally

## Best Practices

### ✅ Recommended

- Use a **headset** or external microphone
- Speak **clearly** at normal pace
- Use in a **quiet environment**
- Check **internet connection**
- **Calibrate** before each session

### ❌ Avoid

- Speaking in **noisy environments**
- **Speaking too fast** or mumbling
- Using **built-in laptop mic** in noisy rooms
- Expecting it to work **offline**

## Troubleshooting

### Microphone Not Detected

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

### Speech Not Recognized

- Speak **louder and clearer**
- Check **internet connection**
- **Reduce background noise**
- **Re-calibrate** (restart app)
- Lower energy threshold:
  ```python
  bot.recognizer.energy_threshold = 2000
  ```

### Timeout Issues

Increase timeout:
```python
speech = bot.listen_for_speech(timeout=20)  # 20 seconds
```

## Advanced Features

### Multi-Language Support

```python
# Recognize in Spanish
text = bot.recognizer.recognize_google(audio, language="es-ES")

# Recognize in French
text = bot.recognizer.recognize_google(audio, language="fr-FR")

# Recognize in Japanese
text = bot.recognizer.recognize_google(audio, language="ja-JP")
```

### Custom Wake Word

```python
from start_audio import AudioChatBot

bot = AudioChatBot()

while True:
    speech = bot.listen_for_speech(timeout=5)

    # Activate on "hey assistant"
    if "hey assistant" in speech.lower():
        print("Activated!")
        query = bot.listen_for_speech(timeout=10)
        bot.chatbot.chat_stream(query)
```

### Continuous Listening

```python
from start_audio import AudioChatBot

bot = AudioChatBot()

# Listen continuously
while True:
    speech = bot.listen_for_speech(timeout=None)
    if speech:
        if "exit" in speech.lower():
            break
        bot.chatbot.chat_stream(speech)
```

## Privacy & Security

### What Gets Sent Where

- **Audio → Google**: Speech recognition (Google Speech API)
- **Text → Local**: Processing via Ollama (stays on your machine)
- **Web Search → Internet**: Only when using web search tool

### Privacy Notes

- ✅ AI processing is **local** (Ollama)
- ⚠️ Speech recognition uses **Google servers**
- ✅ No audio is **saved** by default
- ⚠️ Requires **internet** for speech recognition

### Offline Alternative

For complete privacy, use offline recognition:
```python
# Use CMU Sphinx (offline, less accurate)
text = bot.recognizer.recognize_sphinx(audio)
```

## Use Cases

### Accessibility

Perfect for users with:
- Visual impairments
- Motor disabilities
- Dyslexia or typing difficulties

### Productivity

Great for:
- Hands-free operation while multitasking
- Quick voice queries
- Brainstorming sessions
- Research while taking notes

### Learning

Useful for:
- Practicing pronunciation
- Language learning
- Voice-based study sessions

## Documentation

- **[Quick Start Guide](./docs/AUDIO_QUICK_START.md)** - Get started fast
- **[Complete Documentation](./docs/audio_chatbot.md)** - Full guide
- **[ChatBot Streaming](./docs/chatbot_streaming.md)** - Text-based streaming
- **[API Reference](./docs/audio_chatbot.md#api-reference)** - Python API

## Architecture

```
Microphone
    ↓
PyAudio (Audio Capture)
    ↓
SpeechRecognition (Speech → Text)
    ↓
Google Speech API
    ↓
Text Query
    ↓
ChatBot (with Streaming)
    ↓
Ollama (Local AI)
    ↓
Streaming Text Response
```

## Comparison: Text vs Voice

| Feature | Text Mode | Voice Mode |
|---------|-----------|------------|
| Input | Typing | Speaking |
| Speed | Fast typing | Natural speech |
| Hands-free | No | Yes |
| Accessibility | Requires keyboard | Voice-only |
| Internet | Optional | Required (speech API) |
| Accuracy | 100% | 95%+ (varies) |
| Entry Point | `start.py` | `start_audio.py` |

## Future Enhancements

Planned features:
- [ ] Text-to-speech (TTS) for audio responses
- [ ] Offline speech recognition (Whisper)
- [ ] Wake word detection
- [ ] Voice activity detection (VAD)
- [ ] Multi-speaker support
- [ ] Emotion detection
- [ ] Audio recording/playback

## Contributing

Improvements welcome! Key areas:
- Better offline recognition
- TTS integration
- Wake word detection
- Multi-language improvements

## License

Same as main project license.

## Credits

- **SpeechRecognition** library by Anthony Zhang
- **PyAudio** for audio capture
- **Google Speech API** for recognition
- **Ollama** for local AI processing

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting)
- Read [Full Documentation](./docs/audio_chatbot.md)
- Test with `python start_audio.py --test`

---

**Ready to talk to your AI?** 🎤

```bash
pip install -r requirements_audio.txt
python start_audio.py
```

**Say hello to the future of voice AI!** 🚀
