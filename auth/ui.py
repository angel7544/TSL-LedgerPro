from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFormLayout, QFrame, QCheckBox, QInputDialog, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
import os
from auth.auth_logic import login_user, signup_user, update_password
from auth.session import Session

from database.db import execute_read_query, execute_write_query

class AdminAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Verification Required")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        info = QLabel("Database configuration is restricted. Please enter Administrator (Owner) credentials to continue.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #475569; font-size: 13px; margin-bottom: 10px;")
        layout.addWidget(info)
        
        form_layout = QFormLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Admin Email / User ID")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Admin Password")
        
        form_layout.addRow("Admin Email:", self.email_input)
        form_layout.addRow("Admin Password:", self.password_input)
        
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.handle_verify)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def handle_verify(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Validation Error", "Please enter admin email and password.")
            return
            
        user = login_user(email, password)
        if user and user.get('role', 'owner') in ['owner', 'admin']:
            self.accept()
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid credentials or non-owner account. Database setup is restricted to Administrators.")

def verify_admin_before_db_setup(parent_widget):
    try:
        user_res = execute_read_query("SELECT COUNT(*) FROM users")
        if user_res:
            row = user_res[0]
            user_count = list(row.values())[0] if isinstance(row, dict) else row[0]
        else:
            user_count = 0
    except Exception:
        user_count = 0

    if user_count == 0:
        # Initial database setup before any users exist
        from ui.db_config_dialog import DBConfigDialog
        dialog = DBConfigDialog(parent_widget)
        dialog.exec()
    else:
        auth_dialog = AdminAuthDialog(parent_widget)
        if auth_dialog.exec() == QDialog.DialogCode.Accepted:
            from ui.db_config_dialog import DBConfigDialog
            dialog = DBConfigDialog(parent_widget)
            dialog.exec()

class LoginWindow(QWidget):
    login_successful = Signal(str)
    switch_to_signup = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - LedgerPro")
        self.setFixedSize(900, 600) # Wide layout
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "loginUi.png")
        self.bg_pixmap = QPixmap(bg_path)
        
        # Traditional Accounting Theme
        # Deep Navy Blue: #003366
        # Professional Gray: #F4F4F4
        # Text: #333333
        self.setObjectName("LoginWindow")
        self.setStyleSheet(f"""
            QWidget#LoginWindow {{ 
                background-color: transparent; 
                font-family: 'Segoe UI'; 
                color: #333333; 
            }}
            QFrame#LeftPanel {{ 
                background-color: rgba(0, 51, 102, 0.85); 
                border-right: 1px solid rgba(255, 255, 255, 0.2); 
            }}
            QFrame#RightPanel {{ 
                background-color: rgba(255, 255, 255, 0.90); 
                border-radius: 8px; 
            }}
            
            QLineEdit {{ 
                padding: 12px; 
                border: 1px solid #CCCCCC; 
                border-radius: 4px; 
                font-size: 13px; 
                background-color: #FFFFFF; 
            }}
            QLineEdit:focus {{ border: 1px solid #003366; }}
            
            QPushButton#LoginBtn {{ 
                background-color: #003366; 
                color: white; 
                padding: 12px; 
                border-radius: 4px; 
                font-weight: bold; 
                font-size: 14px; 
                border: none; 
            }}
            QPushButton#LoginBtn:hover {{ background-color: #004080; }}
            
            QPushButton#SignupLink {{ background-color: transparent; color: #003366; font-weight: 600; border: none; }}
            QPushButton#SignupLink:hover {{ text-decoration: underline; }}
            
            QPushButton#ForgotPassBtn {{ background-color: transparent; color: #666666; font-size: 12px; border: none; }}
            QPushButton#ForgotPassBtn:hover {{ color: #003366; text-decoration: underline; }}
            
            QLabel {{ background-color: transparent; color: #333333; }}
            QCheckBox {{ spacing: 5px; color: #555555; background-color: transparent; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; }}
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Panel: Branding (Traditional Dark Blue) ---
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Panel: Branding (Traditional Dark Blue) ---
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logos
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        br31_path = os.path.join(base_dir, "assets", "tsl_icon.png")
        if os.path.exists(br31_path):
            br31_lbl = QLabel()
            # Use a white container for the logo if it has transparency/dark text
            logo_bg = QFrame()
            logo_bg.setStyleSheet(" border-radius: 10px; padding: 10px;")
            bg_layout = QVBoxLayout(logo_bg)
            bg_layout.setContentsMargins(5, 5, 5, 5)
            
            pix = QPixmap(br31_path).scaled(196, 196, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            br31_lbl.setPixmap(pix)
            br31_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bg_layout.addWidget(br31_lbl)
            
            logo_container.addWidget(logo_bg)
            
        left_layout.addLayout(logo_container)
        left_layout.addSpacing(40)
        
        # App Title
        title = QLabel("LedgerPro Desktop")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        left_layout.addWidget(title)
        
        subtitle = QLabel("Professional Accounting & Inventory")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #AACCFF; margin-top: 5px;")
        left_layout.addWidget(subtitle)
        
        left_layout.addStretch()
        
        # Credits
        credits = QLabel("Developed for The Space Labs\nUpdated by Angel (Mehul) Singh\nPowered by Br31Technologies")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setStyleSheet("font-size: 12px; color: #AACCFF; line-height: 1.5;")
        left_layout.addWidget(credits)
        
        version = QLabel("Version 2.6.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("font-size: 11px; color: #88AADD; margin-top: 10px;")
        left_layout.addWidget(version)
        
        main_layout.addWidget(left_panel, stretch=4)
        
        # --- Right Panel: Login Form ---
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.setContentsMargins(60, 40, 60, 40)
        
        form_title = QLabel("Secure Login")
        form_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #003366; margin-bottom: 10px;")
        right_layout.addWidget(form_title)
        
        form_sub = QLabel("Please identify yourself to continue.")
        form_sub.setStyleSheet("font-size: 14px; color: #666666; margin-bottom: 30px;")
        right_layout.addWidget(form_sub)
        
        # Form
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email ID / Username")
        right_layout.addWidget(QLabel("User ID"))
        right_layout.addWidget(self.email_input)
        right_layout.addSpacing(15)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        right_layout.addWidget(QLabel("Password"))
        right_layout.addWidget(self.password_input)
        
        # # Features: Remember Me & Forgot Password
        options_layout = QHBoxLayout()
        # self.remember_cb = QCheckBox("Remember Me")
        # options_layout.addWidget(self.remember_cb)
        # options_layout.addStretch()
        
        # forgot_btn = QPushButton("Forgot Password?")
        # forgot_btn.setObjectName("ForgotPassBtn")
        # forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # forgot_btn.clicked.connect(self.forgot_password)
        # options_layout.addWidget(forgot_btn)
        
        right_layout.addLayout(options_layout)
        right_layout.addSpacing(20)
        
        login_btn = QPushButton("LOGIN")
        login_btn.setObjectName("LoginBtn")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        right_layout.addWidget(login_btn)
        
        right_layout.addSpacing(20)
        
        # Signup Link
        try:
            count_res = execute_read_query("SELECT COUNT(*) FROM users")
            user_count = count_res[0][0] if count_res else 0
            
            if user_count == 0:
                signup_container = QHBoxLayout()
                signup_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
                signup_container.addWidget(QLabel("First time setup?"))
                
                signup_link = QPushButton("Create Admin Account")
                signup_link.setObjectName("SignupLink")
                signup_link.setCursor(Qt.CursorShape.PointingHandCursor)
                signup_link.clicked.connect(self.switch_to_signup.emit)
                signup_container.addWidget(signup_link)
                
                right_layout.addLayout(signup_container)
        except:
            pass
            
        main_layout.addWidget(right_panel, stretch=5)
        
        # Database Setup Button
        db_setup_btn = QPushButton("⚙ Database Setup")
        db_setup_btn.setStyleSheet("background-color: transparent; color: #666666; font-size: 12px; border: none;")
        db_setup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        db_setup_btn.clicked.connect(self.open_db_setup)
        right_layout.addStretch()
        right_layout.addWidget(db_setup_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def open_db_setup(self):
        verify_admin_before_db_setup(self)

    def paintEvent(self, event):
        if not self.bg_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.bg_pixmap)
        # No super().paintEvent(event) call to avoid default background clearing
        # but we must ensure we don't break anything. QWidget's paintEvent is empty usually.
        # However, stylesheet might need it. 
        # But we want to DRAW UNDER stylesheet components.
        # Actually, QWidget.paintEvent is where the stylesheet background is drawn via drawPrimitive.
        # If we don't call it, stylesheet background-color is ignored (which is what we want for the main widget).

    def forgot_password(self):
        email, ok = QInputDialog.getText(self, "Password Recovery", "Enter your registered email address:")
        if ok and email:
            # Check if email exists
            res = execute_read_query("SELECT id FROM users WHERE email = ?", (email,))
            if res:
                QMessageBox.information(self, "Recovery Email Sent", f"If {email} exists in our system, we have sent a password reset link. (Simulation)")
            else:
                QMessageBox.warning(self, "Error", "Email not found.")

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
        self.setFixedSize(900, 600)  # Match LoginWindow size
        self.setObjectName("SignupWindow")
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        bg_path = os.path.join(base_dir, "assets", "loginUi.png")
        self.bg_pixmap = QPixmap(bg_path)
        
        # Use same stylesheet theme as LoginWindow
        self.setStyleSheet(f"""
            QWidget#SignupWindow {{ 
                background-color: transparent; 
                font-family: 'Segoe UI'; 
                color: #333333; 
            }}
            QFrame#LeftPanel {{ 
                background-color: rgba(0, 51, 102, 0.85); 
                border-right: 1px solid rgba(255, 255, 255, 0.2); 
            }}
            QFrame#RightPanel {{ 
                background-color: rgba(255, 255, 255, 0.90); 
                border-radius: 8px; 
            }}
            
            QLineEdit {{ 
                padding: 12px; 
                border: 1px solid #CCCCCC; 
                border-radius: 4px; 
                font-size: 13px; 
                background-color: #FFFFFF; 
            }}
            QLineEdit:focus {{ border: 1px solid #003366; }}
            
            QPushButton#SignupBtn {{ 
                background-color: #003366; 
                color: white; 
                padding: 12px; 
                border-radius: 4px; 
                font-weight: bold; 
                font-size: 14px; 
                border: none; 
            }}
            QPushButton#SignupBtn:hover {{ background-color: #004080; }}
            
            QPushButton#LoginLink {{ background-color: transparent; color: #003366; font-weight: 600; border: none; }}
            QPushButton#LoginLink:hover {{ text-decoration: underline; }}
            
            QLabel {{ background-color: transparent; color: #333333; }}
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Panel: Branding (Same as Login) ---
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        br31_path = os.path.join(base_dir, "assets", "tsl_icon.png")
        if os.path.exists(br31_path):
            br31_lbl = QLabel()
            # Consistent with LoginWindow logo style
            pix = QPixmap(br31_path).scaled(196, 196, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            br31_lbl.setPixmap(pix)
            br31_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_container.addWidget(br31_lbl)
            
        left_layout.addLayout(logo_container)
        left_layout.addSpacing(40)
        
        title = QLabel("LedgerPro Desktop")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        left_layout.addWidget(title)
        
        subtitle = QLabel("Professional Accounting & Inventory")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #AACCFF; margin-top: 5px;")
        left_layout.addWidget(subtitle)
        
        left_layout.addStretch()
        
        credits = QLabel("Developed for The Space Labs\nUpdated by Angel (Mehul) Singh\nPowered by Br31Technologies")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setStyleSheet("font-size: 12px; color: #AACCFF; line-height: 1.5;")
        left_layout.addWidget(credits)
        
        version = QLabel("Version 2.6.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("font-size: 11px; color: #88AADD; margin-top: 10px;")
        left_layout.addWidget(version)
        
        main_layout.addWidget(left_panel, stretch=4)
        
        # --- Right Panel: Signup Form ---
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.setContentsMargins(60, 40, 60, 40)
        
        form_title = QLabel("Create Account")
        form_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #003366; margin-bottom: 10px;")
        right_layout.addWidget(form_title)
        
        form_sub = QLabel("Join LedgerPro today.")
        form_sub.setStyleSheet("font-size: 14px; color: #666666; margin-bottom: 20px;")
        right_layout.addWidget(form_sub)
        
        # Form Fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        right_layout.addWidget(QLabel("Full Name"))
        right_layout.addWidget(self.name_input)
        right_layout.addSpacing(15)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        right_layout.addWidget(QLabel("Email"))
        right_layout.addWidget(self.email_input)
        right_layout.addSpacing(15)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        right_layout.addWidget(QLabel("Password"))
        right_layout.addWidget(self.password_input)
        
        right_layout.addSpacing(30)
        
        signup_btn = QPushButton("SIGN UP")
        signup_btn.setObjectName("SignupBtn")
        signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_btn.clicked.connect(self.handle_signup)
        right_layout.addWidget(signup_btn)
        
        right_layout.addSpacing(20)
        
        login_link = QPushButton("Already have an account? Login")
        login_link.setObjectName("LoginLink")
        login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        login_link.clicked.connect(self.switch_to_login.emit)
        right_layout.addWidget(login_link)
        
        main_layout.addWidget(right_panel, stretch=5)

        # Database Setup Button
        db_setup_btn = QPushButton("⚙ Database Setup")
        db_setup_btn.setStyleSheet("background-color: transparent; color: #666666; font-size: 12px; border: none;")
        db_setup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        db_setup_btn.clicked.connect(self.open_db_setup)
        right_layout.addStretch()
        right_layout.addWidget(db_setup_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def open_db_setup(self):
        verify_admin_before_db_setup(self)

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

    def paintEvent(self, event):
        if not self.bg_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.bg_pixmap)
