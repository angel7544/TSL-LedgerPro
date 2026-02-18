from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame, QDialog, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QPixmap
import os

from ui.dashboard import DashboardPage
from ui.master_data import CustomersPage, VendorsPage, ItemsPage
from ui.invoices import InvoicesPage
from ui.bills import BillsPage
from ui.stock import StockPage
from ui.reports import ReportsPage
from ui.settings import SettingsPage
from ui.styles import STYLESHEET
from auth.session import Session


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About LedgerPro Desktop")
        self.setMinimumSize(600, 500)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "assets", "tsl_icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(base_dir, "assets", "br31logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(64, Qt.SmoothTransformation))
        title_label = QLabel("LedgerPro Desktop")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(logo_label)
        header_layout.addSpacing(12)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setPlainText(
            "🏢 About LedgerPro\n\n"
            "LedgerPro Desktop is a professional accounting and inventory management software designed for small and medium businesses. It provides powerful tools for invoicing, GST billing, stock valuation (FIFO), purchase management, and financial reporting — all in a simple and secure desktop application.\n\n"
            "LedgerPro helps businesses streamline operations, maintain accurate inventory records, and generate compliant GST invoices with ease.\n\n"
            "🚀 App Version\n\n"
            "Application Name: LedgerPro Desktop\n"
            "Current Version: 1.0.0\n"
            "Release Date: February 2026\n"
            "Platform: Windows Desktop\n"
            "Database: SQLite (Local Device Storage)\n"
            "License: Proprietary\n\n"
            "👨‍💻 Developer Information\n\n"
            "Developed By: Angel Mehul\n"
            "Qualification: BCA | MCA (Pursuing)\n"
            "Specialization: Full Stack Development | Cloud & DevOps\n"
            "Technology Stack: Python, PyQt6, SQLite\n\n"
            "This software is built with a focus on performance, reliability, and real-world business needs.\n\n"
            "🏢 Client Information\n\n"
            "This software is designed for:\n\n"
            "Electrical & Hardware Shops\n"
            "Retail Stores\n"
            "Small Manufacturing Units\n"
            "Wholesalers & Distributors\n"
            "MSME Businesses\n"
            "Service Providers requiring GST billing\n\n"
            "For custom deployment or white-label solutions, please contact the developer.\n\n"
            "📞 Contact Details\n\n"
            "📧 Email: your_email@example.com\n"
            "📱 Phone: +91-XXXXXXXXXX\n"
            "🌐 Website: www.yourwebsite.com\n"
            "📍 Location: India\n\n"
            "For technical support, licensing, or feature requests, feel free to reach out.\n\n"
            "🎯 Use Cases\n\n"
            "LedgerPro can be used for:\n\n"
            "✔ GST Invoicing (CGST, SGST, IGST)\n"
            "✔ Quotation Management\n"
            "✔ Vendor Bills & Purchase Tracking\n"
            "✔ FIFO Inventory Valuation\n"
            "✔ Stock Management\n"
            "✔ Outstanding Payment Tracking\n"
            "✔ Sales & Purchase Reports\n"
            "✔ PDF Invoice Printing\n"
            "✔ Local Data Backup & Restore\n\n"
            "❓ Frequently Asked Questions (FAQ)\n\n"
            "1️⃣ Is internet required to use LedgerPro?\n\n"
            "No. LedgerPro is a fully offline desktop application.\n\n"
            "2️⃣ Is GST calculation automatic?\n\n"
            "Yes. The system automatically calculates:\n\n"
            "CGST + SGST for intra-state\n\n"
            "IGST for inter-state transactions\n\n"
            "3️⃣ How is inventory valued?\n\n"
            "LedgerPro uses FIFO (First-In-First-Out) valuation method for accurate stock cost calculation.\n\n"
            "4️⃣ Can I backup my data?\n\n"
            "Yes. You can backup and restore your database anytime from Settings.\n\n"
            "5️⃣ Can I print invoices?\n\n"
            "Yes. Professional PDF invoices can be generated and printed directly.\n\n"
            "6️⃣ Is my data secure?\n\n"
            "Yes. All data is stored locally on your device. Login authentication is protected with encrypted passwords.\n\n"
            "7️⃣ Can this software handle large inventory?\n\n"
            "Yes. It is designed to manage hundreds or thousands of items efficiently.\n\n"
            "🛠 Help & Support\n\n"
            "If you experience any issues:\n\n"
            "Restart the application\n"
            "Check database backup\n"
            "Contact support\n\n"
            "For feature upgrades or enterprise customization, please contact the developer.\n\n"
            "🔒 Disclaimer\n\n"
            "This software is intended for business accounting assistance. Users are responsible for verifying tax compliance as per government regulations.\n\n"
            "🌟 Optional (Premium Touch for Professional Look)\n\n"
            "© 2026 LedgerPro Desktop. All Rights Reserved.\n"
            "Designed & Developed by Angel Mehul."
        )
        layout.addWidget(text_widget)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        footer_layout.addWidget(close_btn)
        layout.addLayout(footer_layout)


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("About")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        base_dir = os.path.dirname(os.path.dirname(__file__))
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(base_dir, "assets", "br31logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToHeight(64, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)
        header_text = QLabel("LedgerPro Desktop")
        header_text.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        text_widget = QTextEdit()
        text_widget.setReadOnly(True)
        text_widget.setPlainText(
            "🏢 About LedgerPro\n\n"
            "LedgerPro Desktop is a professional accounting and inventory management software designed for small and medium businesses. It provides powerful tools for invoicing, GST billing, stock valuation (FIFO), purchase management, and financial reporting — all in a simple and secure desktop application.\n\n"
            "LedgerPro helps businesses streamline operations, maintain accurate inventory records, and generate compliant GST invoices with ease.\n\n"
            "🚀 App Version\n\n"
            "Application Name: LedgerPro Desktop\n"
            "Current Version: 1.0.0\n"
            "Release Date: February 2026\n"
            "Platform: Windows Desktop\n"
            "Database: SQLite (Local Device Storage)\n"
            "License: Proprietary\n\n"
            "👨‍💻 Developer Information\n\n"
            "Developed By: Angel Mehul\n"
            "Qualification: BCA | MCA (Pursuing)\n"
            "Specialization: Full Stack Development | Cloud & DevOps\n"
            "Technology Stack: Python, PyQt6, SQLite\n\n"
            "This software is built with a focus on performance, reliability, and real-world business needs.\n\n"
            "🏢 Client Information\n\n"
            "This software is designed for:\n\n"
            "Electrical & Hardware Shops\n"
            "Retail Stores\n"
            "Small Manufacturing Units\n"
            "Wholesalers & Distributors\n"
            "MSME Businesses\n"
            "Service Providers requiring GST billing\n\n"
            "For custom deployment or white-label solutions, please contact the developer.\n\n"
            "📞 Contact Details\n\n"
            "📧 Email: your_email@example.com\n"
            "📱 Phone: +91-XXXXXXXXXX\n"
            "🌐 Website: www.yourwebsite.com\n"
            "📍 Location: India\n\n"
            "For technical support, licensing, or feature requests, feel free to reach out.\n\n"
            "🎯 Use Cases\n\n"
            "LedgerPro can be used for:\n\n"
            "✔ GST Invoicing (CGST, SGST, IGST)\n"
            "✔ Quotation Management\n"
            "✔ Vendor Bills & Purchase Tracking\n"
            "✔ FIFO Inventory Valuation\n"
            "✔ Stock Management\n"
            "✔ Outstanding Payment Tracking\n"
            "✔ Sales & Purchase Reports\n"
            "✔ PDF Invoice Printing\n"
            "✔ Local Data Backup & Restore\n\n"
            "❓ Frequently Asked Questions (FAQ)\n\n"
            "1️⃣ Is internet required to use LedgerPro?\n\n"
            "No. LedgerPro is a fully offline desktop application.\n\n"
            "2️⃣ Is GST calculation automatic?\n\n"
            "Yes. The system automatically calculates:\n\n"
            "CGST + SGST for intra-state\n\n"
            "IGST for inter-state transactions\n\n"
            "3️⃣ How is inventory valued?\n\n"
            "LedgerPro uses FIFO (First-In-First-Out) valuation method for accurate stock cost calculation.\n\n"
            "4️⃣ Can I backup my data?\n\n"
            "Yes. You can backup and restore your database anytime from Settings.\n\n"
            "5️⃣ Can I print invoices?\n\n"
            "Yes. Professional PDF invoices can be generated and printed directly.\n\n"
            "6️⃣ Is my data secure?\n\n"
            "Yes. All data is stored locally on your device. Login authentication is protected with encrypted passwords.\n\n"
            "7️⃣ Can this software handle large inventory?\n\n"
            "Yes. It is designed to manage hundreds or thousands of items efficiently.\n\n"
            "🛠 Help & Support\n\n"
            "If you experience any issues:\n\n"
            "Restart the application\n"
            "Check database backup\n"
            "Contact support\n\n"
            "For feature upgrades or enterprise customization, please contact the developer.\n\n"
            "🔒 Disclaimer\n\n"
            "This software is intended for business accounting assistance. Users are responsible for verifying tax compliance as per government regulations.\n\n"
            "🌟 Optional (Premium Touch for Professional Look)\n\n"
            "© 2026 LedgerPro Desktop. All Rights Reserved.\n"
            "Designed & Developed by Angel Mehul."
        )
        layout.addWidget(text_widget)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LedgerPro Desktop")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_candidates = [
            os.path.join(base_dir, "tsl_icon.ico"),
            os.path.join(base_dir, "assets", "tsl_icon.ico"),
            os.path.join(base_dir, "tsl_icon.png"),
            os.path.join(base_dir, "assets", "tsl_icon.png"),
        ]
        for path in icon_candidates:
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break

        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About LedgerPro", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout (Horizontal: Sidebar + Content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # App Logo/Title in Sidebar
        app_title = QLabel("LedgerPro")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; padding-left: 20px; margin-bottom: 20px;")
        sidebar_layout.addWidget(app_title)
        
        # Navigation Buttons
        self.nav_buttons = []
        self.add_nav_button("Dashboard", 0, sidebar_layout)
        self.add_nav_button("Customers", 1, sidebar_layout)
        self.add_nav_button("Vendors", 2, sidebar_layout)
        self.add_nav_button("Items", 3, sidebar_layout)
        self.add_nav_button("Invoices", 4, sidebar_layout)
        self.add_nav_button("Purchases", 5, sidebar_layout)
        self.add_nav_button("Stock", 6, sidebar_layout)
        self.add_nav_button("Reports", 7, sidebar_layout)
        self.add_nav_button("Settings", 8, sidebar_layout)
        self.add_nav_button("About", 9, sidebar_layout)
        
        sidebar_layout.addStretch()
        
        # User Info
        user = Session.get_instance().get_user()
        user_name = user['name'] if user else "User"
        user_lbl = QLabel(f"Logged in as:\n{user_name}")
        user_lbl.setStyleSheet("color: #94A3B8; padding-left: 20px; font-size: 12px;")
        sidebar_layout.addWidget(user_lbl)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background-color: transparent; color: #EF4444; border: none; text-align: left; padding: 10px 20px; font-weight: bold;")
        logout_btn.clicked.connect(self.close) # Ideally switch to login screen
        sidebar_layout.addWidget(logout_btn)
        
        main_layout.addWidget(self.sidebar)
        
        # Content Area
        content_container = QWidget()
        content_container.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Bar
        header = QFrame()
        header.setObjectName("Header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Page Title (Dynamic)
        self.page_title = QLabel("Dashboard")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
        
        content_layout.addWidget(header)
        
        # Stacked Pages
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardPage())
        self.stack.addWidget(CustomersPage())
        self.stack.addWidget(VendorsPage())
        self.stack.addWidget(ItemsPage())
        self.stack.addWidget(InvoicesPage())
        self.stack.addWidget(BillsPage())
        self.stack.addWidget(StockPage())
        self.stack.addWidget(ReportsPage())
        self.stack.addWidget(SettingsPage())
        self.stack.addWidget(AboutPage())
        
        content_layout.addWidget(self.stack)
        
        main_layout.addWidget(content_container)

    def add_nav_button(self, text, index, layout):
        btn = QPushButton(text)
        btn.setCheckable(True)
        if index == 0:
            btn.setChecked(True)
            self.current_nav_btn = btn
            
        btn.clicked.connect(lambda: self.switch_page(index, btn))
        layout.addWidget(btn)
        self.nav_buttons.append(btn)

    def switch_page(self, index, btn):
        self.stack.setCurrentIndex(index)
        self.page_title.setText(btn.text())
        
        # Update button styles
        for b in self.nav_buttons:
            b.setChecked(False)
        btn.setChecked(True)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()
