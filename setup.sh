#!/bin/bash
# JARVIS 3.0 ULTIMATE - Setup and Diagnostics Script
# This script installs all dependencies and tests critical system permissions.

echo "================================================="
echo "        JARVIS 3.0 ULTIMATE INITIALIZATION       "
echo "================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then # If python3 is not found
    echo "❌ Python 3 is not installed. Please install Python 3." # Print error
    exit 1 # Exit with error code
else
    echo "✅ Python 3 is installed." # Print success
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then # If pip3 is not found
    echo "❌ pip3 is not installed. Please install pip3." # Print error
    exit 1 # Exit with error code
else
    echo "✅ pip3 is installed." # Print success
fi

echo "Installing Python dependencies from requirements.txt..."
pip3 install -r requirements.txt # Install pip packages

echo "================================================="
echo "            SYSTEM PERMISSION CHECKS             "
echo "================================================="

# Check for Tesseract (needed for OCR)
if ! command -v tesseract &> /dev/null; then # If tesseract is not found
    echo "❌ Tesseract OCR is not installed. Run: brew install tesseract" # Print error
else
    echo "✅ Tesseract OCR is installed." # Print success
fi

# Check for Ollama (Local AI Brain)
if ! command -v ollama &> /dev/null; then # If ollama is not found
    echo "❌ Ollama is not installed. Run: brew install ollama" # Print error
else
    echo "✅ Ollama is installed." # Print success
fi

# Check for Redis (Cache)
if ! command -v redis-cli &> /dev/null; then # If redis is not found
    echo "❌ Redis is not installed. Run: brew install redis" # Print error
else
    echo "✅ Redis is installed." # Print success
fi

echo "================================================="
echo "Please ensure you grant macOS permissions when prompted:"
echo "1. Microphone Access (System Settings -> Privacy & Security -> Microphone)"
echo "2. Screen Recording (System Settings -> Privacy & Security -> Screen Recording)"
echo "3. Accessibility (System Settings -> Privacy & Security -> Accessibility)"
echo "4. Full Disk Access (System Settings -> Privacy & Security -> Full Disk Access)"
echo "================================================="
echo "Setup complete! Run JARVIS with: python3 main.py"
echo "================================================="
