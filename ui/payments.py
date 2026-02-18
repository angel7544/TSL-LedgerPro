
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, 
    QDoubleSpinBox, QMessageBox, QFrame, QCheckBox, QTextEdit, QFileDialog,
    QScrollArea, QWidget, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QDate
import os
import json
from database.db import execute_read_query, execute_write_query, execute_transaction
from modules.payment import get_unpaid_invoices, save_payment, generate_payment_number
import datetime

class RecordPaymentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Payment")
        self.resize(900, 700)
        
        main_layout = QVBoxLayout()
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # --- Header Section ---
        header_layout = QHBoxLayout()
        
        # Left Header
        left_header = QVBoxLayout()
        
        # Customer Selection
        left_header.addWidget(QLabel("Customer Name*"))
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True) 
        self.load_customers()
        self.customer_combo.currentIndexChanged.connect(self.load_invoices)
        left_header.addWidget(self.customer_combo)
        
        left_header.addWidget(QLabel("Amount Received (₹)*"))
        self.amount_received_spin = QDoubleSpinBox()
        self.amount_received_spin.setRange(0, 10000000)
        self.amount_received_spin.setPrefix("₹")
        self.amount_received_spin.valueChanged.connect(self.on_amount_received_changed)
        left_header.addWidget(self.amount_received_spin)
        
        # Bank Charges
        left_header.addWidget(QLabel("Bank Charges (if any)"))
        self.bank_charges = QDoubleSpinBox()
        self.bank_charges.setRange(0, 1000000)
        self.bank_charges.setPrefix("₹")
        left_header.addWidget(self.bank_charges)
        
        header_layout.addLayout(left_header)
        
        # Right Header
        right_header = QVBoxLayout()
        
        # Payment Date
        right_header.addWidget(QLabel("Payment Date*"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        right_header.addWidget(self.date_edit)
        
        # Payment #
        right_header.addWidget(QLabel("Payment #"))
        self.payment_number = QLineEdit()
        self.payment_number.setText(generate_payment_number())
        right_header.addWidget(self.payment_number)
        
        # Payment Mode
        right_header.addWidget(QLabel("Payment Mode"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Cash", "Bank Transfer", "UPI", "Cheque", "Credit Card"])
        right_header.addWidget(self.method_combo)
        
        # Deposit To
        right_header.addWidget(QLabel("Deposit To"))
        self.deposit_to = QLineEdit() # Could be a combo of accounts
        right_header.addWidget(self.deposit_to)
        
        # Reference
        right_header.addWidget(QLabel("Reference#"))
        self.ref_input = QLineEdit()
        right_header.addWidget(self.ref_input)
        
        header_layout.addLayout(right_header)
        layout.addLayout(header_layout)
        
        # --- Tax Deduction ---
        tax_layout = QHBoxLayout()
        self.tax_deducted_chk = QCheckBox("Tax deducted?")
        self.tax_deducted_chk.toggled.connect(self.toggle_tax_fields)
        tax_layout.addWidget(self.tax_deducted_chk)
        
        self.tax_account = QLineEdit()
        self.tax_account.setPlaceholderText("Yes, TDS (Income Tax)")
        self.tax_account.setEnabled(False)
        tax_layout.addWidget(self.tax_account)
        
        self.tax_deducted_amount = QDoubleSpinBox()
        self.tax_deducted_amount.setRange(0, 1000000)
        self.tax_deducted_amount.setPrefix("₹")
        self.tax_deducted_amount.setEnabled(False)
        tax_layout.addWidget(self.tax_deducted_amount)
        
        layout.addLayout(tax_layout)

        # --- Custom Fields ---
        self.load_custom_fields_ui(layout)
        
        # --- Invoices Table ---
        layout.addWidget(QLabel("Unpaid Invoices"))
        
        # Date Filter (Placeholder for now)
        # filter_layout = QHBoxLayout()
        # filter_layout.addWidget(QLabel("Filter by Date Range"))
        # layout.addLayout(filter_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Invoice #", "Invoice Amount", "Amount Due", "Payment", "id"]) 
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.hideColumn(5) 
        self.table.setMinimumHeight(200)
        layout.addWidget(self.table)
        
        # --- Footer / Summary ---
        footer_layout = QHBoxLayout()
        
        # Left Footer (Notes, Attachments)
        left_footer = QVBoxLayout()
        
        left_footer.addWidget(QLabel("Notes (Internal use)"))
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        left_footer.addWidget(self.notes)
        
        # Send Thank You Note Checkbox
        self.send_note_chk = QCheckBox("Send a 'Thank you' note for this payment")
        left_footer.addWidget(self.send_note_chk)
        
        attach_layout = QHBoxLayout()
        self.attach_btn = QPushButton("Attach File")
        self.attach_btn.clicked.connect(self.attach_file)
        self.attach_label = QLabel("No file selected")
        self.attachment_path = ""
        attach_layout.addWidget(self.attach_btn)
        attach_layout.addWidget(self.attach_label)
        left_footer.addLayout(attach_layout)
        
        footer_layout.addLayout(left_footer, stretch=1)
        
        # Right Footer (Summary)
        summary_layout = QVBoxLayout()
        self.lbl_total_due = QLabel("Total Due: ₹0.00")
        self.lbl_amount_used = QLabel("Amount Used: ₹0.00")
        self.lbl_amount_excess = QLabel("Amount Excess: ₹0.00")
        
        # Auto Apply
        self.auto_apply_btn = QPushButton("Auto Apply")
        self.auto_apply_btn.clicked.connect(self.auto_apply_payment)
        summary_layout.addWidget(self.auto_apply_btn)
        
        summary_layout.addWidget(self.lbl_total_due)
        summary_layout.addWidget(self.lbl_amount_used)
        summary_layout.addWidget(self.lbl_amount_excess)
        
        footer_layout.addLayout(summary_layout, stretch=1)
        
        layout.addLayout(footer_layout)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Buttons
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
        
        self.invoices_data = []

    def load_custom_fields_ui(self, parent_layout):
        """Loads custom fields from settings and adds them to the UI."""
        settings = execute_read_query("SELECT value FROM settings WHERE key='custom_fields_payment'")
        if not settings:
            return
            
        try:
            fields = json.loads(settings[0]['value'])
        except:
            return
            
        if not fields:
            return

        group = QGroupBox("Additional Information")
        layout = QFormLayout()
        
        self.custom_fields_widgets = {}
        
        for field in fields:
            name = field.get('name', 'Unknown')
            default = field.get('default', '')
            
            widget = QLineEdit(default)
            layout.addRow(f"{name}:", widget)
            self.custom_fields_widgets[name] = widget
            
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def toggle_tax_fields(self, checked):
        self.tax_account.setEnabled(checked)
        self.tax_deducted_amount.setEnabled(checked)

    def load_customers(self):
        self.customer_combo.clear()
        self.customer_combo.addItem("Select Customer", None)
        customers = execute_read_query("SELECT id, name FROM customers ORDER BY name")
        for c in customers:
            self.customer_combo.addItem(c['name'], c['id'])

    def load_invoices(self):
        idx = self.customer_combo.currentIndex()
        if idx <= 0:
            self.table.setRowCount(0)
            self.invoices_data = []
            return
            
        customer_id = self.customer_combo.currentData()
        self.invoices_data = get_unpaid_invoices(customer_id)
        
        self.table.setRowCount(len(self.invoices_data))
        self.table.blockSignals(True)
        
        total_due = 0.0
        
        for r, inv in enumerate(self.invoices_data):
            self.table.setItem(r, 0, QTableWidgetItem(str(inv['date'])))
            self.table.setItem(r, 1, QTableWidgetItem(inv['invoice_number']))
            self.table.setItem(r, 2, QTableWidgetItem(f"₹{inv['grand_total']:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"₹{inv['balance_due']:.2f}"))
            
            spin = QDoubleSpinBox()
            spin.setRange(0, inv['balance_due']) 
            spin.setPrefix("₹")
            spin.setValue(0.0)
            spin.valueChanged.connect(self.update_summary)
            self.table.setCellWidget(r, 4, spin)
            
            self.table.setItem(r, 5, QTableWidgetItem(str(inv['id'])))
            
            total_due += inv['balance_due']
            
        self.table.blockSignals(False)
        self.lbl_total_due.setText(f"Total Due: ₹{total_due:.2f}")
        self.update_summary()

    def on_amount_received_changed(self):
        self.auto_apply_payment()

    def update_summary(self):
        recv = self.amount_received_spin.value()
        used = 0.0
        
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            if spin:
                used += spin.value()
            
        excess = recv - used
        
        self.lbl_amount_used.setText(f"Amount Used: ₹{used:.2f}")
        self.lbl_amount_excess.setText(f"Amount Excess: ₹{excess:.2f}")
        
        if excess < 0:
             self.lbl_amount_excess.setStyleSheet("color: red;")
        else:
             self.lbl_amount_excess.setStyleSheet("color: green;")

    def auto_apply_payment(self):
        recv = self.amount_received_spin.value()
        remaining = recv
        
        self.table.blockSignals(True)
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            if not spin: continue
            
            due = self.invoices_data[r]['balance_due']
            
            if remaining >= due:
                spin.setValue(due)
                remaining -= due
            else:
                spin.setValue(remaining)
                remaining = 0
                
        self.table.blockSignals(False)
        self.update_summary()
        
    def attach_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Attachment", "", "All Files (*)")
        if path:
            self.attachment_path = path
            self.attach_label.setText(os.path.basename(path))

    def save_payment(self):
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Error", "Please select a customer.")
            return
            
        recv = self.amount_received_spin.value()
        if recv <= 0:
            QMessageBox.warning(self, "Error", "Amount received must be greater than 0.")
            return
            
        allocations = []
        total_allocated = 0.0
        
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            amount = spin.value()
            if amount > 0:
                inv_id = int(self.table.item(r, 5).text())
                allocations.append({'invoice_id': inv_id, 'amount': amount})
                total_allocated += amount
                
        if total_allocated > recv:
            QMessageBox.warning(self, "Error", "Total allocated amount cannot exceed amount received.")
            return
            
        if not allocations:
             QMessageBox.warning(self, "Error", "Please allocate payment to at least one invoice.")
             return

        # Collect Custom Fields
        custom_fields_data = {}
        if hasattr(self, 'custom_fields_widgets'):
            for name, widget in self.custom_fields_widgets.items():
                custom_fields_data[name] = widget.text()

        data = {
            'customer_id': customer_id,
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'method': self.method_combo.currentText(),
            'reference': self.ref_input.text(),
            'payment_number': self.payment_number.text(),
            'deposit_to': self.deposit_to.text(),
            'bank_charges': self.bank_charges.value(),
            'tax_deducted': self.tax_deducted_amount.value() if self.tax_deducted_chk.isChecked() else 0.0,
            'tax_account': self.tax_account.text() if self.tax_deducted_chk.isChecked() else '',
            'notes': self.notes.toPlainText(),
            'attachment_path': self.attachment_path,
            'allocations': allocations,
            'custom_fields': json.dumps(custom_fields_data),
            'send_thank_you': self.send_note_chk.isChecked()
        }
        
        try:
            save_payment(data)
            
            if self.send_note_chk.isChecked():
                QMessageBox.information(self, "Email", "Thank you note email queued (Simulated).")
                
            QMessageBox.information(self, "Success", "Payment recorded successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save payment: {str(e)}")
