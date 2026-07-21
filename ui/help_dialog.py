from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QWidget, QScrollArea, QFrame, QGroupBox
)
from PySide6.QtCore import Qt
from ui.icons import get_icon

class HelpInfoDialog(QDialog):
    """
    Bilingual (English & Hindi) Help & Explanation Modal Dialog for TSL LedgerPro UI screens.
    """
    def __init__(self, screen_name="dashboard", parent=None):
        super().__init__(parent)
        self.screen_name = screen_name.lower()
        
        if self.screen_name == "dashboard":
            self.setWindowTitle("Dashboard Help & Guide / डैशबोर्ड सहायता")
        elif self.screen_name == "settings":
            self.setWindowTitle("Settings & Custom Fields Guide / सेटिंग्स एवं कस्टम फ़ील्ड्स सहायता")
        else:
            self.setWindowTitle("Reports Guide & Explanation / रिपोर्ट सहायता और गाइड")

        self.resize(720, 580)
        self.setMinimumSize(600, 480)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top Banner / Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 12, 15, 12)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon("info", "#2563EB", 32).pixmap(32, 32))

        text_layout = QVBoxLayout()
        if self.screen_name == "dashboard":
            title_text = "Dashboard Guide / डैशबोर्ड उपयोग गाइड"
            sub_text = "Learn how to understand your business overview, metrics & cash flow."
        elif self.screen_name == "settings":
            title_text = "Settings & Custom Fields Guide / सेटिंग्स गाइड"
            sub_text = "Learn how Company Profile, Custom Fields, Printer setup & Security work."
        else:
            title_text = "Reports Guide / रिपोर्ट्स उपयोग गाइड"
            sub_text = "Understand all financial reports, GST summaries, and stock valuation."

        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E40AF;")
        sub_lbl = QLabel(sub_text)
        sub_lbl.setStyleSheet("font-size: 12px; color: #3B82F6;")

        text_layout.addWidget(title_lbl)
        text_layout.addWidget(sub_lbl)

        header_layout.addWidget(icon_lbl)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        main_layout.addWidget(header_frame)

        # Bilingual Tabs (English / हिंदी)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                background: #F1F5F9;
                color: #475569;
                padding: 8px 16px;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2563EB;
                color: white;
            }
        """)

        # English Tab
        en_tab = QWidget()
        en_layout = QVBoxLayout(en_tab)
        en_layout.setContentsMargins(0, 0, 0, 0)
        en_scroll = QScrollArea()
        en_scroll.setWidgetResizable(True)
        en_scroll.setFrameShape(QFrame.Shape.NoFrame)
        en_content = QWidget()
        en_content_layout = QVBoxLayout(en_content)
        en_content_layout.setContentsMargins(15, 15, 15, 15)
        en_content_layout.setSpacing(12)

        # Hindi Tab
        hi_tab = QWidget()
        hi_layout = QVBoxLayout(hi_tab)
        hi_layout.setContentsMargins(0, 0, 0, 0)
        hi_scroll = QScrollArea()
        hi_scroll.setWidgetResizable(True)
        hi_scroll.setFrameShape(QFrame.Shape.NoFrame)
        hi_content = QWidget()
        hi_content_layout = QVBoxLayout(hi_content)
        hi_content_layout.setContentsMargins(15, 15, 15, 15)
        hi_content_layout.setSpacing(12)

        if self.screen_name == "dashboard":
            self.build_dashboard_english(en_content_layout)
            self.build_dashboard_hindi(hi_content_layout)
        elif self.screen_name == "settings":
            self.build_settings_english(en_content_layout)
            self.build_settings_hindi(hi_content_layout)
        else:
            self.build_reports_english(en_content_layout)
            self.build_reports_hindi(hi_content_layout)

        en_scroll.setWidget(en_content)
        en_layout.addWidget(en_scroll)

        hi_scroll.setWidget(hi_content)
        hi_layout.addWidget(hi_scroll)

        self.tabs.addTab(en_tab, "🇬🇧 English Guide")
        self.tabs.addTab(hi_tab, "🇮🇳 हिंदी सहायता (Hindi)")

        main_layout.addWidget(self.tabs)

        # Close Button
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close / बंद करें")
        close_btn.setFixedWidth(140)
        close_btn.setStyleSheet("background-color: #0F172A; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        close_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)

        main_layout.addLayout(btn_layout)

    def create_card(self, title, text_content):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #0F172A;
                font-size: 14px;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #F8FAFC;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout(group)
        lbl = QLabel(text_content)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size: 13px; color: #334155; line-height: 1.4; font-weight: normal;")
        layout.addWidget(lbl)
        return group

    # --- Dashboard English Content ---
    def build_dashboard_english(self, layout):
        layout.addWidget(self.create_card(
            "📌 What is the Dashboard?",
            "The Dashboard provides a real-time command center for your business. It highlights critical financial health metrics, sales growth, pending collections, supplier payments, and low stock warnings at a single glance."
        ))
        layout.addWidget(self.create_card(
            "💳 Total Receivables & Total Payables",
            "• Total Receivables: The total amount of money owed to you by customers for pending or unpaid sales invoices.\n"
            "• Total Payables: The total amount of money you owe to suppliers/vendors for unpaid purchase bills."
        ))
        layout.addWidget(self.create_card(
            "📊 Monthly Sales, Purchases & Net GST",
            "• Total Sales (This Month): Sum of all sales generated in the current calendar month.\n"
            "• Total Purchases (This Month): Total cost of stock/inventory purchased this month.\n"
            "• GST Payable (This Month): Estimated net GST liability (Output GST collected from sales minus Input GST paid on purchases)."
        ))
        layout.addWidget(self.create_card(
            "📦 Inventory & Low Stock Alerts",
            "• Total Items: Count of distinct products registered in your catalog.\n"
            "• Total Stock Value: Total monetary value of your current physical inventory.\n"
            "• Low Stock Items: Highlights items that have dropped below minimum reorder quantity so you never run out of stock."
        ))
        layout.addWidget(self.create_card(
            "📈 Revenue Charts & Due Date Tracking",
            "• Cash Flow Chart: Compares monthly revenue against purchase expenses.\n"
            "• Upcoming Due Dates: Lists invoices and bills reaching payment due dates within the next 7 days."
        ))

    # --- Dashboard Hindi Content ---
    def build_dashboard_hindi(self, layout):
        layout.addWidget(self.create_card(
            "📌 डैशबोर्ड क्या है और इसका क्या उपयोग है?",
            "डैशबोर्ड आपके व्यवसाय का मुख्य नियंत्रण केंद्र (Command Center) है। यह एक ही नज़र में आपकी कुल बिक्री, खरीद खर्च, बकाया उधारी, देनदारी और कम स्टॉक की स्थिति का सटीक सारांश दिखाता है।"
        ))
        layout.addWidget(self.create_card(
            "💳 कुल प्राप्य (Receivables) और कुल देय (Payables)",
            "• कुल प्राप्य (Receivables - उधारी): वह कुल राशि जो ग्राहकों से अनपेड इनवॉइस के बदले आपको मिलनी बाकी है।\n"
            "• कुल देय (Payables - देनदारी): वह कुल राशि जो सप्लायर्स या विक्रेताओं को बकाया बिलों के लिए आपको चुकानी है।"
        ))
        layout.addWidget(self.create_card(
            "📊 चालू माह की बिक्री, खरीद और GST",
            "• कुल बिक्री (इस महीने): चालू कैलेंडर माह में हुई कुल सेल (कमाई)।\n"
            "• कुल खरीद (इस महीने): इस महीने स्टॉक खरीदने में किया गया कुल खर्च।\n"
            "• GST देय (GST Payable): बिक्री से एकत्र किया गया GST माइनस खरीद पर दिया गया इनपुट टैक्स क्रेडिट (ITC)।"
        ))
        layout.addWidget(self.create_card(
            "📦 इन्वेंट्री सारांश और लो-स्टॉक अलर्ट",
            "• कुल उत्पाद (Total Items): आपके कैटलॉग में पंजीकृत कुल अलग-अलग सामान।\n"
            "• कुल स्टॉक मूल्य (Stock Value): गोदाम/दुकान में रखे माल का कुल बाजार मूल्य।\n"
            "• लो-स्टॉक अलर्ट: वे उत्पाद जिनकी संख्या न्यूनतम सीमा से कम हो गई है, ताकि आप समय पर रीऑर्डर कर सकें।"
        ))
        layout.addWidget(self.create_card(
            "📈 कैश फ्लो चार्ट और देय तिथियां",
            "• कैश फ्लो चार्ट: आपकी मासिक आय और व्यय का तुलनात्मक ग्राफ दिखाता है।\n"
            "• आगामी देय तिथियां (Due Dates): अगले 7 दिनों में आने वाले बकाया भुगतान और इनवॉइस की सूची प्रदान करता है।"
        ))

    # --- Reports English Content ---
    def build_reports_english(self, layout):
        layout.addWidget(self.create_card(
            "📑 What is the Reports Module Used For?",
            "The Reports screen aggregates detailed financial data, tax liabilities, customer ledgers, and stock valuation. Use this screen to audit performance, file GST returns, track unpaid debts, and print/export PDF reports."
        ))
        layout.addWidget(self.create_card(
            "1. Sales Report (बिक्री रिपोर्ट)",
            "Lists all sales invoices created within the selected date range. Shows customer name, invoice date, payment status, tax amount, and total revenue."
        ))
        layout.addWidget(self.create_card(
            "2. Purchase Report (खरीद रिपोर्ट)",
            "Displays all vendor bills and inventory purchases. Helps track supplier expenses, bill dates, and total purchase costs."
        ))
        layout.addWidget(self.create_card(
            "3. GST Summary (जीएसटी सारांश)",
            "Provides GST tax breakdown:\n"
            "• Total Output Tax: GST collected from customer sales.\n"
            "• Total Input Tax: GST paid on vendor purchases.\n"
            "• Net GST Payable: Output Tax minus Input Tax (Amount payable to tax authority)."
        ))
        layout.addWidget(self.create_card(
            "4. Outstanding Invoices (बकाया इनवॉइस)",
            "Displays unpaid customer invoices along with due dates and overdue amounts. Essential for daily cash collection follow-ups."
        ))
        layout.addWidget(self.create_card(
            "5. Stock Valuation (स्टॉक मूल्यांकन)",
            "Calculates total inventory asset value by item unit rates and remaining stock quantities."
        ))
        layout.addWidget(self.create_card(
            "6. Price List (मूल्य सूची)",
            "Shows default selling rates and custom tier rates (Special Price 1, 2, 3) for all registered items."
        ))
        layout.addWidget(self.create_card(
            "7. AR Aging & 8. AP Aging Reports (उधारी एवं देनदारी अवधि)",
            "• AR Aging (Accounts Receivable): Categorizes customer debt into age buckets (1-30 days, 31-60 days, 60+ days overdue) to target long-pending payments.\n"
            "• AP Aging (Accounts Payable): Categorizes supplier bills by aging to schedule timely payment payouts."
        ))

    # --- Reports Hindi Content ---
    def build_reports_hindi(self, layout):
        layout.addWidget(self.create_card(
            "📑 रिपोर्ट्स सेक्शन का क्या उपयोग है?",
            "रिपोर्ट्स मॉड्यूल आपके व्यवसाय के सभी वित्तीय आंकड़ों, टैक्स विवरण, ग्राहक उधारी और स्टॉक वैल्यू का विस्तृत ब्योरा देता है। इसका उपयोग जीएसटी रिटर्न भरने, ऑडिट करने, बकाया वसूलने और रिपोर्ट प्रिंट/PDF करने के लिए किया जाता है।"
        ))
        layout.addWidget(self.create_card(
            "1. बिक्री रिपोर्ट (Sales Report)",
            "चयनित समय अवधि में जारी किए गए सभी बिक्री इनवॉइस की सूची दिखाता है। इसमें ग्राहक का नाम, तिथि, भुगतान स्थिति और कुल राशि शामिल है।"
        ))
        layout.addWidget(self.create_card(
            "2. खरीद रिपोर्ट (Purchase Report)",
            "विक्रेता (सप्लायर) से खरीदे गए सामान और बिलों की सूची प्रस्तुत करता है। यह कुल खरीद खर्चों को ट्रैक करने में मदद करता है।"
        ))
        layout.addWidget(self.create_card(
            "3. GST सारांश (GST Summary)",
            "जीएसटी टैक्स की पूरी गणना प्रस्तुत करता है:\n"
            "• आउटपुट टैक्स (Output Tax): बिक्री पर ग्राहकों से एकत्र किया गया टैक्स।\n"
            "• इनपुट टैक्स (Input Tax Credit): माल की खरीद पर दिया गया टैक्स।\n"
            "• कुल देय जीएसटी (Net GST Payable): आउटपुट टैक्स माइनस इनपुट टैक्स।"
        ))
        layout.addWidget(self.create_card(
            "4. बकाया इनवॉइस (Outstanding Invoices)",
            "उन सभी ग्राहक इनवॉइसों की सूची दिखाता है जिनका भुगतान अभी तक प्राप्त नहीं हुआ है, ताकि आप उधारी की वसूली कर सकें।"
        ))
        layout.addWidget(self.create_card(
            "5. स्टॉक मूल्यांकन (Stock Valuation)",
            "गोदाम में मौजूद प्रत्येक वस्तु की मात्रा और खरीद दर के आधार पर इन्वेंट्री का कुल परिसंपत्ति (Asset) मूल्य बताता है।"
        ))
        layout.addWidget(self.create_card(
            "6. मूल्य सूची (Price List)",
            "विभिन्न ग्राहक श्रेणियों के लिए वस्तुओं की डिफ़ॉल्ट बिक्री दरों और विशेष दरों (Special Price 1, 2, 3) का कैटलॉग प्रस्तुत करता है।"
        ))
        layout.addWidget(self.create_card(
            "7. AR Aging एवं 8. AP Aging रिपोर्ट (उधारी एवं देनदारी अवधि)",
            "• AR Aging (ग्राहक उधारी अवधि): ग्राहकों की बकाया राशि को दिनों के हिसाब से बांटता है (1-30 दिन, 31-60 दिन, 60+ दिन) ताकि पुरानी उधारी पहले वसूली जा सके।\n"
            "• AP Aging (सप्लायर देनदारी अवधि): विक्रेताओं के बकाया बिलों को समयावधि के अनुसार वर्गीकृत करता है ताकि समय पर भुगतान किया जा सके।"
        ))

    # --- Settings English Content ---
    def build_settings_english(self, layout):
        layout.addWidget(self.create_card(
            "⚙️ What is Settings Used For?",
            "Settings allows you to configure your business identity, add custom data fields, set default printer services, manage security credentials, and export database backups."
        ))
        layout.addWidget(self.create_card(
            "✨ How Custom Fields Work & Does It Work?",
            "• YES, Custom Fields are 100% active and functional!\n"
            "• What it does: Custom Fields allow you to add extra user-defined fields (e.g. PO Reference, Project Name, Delivery Vehicle #, Serial Number) to Invoices, Bills, or Payments.\n"
            "• Step-by-Step Usage:\n"
            "  1. Go to Settings -> Custom Fields tab.\n"
            "  2. Select module (Invoices, Bills, or Payments).\n"
            "  3. Click 'Add Field', enter the Field Name & Type (Text, Date, Dropdown), and click 'Save Fields'.\n"
            "  4. Open 'Create Invoice', 'Create Bill', or 'Record Payment' – your new custom field will automatically appear on the creation form!\n"
            "  5. Any data entered is saved in the database, shown in transaction details, and printed on generated PDF documents."
        ))
        layout.addWidget(self.create_card(
            "🏢 Company Profile & Rate Types",
            "• Company Details: Edit company name, address, GSTIN, contact numbers, logo, and invoice/payment number prefixes.\n"
            "• Rate Types: Customize labels for Special Price tiers 1, 2, and 3 (e.g., Retailer, Wholesaler, VIP Customer)."
        ))
        layout.addWidget(self.create_card(
            "🖨️ Printer Setup & Default Printers",
            "Select default A4 Document printer and Thermal POS printer (80mm/58mm). Set default print action (Always Ask, Direct Print, System Dialog, or View PDF) and run test prints."
        ))
        layout.addWidget(self.create_card(
            "🔒 Security & Database Backups",
            "• Security: Change account passwords safely.\n"
            "• Database: Create instant local SQLite or MySQL backups for data safety."
        ))

    # --- Settings Hindi Content ---
    def build_settings_hindi(self, layout):
        layout.addWidget(self.create_card(
            "⚙️ सेटिंग्स का उपयोग किसलिए किया जाता है?",
            "सेटिंग्स का उपयोग कंपनी विवरण बदलने, कस्टम डेटा फ़ील्ड जोड़ने, प्रिंटर चुनने, सुरक्षा पासवर्ड बदलने और डेटाबेस का बैकअप लेने के लिए किया जाता है।"
        ))
        layout.addWidget(self.create_card(
            "✨ कस्टम फ़ील्ड्स कैसे काम करते हैं और क्या यह काम करता है?",
            "• हाँ! कस्टम फ़ील्ड्स 100% सक्रिय हैं और पूरी तरह से काम करते हैं!\n"
            "• इसका क्या काम है: यह आपको इनवॉइस, बिल और भुगतान में अपनी आवश्यकतानुसार अतिरिक्त फ़ील्ड्स (जैसे PO नंबर, प्रोजेक्ट नाम, गाड़ी नंबर, वारंटी कोड आदि) जोड़ने की अनुमति देता है।\n"
            "• इस्तेमाल करने का तरीका:\n"
            "  1. सेटिंग्स -> कस्टम फ़ील्ड्स (Custom Fields) टैब पर जाएं।\n"
            "  2. मॉड्यूल चुनें (इनवॉइस, बिल या पेमेंट)।\n"
            "  3. 'Add Field' पर क्लिक करें, फ़ील्ड का नाम दर्ज करें और 'Save Fields' बटन दबाएं।\n"
            "  4. अब जब भी आप 'नया इनवॉइस' या 'बिल' बनाएंगे, तो आपका बनाया गया फ़ील्ड स्वचालित रूप से फ़ॉर्म पर दिखाई देगा!\n"
            "  5. भरा गया डेटा डेटाबेस में सुरक्षित सेव होता है और प्रिंट किए गए PDF पर भी छपता है।"
        ))
        layout.addWidget(self.create_card(
            "🏢 कंपनी प्रोफ़ाइल और रेट टाइप्स",
            "• कंपनी विवरण: कंपनी का नाम, पता, GSTIN, लोगो, फोन नंबर और इनवॉइस प्रिफ़िक्स बदलें।\n"
            "• रेट टाइप्स: विशेष ग्राहक दरों (Special Price 1, 2, 3) का नाम बदलें (उदा. खुदरा विक्रेता, थोक विक्रेता)।"
        ))
        layout.addWidget(self.create_card(
            "🖨️ प्रिंटर सेटअप और डिफ़ॉल्ट प्रिंटर",
            "A4 डॉक्यूमेंट और POS थर्मल प्रिंटर (80mm/58mm) का चयन करें। डिफ़ॉल्ट प्रिंट व्यवहार चुनें और टेस्ट प्रिंट निकालें।"
        ))
        layout.addWidget(self.create_card(
            "🔒 सुरक्षा और डेटाबेस बैकअप",
            "• सुरक्षा: अपना पासवर्ड सुरक्षित रूप से बदलें।\n"
            "• डेटाबेस: किसी भी समय अपनी डेटाबेस फ़ाइल का बैकअप लें।"
        ))

