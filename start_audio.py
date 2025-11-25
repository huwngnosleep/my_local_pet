#!/usr/bin/env python3
"""Audio-based chatbot entry point.

This script provides a voice-interactive chatbot that:
1. Listens to microphone input
2. Converts speech to text
3. Processes with AI
4. Streams text response in real-time
"""

import sys
import time

try:
    import speech_recognition as sr
except ImportError:
    print("Error: speech_recognition library not installed")
    print("Install with: pip install SpeechRecognition pyaudio")
    sys.exit(1)

try:
    import pyttsx3
except ImportError:
    print("Error: pyttsx3 library not installed")
    print("Install with: pip install pyttsx3")
    sys.exit(1)

from chatbot import ChatBot
from config import Config


class AudioChatBot:
    """Voice-interactive chatbot using microphone input.

    Uses speech recognition to convert voice to text, then processes
    queries through the standard ChatBot with streaming responses.
    """

    def __init__(self, config: Config = None):
        """Initialize audio chatbot.

        Args:
            config: Application configuration (creates default if None).
        """
        self.config = config or Config.from_defaults()
        self.chatbot = ChatBot(config=self.config)
        self.recognizer = sr.Recognizer()
        self.microphone = None

        # Audio settings
        self.recognizer.energy_threshold = 4000  # Adjust based on environment
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of silence to consider end

        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self._configure_tts()

    def _configure_tts(self):
        """Configure text-to-speech engine settings."""
        # Set speech rate (default is usually around 200)
        self.tts_engine.setProperty('rate', 175)

        # Set volume (0.0 to 1.0)
        self.tts_engine.setProperty('volume', 1.0)

        # Get available voices and set a default
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to find a female voice for variety (optional)
            # Default to first available voice
            # 0 is male, 1 is female
            self.tts_engine.setProperty('voice', voices[1].id)

    def speak(self, text: str):
        """Convert text to speech and play it.

        Args:
            text: The text to speak aloud.
        """
        # Clean text for better speech (remove markdown, etc.)
        clean_text = self._clean_text_for_speech(text)

        print("\n🔊 Speaking...")

        # Reinitialize TTS engine for each call (fixes Windows issue)
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 1.0)

        voices = engine.getProperty('voices')
        if voices and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)

        engine.say(clean_text)
        engine.runAndWait()
        engine.stop()

    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech output.

        Removes markdown formatting and other elements that don't
        translate well to speech.

        Args:
            text: Raw text that may contain markdown.

        Returns:
            Cleaned text suitable for speech synthesis.
        """
        import re

        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)

        # Remove markdown links, keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'_([^_]+)_', r'\1', text)        # Underscore italic
        text = re.sub(r'#+\s*', '', text)               # Headers

        # Remove bullet points
        text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)

        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)

        return text.strip()

    def test_microphone(self) -> bool:
        """Test microphone availability.

        Returns:
            True if microphone is accessible, False otherwise.
        """
        try:
            with sr.Microphone() as source:
                print("[OK] Microphone detected")
                return True
        except Exception as e:
            print(f"[!] Microphone error: {e}")
            print("\nTroubleshooting:")
            print("  - Check microphone is connected")
            print("  - Install PyAudio: pip install pyaudio")
            print("  - On Linux: sudo apt-get install python3-pyaudio")
            print("  - On macOS: brew install portaudio")
            return False

    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise.

        Adjusts for background noise to improve recognition accuracy.
        """
        print("\n[Calibrating microphone for ambient noise...]")
        print("Please remain silent for a moment...")

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"[OK] Calibration complete")
                print(f"    Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"[!] Calibration failed: {e}")

    def listen_for_speech(self, timeout: int = 10) -> str:
        """Listen for speech input from microphone.

        Args:
            timeout: Maximum seconds to wait for speech.

        Returns:
            Recognized text from speech, or empty string on failure.
        """
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening... (speak now)")

                # Listen for audio
                try:
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=30  # Max 30 seconds per phrase
                    )
                    print("🔄 Processing speech...")

                except sr.WaitTimeoutError:
                    print("⏱️  No speech detected (timeout)")
                    return ""

                # Convert to text using Google Speech Recognition
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"✓ Recognized: \"{text}\"")
                    return text

                except sr.UnknownValueError:
                    print("❌ Could not understand audio")
                    return ""

                except sr.RequestError as e:
                    print(f"❌ Speech recognition service error: {e}")
                    print("\nNote: This uses Google's free speech recognition.")
                    print("Make sure you have an internet connection.")
                    return ""

        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return ""

    def interactive_voice_chat(self):
        """Run interactive voice chat session.

        Continuously listens for voice input, processes with chatbot,
        and displays streaming text responses.
        """
        # Test Ollama connection
        print("Testing connection to Ollama...")
        if not self.chatbot.test_connection():
            print("\n❌ Cannot connect to Ollama. Exiting.")
            return

        # Test microphone
        print("\nTesting microphone...")
        if not self.test_microphone():
            print("\n❌ Microphone not available. Exiting.")
            return

        # Calibrate for ambient noise
        self.calibrate_microphone()

        # Display header
        print("\n" + "=" * 60)
        print("🎤 VOICE-INTERACTIVE CHATBOT")
        print("=" * 60)
        print(f"Model: {self.config.ollama.model_name}")
        print(f"Streaming: Enabled")
        print(f"Web Search: Enabled")
        print("\nControls:")
        print("  - Speak your question into the microphone")
        print("  - Say 'exit', 'quit', or 'goodbye' to end")
        print("  - Press Ctrl+C to interrupt")
        print("=" * 60)
        print()

        conversation_count = 0

        while True:
            # Listen for voice input
            user_speech = self.listen_for_speech(timeout=10)

            if not user_speech:
                continue

            # Check for exit commands
            if user_speech.lower() in ['exit', 'quit', 'goodbye', 'bye']:
                print("\n👋 Goodbye!")
                break

            conversation_count += 1
            print(f"\n[Query #{conversation_count}]")
            print(f"You said: {user_speech}")
            print("-" * 60)

            # Process with chatbot (streaming)
            bot_response = self.chatbot.chat_stream(user_speech)
            print("bot response")
            # Speak the response
            self.speak(bot_response)


    def single_voice_query(self, auto_listen: bool = True) -> str:
        """Process a single voice query.

        Args:
            auto_listen: If True, automatically listen for speech.
                        If False, return empty string.

        Returns:
            Chatbot response text.
        """
        if auto_listen:
            # Calibrate first
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            # Listen for speech
            user_speech = self.listen_for_speech(timeout=10)

            if not user_speech:
                return ""

            print(f"\nYou said: {user_speech}\n")

            # Process with chatbot
            response = self.chatbot.chat_stream(user_speech)

            # Speak the response
            if response:
                self.speak(response)

            return response

        return ""


def main():
    """Main entry point for audio chatbot."""
    print("=" * 60)
    print("AUDIO CHATBOT - Voice Interactive Mode")
    print("=" * 60)

    # Create configuration
    config = Config.from_defaults()
    config.ui.use_streaming = True  # Enable streaming for better UX
    config.ui.show_timing = True    # Show response timing

    # Create audio chatbot
    audio_bot = AudioChatBot(config=config)

    # Check if running with arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Test mode
            print("\n[Test Mode]")
            print("Testing microphone...")
            if audio_bot.test_microphone():
                print("\n✓ Microphone test passed")
                audio_bot.calibrate_microphone()
                print("\n✓ All tests passed")
            else:
                print("\n✗ Microphone test failed")
                sys.exit(1)

        elif sys.argv[1] == "--single":
            # Single query mode
            print("\n[Single Query Mode]")
            audio_bot.single_voice_query(auto_listen=True)

        else:
            print(f"\nUnknown argument: {sys.argv[1]}")
            print("\nUsage:")
            print("  python start_audio.py           # Interactive mode")
            print("  python start_audio.py --test    # Test microphone")
            print("  python start_audio.py --single  # Single query")
            sys.exit(1)
    else:
        # Interactive mode (default)
        audio_bot.interactive_voice_chat()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
