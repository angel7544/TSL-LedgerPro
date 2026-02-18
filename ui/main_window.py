from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame, QDialog, QTextEdit, QStyle, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QAction, QPixmap, QDesktopServices
import os

from ui.dashboard import DashboardPage
from ui.master_data import CustomersPage, VendorsPage, ItemsPage
from ui.invoices import InvoicesPage
from ui.bills import BillsPage
from ui.stock import StockPage
from ui.reports import ReportsPage
from ui.payments import PaymentsPage
from ui.settings import SettingsPage
from ui.styles import STYLESHEET
from auth.session import Session


class AboutWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # --- Left Column: Description & Details ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # App Header
        app_name = QLabel("LedgerPro Desktop")
        app_name.setStyleSheet("font-size: 28px; font-weight: bold; color: #2563EB;")
        left_layout.addWidget(app_name)
        
        version_lbl = QLabel("Version 2.5.6 | Updated on: 2026-02-18")
        version_lbl.setStyleSheet("font-size: 14px; color: #64748B; margin-bottom: 10px;")
        left_layout.addWidget(version_lbl)
        
        # Tabs for Content (About, FAQ)
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: transparent; padding: 8px 16px; font-weight: 600; color: #64748B; }
            QTabBar::tab:selected { color: #2563EB; border-bottom: 2px solid #2563EB; }
        """)
        
        # --- Tab 1: About ---
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_layout.setContentsMargins(0, 10, 0, 0)
        
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setFrameShape(QFrame.Shape.NoFrame)
        content_text.setStyleSheet("background-color: transparent; font-size: 14px; line-height: 1.6;")
        content_text.setHtml(
            "<h3>Overview:</h3>"
            "<p><b>LedgerPro Desktop</b> is a comprehensive, professional-grade accounting and inventory management solution designed for small and medium businesses. "
            "Built with <b>Python</b> and <b>PySide6</b>, it offers a robust, secure, and offline-first desktop experience for managing finances, GST billing, stock, and reports.</p>"
            
            "<h3>Key Features:</h3>"
            "<ul>"
            "<li><b>Dashboard:</b> Real-time overview of Sales, Purchases, and Receivables with visual charts.</li>"
            "<li><b>Invoicing & Billing:</b> Create professional GST-compliant B2B/B2C invoices with automatic tax calculations. Manage customer credits and advance payments.</li>"
            "<li><b>Inventory Management:</b> FIFO-based stock valuation, real-time tracking with low-stock alerts, and HSN/SAC support.</li>"
            "<li><b>Financial Management:</b> Track Accounts Receivable (AR) & Payable (AP), record payments with partial allocations, and monitor expenses.</li>"
            "<li><b>Reports & Analytics:</b> Generate detailed Sales/Purchase registers, GST Summaries, Stock Valuation, and Aging reports.</li>"
            "<li><b>Security & Data:</b> Secure local SQLite database with user authentication and backup/restore tools.</li>"
            "</ul>"
            
            "<h3>Technical Stack:</h3>"
            "<p>Built using <b>Python 3.11+</b>, <b>PySide6</b> (Qt for Python), <b>SQLite3</b>, and <b>ReportLab</b> for PDF generation.</p>"
            
            "<p style='color: #64748B; font-size: 12px; margin-top: 20px;'>"
            "<i>Disclaimer: This software is intended to assist with business accounting. "
            "Users are responsible for verifying that all tax calculations and filings comply with the latest government regulations.</i></p>"
            
            "<p style='color: #64748B; font-size: 12px;'>"
            "© 2026 LedgerPro Desktop. All rights reserved."
            "</p>"
        )
        
        content_scroll.setWidget(content_text)
        about_layout.addWidget(content_scroll)
        tabs.addTab(about_tab, "About")
        
        # --- Tab 2: FAQ & Help ---
        faq_tab = QWidget()
        faq_layout = QVBoxLayout(faq_tab)
        faq_layout.setContentsMargins(0, 10, 0, 0)
        
        faq_scroll = QScrollArea()
        faq_scroll.setWidgetResizable(True)
        faq_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        faq_text = QTextEdit()
        faq_text.setReadOnly(True)
        faq_text.setFrameShape(QFrame.Shape.NoFrame)
        faq_text.setStyleSheet("background-color: transparent; font-size: 14px; line-height: 1.6;")
        
        faq_content = """
        <h3>Frequently Asked Questions</h3>
        
        <p><b>Q: How do I create a new invoice?</b><br>
        A: Go to the <b>Invoices</b> tab and click the <b>+ Create Invoice</b> button. Select a customer, add items, and save.</p>
        
        <p><b>Q: How is stock calculated?</b><br>
        A: Stock is tracked using the <b>FIFO (First-In-First-Out)</b> method. When you sell an item, the cost is calculated based on the oldest available stock batch.</p>
        
        <p><b>Q: Can I record partial payments?</b><br>
        A: Yes! In the <b>Payments</b> tab, click <b>Record Payment</b>. Enter the amount received, and the system will automatically allocate it to the oldest unpaid invoices. You can also manually adjust the allocation.</p>
        
        <p><b>Q: How do I handle customer credits/advances?</b><br>
        A: If a customer pays more than the invoice amount, the excess is stored as <b>Credits</b>. You can view available credits in the <b>Customers</b> list. These credits can be applied to future invoices.</p>
        
        <p><b>Q: How do I export reports?</b><br>
        A: Navigate to the <b>Reports</b> tab. Select the report type (e.g., Sales Register, GST Summary), choose a date range, and click <b>Generate PDF</b> or <b>Export CSV</b>.</p>
        
        <p><b>Q: Where is my data stored?</b><br>
        A: All data is stored securely in a local <b>SQLite database</b> file on your computer. We recommend regularly backing up this file using the <b>Settings</b> > <b>Backup</b> option.</p>
        
        <p><b>Q: How do I update my company logo?</b><br>
        A: Go to <b>Settings</b> and look for the <b>Company Logo</b> section. Upload a new image to reflect it on all invoices and reports.</p>
        
        <p><b>Q: Can I use this software offline?</b><br>
        A: Absolutely! LedgerPro Desktop is designed to work fully offline without an internet connection.</p>
        """
        
        faq_text.setHtml(faq_content)
        faq_scroll.setWidget(faq_text)
        faq_layout.addWidget(faq_scroll)
        tabs.addTab(faq_tab, "FAQ & Help")
        
        left_layout.addWidget(tabs)
        
        main_layout.addWidget(left_widget, stretch=6)
        
        # --- Right Column: Credits & Logos ---
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Logos
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        logo_container = QHBoxLayout()
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # # TSL Icon
        # tsl_path = os.path.join(base_dir, "assets", "tsl_icon.png")
        # if os.path.exists(tsl_path):
        #     tsl_lbl = QLabel()
        #     pix = QPixmap(tsl_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        #     tsl_lbl.setPixmap(pix)
        #     logo_container.addWidget(tsl_lbl)
            
        # logo_container.addSpacing(20)
        
        # BR31 Logo
        br31_path = os.path.join(base_dir, "assets", "br31logo.png")
        if os.path.exists(br31_path):
            br31_lbl = QLabel()
            pix = QPixmap(br31_path).scaled(256, 175, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            br31_lbl.setPixmap(pix)
            logo_container.addWidget(br31_lbl)
            
        right_layout.addLayout(logo_container)
        right_layout.addSpacing(40)
        
        # Credits
        def add_credit_section(title, name, color="#1E293B", large=False):
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-size: 12px; color: #64748B; font-weight: 600;")
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(lbl_title)
            
            lbl_name = QLabel(name)
            font_size = "16px" if large else "14px"
            font_weight = "bold" if large else "500"
            lbl_name.setStyleSheet(f"font-size: {font_size}; color: {color}; font-weight: {font_weight}; margin-bottom: 15px;")
            lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(lbl_name)

        add_credit_section("Developed for", "The Space Labs")
        add_credit_section("Updated and extensively upgraded by", "Angel (Mehul) Singh", color="#2563EB", large=True)
        add_credit_section("Developed at", "Br31Technologies\n(Lite and Robust version)")
        
        right_layout.addStretch()
        
        # Contact Buttons
        btn_style = """
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
        """
        
        email_btn = QPushButton("Email Us")
        email_btn.setStyleSheet(btn_style)
        email_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("mailto:support@br31tech.live")))
        right_layout.addWidget(email_btn)
        
        web_btn = QPushButton("Visit Website")
        web_btn.setStyleSheet(btn_style)
        web_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.br31tech.live/products")))
        right_layout.addWidget(web_btn)
        
        github_btn = QPushButton("GitHub")
        github_btn.setStyleSheet(btn_style)
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.github.com/angel7544")))
        right_layout.addWidget(github_btn)

        linkedin_btn = QPushButton("LinkedIn")
        linkedin_btn.setStyleSheet(btn_style)
        linkedin_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.linkedin.com/in/angel3002")))
        right_layout.addWidget(linkedin_btn)
        
        main_layout.addWidget(right_widget, stretch=2)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About LedgerPro Desktop")
        self.setMinimumSize(800, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        about_widget = AboutWidget()
        layout.addWidget(about_widget)
        
        # Close Button Footer
        footer = QFrame()
        footer.setStyleSheet("background-color: #F8FAFC; border-top: 1px solid #E2E8F0;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 6px 16px;")
        close_btn.clicked.connect(self.accept)
        footer_layout.addWidget(close_btn)
        
        layout.addWidget(footer)


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Just reuse the widget
        about_widget = AboutWidget()
        layout.addWidget(about_widget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LedgerPro Desktop")
        self.resize(1200, 800)
        
        # Set window flags to support minimize and maximize
        # While QMainWindow usually supports this, ensuring it for custom styles or behaviors
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        
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
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 0, 20, 20)
        logo_layout.setSpacing(10)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Logo Image
        icon_path = os.path.join(base_dir, "tsl_icon.png")
        if not os.path.exists(icon_path):
             icon_path = os.path.join(base_dir, "assets", "tsl_icon.png")
             
        if os.path.exists(icon_path):
            logo_lbl = QLabel()
            pix = QPixmap(icon_path).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pix)
            logo_layout.addWidget(logo_lbl)

        app_title = QLabel("LedgerPro")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E293B;")
        logo_layout.addWidget(app_title)
        
        sidebar_layout.addWidget(logo_container)
        
        # Navigation Buttons
        self.nav_buttons = []
        self.add_nav_button("Dashboard", 0, sidebar_layout)
        self.add_nav_button("Customers", 1, sidebar_layout)
        self.add_nav_button("Vendors", 2, sidebar_layout)
        self.add_nav_button("Items", 3, sidebar_layout)
        self.add_nav_button("Invoices", 4, sidebar_layout)
        self.add_nav_button("Purchases", 5, sidebar_layout)
        self.add_nav_button("Payments", 6, sidebar_layout)
        self.add_nav_button("Stock", 7, sidebar_layout)
        self.add_nav_button("Reports", 8, sidebar_layout)
        self.add_nav_button("Settings", 9, sidebar_layout)
        self.add_nav_button("About", 10, sidebar_layout)
        
        sidebar_layout.addStretch()
        
        # User Info
        user = Session.get_instance().get_user()
        user_name = user['name'] if user else "User"
        user_lbl = QLabel(f"Logged in as:\n{user_name}")
        user_lbl.setStyleSheet("color: #64748B; padding-left: 20px; font-size: 12px;")
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
        self.stack.addWidget(PaymentsPage())
        self.stack.addWidget(StockPage())
        self.stack.addWidget(ReportsPage())
        self.stack.addWidget(SettingsPage())
        self.stack.addWidget(AboutPage())
        
        content_layout.addWidget(self.stack)
        
        main_layout.addWidget(content_container)

    def add_nav_button(self, text, index, layout):
        btn = QPushButton(text)
        
        # Add Icon
        icon_map = {
            "Dashboard": QStyle.StandardPixmap.SP_ComputerIcon,
            "Customers": QStyle.StandardPixmap.SP_DirHomeIcon,
            "Vendors": QStyle.StandardPixmap.SP_DirIcon,
            "Items": QStyle.StandardPixmap.SP_FileIcon,
            "Invoices": QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "Purchases": QStyle.StandardPixmap.SP_FileDialogListView,
            "Payments": QStyle.StandardPixmap.SP_DialogApplyButton,
            "Stock": QStyle.StandardPixmap.SP_DriveHDIcon,
            "Reports": QStyle.StandardPixmap.SP_DialogHelpButton,
            "Settings": QStyle.StandardPixmap.SP_BrowserReload,
            "About": QStyle.StandardPixmap.SP_MessageBoxInformation
        }
        
        if text in icon_map:
            btn.setIcon(self.style().standardIcon(icon_map[text]))
            btn.setIconSize(QSize(20, 20))

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

        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, "refresh_data"):
            current_widget.refresh_data()
        
        # Update button styles
        for b in self.nav_buttons:
            b.setChecked(False)
        btn.setChecked(True)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()
