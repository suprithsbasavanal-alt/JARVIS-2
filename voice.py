import speech_recognition as sr  # Voice to text
import logging                    # Error logging
import os                         # OS functions
import asyncio                    # For async input

try:
    import pyttsx3  # Local TTS fallback
except ImportError:
    pyttsx3 = None

try:
    import pvporcupine  # Wake word detection (requires Picovoice API key)
except ImportError:
    pvporcupine = None
    print("[WARN] pvporcupine not installed — wake word disabled, using text input mode.")

try:
    import pyaudio  # Audio streaming for mic input
    import struct
except ImportError:
    pyaudio = None
    struct = None
    print("[WARN] pyaudio not installed — microphone input disabled, using text input mode.")


class VoiceSystem:
    """
    JARVIS 3.0 Voice and Audio System.
    Handles wake word detection, STT, and pyttsx3 / macOS TTS.

    Fallback hierarchy:
      Wake word  : pvporcupine → async text input prompt
      Command    : Google STT  → async text input prompt
      TTS        : pyttsx3     → macOS 'say' command
    """

    def __init__(self, config):
        """Initializes TTS and optional wake-word engine."""
        self.config      = config
        self.voice_speed = config.get("voice_speed", 1.0)

        # ── TTS engine ──────────────────────────────────────────────────
        self.tts_engine = None
        if pyttsx3:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', int(150 * self.voice_speed))
                logging.info("pyttsx3 TTS engine initialised.")
            except Exception as e:
                logging.error(f"pyttsx3 init failed: {e}")
                self.tts_engine = None

        # ── STT recogniser ──────────────────────────────────────────────
        self.recognizer = sr.Recognizer()

        # ── Wake-word engine ────────────────────────────────────────────
        self.porcupine     = None
        self.porcupine_key = os.environ.get("PORCUPINE_KEY", "")
        if pvporcupine and self.porcupine_key:
            try:
                self.porcupine = pvporcupine.create(
                    access_key=self.porcupine_key, keywords=["jarvis"]
                )
                logging.info("Porcupine wake-word engine ready.")
            except Exception as e:
                logging.error(f"Porcupine init failed: {e}")
                self.porcupine = None

        # Advertise mode on startup
        if not self.porcupine:
            print("\n" + "═" * 55)
            print("  🎙  JARVIS INPUT MODE: TEXT")
            print("  No wake-word engine — type your commands below.")
            print("  Type  'exit' or press Ctrl-C to shut down.")
            print("═" * 55 + "\n")
        else:
            print("\n✅ Wake-word engine active — say 'Jarvis' to activate.\n")

    # ── Wake word / text prompt ──────────────────────────────────────────

    async def async_listen_for_wake_word(self):
        """
        Non-blocking wake-word detection.
        • If pvporcupine is available and configured → uses hardware mic.
        • Otherwise → prompts the user to type a command directly.
        Returns (triggered: bool, typed_command: str | None)
        """
        if self.porcupine and pyaudio:
            # Hardware wake-word path (runs in executor so it doesn't block asyncio)
            triggered = await asyncio.get_event_loop().run_in_executor(
                None, self._porcupine_listen
            )
            return triggered, None
        else:
            # Text-input fallback — completely non-blocking for asyncio
            loop    = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(
                None, lambda: input("You › ").strip()
            )
            if user_input.lower() in ("exit", "quit", "bye"):
                print("Shutting down JARVIS...")
                os._exit(0)
            # Return the typed text directly as the command
            return True, user_input if user_input else None

    def _porcupine_listen(self):
        """Blocking pvporcupine listener — call via run_in_executor."""
        try:
            pa = pyaudio.PyAudio()
            stream = pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )
            print("Listening for wake word 'Jarvis'…")
            while True:
                pcm = stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                if self.porcupine.process(pcm) >= 0:
                    stream.close()
                    pa.terminate()
                    return True
        except Exception as e:
            logging.error(f"Wake-word listener error: {e}")
            return False

    # ── Command capture ──────────────────────────────────────────────────

    async def async_listen_for_command(self):
        """
        Non-blocking command capture.
        • If pyaudio is available → Google STT via microphone.
        • Otherwise → reads a line of text from the terminal.
        """
        if pyaudio:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._mic_listen)
        else:
            # Already captured via text input in async_listen_for_wake_word,
            # so this path should rarely be hit in text mode.
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, lambda: input("Command › ").strip() or None
            )

    def _mic_listen(self):
        """Blocking microphone STT — call via run_in_executor."""
        try:
            with sr.Microphone() as source:
                print("🎙  Listening…")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("⚙  Processing speech…")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
        except sr.UnknownValueError:
            logging.warning("Speech not recognised.")
            return None
        except sr.RequestError as e:
            logging.error(f"STT API error: {e}")
            self.speak("My speech recognition is unavailable right now.")
            return None
        except Exception as e:
            logging.error(f"Microphone error: {e}")
            return None

    # ── Audio helpers ─────────────────────────────────────────────────────

    def play_activation_sound(self):
        """Plays macOS Ping sound when JARVIS activates."""
        os.system("afplay /System/Library/Sounds/Ping.aiff &")  # non-blocking

    # ── TTS ───────────────────────────────────────────────────────────────

    def speak(self, text):
        """Text-to-speech: pyttsx3 → macOS 'say' fallback."""
        print(f"\nJARVIS › {text}\n")
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logging.error(f"pyttsx3 speak error: {e}")
                os.system(f"say '{text}' &")
        else:
            os.system(f"say '{text}' &")  # macOS built-in TTS (non-blocking)
