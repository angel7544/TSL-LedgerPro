
import sys
from PySide6.QtWidgets import QApplication, QLabel
from auth.ui import LoginWindow

def verify_styles():
    app = QApplication(sys.argv)
    window = LoginWindow()
    
    print(f"Window Object Name: {window.objectName()}")
    print(f"Window Stylesheet: {window.styleSheet()[:100]}...")
    
    # Check left panel labels
    left_panel = window.findChild(object, "LeftPanel")
    if left_panel:
        labels = left_panel.findChildren(QLabel)
        print(f"Found {len(labels)} labels in LeftPanel")
        for label in labels:
            print(f"Label Text: {label.text()[:20]}")
            # We can't easily check computed style without rendering, 
            # but we can check if they have inline styles or if the main stylesheet covers them.
            pass
            
    window.show()
    # app.exec() # Don't block
    print("Verification complete.")

if __name__ == "__main__":
    verify_styles()
