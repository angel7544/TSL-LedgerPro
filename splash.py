from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont
import os
import sys

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
                border: 1px solid #E8E8F3;
                background-color: #F1F5F9;
                border-radius: 10px;
                height: 22px;
                text-align: center;
                font-weight: bold;
                color: #348545;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #3B82F6);
                border-radius: 8px;
                width: 10px;
                margin: 1px;
            }
        """)

        logo_img = QLabel()
        logo_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(base_dir)
        meipass = getattr(sys, "_MEIPASS", None)
        candidate_paths = [
            os.path.join(base_dir, "assets", "br31logo.png"),
            os.path.join(base_dir, "br31logo.png"),
            os.path.join(project_root, "assets", "br31logo.png"),
            os.path.join(project_root, "br31logo.png"),
            os.path.join(base_dir, "assets", "tsl_icon.png"),
            os.path.join(project_root, "assets", "tsl_icon.png"),
        ]
        if meipass:
            candidate_paths.extend([
                os.path.join(meipass, "assets", "br31logo.png"),
                os.path.join(meipass, "br31logo.png"),
                os.path.join(meipass, "assets", "tsl_icon.png"),
            ])
        for path in candidate_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    logo_img.setPixmap(pixmap.scaledToHeight(72, Qt.SmoothTransformation))
                    break
        layout.addWidget(logo_img)

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
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress)
        
        layout.addStretch()

    def update_progress(self, value, text=None):
        self.progress.setValue(value)
        if text:
            self.loading_label.setText(text)
