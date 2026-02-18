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
        text_widget.setHtml(
            "<h2>About LedgerPro Desktop</h2>"
            "<p>LedgerPro Desktop is a professional accounting and inventory management solution for small and medium businesses. "
            "It provides powerful tools for invoicing, GST billing, FIFO stock valuation, purchase management and financial reporting "
            "in a fast and secure Windows desktop application.</p>"
            "<h3>App Version</h3>"
            "<p>"
            "<b>Application Name:</b> LedgerPro Desktop<br>"
            "<b>Current Version:</b> 1.0.0<br>"
            "<b>Release Date:</b> February 2026<br>"
            "<b>Platform:</b> Windows Desktop<br>"
            "<b>Database:</b> SQLite (Local Device Storage)<br>"
            "<b>License:</b> Proprietary"
            "</p>"
            "<h3>Developer</h3>"
            "<p>"
            "<b>Name:</b> Angel (Mehul) Singh<br>"
            "<b>Company:</b> BR31Technologies<br>"
            "<b>Specialization:</b> Full Stack Development, Cloud & DevOps<br>"
            "<b>Technology Stack:</b> Python, PySide6, SQLite"
            "</p>"
            "<h3>Client</h3>"
            "<p><b>Primary Client:</b> The Space Labs</p>"
            "<h3>Contact</h3>"
            "<p>"
            "<b>Email:</b> support@br31tech.live<br>"
            "<b>Phone:</b> +91 9135893002<br>"
            "<b>Location:</b> India"
            "</p>"
            "<h3>Key Capabilities</h3>"
            "<ul>"
            "<li>GST invoicing (CGST, SGST, IGST)</li>"
            "<li>Quotation and billing management</li>"
            "<li>FIFO-based inventory and stock valuation</li>"
            "<li>Purchase, sales and outstanding tracking</li>"
            "<li>Stock management and reporting</li>"
            "<li>PDF invoice and report generation</li>"
            "<li>Local data backup and restore</li>"
            "</ul>"
            "<h3>Help &amp; Support</h3>"
            "<p>If you experience any issues, you can restart the application, verify your latest backup or contact support using the details above.</p>"
            "<h3>Disclaimer</h3>"
            "<p>This software is intended to assist with business accounting. "
            "Users are responsible for verifying that all tax calculations and filings comply with the latest government regulations.</p>"
            "<p style='margin-top: 16px; font-size: 11px;'>"
            "© 2026 LedgerPro Desktop. All rights reserved. Designed &amp; developed by Angel (Mehul) Singh."
            "</p>"
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

        # title = QLabel("About")
        # title.setStyleSheet("font-size: 24px; font-weight: bold;")
        # layout.addWidget(title)

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
        text_widget.setHtml(
            "<h2>About LedgerPro Desktop</h2>"
            "<p>LedgerPro Desktop is a professional accounting and inventory management solution for small and medium businesses. "
            "It helps streamline operations, maintain accurate inventory records and generate compliant GST invoices with ease.</p>"
            "<h3>App Version</h3>"
            "<p>"
            "<b>Application Name:</b> LedgerPro Desktop<br>"
            "<b>Current Version:</b> 1.0.0<br>"
            "<b>Release Date:</b> February 2026<br>"
            "<b>Platform:</b> Windows Desktop<br>"
            "<b>Database:</b> SQLite (Local Device Storage)<br>"
            "<b>License:</b> Proprietary"
            "</p>"
            "<h3>Developer</h3>"
            "<p>"
            "<b>Name:</b> Angel (Mehul) Singh<br>"
            "<b>Company:</b> BR31Technologies<br>"
            "<b>Specialization:</b> Full Stack Development, Cloud & DevOps<br>"
            "<b>Technology Stack:</b> Python, PySide6, SQLite"
            "</p>"
            "<h3>Client</h3>"
            "<p><b>Primary Client:</b> The Space Labs</p>"
            "<h3>Key Capabilities</h3>"
            "<ul>"
            "<li>GST invoicing (CGST, SGST, IGST)</li>"
            "<li>Quotation management</li>"
            "<li>Vendor bills and purchase tracking</li>"
            "<li>FIFO inventory valuation</li>"
            "<li>Stock and outstanding management</li>"
            "<li>Sales and purchase reports</li>"
            "<li>PDF invoice printing</li>"
            "<li>Local data backup and restore</li>"
            "</ul>"
            "<h3>Help &amp; Support</h3>"
            "<p>If you experience any issues, you can restart the application, verify your latest backup or contact support.</p>"
            "<h3>Contact</h3>"
            "<p>"
            "<b>Email:</b> support@br31tech.live<br>"
            "<b>Phone:</b> +91 9135893002<br>"
            "<b>Location:</b> India"
            "</p>"
            "<h3>Disclaimer</h3>"
            "<p>This software is intended to assist with business accounting. "
            "Users are responsible for verifying that all tax calculations and filings comply with the latest government regulations.</p>"
            "<p style='margin-top: 16px; font-size: 11px;'>"
            "© 2026 LedgerPro Desktop. All rights reserved. Designed &amp; developed by Angel (Mehul) Singh."
            "</p>"
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

        # menu_bar = self.menuBar()
        # help_menu = menu_bar.addMenu("Help")
        # about_action = QAction("About LedgerPro", self)
        # about_action.triggered.connect(self.show_about_dialog)
        # help_menu.addAction(about_action)
        
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
