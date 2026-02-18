from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox, 
    QDateEdit, QFormLayout, QDialog, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QCheckBox, QFileDialog, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QDesktopServices
import os
import json
from database.db import execute_read_query, execute_write_query
from modules.invoice import create_bill, update_bill
from modules.payment import get_unpaid_bills, save_bill_payment, generate_payment_number, get_vendor_credits
from pdf.generator import generate_bill_pdf
import datetime

class BillsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Purchases (Bills)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        create_btn = QPushButton("+ New Bill")
        create_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 16px; border-radius: 6px;")
        create_btn.clicked.connect(self.open_create_dialog)
        
        pay_btn = QPushButton("Record Payment")
        pay_btn.setStyleSheet("background-color: #10B981; color: white; padding: 8px 16px; border-radius: 6px;")
        pay_btn.clicked.connect(self.open_payment_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(pay_btn)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Bill #", "Vendor", "Date", "Total", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh_data()

    def open_payment_dialog(self):
        dialog = RecordBillPaymentDialog(self)
        if dialog.exec():
            self.refresh_data()

    def refresh_data(self):
        query = """
            SELECT b.id, b.bill_number, v.name as vendor_name, b.date, b.grand_total, b.status
            FROM bills b
            JOIN vendors v ON b.vendor_id = v.id
            ORDER BY b.created_at DESC
        """
        rows = execute_read_query(query)
        self.table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row['bill_number']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['vendor_name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['date'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"₹{row['grand_total']:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row['status']))
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, r=row['id']: self.view_bill(r))
            btn_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=row['id']: self.edit_bill(r))
            btn_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(row_idx, 5, btn_widget)

    def edit_bill(self, bill_id):
        # Fetch full details
        bill_query = "SELECT * FROM bills WHERE id = ?"
        bill_rows = execute_read_query(bill_query, (bill_id,))
        if not bill_rows:
            return
            
        bill = dict(bill_rows[0])
        
        # Fetch items
        items_query = """
            SELECT bi.*, i.name as item_name, i.purchase_price as list_price, i.gst_rate as list_gst
            FROM bill_items bi
            JOIN items i ON bi.item_id = i.id
            WHERE bi.bill_id = ?
        """
        items = execute_read_query(items_query, (bill_id,))
        bill['items'] = [dict(item) for item in items]
        
        dialog = CreateBillDialog(self, bill_data=bill)
        if dialog.exec():
            self.refresh_data()

    def view_bill(self, bill_id):
        # Fetch full details
        bill_query = """
            SELECT b.*, v.name as vendor_name, v.address as vendor_address, v.gstin as vendor_gstin
            FROM bills b
            JOIN vendors v ON b.vendor_id = v.id
            WHERE b.id = ?
        """
        rows = execute_read_query(bill_query, (bill_id,))
        if not rows:
            return
            
        bill = rows[0]
        
        # Fetch items
        items_query = """
            SELECT bi.*, i.name as item_name
            FROM bill_items bi
            JOIN items i ON bi.item_id = i.id
            WHERE bi.bill_id = ?
        """
        items = execute_read_query(items_query, (bill_id,))
        
        # Show Dialog
        dialog = ViewBillDialog(dict(bill), [dict(i) for i in items], self)
        dialog.exec()

    def open_create_dialog(self):
        dialog = CreateBillDialog(self)
        if dialog.exec():
            self.refresh_data()

class RecordBillPaymentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Payment (Purchases)")
        self.resize(900, 700)
        # Enable Maximize Button
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        main_layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        header_layout = QHBoxLayout()
        
        left_header = QVBoxLayout()
        left_header.addWidget(QLabel("Vendor Name*"))
        self.vendor_combo = QComboBox()
        self.vendor_combo.setEditable(True)
        self.load_vendors_for_payment()
        self.vendor_combo.currentIndexChanged.connect(self.load_bills)
        left_header.addWidget(self.vendor_combo)
        
        # Credits Display
        self.lbl_credits = QLabel("Available Credits: ₹0.00")
        self.lbl_credits.setStyleSheet("color: green; font-weight: bold;")
        left_header.addWidget(self.lbl_credits)
        
        self.chk_use_credits = QCheckBox("Use Available Credits")
        self.chk_use_credits.setChecked(True)
        self.chk_use_credits.toggled.connect(self.on_amount_paid_changed)
        left_header.addWidget(self.chk_use_credits)
        
        left_header.addWidget(QLabel("Amount Paid (₹)*"))
        self.amount_paid_spin = QDoubleSpinBox()
        self.amount_paid_spin.setRange(0, 10000000)
        self.amount_paid_spin.setPrefix("₹")
        self.amount_paid_spin.valueChanged.connect(self.on_amount_paid_changed)
        left_header.addWidget(self.amount_paid_spin)
        
        header_layout.addLayout(left_header)
        
        right_header = QVBoxLayout()
        right_header.addWidget(QLabel("Payment Date*"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        right_header.addWidget(self.date_edit)
        
        right_header.addWidget(QLabel("Payment #"))
        self.payment_number = QLineEdit()
        self.payment_number.setText(generate_payment_number())
        right_header.addWidget(self.payment_number)
        
        right_header.addWidget(QLabel("Payment Mode"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Cash", "Bank Transfer", "UPI", "Cheque", "Credit Card"])
        right_header.addWidget(self.method_combo)
        
        right_header.addWidget(QLabel("Paid From"))
        self.paid_from = QLineEdit()
        right_header.addWidget(self.paid_from)
        
        right_header.addWidget(QLabel("Reference#"))
        self.ref_input = QLineEdit()
        right_header.addWidget(self.ref_input)
        
        header_layout.addLayout(right_header)
        layout.addLayout(header_layout)
        
        layout.addWidget(QLabel("Unpaid Bills"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Bill #", "Bill Amount", "Amount Due", "Payment", "id"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.hideColumn(5)
        self.table.setMinimumHeight(200)
        layout.addWidget(self.table)
        
        footer_layout = QHBoxLayout()
        
        left_footer = QVBoxLayout()
        left_footer.addWidget(QLabel("Notes"))
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        left_footer.addWidget(self.notes)
        footer_layout.addLayout(left_footer, stretch=1)
        
        summary_layout = QVBoxLayout()
        self.lbl_total_due = QLabel("Total Due: ₹0.00")
        self.lbl_amount_used = QLabel("Amount Used: ₹0.00")
        self.lbl_amount_excess = QLabel("Amount Balance: ₹0.00")
        summary_layout.addWidget(self.lbl_total_due)
        summary_layout.addWidget(self.lbl_amount_used)
        summary_layout.addWidget(self.lbl_amount_excess)
        footer_layout.addLayout(summary_layout, stretch=1)
        
        layout.addLayout(footer_layout)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Payment")
        save_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 16px;")
        save_btn.clicked.connect(self.save_payment)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
        self.bills_data = []
    
    def load_vendors_for_payment(self):
        self.vendor_combo.clear()
        self.vendor_combo.addItem("Select Vendor", None)
        vendors = execute_read_query("SELECT id, name FROM vendors ORDER BY name")
        for v in vendors:
            self.vendor_combo.addItem(v['name'], v['id'])
    
    def load_bills(self):
        idx = self.vendor_combo.currentIndex()
        if idx <= 0:
            self.table.setRowCount(0)
            self.bills_data = []
            self.lbl_total_due.setText("Total Due: ₹0.00")
            self.lbl_credits.setText("Available Credits: ₹0.00")
            self.current_credits = 0.0
            self.update_summary()
            return
        
        vendor_id = self.vendor_combo.currentData()
        self.bills_data = get_unpaid_bills(vendor_id)
        
        # Fetch Credits
        self.current_credits = get_vendor_credits(vendor_id)
        self.lbl_credits.setText(f"Available Credits: ₹{self.current_credits:.2f}")
        
        self.table.setRowCount(len(self.bills_data))
        self.table.blockSignals(True)
        
        total_due = 0.0
        for r, bill in enumerate(self.bills_data):
            self.table.setItem(r, 0, QTableWidgetItem(str(bill['date'])))
            self.table.setItem(r, 1, QTableWidgetItem(bill['bill_number']))
            self.table.setItem(r, 2, QTableWidgetItem(f"₹{bill['grand_total']:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"₹{bill['balance_due']:.2f}"))
            
            spin = QDoubleSpinBox()
            spin.setRange(0, bill['balance_due'])
            spin.setPrefix("₹")
            spin.setValue(0.0)
            spin.valueChanged.connect(self.update_summary)
            self.table.setCellWidget(r, 4, spin)
            
            self.table.setItem(r, 5, QTableWidgetItem(str(bill['id'])))
            
            total_due += bill['balance_due']
        
        self.table.blockSignals(False)
        self.lbl_total_due.setText(f"Total Due: ₹{total_due:.2f}")
        self.update_summary()
    
    def on_amount_paid_changed(self):
        self.auto_allocate()
        self.update_summary()

    def auto_allocate(self):
        paid = self.amount_paid_spin.value()
        
        credits_to_use = 0.0
        if self.chk_use_credits.isChecked() and hasattr(self, 'current_credits'):
            credits_to_use = self.current_credits
            
        remaining = paid + credits_to_use
        
        self.table.blockSignals(True)
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            balance_due = float(self.table.item(r, 3).text().replace('₹', ''))
            
            if remaining > 0:
                if remaining >= balance_due:
                    spin.setValue(balance_due)
                    remaining -= balance_due
                else:
                    spin.setValue(remaining)
                    remaining = 0
            else:
                spin.setValue(0)
        self.table.blockSignals(False)
    
    def update_summary(self):
        paid = self.amount_paid_spin.value()
        
        credits_to_use = 0.0
        if self.chk_use_credits.isChecked() and hasattr(self, 'current_credits'):
            credits_to_use = self.current_credits
            
        total_available = paid + credits_to_use
        
        used = 0.0
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            if spin:
                used += spin.value()
        balance = total_available - used
        self.lbl_amount_used.setText(f"Amount Used: ₹{used:.2f}")
        self.lbl_amount_excess.setText(f"Amount Balance: ₹{balance:.2f}")
        if balance < 0:
            self.lbl_amount_excess.setStyleSheet("color: red;")
        else:
            self.lbl_amount_excess.setStyleSheet("color: green;")
    
    def save_payment(self):
        vendor_id = self.vendor_combo.currentData()
        if not vendor_id:
            QMessageBox.warning(self, "Error", "Please select a vendor.")
            return
        
        paid = self.amount_paid_spin.value()
        if paid <= 0:
            QMessageBox.warning(self, "Error", "Amount paid must be greater than 0.")
            return
        
        allocations = []
        total_allocated = 0.0
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            amount = spin.value()
            if amount > 0:
                bill_id = int(self.table.item(r, 5).text())
                allocations.append({'bill_id': bill_id, 'amount': amount})
                total_allocated += amount
        
        if total_allocated > paid:
            QMessageBox.warning(self, "Error", "Total allocated amount cannot exceed amount paid.")
            return
        
        # Allow saving if there is an excess amount (credit), even if no allocations
        if not allocations and paid <= 0:
             QMessageBox.warning(self, "Error", "Please allocate payment to at least one bill or enter an amount greater than 0.")
             return

        data = {
            'vendor_id': vendor_id,
            'amount_paid': paid,  # Pass total paid amount
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'method': self.method_combo.currentText(),
            'reference': self.ref_input.text(),
            'payment_number': self.payment_number.text(),
            'deposit_to': self.paid_from.text(),
            'bank_charges': 0.0,
            'tax_deducted': 0.0,
            'tax_account': '',
            'notes': self.notes.toPlainText(),
            'attachment_path': '',
            'allocations': allocations,
            'custom_fields': '{}',
            'use_credits': self.chk_use_credits.isChecked()
        }
        
        try:
            save_bill_payment(data)
            QMessageBox.information(self, "Success", "Payment recorded successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save payment: {str(e)}")

class ViewBillDialog(QDialog):
    def __init__(self, bill_data, items_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Bill #{bill_data['bill_number']}")
        self.setFixedSize(600, 700)
        
        self.bill_data = bill_data
        self.bill_data['items'] = items_data
        
        # Fetch company settings for PDF
        settings = execute_read_query("SELECT key, value FROM settings")
        self.settings_dict = {row['key']: row['value'] for row in settings}
        self.bill_data.update(self.settings_dict)
        self.bill_data['logo_path'] = self.settings_dict.get('company_logo', '')
        
        layout = QVBoxLayout()
        
        # Details Area
        details = QTextEdit()
        details.setReadOnly(True)
        
        html = f"""
        <h2>Bill #{bill_data['bill_number']}</h2>
        <p><b>Date:</b> {bill_data['date']}<br>
        <b>Due Date:</b> {bill_data.get('due_date', '')}</p>
        <p><b>Vendor:</b> {bill_data['vendor_name']}<br>
        {bill_data['vendor_address'] or ''}<br>
        GSTIN: {bill_data.get('vendor_gstin', '')}</p>
        
        <table border="1" cellspacing="0" cellpadding="5" width="100%">
            <tr>
                <th>Item</th>
                <th>Qty</th>
                <th>Rate</th>
                <th>Total</th>
            </tr>
        """
        
        for item in items_data:
            html += f"""
            <tr>
                <td>{item['item_name']}</td>
                <td>{item['quantity']}</td>
                <td>{item['rate']}</td>
                <td>{item['amount']}</td>
            </tr>
            """
            
        html += f"""
        </table>
        <h3 align="right">Total: ₹{bill_data['grand_total']:.2f}</h3>
        """
        
        # Custom Fields Display
        if bill_data.get('custom_fields'):
            try:
                custom_fields = json.loads(bill_data['custom_fields'])
                if custom_fields:
                    html += "<h3>Additional Information</h3><ul>"
                    for key, value in custom_fields.items():
                        html += f"<li><b>{key}:</b> {value}</li>"
                    html += "</ul>"
            except:
                pass
        
        details.setHtml(html)
        layout.addWidget(details)
        
        # Buttons
        btn_layout = QHBoxLayout()
        print_btn = QPushButton("Print / Save PDF")
        print_btn.clicked.connect(self.print_pdf)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def print_pdf(self):
        try:
            folder = os.path.join(os.getcwd(), "bills_pdf")
            if not os.path.exists(folder):
                os.makedirs(folder)
                
            filename = os.path.join(folder, f"{self.bill_data['bill_number']}.pdf")
            generate_bill_pdf(self.bill_data, filename)
            
            QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")

class CreateBillDialog(QDialog):
    def __init__(self, parent=None, bill_data=None):
        super().__init__(parent)
        self.bill_data = bill_data
        self.setWindowTitle("Edit Purchase (Bill)" if bill_data else "Record New Purchase (Bill)")
        self.setFixedSize(900, 700)
        
        main_layout = QVBoxLayout()
        
        # Scroll Area for long form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # --- Header Section ---
        header_form = QFormLayout()
        
        # Vendor
        self.vendor_combo = QComboBox()
        self.load_vendors()
        header_form.addRow("Vendor:", self.vendor_combo)
        
        # Bill # and Order #
        row1 = QHBoxLayout()
        self.bill_number = QLineEdit()
        self.bill_number.setPlaceholderText("Enter Bill #")
        self.order_number = QLineEdit()
        self.order_number.setPlaceholderText("Order #")
        row1.addWidget(QLabel("Bill #:"))
        row1.addWidget(self.bill_number)
        row1.addWidget(QLabel("Order #:"))
        row1.addWidget(self.order_number)
        header_form.addRow(row1)
        
        # Dates
        date_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setCalendarPopup(True)
        
        date_layout.addWidget(QLabel("Bill Date:"))
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(QLabel("Due Date:"))
        date_layout.addWidget(self.due_date)
        header_form.addRow(date_layout)
        
        # Terms & Reverse Charge
        self.payment_terms = QLineEdit()
        header_form.addRow("Payment Terms:", self.payment_terms)
        
        self.reverse_charge = QCheckBox("This transaction is applicable for reverse charge")
        header_form.addRow("", self.reverse_charge)
        
        layout.addLayout(header_form)
        
        # --- Items Table ---
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Item", "Qty", "Purchase Rate", "GST %", "Total", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setMinimumHeight(200)
        
        layout.addWidget(self.items_table)
        
        # Add Item Button
        add_item_btn = QPushButton("+ Add Line Item")
        add_item_btn.clicked.connect(self.add_item_row)
        layout.addWidget(add_item_btn)
        
        # --- Footer Section ---
        footer_layout = QHBoxLayout()
        
        # Left Side (Notes, Attachments)
        left_footer = QVBoxLayout()
        
        left_footer.addWidget(QLabel("Notes"))
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("It will not be shown in PDF")
        self.notes.setMaximumHeight(60)
        left_footer.addWidget(self.notes)
        
        # Attachment
        attach_layout = QHBoxLayout()
        self.attach_btn = QPushButton("Attach File")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_label = QLabel("No file selected")
        self.attachment_path = ""
        attach_layout.addWidget(self.attach_btn)
        attach_layout.addWidget(self.attach_label)
        left_footer.addLayout(attach_layout)
        
        # --- Custom Fields Section ---
        self.custom_fields_widgets = {}
        self.load_custom_fields_ui(left_footer)
        
        footer_layout.addLayout(left_footer, stretch=1)
        
        # Right Side (Totals)
        right_footer = QFormLayout()
        
        self.subtotal_label = QLabel("0.00")
        
        self.discount_amount = QDoubleSpinBox()
        self.discount_amount.setRange(0, 1000000)
        self.discount_amount.setPrefix("- ")
        
        self.tds_amount = QDoubleSpinBox()
        self.tds_amount.setRange(0, 1000000)
        self.tds_amount.setPrefix("- ")
        
        self.tcs_amount = QDoubleSpinBox()
        self.tcs_amount.setRange(0, 1000000)
        self.tcs_amount.setPrefix("+ ")
        
        self.adjustment = QDoubleSpinBox()
        self.adjustment.setRange(-1000000, 1000000)
        
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        right_footer.addRow("Sub Total:", self.subtotal_label)
        right_footer.addRow("Discount:", self.discount_amount)
        right_footer.addRow("TDS:", self.tds_amount)
        right_footer.addRow("TCS:", self.tcs_amount)
        right_footer.addRow("Adjustment:", self.adjustment)
        right_footer.addRow("", self.total_label)
        
        # Connect signals
        self.discount_amount.valueChanged.connect(self.calculate_final_total)
        self.tds_amount.valueChanged.connect(self.calculate_final_total)
        self.tcs_amount.valueChanged.connect(self.calculate_final_total)
        self.adjustment.valueChanged.connect(self.calculate_final_total)
        
        footer_layout.addLayout(right_footer, stretch=1)
        
        layout.addLayout(footer_layout)
        
        # Set scroll widget
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Update Bill" if self.bill_data else "Save Bill")
        save_btn.clicked.connect(self.save_bill)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
        self.available_items = execute_read_query(
            "SELECT id, name, sku, purchase_price, gst_rate, is_purchasable FROM items"
        )
        self.calculated_subtotal = 0.0

        if self.bill_data:
            self.populate_data()
            
    def populate_data(self):
        data = self.bill_data
        
        # Vendor
        idx = self.vendor_combo.findData(data['vendor_id'])
        if idx >= 0:
            self.vendor_combo.setCurrentIndex(idx)
            
        self.bill_number.setText(data.get('bill_number', ''))
        self.order_number.setText(data.get('order_number', ''))
        self.date_edit.setDate(QDate.fromString(data['date'], "yyyy-MM-dd"))
        if data.get('due_date'):
            self.due_date.setDate(QDate.fromString(data['due_date'], "yyyy-MM-dd"))
            
        self.payment_terms.setText(data.get('payment_terms', ''))
        self.reverse_charge.setChecked(bool(data.get('reverse_charge', 0)))
        
        self.notes.setText(data.get('notes', ''))
        self.discount_amount.setValue(data.get('discount_amount', 0.0))
        self.tds_amount.setValue(data.get('tds_amount', 0.0))
        self.tcs_amount.setValue(data.get('tcs_amount', 0.0))
        self.adjustment.setValue(data.get('adjustment', 0.0))
        
        if data.get('attachment_path'):
            self.attachment_path = data['attachment_path']
            self.attach_label.setText(os.path.basename(self.attachment_path))
            
        # Custom Fields
        if data.get('custom_fields'):
            try:
                cfields = json.loads(data['custom_fields'])
                for name, val in cfields.items():
                    if name in self.custom_fields_widgets:
                        self.custom_fields_widgets[name].setText(val)
            except:
                pass
                
        # Items
        for item in data.get('items', []):
            self.add_item_row(item)

    def load_custom_fields_ui(self, parent_layout):
        """Loads custom fields from settings and adds them to the UI."""
        settings = execute_read_query("SELECT value FROM settings WHERE key='custom_fields_bill'")
        if not settings:
            return
            
        try:
            fields = json.loads(settings[0]['value'])
        except:
            return
            
        if not fields:
            return

        group = QGroupBox("Additional Fields")
        layout = QFormLayout()
        
        for field in fields:
            name = field.get('name', 'Unknown')
            default = field.get('default', '')
            
            widget = QLineEdit(default)
            layout.addRow(f"{name}:", widget)
            self.custom_fields_widgets[name] = widget
            
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def load_vendors(self):
        vendors = execute_read_query("SELECT id, name FROM vendors")
        for v in vendors:
            self.vendor_combo.addItem(v['name'], v['id'])

    def add_item_row(self, item_data=None):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Item Combo
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        for item in self.available_items:
            name = item['name']
            sku_text = ""
            if 'sku' in item.keys() and item['sku']:
                sku_text = f" ({item['sku']})"
            is_purchasable = 1
            if 'is_purchasable' in item.keys():
                try:
                    is_purchasable = int(item['is_purchasable'])
                except (ValueError, TypeError):
                    is_purchasable = 1
            display_text = f"{name}{sku_text}"
            if not is_purchasable:
                display_text = f"{display_text} [NOT PURCHASABLE]"
            combo.addItem(display_text, item)
            if not is_purchasable:
                idx_added = combo.count() - 1
                combo.setItemData(idx_added, Qt.red, Qt.ForegroundRole)
        
        # Default values
        if item_data:
            idx = -1
            for i in range(combo.count()):
                if combo.itemData(i)['id'] == item_data['item_id']:
                    idx = i
                    break
            if idx >= 0:
                combo.setCurrentIndex(idx)
            
            rate = str(item_data['rate'])
            gst = str(item_data['gst_percent'])
            qty_val = str(item_data['quantity'])
        elif self.available_items:
            first_item = self.available_items[0]
            rate = str(first_item['purchase_price'])
            gst = str(first_item['gst_rate'])
            qty_val = "1"
        else:
            rate = "0"
            gst = "0"
            qty_val = "1"

        combo.currentIndexChanged.connect(lambda idx, r=row: self.on_item_changed(r))
        
        qty = QLineEdit(qty_val)
        rate_edit = QLineEdit(rate)
        gst_edit = QLineEdit(gst)
        total = QLabel("0.00")
        
        # Delete button
        del_btn = QPushButton("X")
        del_btn.setStyleSheet("color: red; font-weight: bold;")
        del_btn.clicked.connect(lambda: self.remove_row(row))
        
        # Connect signals
        qty.textChanged.connect(self.calculate_total)
        rate_edit.textChanged.connect(self.calculate_total)
        gst_edit.textChanged.connect(self.calculate_total)
        
        self.items_table.setCellWidget(row, 0, combo)
        self.items_table.setCellWidget(row, 1, qty)
        self.items_table.setCellWidget(row, 2, rate_edit)
        self.items_table.setCellWidget(row, 3, gst_edit)
        self.items_table.setCellWidget(row, 4, total)
        self.items_table.setCellWidget(row, 5, del_btn)
        
        self.calculate_total()

    def remove_row(self, row):
        self.items_table.removeRow(row)
        self.calculate_total()

    def on_item_changed(self, row):
        combo = self.items_table.cellWidget(row, 0)
        # Handle editable combo returning index -1 if text doesn't match
        idx = combo.currentIndex()
        if idx >= 0:
            item_data = combo.itemData(idx)
            if item_data:
                self.items_table.cellWidget(row, 2).setText(str(item_data['purchase_price']))
                self.items_table.cellWidget(row, 3).setText(str(item_data['gst_rate']))
                self.calculate_total()

    def calculate_total(self):
        grand_total = 0.0
        try:
            for row in range(self.items_table.rowCount()):
                # Check if widgets exist (might be deleted)
                if not self.items_table.cellWidget(row, 1): continue
                
                qty_txt = self.items_table.cellWidget(row, 1).text()
                rate_txt = self.items_table.cellWidget(row, 2).text()
                gst_txt = self.items_table.cellWidget(row, 3).text()
                
                qty = float(qty_txt or 0)
                rate = float(rate_txt or 0)
                gst = float(gst_txt or 0)
                
                amount = rate * qty
                tax = amount * (gst/100)
                line_total = amount + tax
                
                self.items_table.cellWidget(row, 4).setText(f"{line_total:.2f}")
                grand_total += line_total
        except ValueError:
            pass
            
        self.calculated_subtotal = grand_total
        self.subtotal_label.setText(f"{grand_total:.2f}")
        self.calculate_final_total()

    def calculate_final_total(self):
        total = self.calculated_subtotal
        total -= self.discount_amount.value()
        total -= self.tds_amount.value()
        total += self.tcs_amount.value()
        total += self.adjustment.value()
        self.total_label.setText(f"Total: ₹{total:.2f}")

    def attach_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Attachment", "", "All Files (*)")
        if path:
            self.attachment_path = path
            self.attach_label.setText(os.path.basename(path))

    def save_bill(self):
        vendor_id = self.vendor_combo.currentData()
        if not vendor_id:
            QMessageBox.warning(self, "Error", "Please select a vendor")
            return
            
        items = []
        for row in range(self.items_table.rowCount()):
            combo = self.items_table.cellWidget(row, 0)
            idx = combo.currentIndex()
            if idx < 0:
                continue
            
            item_data = combo.itemData(idx)
            if not item_data:
                continue
            is_purchasable = 1
            if 'is_purchasable' in item_data.keys():
                try:
                    is_purchasable = int(item_data['is_purchasable'])
                except (ValueError, TypeError):
                    is_purchasable = 1
            if not is_purchasable:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Item '{item_data['name']}' is marked as not inactive(purchasable) in Items."
                )
                return
                
            try:
                qty = float(self.items_table.cellWidget(row, 1).text())
                rate = float(self.items_table.cellWidget(row, 2).text())
                gst = float(self.items_table.cellWidget(row, 3).text())
                
                items.append({
                    "item_id": item_data['id'],
                    "quantity": qty,
                    "rate": rate,
                    "gst_percent": gst
                })
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid number format in items")
                return
                
        if not items:
            QMessageBox.warning(self, "Error", "Please add at least one item")
            return

        # Collect Custom Fields
        custom_fields_data = {}
        for name, widget in self.custom_fields_widgets.items():
            custom_fields_data[name] = widget.text()

        bill_data = {
            "vendor_id": vendor_id,
            "bill_number": self.bill_number.text(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "due_date": self.due_date.date().toString("yyyy-MM-dd"),
            "items": items,
            "order_number": self.order_number.text(),
            "payment_terms": self.payment_terms.text(),
            "reverse_charge": 1 if self.reverse_charge.isChecked() else 0,
            "notes": self.notes.toPlainText(),
            "discount_amount": self.discount_amount.value(),
            "tds_amount": self.tds_amount.value(),
            "tcs_amount": self.tcs_amount.value(),
            "adjustment": self.adjustment.value(),
            "attachment_path": self.attachment_path,
            "custom_fields": json.dumps(custom_fields_data)
        }
        
        try:
            if self.bill_data:
                # Update
                bill_data['status'] = self.bill_data.get('status', 'Draft')
                update_bill(self.bill_data['id'], bill_data)
                QMessageBox.information(self, "Success", "Bill updated successfully")
            else:
                create_bill(bill_data)
                QMessageBox.information(self, "Success", "Bill saved successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save bill: {str(e)}")
