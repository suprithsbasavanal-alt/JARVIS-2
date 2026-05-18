import sys # System arguments
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout # UI elements
from PyQt6.QtCore import Qt, QTimer # Core features
from PyQt6.QtGui import QColor, QFont # Graphics
import datetime # Time tracking

class JarvisUI(QWidget):
    """
    JARVIS 3.0 Desktop Widget.
    A floating, transparent, draggable PyQt6 HUD.
    """
    def __init__(self, core):
        """Initializes the UI window."""
        super().__init__() # Call parent constructor
        self.core = core # Store JARVIS core instance
        self._setup_ui() # Configure UI
        
    def _setup_ui(self):
        """Configures the window appearance to be transparent and borderless."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint) # Float on top, no borders
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Transparent background
        self.resize(300, 200) # Set size
        
        # Main layout
        layout = QVBoxLayout() # Vertical box layout
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center content
        
        # Title Label (JARVIS Logo substitute)
        self.title_label = QLabel("JARVIS 3.0") # Text label
        self.title_label.setStyleSheet("color: #00f3ff; font-size: 24px; font-weight: bold;") # Cyberpunk cyan
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center text
        
        # Time Label
        self.time_label = QLabel() # Empty label for time
        self.time_label.setStyleSheet("color: #ffffff; font-size: 16px;") # White text
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center text
        
        # Status Label
        self.status_label = QLabel("Online and Listening...") # Status text
        self.status_label.setStyleSheet("color: #00ff00; font-size: 12px;") # Green text
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center text
        
        # Add widgets to layout
        layout.addWidget(self.title_label) # Add title
        layout.addWidget(self.time_label) # Add time
        layout.addWidget(self.status_label) # Add status
        
        self.setLayout(layout) # Set layout to window
        
        # Start a timer to update the clock
        self.timer = QTimer(self) # Create timer
        self.timer.timeout.connect(self.update_time) # Connect to function
        self.timer.start(1000) # Update every second (1000ms)
        self.update_time() # Initial call
        
    def update_time(self):
        """Updates the time label with current time."""
        current_time = datetime.datetime.now().strftime("%H:%M:%S") # Get formatted time
        self.time_label.setText(current_time) # Set text

    def pulse_ui(self):
        """Called when JARVIS is listening or speaking."""
        # Simple animation: change color to red when active
        self.title_label.setStyleSheet("color: #ff0055; font-size: 24px; font-weight: bold;") # Pulse red
        QTimer.singleShot(2000, self.reset_pulse) # Reset after 2 seconds
        
    def reset_pulse(self):
        """Resets the UI color back to idle."""
        self.title_label.setStyleSheet("color: #00f3ff; font-size: 24px; font-weight: bold;") # Back to cyan

    def mousePressEvent(self, event):
        """Allows dragging the frameless window."""
        self.oldPos = event.globalPosition().toPoint() # Save click position

    def mouseMoveEvent(self, event):
        """Moves the window when dragged."""
        delta = event.globalPosition().toPoint() - self.oldPos # Calculate movement
        self.move(self.x() + delta.x(), self.y() + delta.y()) # Move window
        self.oldPos = event.globalPosition().toPoint() # Update position

    def start(self):
        """Launches the PyQt Application loop."""
        app = QApplication(sys.argv) # Create Qt App
        self.show() # Show window
        app.exec() # Start event loop
