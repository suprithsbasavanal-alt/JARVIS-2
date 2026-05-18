# JARVIS 3.0 ULTIMATE

The most powerful, animated, and feature-rich AI assistant ever built on a Mac using Python.
This repository contains the full source code for JARVIS 3.0.

## Overview
JARVIS 3.0 is an asynchronous, highly-threaded, multi-modal AI assistant utilizing local LLMs (Ollama), semantic memory (ChromaDB), wake-word detection (Porcupine), screen vision (Tesseract), and full Mac OS integration.

## Installation Instructions (Mac Only)

**1. Install Python 3**
Ensure you have Python 3 installed. If not, install via Homebrew:
```bash
brew install python3
```

**2. Install System Dependencies**
JARVIS requires local instances of Ollama, Tesseract (OCR), and Redis.
```bash
brew install ollama tesseract redis
```

**3. Start Background Services**
```bash
brew services start redis
brew services start ollama
# Download the LLama3 model into Ollama
ollama run llama3
```

**4. Install Python Libraries**
Run the setup script which will test your environment and install pip packages:
```bash
chmod +x setup.sh
./setup.sh
```

**5. Set API Keys**
You must set your Picovoice Porcupine API key in your environment variables for the wake word to work.
```bash
export PORCUPINE_KEY="YOUR_KEY_HERE"
```

## Running JARVIS
Run the main script:
```bash
python3 main.py
```

## Common Errors & Fixes
- **Error: `PyAudio: portaudio not found`** -> Run `brew install portaudio` before `pip install pyaudio`.
- **Error: `tesseract is not installed`** -> Ensure you ran `brew install tesseract`.
- **Error: Microphone permissions** -> Go to System Settings > Privacy & Security > Microphone and allow your Terminal/Python.
- **Error: Screen recording missing** -> Go to System Settings > Privacy & Security > Screen Recording and allow your Terminal/Python.

## Features Included in Version 3.0
- **Asynchronous Architecture:** UI and Voice loops run non-blocking.
- **Strict No-Hallucination Brain:** JARVIS enforces factual reporting and real internet searches.
- **Quantum Memory:** Episodic memory stored in ChromaDB vector database.
- **Real OS Integration:** Executes `open`, `osascript`, and reads `psutil`.

*Created for Boss.*
