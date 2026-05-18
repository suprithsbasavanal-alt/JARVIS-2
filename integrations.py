import subprocess # For AppleScript
import requests # For APIs
import logging # For logging

class ThirdPartyIntegrations:
    """
    JARVIS 3.0 External Integrations.
    Connects to native macOS apps via AppleScript and APIs like OpenWeatherMap.
    """
    def __init__(self, config):
        """Initializes integration keys."""
        self.weather_api_key = config.get("weather_api_key", "") # Set API key
        logging.info("Third Party Integrations initialized.") # Log ready

    def get_weather(self, city="San Francisco"):
        """Fetches real weather data from OpenWeatherMap."""
        if not self.weather_api_key: # Check if key exists
            return "I don't have a Weather API key configured in config.json." # Warning
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric" # API URL
            response = requests.get(url) # Make request
            data = response.json() # Parse JSON
            
            if response.status_code == 200: # Success
                temp = data['main']['temp'] # Get temp
                desc = data['weather'][0]['description'] # Get description
                return f"The current weather in {city} is {temp} degrees Celsius with {desc}." # Return string
            else:
                return f"Weather API error: {data.get('message', 'Unknown error')}" # Return error
        except Exception as e:
            logging.error(f"Weather fetch failed: {e}") # Log
            return "I could not fetch the weather data." # Return fallback

    def get_calendar_events(self):
        """Reads today's events from macOS Calendar using AppleScript."""
        try:
            script = '''
            tell application "Calendar"
                set today to current date
                set time of today to 0
                set tomorrow to today + (1 * days)
                set output to ""
                
                tell calendar "Work" -- Change to your main calendar name if different
                    set theEvents to (every event whose start date is greater than or equal to today and start date is less than tomorrow)
                    repeat with theEvent in theEvents
                        set output to output & (summary of theEvent) & " at " & (start date of theEvent) & ", "
                    end repeat
                end tell
                return output
            end tell
            ''' # AppleScript to get events
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True) # Run script
            
            if result.stdout.strip(): # If events exist
                return f"Here are your events for today: {result.stdout.strip()}" # Return string
            return "You have no events scheduled for today." # Return empty
        except Exception as e:
            logging.error(f"Calendar sync failed: {e}") # Log
            return "I cannot access your calendar right now." # Return fallback

    def read_unread_emails(self):
        """Reads unread emails from macOS Mail app."""
        try:
            script = '''
            tell application "Mail"
                set unreadMsgs to (messages of inbox whose read status is false)
                set output to ""
                set msgCount to 0
                
                repeat with msg in unreadMsgs
                    if msgCount < 5 then -- Limit to 5 emails
                        set output to output & "From " & (sender of msg) & ": " & (subject of msg) & ". "
                        set msgCount to msgCount + 1
                    end if
                end repeat
                return output
            end tell
            ''' # AppleScript
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True) # Run
            
            if result.stdout.strip(): # If emails exist
                return f"Here are your latest unread emails: {result.stdout.strip()}" # Return string
            return "You have no unread emails." # Return empty
        except Exception as e:
            logging.error(f"Mail sync failed: {e}") # Log
            return "I cannot access your email right now." # Return fallback

    def control_spotify(self, action="play"):
        """Controls Spotify native Mac app."""
        try:
            script = f'tell application "Spotify" to {action}' # Build AppleScript
            subprocess.run(["osascript", "-e", script]) # Run
            return f"Spotify {action} command executed." # Success string
        except Exception as e:
            logging.error(f"Spotify control failed: {e}") # Log
            return "I cannot control Spotify right now." # Return fallback

    def get_current_track(self):
        """Gets currently playing track from Spotify."""
        try:
            script = '''
            tell application "Spotify"
                if player state is playing then
                    set trackName to name of current track
                    set artistName to artist of current track
                    return "Playing " & trackName & " by " & artistName
                else
                    return "Spotify is paused."
                end if
            end tell
            ''' # AppleScript
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True) # Run
            return result.stdout.strip() # Return text
        except Exception as e:
            logging.error(f"Spotify sync failed: {e}") # Log
            return "I cannot read Spotify right now." # Return fallback
