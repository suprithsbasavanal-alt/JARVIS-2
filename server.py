import asyncio # Async
import websockets # WebSocket server
import json # JSON parsing
import logging # Logging
from brain import AIBrain # Connect to JARVIS brain
from control import MacController # Connect to Mac controller
import psutil # For system stats

class JarvisWebSocketServer:
    """
    JARVIS 3.0 WebSocket Server.
    Provides real-time communication for holographic browser dashboards.
    """
    def __init__(self, jarvis_core):
        self.host = "localhost" # Local host
        self.port = 8765 # Port
        self.clients = set() # Connected clients
        self.core = jarvis_core # Main JARVIS instance
        logging.info(f"WebSocket server initialized on {self.host}:{self.port}") # Log ready
        
    async def register(self, websocket):
        """Registers a new client."""
        self.clients.add(websocket) # Add client
        logging.info("New dashboard client connected.") # Log
        # Send initial state
        await self.send_system_stats(websocket) # Send stats

    async def unregister(self, websocket):
        """Removes a disconnected client."""
        self.clients.remove(websocket) # Remove client
        logging.info("Dashboard client disconnected.") # Log

    async def handler(self, websocket, path):
        """Handles incoming websocket messages."""
        await self.register(websocket) # Register client
        try:
            async for message in websocket: # Listen for messages
                data = json.loads(message) # Parse JSON
                command = data.get("command") # Get command type
                
                if command == "chat":
                    user_text = data.get("text", "") # Get user message
                    # Process via core JARVIS brain
                    response = await self.core.brain.think(user_text) # Get AI response
                    # Send response back to dashboard
                    await websocket.send(json.dumps({"type": "response", "text": response})) # Send JSON
                elif command == "system_stats":
                    await self.send_system_stats(websocket) # Send stats manually
                elif command == "execute":
                    sys_command = data.get("action", "") # Get action
                    await self.core.control.execute_if_system_command(sys_command) # Execute
                    await websocket.send(json.dumps({"type": "status", "message": f"Executed: {sys_command}"})) # Send confirm
        except websockets.exceptions.ConnectionClosed:
            pass # Ignore standard disconnects
        except Exception as e:
            logging.error(f"WebSocket Error: {e}") # Log error
        finally:
            await self.unregister(websocket) # Ensure client is removed

    async def send_system_stats(self, websocket):
        """Sends real system stats to the dashboard."""
        try:
            stats = {
                "type": "stats",
                "cpu": psutil.cpu_percent(interval=0.1), # CPU usage
                "ram": psutil.virtual_memory().percent, # RAM usage
                "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 100 # Battery
            }
            await websocket.send(json.dumps(stats)) # Send JSON
        except Exception as e:
            logging.error(f"Error sending stats: {e}") # Log error

    async def broadcast_status(self, status_text):
        """Broadcasts JARVIS status to all connected dashboards."""
        if self.clients: # If clients exist
            message = json.dumps({"type": "status", "message": status_text}) # Create JSON
            await asyncio.gather(*[client.send(message) for client in self.clients]) # Send to all

    async def start_server(self):
        """Starts the WebSocket server."""
        print(f"Starting WebSocket server on ws://{self.host}:{self.port}") # Console out
        async with websockets.serve(self.handler, self.host, self.port): # Start server
            await asyncio.Future()  # Run forever
