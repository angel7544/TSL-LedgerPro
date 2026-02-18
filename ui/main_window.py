from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

from ui.dashboard import DashboardPage
from ui.master_data import CustomersPage, VendorsPage, ItemsPage
from ui.invoices import InvoicesPage
from ui.bills import BillsPage
from ui.stock import StockPage
from ui.reports import ReportsPage
from ui.settings import SettingsPage
from ui.styles import STYLESHEET
from auth.session import Session

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LedgerPro Desktop")
        self.resize(1200, 800)
        self.setStyleSheet(STYLESHEET)
        
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
