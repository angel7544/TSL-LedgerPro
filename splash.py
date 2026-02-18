from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)
        
        # Background
        self.setStyleSheet("""
            QSplashScreen {
                background-color: #FFFFFF;
                border-radius: 15px;
                border: 1px solid #E2E8F0;
            }
            QLabel { color: #1E293B; }
            QProgressBar {
                border: none;
                background-color: #F1F5F9;
                border-radius: 5px;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 5px;
            }
        """)
        
        # Logo
        logo = QLabel("LedgerPro")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 32px; font-weight: bold; color: #2563EB; margin-bottom: 10px;")
        layout.addWidget(logo)
        
        # Loading Text
        self.loading_label = QLabel("Initializing LedgerPro...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        
        layout.addStretch()

    def update_progress(self, value, text=None):
        self.progress.setValue(value)
        if text:
            self.loading_label.setText(text)
