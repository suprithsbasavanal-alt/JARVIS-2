import asyncio # Async I/O for concurrency
import logging # For error logging
import json # For reading config.json
import os # For file system operations
import sys # For system specific parameters

# Import JARVIS modules
# Note: In a real environment, we would handle module loading carefully.
from brain import AIBrain # Connects to local LLMs
from voice import VoiceSystem # Handles STT and TTS
from memory import MemorySystem # Handles ChromaDB and SQLite
from control import MacController # Handles Mac app control
from automation import AutomationManager # Handles modes
from vision import VisionSystem # Handles OCR and object detection
from ui import JarvisUI # Handles the PyQt6/VisPy Interface
from server import JarvisWebSocketServer # Handles WebSocket API
from integrations import ThirdPartyIntegrations # Handles Calendar, Mail, Spotify, Weather

# Configure logging to save all errors with timestamps
logging.basicConfig(
    filename='jarvis_log.txt', # Log file name
    level=logging.INFO, # Log level
    format='%(asctime)s - %(levelname)s - %(message)s' # Log format
)

class Jarvis:
    """
    Main JARVIS 3.0 Ultimate Class.
    Initializes all subsystems and runs the main event loop.
    """
    def __init__(self):
        """Initializes JARVIS components and loads configuration."""
        self.config = self.load_config() # Load settings
        self.user_name = self.config.get("user_name", "Sir") # Get user name
        
        logging.info("Initializing JARVIS 3.0 Ultimate...") # Log startup
        
        # Initialize subsystems
        try:
            self.brain = AIBrain(self.config) # AI Brain
            self.voice = VoiceSystem(self.config) # Voice Input/Output
            self.memory = MemorySystem(self.config) # Database
            self.control = MacController() # System Control
            self.integrations = ThirdPartyIntegrations(self.config) # Third Party Apps
            self.automation = AutomationManager(self.control, self.config) # Routines
            self.vision = VisionSystem() # Camera and Screen Reading
            self.ui = JarvisUI(self) # User Interface
            self.server = JarvisWebSocketServer(self) # WebSocket Server
            logging.info("All subsystems initialized successfully.") # Success log
        except Exception as e:
            logging.error(f"Error initializing subsystems: {e}") # Log failure
            print(f"Critical System Failure: {e}") # Print to console
            
    def load_config(self):
        """Reads config.json and returns a dictionary."""
        try:
            with open('config.json', 'r') as file: # Open config file
                return json.load(file) # Parse JSON
        except FileNotFoundError:
            logging.warning("config.json not found, using default settings.") # Log warning
            return {"user_name": "Boss", "ai_model": "llama3"} # Default config
            
    async def startup_sequence(self):
        """Runs the startup animation and greeting."""
        print(f"Initializing JARVIS 3.0 Ultimate... Welcome back, {self.user_name}.") # Console out
        # In a real scenario, this would play an audio file and show an animation in the UI
        self.voice.speak(f"Welcome back, {self.user_name}. JARVIS 3 point 0 is online and ready.") # Voice greeting
        
    async def process_command(self, command_text):
        """
        Sends the command to the AI brain, gets the response, and acts on it.
        """
        if not command_text: # If command is empty
            return # Do nothing
            
        logging.info(f"User Command: {command_text}") # Log user command
        
        try:
            # 1. Retrieve context from memory
            context = self.memory.search_memory(command_text) # Get relevant memories
            
            # 2. Get AI response
            response = await self.brain.think(command_text, context) # Ask AI
            
            # 3. Speak response
            self.voice.speak(response) # TTS
            
            # 4. Save to short-term and long-term memory
            self.memory.save_memory(command_text, response) # Store interaction
            
            # 5. Check if command is a system action
            command_lower = command_text.lower()
            if "weather" in command_lower:
                response = self.integrations.get_weather()
                self.voice.speak(response)
            elif "calendar" in command_lower or "schedule" in command_lower:
                response = self.integrations.get_calendar_events()
                self.voice.speak(response)
            elif "read my emails" in command_lower or "unread emails" in command_lower:
                response = self.integrations.read_unread_emails()
                self.voice.speak(response)
            elif "play music" in command_lower or "spotify play" in command_lower:
                self.integrations.control_spotify("play")
            elif "pause music" in command_lower or "spotify pause" in command_lower:
                self.integrations.control_spotify("pause")
            elif "what song is this" in command_lower or "current track" in command_lower:
                response = self.integrations.get_current_track()
                self.voice.speak(response)
            elif "read my screen" in command_lower or "what is on my screen" in command_lower:
                self.voice.speak("Scanning screen...")
                screen_text = self.vision.read_screen_text()
                # Pass the raw text to the brain for summarization
                summary = await self.brain.think(f"Summarize this text found on my screen in two sentences: {screen_text}")
                self.voice.speak(summary)
            elif "what is this" in command_lower or "what do you see" in command_lower:
                self.voice.speak("Processing visual feed...")
                vision_response = self.vision.detect_objects_in_webcam()
                self.voice.speak(vision_response)
                
            await self.control.execute_if_system_command(command_text) # Act on Mac
            
        except Exception as e:
            error_msg = f"I encountered an error processing your command: {str(e)}" # Error string
            logging.error(error_msg) # Log error
            self.voice.speak(error_msg) # Announce error
            
    async def listen_loop(self):
        """Continuously listens for wake word and commands."""
        while True:
            try:
                # 1. Wait for wake word "Hey Jarvis"
                if self.voice.listen_for_wake_word(): # Blocking call for Porcupine
                    self.ui.pulse_ui() # Trigger UI animation
                    self.voice.play_activation_sound() # Play beep
                    
                    # 2. Listen for actual command
                    command = self.voice.listen_for_command() # STT
                    
                    if command: # If a command was heard
                        # 3. Process the command asynchronously
                        asyncio.create_task(self.process_command(command)) # Run non-blocking
                        
            except Exception as e:
                logging.error(f"Error in listen loop: {e}") # Log error
                await asyncio.sleep(1) # Prevent rapid failure loop

    async def run(self):
        """Starts the JARVIS main loop and UI."""
        await self.startup_sequence() # Run startup
        
        # Start the listening loop in the background
        asyncio.create_task(self.listen_loop()) # Start listener
        
        # Start the WebSocket server in the background
        asyncio.create_task(self.server.start_server()) # Start WebSocket
        
        
        # Start the UI (This usually blocks the main thread in PyQt)
        # Assuming the UI framework handles its own event loop or we bridge it properly
        self.ui.start() # Launch graphical interface

if __name__ == "__main__":
    jarvis_instance = Jarvis() # Create JARVIS object
    try:
        asyncio.run(jarvis_instance.run()) # Run the async main loop
    except KeyboardInterrupt:
        print("Shutting down JARVIS...") # Handle Ctrl+C
        sys.exit(0) # Exit cleanly
