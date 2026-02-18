import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer

from database.db import init_db
from splash import SplashScreen
from auth.ui import LoginWindow, SignupWindow
from ui.main_window import MainWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("LedgerPro Desktop")
        
        # Show Splash
        self.splash = SplashScreen()
        self.splash.show()
        
        # Initialize Logic
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.loading_step)
        self.timer.start(30) # 30ms * 100 steps = 3 seconds roughly
        
        # Windows
        self.login_window = None
        self.signup_window = None
        self.main_window = None

    def loading_step(self):
        self.progress += 1
        self.splash.update_progress(self.progress)
        
        if self.progress == 30:
            self.splash.update_progress(self.progress, "Connecting to Database...")
            init_db()
            
        if self.progress == 70:
            self.splash.update_progress(self.progress, "Loading User Interface...")
            
        if self.progress >= 100:
            self.timer.stop()
            self.show_login()

    def show_login(self):
        self.splash.close()
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.switch_to_signup.connect(self.show_signup)
        self.login_window.show()

    def show_signup(self):
        if self.login_window:
            self.login_window.close()
        self.signup_window = SignupWindow()
        self.signup_window.switch_to_login.connect(self.show_login_from_signup)
        self.signup_window.show()

    def show_login_from_signup(self):
        if self.signup_window:
            self.signup_window.close()
        self.show_login()

    def show_main_window(self):
        if self.login_window:
            self.login_window.close()
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.run()
