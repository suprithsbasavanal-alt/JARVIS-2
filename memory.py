import sqlite3 # Permanent storage
import chromadb # Vector database for semantic memory
import logging # Error logging
from datetime import datetime # For timestamps

class MemorySystem:
    """
    JARVIS 3.0 Quantum Memory Architecture.
    Combines SQLite for structured data and ChromaDB for semantic vector memory.
    """
    def __init__(self, config):
        """Initializes SQLite and ChromaDB connections."""
        self.config = config # Store config
        
        # Initialize SQLite
        try:
            self.conn = sqlite3.connect('jarvis_memory.db') # Connect to DB
            self.cursor = self.conn.cursor() # Get cursor
            self._create_tables() # Setup tables
        except Exception as e:
            logging.error(f"SQLite initialization failed: {e}") # Log error

        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db") # Create client
            self.collection = self.chroma_client.get_or_create_collection(name="jarvis_episodic_memory") # Create collection
        except Exception as e:
            logging.error(f"ChromaDB initialization failed: {e}") # Log error
            self.collection = None # Disable Chroma if failed
            
    def _create_tables(self):
        """Creates basic SQLite tables if they do not exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                timestamp DATETIME
            )
        ''') # Table for exact facts like 'name', 'preferences'
        self.conn.commit() # Save changes

    def save_memory(self, user_input, ai_response):
        """
        Saves a conversation turn into ChromaDB for semantic retrieval.
        """
        if not self.collection: return # Skip if Chroma failed
        
        timestamp = datetime.now().isoformat() # Get time
        memory_id = f"mem_{timestamp}" # Generate unique ID
        memory_text = f"User said: {user_input} | Jarvis replied: {ai_response}" # Format memory
        
        try:
            # Add to vector DB
            self.collection.add(
                documents=[memory_text], # The text to vectorize
                metadatas=[{"timestamp": timestamp, "type": "conversation"}], # Metadata
                ids=[memory_id] # Unique ID
            )
        except Exception as e:
            logging.error(f"Failed to save to ChromaDB: {e}") # Log error

    def search_memory(self, query, top_k=3):
        """
        Searches ChromaDB for memories related to the current query.
        """
        if not self.collection: return "" # Return empty if no DB
        
        try:
            # Query the vector DB
            results = self.collection.query(
                query_texts=[query], # The query to match against
                n_results=top_k # Number of results
            )
            
            if results and results['documents'] and len(results['documents'][0]) > 0: # If found
                docs = results['documents'][0] # Extract docs
                return "\n".join(docs) # Join into a single context string
            return "No relevant past memories found." # Default text
        except Exception as e:
            logging.error(f"ChromaDB search failed: {e}") # Log error
            return "" # Return empty

    def save_fact(self, key, value):
        """Saves a structured fact to SQLite."""
        try:
            timestamp = datetime.now().isoformat() # Current time
            self.cursor.execute(
                "INSERT OR REPLACE INTO facts (key, value, timestamp) VALUES (?, ?, ?)",
                (key, value, timestamp) # Parameterized query
            )
            self.conn.commit() # Save
        except Exception as e:
            logging.error(f"Failed to save fact {key}: {e}") # Log error

    def get_fact(self, key):
        """Retrieves a structured fact from SQLite."""
        try:
            self.cursor.execute("SELECT value FROM facts WHERE key = ?", (key,)) # Query DB
            result = self.cursor.fetchone() # Get first result
            return result[0] if result else None # Return value or None
        except Exception as e:
            logging.error(f"Failed to get fact {key}: {e}") # Log error
            return None # Return None on failure
