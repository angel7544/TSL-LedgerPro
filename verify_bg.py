
import sys
import os
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QPixmap
from auth.ui import LoginWindow

def verify_bg():
    app = QApplication(sys.argv)
    window = LoginWindow()
    
    print(f"Window Object Name: {window.objectName()}")
    
    # Check if bg_pixmap is loaded
    if hasattr(window, 'bg_pixmap'):
        if window.bg_pixmap.isNull():
             print("ERROR: Background pixmap is NULL. Check path.")
        else:
             print(f"Background pixmap loaded. Size: {window.bg_pixmap.size()}")
    else:
        print("ERROR: bg_pixmap attribute not found on LoginWindow")

    # Check path construction
    base_dir = os.path.dirname(os.path.abspath("auth/ui.py")) # Mocking what auth/ui.py does roughly
    # Actually let's replicate the logic in ui.py
    # base_dir = os.path.dirname(os.path.dirname(__file__))
    # But here we are running from root.
    
    expected_path = os.path.abspath("assets/loginUi.png")
    print(f"Expected Asset Path: {expected_path}")
    print(f"Exists: {os.path.exists(expected_path)}")
    
    window.show()
    # app.exec()
    print("Verification complete.")

if __name__ == "__main__":
    verify_bg()
