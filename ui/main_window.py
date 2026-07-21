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
from ui.user_management import UserManagementPage
from ui.audit_logs import AuditLogsPage
from ui.styles import STYLESHEET
from ui.icons import get_icon
from auth.session import Session
from auth.auth_logic import log_audit_action


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
        app_name = QLabel("TSL SwiftBill ERP")
        app_name.setStyleSheet("font-size: 28px; font-weight: bold; color: #2563EB;")
        left_layout.addWidget(app_name)
        
        version_lbl = QLabel("Version 3.5.0 | Updated on: 2026-07-19")
        version_lbl.setStyleSheet("font-size: 14px; color: #64748B; margin-bottom: 10px;")
        left_layout.addWidget(version_lbl)
        
        # Tabs for Content (About English, About Hindi, FAQ)
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { background: #F1F5F9; padding: 8px 16px; font-weight: 600; color: #64748B; border-radius: 4px; margin-right: 4px; }
            QTabBar::tab:selected { background: #2563EB; color: white; }
        """)
        
        # --- Tab 1: About (English) ---
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
            "<h3>Overview (Version 3.5.0):</h3>"
            "<p><b>TSL SwiftBill ERP v3.5.0</b> is a comprehensive, professional-grade accounting, SME billing, and inventory management solution designed for small and medium businesses. "
            "Built with <b>Python</b>, <b>PySide6</b>, <b>SQLite3</b>, and <b>MySQL</b>, it delivers high performance, multi-user role access, thermal receipt printing, and offline-first reliability.</p>"
            
            "<h3>What's New in Version 3.5.0:</h3>"
            "<ul>"
            "<li><b>Built-in Printer Service & Selection Dialog:</b> Direct thermal POS receipt & A4 PDF printing with printer selection dialogs.</li>"
            "<li><b>Dynamic Custom Fields Support:</b> Configure custom fields in Settings for Invoices, Bills, and Payments.</li>"
            "<li><b>Due Date Terms Presets:</b> Select Net 7, 10, 15, 30, 45, 60 days or custom due dates automatically.</li>"
            "<li><b>Multi-Role Access Control (RBAC):</b> Support for <b>Owner</b>, <b>Manager</b>, and <b>Staff</b> roles.</li>"
            "<li><b>Dedicated User Management Screen:</b> Admin interface for managing users, updating roles, and resetting passwords.</li>"
            "<li><b>Audit Logging Engine:</b> Automatic tracking of system activities per user.</li>"
            "</ul>"

            "<h3>Core Features:</h3>"
            "<ul>"
            "<li><b>Dashboard:</b> Real-time analytics of Sales, Purchases, and Receivables with visual charts.</li>"
            "<li><b>Invoicing & Billing:</b> GST-compliant B2B/B2C invoices with automatic tax calculations, stock deduction, and PDF generation.</li>"
            "<li><b>Purchases & Bills:</b> Manage vendor bills with <b>FIFO-based stock valuation</b>.</li>"
            "<li><b>Inventory Management:</b> Real-time stock tracking using FIFO method.</li>"
            "<li><b>Payments & Credits:</b> Record partial payments, track balances, and manage Customer/Vendor Credits.</li>"
            "<li><b>Reports & Analytics:</b> Sales/Purchase registers, GST Summaries, Stock Valuation, and Aging reports.</li>"
            "</ul>"
            
            "<h3>Technical Stack:</h3>"
            "<p>Built using <b>Python 3.11+</b>, <b>PySide6</b> (Qt for Python), <b>SQLite3 / PyMySQL</b>, and <b>ReportLab</b>.</p>"
            
            "<p style='color: #64748B; font-size: 12px; margin-top: 20px;'>"
            "<i>© 2026 TSL SwiftBill ERP. All rights reserved. Powered by Br31Technologies.</i>"
            "</p>"
        )
        
        content_scroll.setWidget(content_text)
        about_layout.addWidget(content_scroll)
        tabs.addTab(about_tab, "🇬🇧 About (English)")

        # --- Tab 2: About (Hindi / हिंदी) ---
        about_hi_tab = QWidget()
        about_hi_layout = QVBoxLayout(about_hi_tab)
        about_hi_layout.setContentsMargins(0, 10, 0, 0)
        
        content_hi_scroll = QScrollArea()
        content_hi_scroll.setWidgetResizable(True)
        content_hi_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content_hi_text = QTextEdit()
        content_hi_text.setReadOnly(True)
        content_hi_text.setFrameShape(QFrame.Shape.NoFrame)
        content_hi_text.setStyleSheet("background-color: transparent; font-size: 14px; line-height: 1.6;")
        content_hi_text.setHtml(
            "<h3>विवरण (सॉफ्टवेयर वर्ज़न 3.5.0):</h3>"
            "<p><b>TSL SwiftBill ERP v3.5.0</b> छोटे और मध्यम व्यापारों के लिए एक संपूर्ण, पेशेवर अकाउंटिंग, SME बिलिंग और इन्वेंट्री मैनेजमेंट सॉफ्टवेयर है। "
            "यह <b>Python</b>, <b>PySide6</b>, <b>SQLite3</b> और <b>MySQL</b> से निर्मित है, जो उच्च प्रदर्शन, बहु-उपयोगकर्ता पहुंच (Multi-User Roles), थर्मल रसीद प्रिंटिंग और ऑफलाइन-फर्स्ट विश्वसनीयता प्रदान करता है।</p>"

            "<h3>वर्ज़न 3.5.0 की नई विशेषताएं:</h3>"
            "<ul>"
            "<li><b>इनबिल्ट प्रिंटर सर्विस एवं चयन (Printer Selection):</b> थर्मल POS (80mm/58mm) और A4 PDF के लिए डायरेक्ट प्रिंटर चयन डायलॉग।</li>"
            "<li><b>डायनामिक कस्टम फ़ील्ड्स (Custom Fields):</b> इनवॉइस, बिल और पेमेंट में अपनी पसंद के फ़ील्ड्स (PO नंबर, प्रोजेक्ट नाम आदि) जोड़ें।</li>"
            "<li><b>भुगतान समय सीमा (Due Date Presets):</b> इनवॉइस/बिल बनाते समय Net 7, 10, 15, 30, 45, 60 दिन या कस्टम तिथि चुनें।</li>"
            "<li><b>मल्टी-रोल एक्सेस कंट्रोल (RBAC):</b> Owner, Manager और Staff भूमिकाओं के लिए अलग-अलग अधिकार।</li>"
            "<li><b>यूजर मैनेजमेंट स्क्रीन:</b> नए यूजर्स बनाने, पासवर्ड बदलने और रोल अपडेट करने के लिए एडमिन इंटरफेस।</li>"
            "<li><b>ऑडिट लॉगिंग इंजन (Audit Logs):</b> हर यूजर द्वारा की गई गतिविधियों की स्वचालित रिकॉर्डिंग।</li>"
            "</ul>"

            "<h3>मुख्य सुविधाएं (Core Features):</h3>"
            "<ul>"
            "<li><b>डैशबोर्ड (Dashboard):</b> कुल बिक्री, खरीद, उधारी (Receivables) और कैश फ्लो का वास्तविक समय में ग्राफ और आंकड़े।</li>"
            "<li><b>इनवॉइसिंग एवं बिलिंग:</b> GST-अनुपालन इनवॉइस, टैक्स गणना, ऑटो स्टॉक कटौती और PDF जेनरेशन।</li>"
            "<li><b>खरीद एवं परचेस बिल:</b> सप्लायर बिल मैनेजमेंट और <b>FIFO आधारित स्टॉक मूल्यांकन</b>।</li>"
            "<li><b>इन्वेन्ट्री ट्रैकिंग:</b> स्टॉक का वास्तविक समय में प्रबंधन और लो-स्टॉक अलर्ट।</li>"
            "<li><b>पेमेंट्स एवं क्रेडिट्स:</b> आंशिक भुगतान दर्ज करें और उधारी/क्रेडिट का ट्रैक रखें।</li>"
            "<li><b>रिपोर्ट्स एवं एनालिटिक्स:</b> सेल्स/परचेस रजिस्टर, GST सारांश, स्टॉक मूल्यांकन और उधारी अवधि (Aging) रिपोर्ट।</li>"
            "</ul>"

            "<p style='color: #64748B; font-size: 12px; margin-top: 20px;'>"
            "<i>© 2026 TSL SwiftBill ERP. सर्वाधिकार सुरक्षित। संचालित: Br31Technologies.</i>"
            "</p>"
        )
        content_hi_scroll.setWidget(content_hi_text)
        about_hi_layout.addWidget(content_hi_scroll)
        tabs.addTab(about_hi_tab, "🇮🇳 ऐप जानकारी (हिंदी)")
        
        # --- Tab 3: FAQ & Help ---
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
        <h3>Frequently Asked Questions & User Guide / सामान्य प्रश्न (v3.5.0)</h3>
        
        <p><b>Q: How do Due Date presets (10 days, 15 days, 45 days) work?</b><br>
        A: When creating an Invoice or Bill, select a Payment Term preset (e.g. <b>Net 10 Days</b>, <b>Net 15 Days</b>, <b>Net 45 Days</b>). The system automatically calculates and fills the exact Due Date (Date + N days). You can also select <b>Custom Date</b> for manual dates.</p>

        <p><b>Q: How do Custom Fields work? / कस्टम फ़ील्ड्स कैसे काम करते हैं?</b><br>
        A: Go to <b>Settings > Custom Fields</b>, select module (Invoices, Bills, Payments), click <b>Add Field</b> and save. When creating a new Invoice or Bill, your custom field dynamically appears on the form and prints on PDFs.</p>

        <p><b>Q: How do I select or change default printers? / प्रिंटर कैसे चुनें?</b><br>
        A: When clicking <b>Print A4 PDF</b> or <b>POS Receipt</b>, a printer selection dialog appears with all available installed printers. You can also configure default printers in <b>Settings > Printer Setup</b>.</p>

        <p><b>Q: How do user roles work?</b><br>
        A: <br>
        - <b>Owner</b>: Full system access, User Management, Financial Reports, Settings, and Database Maintenance.<br>
        - <b>Manager</b>: Operational access (Invoices, Purchases, Payments, Stock, Reports), restricted from User Management.<br>
        - <b>Staff</b>: Daily entries (Invoices, Purchases, Payments, Stock, Customers, Vendors), restricted from Reports and Settings.</p>

        <p><b>Q: How do I create a new invoice?</b><br>
        A: Go to the <b>Invoices</b> tab and click <b>+ Create Invoice</b>. Select a customer, add items, set payment terms, and save. Stock is deducted automatically.</p>

        <p><b>Q: How is stock calculated?</b><br>
        A: Stock is tracked using the <b>FIFO (First-In-First-Out)</b> method to calculate COGS based on oldest available stock batches.</p>

        <p><b>Q: How do I backup or restore my data?</b><br>
        A: Go to <b>Settings > Database</b>. Click <b>Backup Database (Export)</b> to save a local backup file (SQLite or MySQL).</p>
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
        email_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("mailto:support@br31tech.in")))
        right_layout.addWidget(email_btn)
        
        web_btn = QPushButton("Visit Website")
        web_btn.setStyleSheet(btn_style)
        web_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.br31tech.in/products")))
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
        self.setWindowTitle("About TSL SwiftBill ERP")
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
        self.setWindowTitle("TSL SwiftBill ERP")
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

        app_title = QLabel("TSL SwiftBill ERP")
        app_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B;")
        logo_layout.addWidget(app_title)
        
        sidebar_layout.addWidget(logo_container)
        
        # Scrollable area for Navigation Buttons
        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("SidebarScroll")
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        nav_content = QWidget()
        nav_layout = QVBoxLayout(nav_content)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Dynamic Navigation & Pages based on User Role
        self.nav_buttons = []
        self.stack = QStackedWidget()
        
        pages_config = [
            ("Dashboard", DashboardPage),
            ("Customers", CustomersPage),
            ("Vendors", VendorsPage),
            ("Items", ItemsPage),
            ("Invoices", InvoicesPage),
            ("Purchases", BillsPage),
            ("Payments", PaymentsPage),
            ("Stock", StockPage),
            ("Reports", ReportsPage),
            ("Audit Logs", AuditLogsPage),
            ("Users", UserManagementPage),
            ("Settings", SettingsPage),
            ("About", AboutPage),
        ]
        
        session = Session.get_instance()
        stack_index = 0
        for name, widget_cls in pages_config:
            if session.can_access_module(name):
                page_instance = widget_cls()
                self.stack.addWidget(page_instance)
                self.add_nav_button(name, stack_index, nav_layout)
                stack_index += 1
                
        nav_layout.addStretch()
        nav_scroll.setWidget(nav_content)
        sidebar_layout.addWidget(nav_scroll)
        
        # User Info & Role Badge (Fixed at bottom)
        user = session.get_user()
        user_name = user.get('name', 'User') if user else "User"
        user_role = session.get_role().upper()
        
        role_color = "#7C3AED" if user_role == "OWNER" else ("#2563EB" if user_role == "MANAGER" else "#059669")
        
        user_lbl = QLabel(f"Logged in as:<br><b>{user_name}</b><br><span style='color: {role_color}; font-weight: bold;'>[{user_role}]</span>")
        user_lbl.setTextFormat(Qt.TextFormat.RichText)
        user_lbl.setStyleSheet("color: #64748B; padding-left: 20px; font-size: 12px; line-height: 1.4; margin-top: 5px;")
        sidebar_layout.addWidget(user_lbl)
        
        logout_btn = QPushButton(" Logout")
        logout_btn.setIcon(get_icon("logout", "#EF4444", 18))
        logout_btn.setIconSize(QSize(18, 18))
        logout_btn.setStyleSheet("background-color: transparent; color: #EF4444; border: none; text-align: left; padding: 10px 20px; font-weight: bold;")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(logout_btn)
        
        main_layout.addWidget(self.sidebar)
        
        # Content Area
        content_container = QWidget()
        content_container.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.stack)
        
        main_layout.addWidget(content_container)

        # Show full-screen maximized window
        self.showMaximized()

    def handle_logout(self):
        try:
            from auth.session import Session
            user = Session.get_instance().get_user()
            u_name = user.get('name', 'User') if user else 'User'
            log_audit_action("LOGOUT", "Auth", "", f"User {u_name} logged out")
        except Exception as e:
            print(f"Logout audit log error: {e}")
        self.close()

    def add_nav_button(self, text, index, layout):
        btn = QPushButton(f" {text}")
        
        # Set clean vector icon
        icon_color = "#2563EB"
        btn.setIcon(get_icon(text, icon_color, 20))
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
