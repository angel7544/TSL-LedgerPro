from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QMessageBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from auth.auth_logic import login_user, signup_user
from auth.session import Session

class LoginWindow(QWidget):
    login_successful = Signal(str)
    switch_to_signup = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - LedgerPro")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget { background-color: #F5F7FA; font-family: 'Segoe UI'; color: #334155; }
            QLineEdit { padding: 10px; border: 1px solid #CBD5E1; border-radius: 6px; color: #334155; background-color: white; }
            QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; }
            QPushButton#LoginBtn { background-color: #2563EB; color: white; }
            QPushButton#LoginBtn:hover { background-color: #1D4ED8; }
            QPushButton#SignupLink { background-color: transparent; color: #2563EB; border: none; }
            QPushButton#SignupLink:hover { text-decoration: underline; }
            QLabel { color: #334155; }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        
        # Logo / Title
        title = QLabel("LedgerPro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form Container
        form_container = QFrame()
        form_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        form_layout.addWidget(QLabel("Email"))
        form_layout.addWidget(self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.password_input)
        
        login_btn = QPushButton("Login")
        login_btn.setObjectName("LoginBtn")
        login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(login_btn)
        
        layout.addWidget(form_container)
        
        # Signup Link
        signup_link = QPushButton("Don't have an account? Sign up")
        signup_link.setObjectName("SignupLink")
        signup_link.clicked.connect(self.switch_to_signup.emit)
        layout.addWidget(signup_link)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        user = login_user(email, password)
        if user:
            Session.get_instance().set_user(user)
            self.login_successful.emit(user.get('name', email))
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid email or password")

class SignupWindow(QWidget):
    signup_successful = Signal()
    switch_to_login = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up - LedgerPro")
        self.setFixedSize(400, 550)
        self.setStyleSheet("""
            QWidget { background-color: #F5F7FA; font-family: 'Segoe UI'; color: #334155; }
            QLineEdit { padding: 10px; border: 1px solid #CBD5E1; border-radius: 6px; color: #334155; background-color: white; }
            QPushButton { padding: 10px; border-radius: 6px; font-weight: bold; }
            QPushButton#SignupBtn { background-color: #2563EB; color: white; }
            QPushButton#SignupBtn:hover { background-color: #1D4ED8; }
            QPushButton#LoginLink { background-color: transparent; color: #2563EB; border: none; }
            QPushButton#LoginLink:hover { text-decoration: underline; }
            QLabel { color: #334155; }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        
        # Logo / Title
        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form Container
        form_container = QFrame()
        form_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        form_layout.addWidget(QLabel("Name"))
        form_layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        form_layout.addWidget(QLabel("Email"))
        form_layout.addWidget(self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.password_input)
        
        signup_btn = QPushButton("Sign Up")
        signup_btn.setObjectName("SignupBtn")
        signup_btn.clicked.connect(self.handle_signup)
        form_layout.addWidget(signup_btn)
        
        layout.addWidget(form_container)
        
        # Login Link
        login_link = QPushButton("Already have an account? Login")
        login_link.setObjectName("LoginLink")
        login_link.clicked.connect(self.switch_to_login.emit)
        layout.addWidget(login_link)

    def handle_signup(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not name or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        success = signup_user(name, email, password)
        if success:
            QMessageBox.information(self, "Success", "Account created! Please login.")
            self.switch_to_login.emit()
        else:
            QMessageBox.critical(self, "Error", "Email already exists or invalid data")
