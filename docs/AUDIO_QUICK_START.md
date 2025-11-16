# Audio Chatbot - Quick Start

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_audio.txt
```

Or manually:
```bash
pip install SpeechRecognition pyaudio
```

### 2. Platform Setup

**Windows:**
```bash
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

## Basic Usage

### Interactive Voice Chat

```bash
python start_audio.py
```

**What happens:**
1. Microphone calibrates for ambient noise
2. Says "🎤 Listening..." when ready
3. Speak your question naturally
4. AI responds with streaming text
5. Repeat or say "exit" to quit

### Test Your Microphone

```bash
python start_audio.py --test
```

### Single Query

```bash
python start_audio.py --single
```

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
✓ Recognized: "What is Python?"

[Query #1]
You said: What is Python?
------------------------------------------------------------
AI: Python is a high-level, interpreted programming language
    known for its simplicity and readability. It was created
    by Guido van Rossum and first released in 1991...

[Timing] Total: 3.5s

🎤 Listening... (speak now)
✓ Recognized: "Tell me about machine learning"

[Query #2]
You said: Tell me about machine learning
------------------------------------------------------------
AI: Machine learning is a subset of artificial intelligence...
```

## Quick Tips

### For Best Results

✅ **Do:**
- Use a headset or external microphone
- Speak clearly at normal pace
- Use in a quiet environment
- Wait for "Listening..." prompt

❌ **Don't:**
- Speak too fast or mumble
- Use in noisy environments
- Speak while it's processing
- Expect it to work offline (needs internet)

### Troubleshooting

**Microphone not detected?**
```bash
# Windows
pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

**Speech not recognized?**
- Speak louder and clearer
- Check internet connection (uses Google API)
- Reduce background noise
- Try recalibrating (restart the app)

**Timeout too short?**
- The default is 10 seconds
- You can modify in `start_audio.py`

## Python API

```python
from start_audio import AudioChatBot

# Create bot
bot = AudioChatBot()

# Interactive mode
bot.interactive_voice_chat()

# Single query
response = bot.single_voice_query()

# Custom usage
speech = bot.listen_for_speech(timeout=15)
if speech:
    response = bot.chatbot.chat_stream(speech)
```

## Configuration

```python
from start_audio import AudioChatBot
from config import Config

config = Config.from_defaults()
config.ui.use_streaming = True
config.ui.show_timing = True

bot = AudioChatBot(config=config)

# Adjust sensitivity
bot.recognizer.energy_threshold = 3000  # Lower = more sensitive

# Adjust pause detection
bot.recognizer.pause_threshold = 1.0    # Seconds of silence

bot.interactive_voice_chat()
```

## Features

- 🎤 **Voice Input**: Speak naturally, no typing
- 🔄 **Speech-to-Text**: Automatic conversion
- 🤖 **AI Processing**: Full chatbot capabilities
- 📝 **Streaming**: Real-time text responses
- 🔍 **Web Search**: Tool integration works
- 🌐 **Multi-language**: Supports multiple languages
- 🆓 **Free**: Uses Google's free speech API

## Commands

| Command | Description |
|---------|-------------|
| `python start_audio.py` | Interactive voice chat |
| `python start_audio.py --test` | Test microphone |
| `python start_audio.py --single` | Single query mode |

## Exit Commands

Say any of these to exit:
- "exit"
- "quit"
- "goodbye"
- "bye"

Or press **Ctrl+C** anytime.

## Full Documentation

- **[Complete Audio Chatbot Guide](./audio_chatbot.md)**
- **[ChatBot Streaming](./chatbot_streaming.md)**
- **[Configuration](../config.py)**

## Privacy Note

- Audio is sent to Google Speech Recognition API (requires internet)
- Text processing happens locally via Ollama
- No audio is saved (unless you modify the code)

## Next Steps

1. ✅ Install dependencies
2. ✅ Test microphone with `--test`
3. ✅ Try interactive mode
4. ✅ Read [full documentation](./audio_chatbot.md)
5. ✅ Customize configuration as needed

Enjoy your voice-interactive AI assistant! 🎤🤖
