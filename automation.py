import logging # For error logging

class AutomationManager:
    """
    JARVIS 3.0 Automation Modes.
    Handles running multi-step macros and routines.
    """
    def __init__(self, mac_controller, config):
        """Initializes the manager with the controller instance and config."""
        self.mac = mac_controller # Save controller reference
        self.modes = config.get("default_automation_modes", {}) # Load modes
        logging.info("Automation Manager initialized.") # Log ready

    async def run_mode(self, mode_name):
        """Executes a series of actions defined in a mode."""
        if mode_name not in self.modes: # Check if mode exists
            logging.warning(f"Mode {mode_name} not found.") # Log missing
            return False # Return failure
            
        print(f"Activating {mode_name} mode...") # Console output
        
        try:
            actions = self.modes[mode_name] # Get actions list
            for action in actions: # Loop through actions
                # Simple parser for the pre-defined modes in config
                if action == "open_notes":
                    self.mac.open_app("Notes") # Open Notes
                elif action == "play_lofi":
                    self.mac.open_app("Spotify") # Open Spotify
                    # In a full implementation, we'd use Spotify API here to play a specific playlist
                elif action == "open_vscode":
                    self.mac.open_app("Visual Studio Code") # Open VSCode
                elif action == "open_terminal":
                    self.mac.open_app("Terminal") # Open Terminal
                    
            return True # Return success
        except Exception as e:
            logging.error(f"Error running mode {mode_name}: {e}") # Log error
            return False # Return failure
