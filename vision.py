import pyautogui # Screen capture
import pytesseract # OCR for text extraction
import cv2 # OpenCV for image processing
import numpy as np # Array operations
import logging # Error logging

class VisionSystem:
    """
    JARVIS 3.0 Vision System.
    Handles screen reading, text extraction, and object detection.
    """
    def __init__(self):
        """Initializes the vision system."""
        logging.info("Vision System initialized.") # Log ready
        
    def capture_screen(self, save_path="current_screen.png"):
        """Takes a screenshot of the entire primary display."""
        try:
            print("Taking real screenshot...") # Console output
            screenshot = pyautogui.screenshot() # Capture screen
            screenshot.save(save_path) # Save image
            return save_path # Return path
        except Exception as e:
            logging.error(f"Failed to capture screen: {e}") # Log error
            return None # Return None

    def read_screen_text(self):
        """
        Takes a screenshot, processes it with OpenCV, and extracts text with Tesseract.
        """
        img_path = self.capture_screen() # Take screenshot
        if not img_path: return "I could not capture the screen." # Abort if failed
        
        try:
            print("Processing image for OCR...") # Console output
            # Read image using OpenCV
            img = cv2.imread(img_path) # Load image
            
            # Convert to grayscale to improve OCR accuracy
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Convert to gray
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV) # Threshold
            
            # Extract text using Tesseract
            print("Running Tesseract OCR...") # Console output
            extracted_text = pytesseract.image_to_string(thresh) # Run OCR
            
            return extracted_text if extracted_text.strip() else "I don't see any clear text on the screen." # Return text
        except Exception as e:
            logging.error(f"OCR processing failed: {e}") # Log error
            return "I encountered an error trying to read the screen." # Error message
