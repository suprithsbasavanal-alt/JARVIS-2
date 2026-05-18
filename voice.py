import speech_recognition as sr # Voice to text
import pyttsx3 # Fallback TTS
import pvporcupine # Wake word detection
import pyaudio # Audio streaming
import struct # Binary data packing
import logging # Error logging
import os # OS functions

class VoiceSystem:
    """
    JARVIS 3.0 Voice and Audio System.
    Handles wake word detection, STT, and ElevenLabs/pyttsx3 TTS.
    """
    def __init__(self, config):
        """Initializes microphones and TTS engines."""
        self.recognizer = sr.Recognizer() # Initialize STT
        self.config = config # Save config
        self.voice_speed = config.get("voice_speed", 1.0) # Set speed
        
        # Initialize pyttsx3 fallback
        try:
            self.tts_engine = pyttsx3.init() # Initialize local TTS
            self.tts_engine.setProperty('rate', int(150 * self.voice_speed)) # Set speed
        except Exception as e:
            logging.error(f"pyttsx3 init failed: {e}") # Log error
            self.tts_engine = None # Disable fallback

        # Initialize Wake Word (Porcupine)
        # NOTE: Requires access key from picovoice console in a real app
        self.porcupine_key = os.environ.get("PORCUPINE_KEY", "YOUR_PICOVOICE_KEY") # Get API key
        try:
            # We use "jarvis" keyword if available, else "hey siri" as placeholder for demo
            self.porcupine = pvporcupine.create(access_key=self.porcupine_key, keywords=["jarvis"]) # Create wake word
        except Exception as e:
            logging.error(f"Porcupine wake word failed (maybe missing API key): {e}") # Log error
            self.porcupine = None # Disable wake word if no key

    def listen_for_wake_word(self):
        """
        Listens continuously using virtually zero CPU until 'Hey Jarvis' is heard.
        """
        if not self.porcupine: # If no wake word engine
            print("Wake word engine offline. Press Enter to simulate wake word.") # Prompt user
            input() # Wait for Enter
            return True # Simulate wake word detected
            
        try:
            pa = pyaudio.PyAudio() # Init PyAudio
            audio_stream = pa.open(
                rate=self.porcupine.sample_rate, # Set rate
                channels=1, # Mono audio
                format=pyaudio.paInt16, # 16-bit format
                input=True, # Read from mic
                frames_per_buffer=self.porcupine.frame_length # Set buffer size
            )
            
            print("Listening for wake word 'Jarvis'...") # Console output
            while True:
                pcm = audio_stream.read(self.porcupine.frame_length) # Read audio chunk
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm) # Unpack binary
                
                keyword_index = self.porcupine.process(pcm) # Check for wake word
                if keyword_index >= 0: # If wake word found
                    audio_stream.close() # Close stream
                    pa.terminate() # Terminate PyAudio
                    return True # Return success
        except Exception as e:
            logging.error(f"Wake word listening error: {e}") # Log error
            return False # Return failure

    def play_activation_sound(self):
        """Plays a futuristic beep when JARVIS wakes up."""
        # Simple terminal bell or OS sound for demo
        os.system("afplay /System/Library/Sounds/Ping.aiff") # Play macOS sound

    def listen_for_command(self):
        """
        Uses Google Speech API to convert voice to text.
        """
        try:
            with sr.Microphone() as source: # Open mic
                print("Listening for command...") # Console output
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5) # Calibrate noise
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10) # Record audio
                
                print("Processing speech...") # Console output
                text = self.recognizer.recognize_google(audio) # STT via Google
                return text # Return recognized text
        except sr.UnknownValueError:
            logging.warning("Speech not recognized.") # Log unrecognized
            return None # Return empty
        except sr.RequestError as e:
            logging.error(f"Speech API error: {e}") # Log API failure
            self.speak("My speech recognition connection is down.") # Announce error
            return None # Return empty
        except Exception as e:
            logging.error(f"Microphone error: {e}") # Log general error
            return None # Return empty

    def speak(self, text):
        """
        Converts text to speech using ElevenLabs API, or pyttsx3 fallback.
        """
        print(f"JARVIS: {text}") # Show text in console
        
        # TODO: Integrate ElevenLabs API here.
        # Fallback to local pyttsx3 for now to ensure it works without API keys.
        if self.tts_engine: # If local TTS is available
            try:
                self.tts_engine.say(text) # Queue text
                self.tts_engine.runAndWait() # Speak text
            except Exception as e:
                logging.error(f"pyttsx3 speaking error: {e}") # Log error
        else:
            os.system(f"say '{text}'") # Absolute fallback using macOS 'say' command
