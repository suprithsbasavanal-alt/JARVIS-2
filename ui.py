import sys          # System arguments
import logging       # Error logging
import datetime      # Time tracking

try:
    from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout # UI elements
    from PyQt6.QtCore import Qt, QTimer   # Core features
    from PyQt6.QtGui import QColor, QFont  # Graphics
    HAS_QT = True
except ImportError:
    HAS_QT = False

try:
    import pyautogui  # Screen capture
    import cv2        # OpenCV for image processing
    import numpy as np  # Array operations
    import pytesseract  # OCR for text extraction
    HAS_VISION = True
except ImportError:
    HAS_VISION = False


class JarvisUI:
    """
    JARVIS 3.0 Desktop HUD.
    A floating, transparent, draggable PyQt6 widget.

    NOTE: __init__ intentionally does NOT create any QWidget objects —
    that is deferred to start() so that a QApplication can be created
    first in main.py without triggering the
    'Must construct a QApplication before a QWidget' abort.
    """

    def __init__(self, core):
        """Store core reference only — no Qt objects created here."""
        self.core   = core   # JARVIS core instance
        self._widget = None  # Created lazily in start()

    # ── Internal widget builder (called only after QApplication exists) ────

    def _build_widget(self):
        """Creates the actual Qt window and wires up the clock timer."""
        if not HAS_QT:
            return

        # Inline QWidget subclass so the class itself never inherits QWidget
        # at module import time.
        class _HUD(QWidget):
            def mousePressEvent(inner_self, event):
                inner_self._drag_pos = event.globalPosition().toPoint()

            def mouseMoveEvent(inner_self, event):
                delta = event.globalPosition().toPoint() - inner_self._drag_pos
                inner_self.move(inner_self.x() + delta.x(), inner_self.y() + delta.y())
                inner_self._drag_pos = event.globalPosition().toPoint()

        w = _HUD()
        w.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )                                               # Float on top, no borders
        w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Transparent background
        w.resize(300, 200)

        # ── Layout ──────────────────────────────────────────────────────
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("JARVIS 3.0")
        title_label.setStyleSheet("color: #00f3ff; font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        time_label = QLabel()
        time_label.setStyleSheet("color: #ffffff; font-size: 16px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_label = QLabel("Online and Listening...")
        status_label.setStyleSheet("color: #00ff00; font-size: 12px;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(time_label)
        layout.addWidget(status_label)
        w.setLayout(layout)

        # Store references for later mutation
        w._title_label  = title_label
        w._time_label   = time_label
        w._status_label = status_label
        w._drag_pos     = None

        # Clock timer
        timer = QTimer(w)
        timer.timeout.connect(lambda: time_label.setText(
            datetime.datetime.now().strftime("%H:%M:%S")
        ))
        timer.start(1000)
        time_label.setText(datetime.datetime.now().strftime("%H:%M:%S"))

        self._widget = w

    # ── Public API ────────────────────────────────────────────────────────

    def pulse_ui(self):
        """Called when JARVIS is listening / speaking — pulses the title red."""
        if not (HAS_QT and self._widget):
            return
        self._widget._title_label.setStyleSheet(
            "color: #ff0055; font-size: 24px; font-weight: bold;"
        )
        QTimer.singleShot(2000, self.reset_pulse)

    def reset_pulse(self):
        """Resets the title colour back to idle cyan."""
        if not (HAS_QT and self._widget):
            return
        self._widget._title_label.setStyleSheet(
            "color: #00f3ff; font-size: 24px; font-weight: bold;"
        )

    def capture_screen(self, save_path="current_screen.png"):
        """Takes a screenshot of the primary display."""
        if not HAS_VISION:
            return None
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return save_path
        except Exception as e:
            logging.error(f"Failed to capture screen: {e}")
            return None

    def start(self):
        """
        Builds the Qt widget (QApplication already exists at this point)
        and shows it.  In qasync mode this is non-blocking; in threading
        mode the caller handles the Qt event loop separately.
        """
        if HAS_QT:
            self._build_widget()  # Safe now — QApplication is already alive
            self._widget.show()
            logging.info("JARVIS HUD displayed.")
        else:
            print("PyQt6 is not installed. Running in headless mode.")
