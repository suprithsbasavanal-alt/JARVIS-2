try:
    import ollama # Local AI inference
except ImportError:
    ollama = None
    print("[WARN] ollama package not installed — AI brain will return offline message.")
import logging # For logging
import asyncio # For async requests
import requests # For real internet access
from bs4 import BeautifulSoup # For web scraping

class AIBrain:
    """
    JARVIS 3.0 Superintelligent Brain.
    Connects to Ollama, enforces No-Hallucination policy, and accesses the internet.
    """
    def __init__(self, config):
        """Initializes the AI Brain with the selected model."""
        self.model = config.get("ai_model", "llama3") # Default to llama3
        self.system_prompt = self._build_system_prompt() # Generate strict prompt
        logging.info(f"AI Brain initialized with model: {self.model}") # Log success
        
    def _build_system_prompt(self):
        """Creates the strict No-Hallucination system prompt."""
        return (
            "You are JARVIS, a highly advanced AI assistant. "
            "STRICT RULES: "
            "1. You NEVER make up information. NO HALLUCINATIONS. "
            "2. If you do not know something, say exactly 'I do not know'. "
            "3. If you cannot access a file or data, say 'I cannot access that right now'. "
            "4. Always cite your sources if providing facts. "
            "5. If you are not 100% sure, say 'I am not certain but here is what I found'. "
            "6. You have real access to the Mac system, so respond as if you are executing commands."
        ) # Return the prompt string
        
    async def think(self, user_input, context=""):
        """
        Processes user input, searches internet if needed, and queries the local LLM.
        """
        # 1. Determine if internet search is needed (simple heuristic)
        if "search" in user_input.lower() or "what is the latest" in user_input.lower() or "who won" in user_input.lower():
            # Perform real internet search
            search_results = await self.search_internet(user_input) # Get real web data
            user_input = f"User asked: {user_input}\nReal Internet Data found: {search_results}" # Inject data
            
        # 2. Build the message array for Ollama
        messages = [
            {"role": "system", "content": self.system_prompt}, # System instructions
            {"role": "system", "content": f"Memory Context: {context}"}, # Injected memory
            {"role": "user", "content": user_input} # User query
        ]
        
        if not ollama: # Module not installed
            return "I am currently offline — the ollama package is not installed. Please check Ollama."
            
        try:
            # 3. Call Ollama API asynchronously
            # Run the synchronous ollama.chat in an executor to avoid blocking the event loop
            loop = asyncio.get_event_loop() # Get async loop
            response = await loop.run_in_executor(
                None, # Default executor
                lambda: ollama.chat(model=self.model, messages=messages) # API call
            )
            return response['message']['content'] # Return text
        except Exception as e:
            logging.error(f"Ollama inference failed: {e}") # Log error
            return "I am currently offline or my neural net is unreachable. Please check Ollama." # Safe fallback

    async def search_internet(self, query):
        """
        Performs a real DuckDuckGo search to prevent hallucinations.
        """
        try:
            # Format query for DuckDuckGo HTML version
            url = f"https://html.duckduckgo.com/html/?q={query}" # Target URL
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"} # Spoof User-Agent
            
            loop = asyncio.get_event_loop() # Get async loop
            # Run request in background
            res = await loop.run_in_executor(None, lambda: requests.get(url, headers=headers)) # Fetch page
            
            if res.status_code == 200: # If successful
                soup = BeautifulSoup(res.text, 'html.parser') # Parse HTML
                results = soup.find_all('a', class_='result__snippet') # Find snippets
                if results:
                    # Return top 3 results text
                    return " ".join([r.text for r in results[:3]]) # Combine text
            return "No real-time web results found." # No data
        except Exception as e:
            logging.error(f"Internet search failed: {e}") # Log error
            return "I cannot access the internet right now." # Offline fallback
