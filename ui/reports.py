from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QTabWidget, QDateEdit,
    QFormLayout, QLineEdit, QMessageBox
)
from PySide6.QtCore import QDate, QUrl
from PySide6.QtGui import QDesktopServices
from modules.reports_logic import (
    get_sales_report, get_purchase_report, get_gst_report, 
    get_outstanding_invoices, get_stock_valuation,
    get_ar_aging_report, get_ap_aging_report
)
from database.db import execute_read_query
from pdf.generator import generate_price_list_pdf, generate_generic_report_pdf
import os

class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        layout.addLayout(header)
        
        # Date Range
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        
        print_btn = QPushButton("Print Report")
        print_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 6px 12px; border-radius: 4px;")
        print_btn.clicked.connect(self.print_current_report)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search current report...")
        self.search_bar.setFixedWidth(200)
        self.search_bar.textChanged.connect(self.filter_current_tab)
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date)
        date_layout.addWidget(refresh_btn)
        date_layout.addWidget(print_btn)
        date_layout.addStretch()
        date_layout.addWidget(self.search_bar)
        
        layout.addLayout(date_layout)
        
        # Initialize data containers
        self.sales_data = []
        self.purchase_data = []
        self.outstanding_data = []
        self.stock_data_list = []
        self.price_list_data = []
        self.ar_aging_data = {}
        self.ap_aging_data = {}

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.filter_current_tab)
        self.tabs.addTab(self.create_sales_tab(), "Sales")
        self.tabs.addTab(self.create_purchase_tab(), "Purchases")
        self.tabs.addTab(self.create_gst_tab(), "GST Summary")
        self.tabs.addTab(self.create_outstanding_tab(), "Outstanding")
        self.tabs.addTab(self.create_stock_tab(), "Stock Valuation")
        self.tabs.addTab(self.create_price_list_tab(), "Price List")
        self.tabs.addTab(self.create_ar_aging_tab(), "AR Aging")
        self.tabs.addTab(self.create_ap_aging_tab(), "AP Aging")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)


    def create_sales_tab(self):
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["Inv #", "Customer", "Date", "Total", "Status"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.sales_table

    def create_purchase_tab(self):
        self.purchase_table = QTableWidget()
        self.purchase_table.setColumnCount(5)
        self.purchase_table.setHorizontalHeaderLabels(["Bill #", "Vendor", "Date", "Total", "Status"])
        self.purchase_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.purchase_table

    def create_gst_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.output_tax_lbl = QLabel("₹0.00")
        self.input_tax_lbl = QLabel("₹0.00")
        self.net_gst_lbl = QLabel("₹0.00")
        
        layout.addRow("Total Output Tax (Sales):", self.output_tax_lbl)
        layout.addRow("Total Input Tax (Purchases):", self.input_tax_lbl)
        layout.addRow("Net GST Payable:", self.net_gst_lbl)
        
        widget.setLayout(layout)
        return widget

    def create_outstanding_tab(self):
        self.outstanding_table = QTableWidget()
        self.outstanding_table.setColumnCount(5)
        self.outstanding_table.setHorizontalHeaderLabels(["Inv #", "Customer", "Date", "Due Date", "Amount"])
        self.outstanding_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.outstanding_table

    def create_stock_tab(self):
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels(["Item Name", "SKU", "Stock Qty", "Purchase Price", "Total Value"])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.stock_table

    def create_price_list_tab(self):
        self.price_table = QTableWidget()
        self.price_table.setColumnCount(3)
        self.price_table.setHorizontalHeaderLabels(["Item Name", "SKU", "Selling Price"])
        self.price_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.price_table

    def create_ar_aging_tab(self):
        self.ar_aging_table = QTableWidget()
        self.ar_aging_table.setColumnCount(6)
        self.ar_aging_table.setHorizontalHeaderLabels(["Inv #", "Customer", "Due Date", "Bucket", "Days Overdue", "Amount"])
        self.ar_aging_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.ar_aging_table
        
    def create_ap_aging_tab(self):
        self.ap_aging_table = QTableWidget()
        self.ap_aging_table.setColumnCount(6)
        self.ap_aging_table.setHorizontalHeaderLabels(["Bill #", "Vendor", "Due Date", "Bucket", "Days Overdue", "Amount"])
        self.ap_aging_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return self.ap_aging_table

    def refresh_all(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        # Sales
        self.sales_data = get_sales_report(start, end)
        
        # Purchases
        self.purchase_data = get_purchase_report(start, end)
        
        # GST
        gst = get_gst_report(start, end)
        self.output_tax_lbl.setText(f"₹{gst['output_tax']:.2f}")
        self.input_tax_lbl.setText(f"₹{gst['input_tax']:.2f}")
        self.net_gst_lbl.setText(f"₹{gst['net_gst_payable']:.2f}")
        
        # Outstanding
        self.outstanding_data = get_outstanding_invoices()
        
        # Stock Valuation
        self.stock_data_list = get_stock_valuation()
        
        # Price List
        self.price_list_data = execute_read_query("SELECT name, sku, selling_price FROM items ORDER BY name")
        
        # Aging Reports
        self.ar_aging_data = get_ar_aging_report()
        self.ap_aging_data = get_ap_aging_report()
        
        self.filter_current_tab()

    def filter_current_tab(self):
        tab_index = self.tabs.currentIndex()
        search_text = self.search_bar.text().lower()
        
        def matches(row, keys):
            if not search_text: return True
            for k in keys:
                if search_text in str(row.get(k, "") or "").lower():
                    return True
            return False

        if tab_index == 0: # Sales
            filtered = [r for r in self.sales_data if matches(r, ['invoice_number', 'customer_name', 'status'])]
            self.sales_table.setRowCount(len(filtered))
            for r, row in enumerate(filtered):
                self.sales_table.setItem(r, 0, QTableWidgetItem(row['invoice_number']))
                self.sales_table.setItem(r, 1, QTableWidgetItem(row['customer_name']))
                self.sales_table.setItem(r, 2, QTableWidgetItem(str(row['date'])))
                self.sales_table.setItem(r, 3, QTableWidgetItem(f"₹{row['grand_total']:.2f}"))
                self.sales_table.setItem(r, 4, QTableWidgetItem(row['status']))

        elif tab_index == 1: # Purchases
            filtered = [r for r in self.purchase_data if matches(r, ['bill_number', 'vendor_name', 'status'])]
            self.purchase_table.setRowCount(len(filtered))
            for r, row in enumerate(filtered):
                self.purchase_table.setItem(r, 0, QTableWidgetItem(row['bill_number']))
                self.purchase_table.setItem(r, 1, QTableWidgetItem(row['vendor_name']))
                self.purchase_table.setItem(r, 2, QTableWidgetItem(str(row['date'])))
                self.purchase_table.setItem(r, 3, QTableWidgetItem(f"₹{row['grand_total']:.2f}"))
                self.purchase_table.setItem(r, 4, QTableWidgetItem(row['status']))
                
        elif tab_index == 3: # Outstanding
            filtered = [r for r in self.outstanding_data if matches(r, ['invoice_number', 'customer_name'])]
            self.outstanding_table.setRowCount(len(filtered))
            for r, row in enumerate(filtered):
                self.outstanding_table.setItem(r, 0, QTableWidgetItem(row['invoice_number']))
                self.outstanding_table.setItem(r, 1, QTableWidgetItem(row['customer_name']))
                self.outstanding_table.setItem(r, 2, QTableWidgetItem(str(row['date'])))
                self.outstanding_table.setItem(r, 3, QTableWidgetItem(str(row['due_date'])))
                self.outstanding_table.setItem(r, 4, QTableWidgetItem(f"₹{row['grand_total']:.2f}"))

        elif tab_index == 4: # Stock
            filtered = [r for r in self.stock_data_list if matches(r, ['name', 'sku'])]
            self.stock_table.setRowCount(len(filtered))
            for r, row in enumerate(filtered):
                self.stock_table.setItem(r, 0, QTableWidgetItem(row['name']))
                self.stock_table.setItem(r, 1, QTableWidgetItem(row['sku'] or ""))
                self.stock_table.setItem(r, 2, QTableWidgetItem(str(row['stock_on_hand'])))
                self.stock_table.setItem(r, 3, QTableWidgetItem(f"₹{row['purchase_price']:.2f}"))
                self.stock_table.setItem(r, 4, QTableWidgetItem(f"₹{row['total_value']:.2f}"))
        
        elif tab_index == 5: # Price List
            filtered = [r for r in self.price_list_data if matches(r, ['name', 'sku'])]
            self.price_table.setRowCount(len(filtered))
            for r, row in enumerate(filtered):
                self.price_table.setItem(r, 0, QTableWidgetItem(row['name']))
                self.price_table.setItem(r, 1, QTableWidgetItem(row['sku'] or ""))
                self.price_table.setItem(r, 2, QTableWidgetItem(f"₹{row['selling_price']:.2f}"))
        
        elif tab_index == 6: # AR Aging
            rows = []
            for bucket, items in self.ar_aging_data.items():
                for item in items:
                    item['bucket'] = bucket
                    if matches(item, ['invoice_number', 'customer_name', 'bucket']):
                        rows.append(item)
            
            self.ar_aging_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.ar_aging_table.setItem(r, 0, QTableWidgetItem(row['invoice_number']))
                self.ar_aging_table.setItem(r, 1, QTableWidgetItem(row['customer_name']))
                self.ar_aging_table.setItem(r, 2, QTableWidgetItem(str(row['due_date'])))
                self.ar_aging_table.setItem(r, 3, QTableWidgetItem(row['bucket']))
                self.ar_aging_table.setItem(r, 4, QTableWidgetItem(str(row['days_overdue'])))
                self.ar_aging_table.setItem(r, 5, QTableWidgetItem(f"₹{row['amount']:.2f}"))
                
        elif tab_index == 7: # AP Aging
            rows = []
            for bucket, items in self.ap_aging_data.items():
                for item in items:
                    item['bucket'] = bucket
                    if matches(item, ['bill_number', 'vendor_name', 'bucket']):
                        rows.append(item)
            
            self.ap_aging_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.ap_aging_table.setItem(r, 0, QTableWidgetItem(row['bill_number']))
                self.ap_aging_table.setItem(r, 1, QTableWidgetItem(row['vendor_name']))
                self.ap_aging_table.setItem(r, 2, QTableWidgetItem(str(row['due_date'])))
                self.ap_aging_table.setItem(r, 3, QTableWidgetItem(row['bucket']))
                self.ap_aging_table.setItem(r, 4, QTableWidgetItem(str(row['days_overdue'])))
                self.ap_aging_table.setItem(r, 5, QTableWidgetItem(f"₹{row['amount']:.2f}"))

    def print_current_report(self):
        tab_index = self.tabs.currentIndex()
        
        # 1. Fetch Company Settings
        try:
            settings = execute_read_query("SELECT key, value FROM settings")
            settings_dict = {row['key']: row['value'] for row in settings}
        except Exception as e:
            print(f"Error fetching settings: {e}")
            settings_dict = {}
        
        report_data = {
            'company_name': settings_dict.get('company_name', 'Company Name'),
            'company_address': settings_dict.get('company_address', ''),
            'company_email': settings_dict.get('company_email', ''),
            'company_phone': settings_dict.get('company_phone', ''),
            'company_website': settings_dict.get('company_website', ''),
            'company_gstin': settings_dict.get('company_gstin', ''),
            'logo_path': settings_dict.get('company_logo', ''),
            'generated_date': QDate.currentDate().toString("yyyy-MM-dd"),
            'date_range': f"{self.start_date.date().toString('yyyy-MM-dd')} to {self.end_date.date().toString('yyyy-MM-dd')}"
        }

        # 2. Get Data based on Tab
        headers = []
        rows = []
        title = "REPORT"
        filename = "report.pdf"
        
        try:
            folder = os.path.join(os.getcwd(), "reports_pdf")
            if not os.path.exists(folder):
                os.makedirs(folder)

            if tab_index == 0: # Sales
                title = "SALES REPORT"
                filename = os.path.join(folder, "sales_report.pdf")
                headers = ["Inv #", "Customer", "Date", "Total", "Status"]
                rows = self.get_table_data(self.sales_table)
                
            elif tab_index == 1: # Purchases
                title = "PURCHASE REPORT"
                filename = os.path.join(folder, "purchase_report.pdf")
                headers = ["Bill #", "Vendor", "Date", "Total", "Status"]
                rows = self.get_table_data(self.purchase_table)

            elif tab_index == 2: # GST Summary
                title = "GST SUMMARY"
                filename = os.path.join(folder, "gst_summary.pdf")
                headers = ["Description", "Amount"]
                rows = [
                    ["Total Output Tax (Sales)", self.output_tax_lbl.text()],
                    ["Total Input Tax (Purchases)", self.input_tax_lbl.text()],
                    ["Net GST Payable", self.net_gst_lbl.text()]
                ]
                
            elif tab_index == 3: # Outstanding
                title = "OUTSTANDING INVOICES"
                filename = os.path.join(folder, "outstanding_report.pdf")
                headers = ["Inv #", "Customer", "Date", "Due Date", "Amount"]
                rows = self.get_table_data(self.outstanding_table)

            elif tab_index == 4: # Stock
                title = "STOCK VALUATION"
                filename = os.path.join(folder, "stock_valuation.pdf")
                headers = ["Item Name", "SKU", "Stock Qty", "Purchase Price", "Total Value"]
                rows = self.get_table_data(self.stock_table)

            elif tab_index == 5: # Price List
                title = "PRICE LIST"
                filename = os.path.join(folder, "price_list.pdf")
                headers = ["Item Name", "SKU", "Selling Price"]
                rows = self.get_table_data(self.price_table)
                
            elif tab_index == 6: # AR Aging
                title = "AR AGING REPORT"
                filename = os.path.join(folder, "ar_aging_report.pdf")
                headers = ["Inv #", "Customer", "Due Date", "Bucket", "Days Overdue", "Amount"]
                rows = self.get_table_data(self.ar_aging_table)
                
            elif tab_index == 7: # AP Aging
                title = "AP AGING REPORT"
                filename = os.path.join(folder, "ap_aging_report.pdf")
                headers = ["Bill #", "Vendor", "Due Date", "Bucket", "Days Overdue", "Amount"]
                rows = self.get_table_data(self.ap_aging_table)
            
            # 3. Generate PDF
            generate_generic_report_pdf(report_data, headers, rows, filename, title)
            
            QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")

    def get_table_data(self, table_widget):
        rows = []
        for r in range(table_widget.rowCount()):
            row_data = []
            for c in range(table_widget.columnCount()):
                item = table_widget.item(r, c)
                row_data.append(item.text() if item else "")
            rows.append(row_data)
        return rows

