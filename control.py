import os # OS commands
import subprocess # Running shell commands
import psutil # System information
import logging # Logging errors

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
