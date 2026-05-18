import os # OS commands
import subprocess # Running shell commands
import psutil # System information
import logging # Logging errors
try:
    import pyautogui # For window/mouse management
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
import shutil # For file operations
from pathlib import Path # For better path handling

class MacController:
    """
    JARVIS 3.0 System Control.
    Executes real Mac commands via AppleScript and shell, and reads real system stats.
    """
    def __init__(self):
        """Initializes the Mac Controller."""
        logging.info("Mac Controller initialized.") # Log ready

    async def execute_if_system_command(self, command_text):
        """
        Parses text for system actions and executes them.
        """
        text = command_text.lower() # Normalize text
        
        try:
            if "open chrome" in text:
                self.open_app("Google Chrome") # Open Chrome
            elif "open spotify" in text:
                self.open_app("Spotify") # Open Spotify
            elif "open vs code" in text or "open vscode" in text:
                self.open_app("Visual Studio Code") # Open VS Code
            elif "open terminal" in text:
                self.open_app("Terminal") # Open Terminal
            elif "close" in text and "app" in text:
                # Naive implementation for demo: 'close Chrome app'
                words = text.split() # Split words
                if "close" in words:
                    idx = words.index("close") # Find index
                    if len(words) > idx + 1:
                        self.close_app(words[idx + 1]) # Try to close the next word
            elif "increase volume" in text:
                self.set_volume(75) # Set volume
            elif "decrease volume" in text:
                self.set_volume(25) # Set volume
            elif "mute" in text:
                self.set_volume(0) # Mute
            elif "system stats" in text or "cpu usage" in text or "battery" in text:
                # Provide real stats
                stats = self.get_system_stats() # Get actual data
                logging.info(f"System Stats: {stats}") # Log stats
                # In main.py, JARVIS should speak this, but for now we log it.
            elif "search spotlight for" in text:
                query = text.split("search spotlight for")[-1].strip() # Get query
                self.spotlight_search(query) # Run search
            elif "tile windows" in text or "split screen" in text:
                self.tile_windows() # Tile windows
        except Exception as e:
            logging.error(f"Failed to execute system command: {e}") # Log error

    def open_app(self, app_name):
        """Opens a macOS application using the 'open' command."""
        print(f"Opening {app_name}...") # Console output
        os.system(f"open -a '{app_name}'") # Execute shell command

    def close_app(self, app_name):
        """Closes a macOS application using AppleScript."""
        print(f"Closing {app_name}...") # Console output
        script = f'tell application "{app_name}" to quit' # AppleScript string
        subprocess.run(["osascript", "-e", script]) # Run AppleScript

    def set_volume(self, percentage):
        """Sets macOS system volume (0-100)."""
        print(f"Setting volume to {percentage}%...") # Console output
        script = f"set volume output volume {percentage}" # AppleScript string
        subprocess.run(["osascript", "-e", script]) # Run AppleScript
        
    def get_system_stats(self):
        """Returns real-time system usage using psutil."""
        try:
            cpu = psutil.cpu_percent(interval=0.5) # Get CPU %
            ram = psutil.virtual_memory().percent # Get RAM %
            battery = psutil.sensors_battery() # Get Battery info
            batt_percent = battery.percent if battery else "Unknown" # Parse battery
            
            return f"CPU is at {cpu}%. RAM usage is {ram}%. Battery is at {batt_percent}%." # Format string
        except Exception as e:
            logging.error(f"psutil failed to get stats: {e}") # Log error
            return "I cannot access system statistics right now." # Error message

    def spotlight_search(self, query):
        """Uses PyAutoGUI to open Spotlight and search for a query."""
        if not HAS_GUI:
            print(f"Spotlight Search not available headless. (Query: {query})")
            return
        print(f"Searching Spotlight for '{query}'...") # Log
        pyautogui.hotkey('command', 'space') # Open Spotlight
        pyautogui.sleep(0.5) # Wait for it to open
        pyautogui.typewrite(query) # Type query
        pyautogui.sleep(0.5) # Wait for results
        pyautogui.press('enter') # Press enter to open top result
        
    def tile_windows(self):
        """Uses AppleScript to tile the front two windows (requires Magnet or Rectangle, or native macOS 15+).
           For a generic approach, we can just use AppleScript to resize."""
        print("Tiling windows...") # Log
        script = '''
        tell application "System Events"
            set frontApp to first application process whose frontmost is true
            tell frontApp
                set theWindow to window 1
                set position of theWindow to {0, 25}
                set size of theWindow to {1440, 900}
            end tell
        end tell
        ''' # Basic script to resize window
        subprocess.run(["osascript", "-e", script]) # Execute

    def list_folder(self, folder_path="~/Desktop"):
        """Lists files in a folder using pathlib."""
        path = Path(folder_path).expanduser() # Expand ~
        if not path.exists():
            return "Folder does not exist." # Handle error
        return [f.name for f in path.iterdir() if f.is_file()] # Return file list
