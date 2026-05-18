try:
    import pyautogui # Screen capture
    import cv2 # OpenCV for image processing
    import numpy as np # Array operations
    import pytesseract # OCR for text extraction
    HAS_VISION_LIBS = True
except ImportError:
    HAS_VISION_LIBS = False
import logging # Error logging
try:
    from ultralytics import YOLO # YOLO for object detection
except ImportError:
    YOLO = None # Fallback if not installed

class VisionSystem:
    """
    JARVIS 3.0 Vision System.
    Handles screen reading, text extraction, and object detection.
    """
    def __init__(self):
        """Initializes the vision system and loads YOLO model."""
        logging.info("Vision System initialized.") # Log ready
        self.yolo_model = None
        if YOLO:
            try:
                # Load the smallest, fastest YOLO model
                self.yolo_model = YOLO("yolov8n.pt")
                logging.info("YOLOv8 model loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load YOLO model: {e}")
        
    def capture_screen(self, save_path="current_screen.png"):
        """Takes a screenshot of the entire primary display."""
        if not HAS_VISION_LIBS:
            return None
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

    def detect_objects_in_webcam(self):
        """Uses OpenCV to capture a webcam frame and YOLOv8 to detect objects."""
        if not self.yolo_model:
            return "Object detection model is offline."
            
        try:
            print("Capturing webcam frame for object detection...")
            cap = cv2.VideoCapture(0) # Open default camera
            ret, frame = cap.read() # Read frame
            cap.release() # Release camera immediately
            
            if not ret:
                return "I couldn't access your webcam."
                
            results = self.yolo_model(frame) # Run inference
            
            detected_items = []
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0]) # Get class ID
                    conf = float(box.conf[0]) # Get confidence
                    name = self.yolo_model.names[cls_id] # Get class name
                    if conf > 0.5: # Filter by confidence
                        detected_items.append(name)
                        
            if detected_items:
                unique_items = list(set(detected_items)) # Remove duplicates
                return f"I can see: {', '.join(unique_items)}."
            else:
                return "I don't see any distinct objects in front of the camera."
                
        except Exception as e:
            logging.error(f"Object detection failed: {e}")
            return "I encountered an error processing the webcam feed."
