
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
from modules.payment import get_unpaid_invoices, save_payment, generate_payment_number, get_customer_credits
import datetime

class PaymentsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Payment Records")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Date", "Payment #", "Party", "Type", "Invoice/Bill #", "Amount", "Mode", "Reference", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        # Query for Customer Payments
        # Include payments with invoice_id IS NULL (Credits)
        query_cust = """
            SELECT MIN(p.id) as id, p.date, p.payment_number, SUM(p.amount) as amount, p.method, p.reference, MAX(p.notes) as notes,
                   c.name as party_name, 'Customer' as party_type,
                   GROUP_CONCAT(i.invoice_number, ', ') as invoice_numbers
            FROM payments p
            JOIN customers c ON p.customer_id = c.id
            LEFT JOIN invoices i ON p.invoice_id = i.id
            GROUP BY p.payment_number
        """
        
        # Query for Vendor Payments (Bills)
        # Note: This query might miss unallocated vendor payments (credits) because of INNER JOIN on bills
        # But we keep it as is for now to match original behavior, just adding GROUP BY
        query_vend = """
            SELECT MIN(p.id) as id, p.date, p.payment_number, SUM(p.amount) as amount, p.method, p.reference, MAX(p.notes) as notes,
                   v.name as party_name, 'Vendor' as party_type,
                   GROUP_CONCAT(b.bill_number, ', ') as invoice_numbers
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            JOIN vendors v ON b.vendor_id = v.id
            GROUP BY p.payment_number
        """
        
        rows = []
        try:
            rows_cust = execute_read_query(query_cust)
            rows.extend(rows_cust)
        except Exception as e:
            print(f"Error fetching customer payments: {e}")

        try:
            rows_vend = execute_read_query(query_vend)
            rows.extend(rows_vend)
        except Exception as e:
            # It's possible bill_id column or tables don't exist yet if purchase module isn't fully set up
            print(f"Error fetching vendor payments: {e}")
            
        # Sort by date desc
        rows.sort(key=lambda x: x['date'], reverse=True)
        
        self.table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['date'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['payment_number'] or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row['party_name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row['party_type']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row['invoice_numbers'] or "-"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"₹{row['amount']:.2f}"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(row['method']))
            self.table.setItem(row_idx, 7, QTableWidgetItem(row['reference'] or ""))
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=row['id']: self.edit_payment(r))
            btn_layout.addWidget(edit_btn)
            
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, r=row['id']: self.view_payment(r))
            btn_layout.addWidget(view_btn)
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("color: white; background-color: #EF4444;")
            del_btn.clicked.connect(lambda checked, r=row['id']: self.delete_payment_ui(r))
            btn_layout.addWidget(del_btn)
            
            self.table.setCellWidget(row_idx, 8, btn_widget)

    def delete_payment_ui(self, payment_id):
        # Get Payment Number
        res = execute_read_query("SELECT payment_number FROM payments WHERE id = ?", (payment_id,))
        if not res: return
        payment_number = res[0]['payment_number']
        
        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            f"Are you sure you want to delete payment {payment_number}? This will delete ALL allocations associated with this payment number.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # 1. Get all invoices/bills affected to update status later? 
                # Actually, status is calculated based on balance. 
                # If we delete payment, we need to update status of invoices to 'Sent'/'Partial'.
                # My system updates status to 'Paid' when balance <= 0.
                # It does NOT automatically revert to 'Sent' if balance > 0.
                # I need to handle status reversal.
                
                # Get affected invoices
                inv_rows = execute_read_query("SELECT DISTINCT invoice_id FROM payments WHERE payment_number = ? AND invoice_id IS NOT NULL", (payment_number,))
                bill_rows = execute_read_query("SELECT DISTINCT bill_id FROM payments WHERE payment_number = ? AND bill_id IS NOT NULL", (payment_number,))
                
                # Delete
                execute_write_query("DELETE FROM payments WHERE payment_number = ?", (payment_number,))
                
                # Update Invoice Statuses
                for row in inv_rows:
                    inv_id = row['invoice_id']
                    # Recalculate status
                    # Check balance
                    # We can just set to 'Sent' (or 'Partial' if we had that, but we use 'Sent' for unpaid).
                    # Actually, we should check if there are OTHER payments.
                    # Or just blindly set to 'Sent' if balance > 0?
                    # My logic: "UPDATE invoices SET status = 'Paid' WHERE id = ?" happens in save_payment.
                    # I should revert it.
                    
                    # Let's calculate balance.
                    # Re-use logic? Or just simple check.
                    
                    # Fetch grand_total and paid
                    # ... simple query ...
                    q = """
                        SELECT i.grand_total, COALESCE(SUM(p.amount), 0) as paid
                        FROM invoices i
                        LEFT JOIN payments p ON i.id = p.invoice_id
                        WHERE i.id = ?
                    """
                    data = execute_read_query(q, (inv_id,))
                    if data:
                        grand_total = data[0]['grand_total']
                        paid = data[0]['paid']
                        new_status = 'Paid' if paid >= grand_total - 0.01 else 'Sent'
                        execute_write_query("UPDATE invoices SET status = ? WHERE id = ?", (new_status, inv_id))

                # Update Bill Statuses
                for row in bill_rows:
                    bill_id = row['bill_id']
                    q = """
                        SELECT b.grand_total, COALESCE(SUM(p.amount), 0) as paid
                        FROM bills b
                        LEFT JOIN payments p ON b.id = p.bill_id
                        WHERE b.id = ?
                    """
                    data = execute_read_query(q, (bill_id,))
                    if data:
                        grand_total = data[0]['grand_total']
                        paid = data[0]['paid']
                        new_status = 'Paid' if paid >= grand_total - 0.01 else 'Sent'
                        execute_write_query("UPDATE bills SET status = ? WHERE id = ?", (new_status, bill_id))

                self.refresh_data()
                QMessageBox.information(self, "Success", "Payment deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete payment: {str(e)}")

    def view_payment(self, payment_id):
        dialog = ViewPaymentDialog(payment_id, self)
        dialog.exec()

    def edit_payment(self, payment_id):
        dialog = EditPaymentDialog(payment_id, self)
        if dialog.exec():
            self.refresh_data()

class EditPaymentDialog(QDialog):
    def __init__(self, payment_id, parent=None):
        super().__init__(parent)
        self.payment_id = payment_id
        self.setWindowTitle("Edit Payment")
        self.setMinimumSize(500, 400)
        # Enable Maximize Button
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        layout = QFormLayout()
        
        # Load Data
        # First get the payment number from the ID
        query_pn = "SELECT payment_number FROM payments WHERE id = ?"
        res = execute_read_query(query_pn, (payment_id,))
        if not res:
            self.reject()
            return
            
        self.payment_number_val = res[0]['payment_number']
        
        # Now fetch all rows for this payment number
        query_all = "SELECT * FROM payments WHERE payment_number = ?"
        self.rows = execute_read_query(query_all, (self.payment_number_val,))
        
        if not self.rows:
            self.reject()
            return
            
        self.data = self.rows[0] # Use first row for common fields
        self.total_amount = sum(row['amount'] for row in self.rows)
        self.is_split = len(self.rows) > 1
        
        # Fields
        self.payment_number = QLineEdit(self.data['payment_number'])
        self.payment_number.setReadOnly(True) 
        layout.addRow("Payment #:", self.payment_number)
        
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 10000000)
        self.amount.setPrefix("₹")
        self.amount.setValue(self.total_amount)
        self.original_amount = self.total_amount
        
        if self.is_split:
            self.amount.setReadOnly(True)
            self.amount.setToolTip("Cannot edit amount for split payments. Delete and re-create if needed.")
            layout.addRow("Amount:", self.amount)
            layout.addRow(QLabel("<small style='color: red'>Amount cannot be edited for split payments</small>"))
        else:
            layout.addRow("Amount:", self.amount)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.fromString(self.data['date'], "yyyy-MM-dd"))
        layout.addRow("Date:", self.date_edit)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Cash", "Bank Transfer", "UPI", "Cheque", "Credit Card"])
        self.method_combo.setCurrentText(self.data['method'])
        layout.addRow("Method:", self.method_combo)
        
        self.reference = QLineEdit(self.data['reference'] or "")
        layout.addRow("Reference:", self.reference)
        
        self.notes = QTextEdit()
        # combine notes if different? For now just take first or max (from list query)
        # But here we are editing. Let's show the note from the first row.
        self.notes.setPlainText(self.data['notes'] or "")
        layout.addRow("Notes/Remarks:", self.notes)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Update")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)

    def save(self):
        new_date = self.date_edit.date().toString("yyyy-MM-dd")
        new_method = self.method_combo.currentText()
        new_ref = self.reference.text()
        new_notes = self.notes.toPlainText()
        new_amount = self.amount.value()

        if not self.is_split and new_amount != self.original_amount and not new_notes.strip():
            QMessageBox.warning(self, "Validation Error", "Please provide a note/remark for changing the payment amount.")
            return
        
        try:
            # Update common fields for ALL rows with this payment number
            query_common = """
                UPDATE payments 
                SET date = ?, method = ?, reference = ?, notes = ?
                WHERE payment_number = ?
            """
            execute_write_query(query_common, (new_date, new_method, new_ref, new_notes, self.payment_number_val))
            
            # Update Amount ONLY if not split
            if not self.is_split and abs(new_amount - self.original_amount) > 0.01:
                query_amt = "UPDATE payments SET amount = ? WHERE id = ?"
                execute_write_query(query_amt, (new_amount, self.data['id']))
            
            QMessageBox.information(self, "Success", "Payment updated successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment: {str(e)}")

class ViewPaymentDialog(QDialog):
    def __init__(self, payment_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("View Payment Details")
        self.setMinimumSize(600, 500)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        layout = QVBoxLayout()
        
        # --- Load Data ---
        # Get Payment Number first
        query_pn = "SELECT payment_number FROM payments WHERE id = ?"
        res = execute_read_query(query_pn, (payment_id,))
        if not res:
            self.reject()
            return
        
        payment_number = res[0]['payment_number']
        
        # Fetch All Records for this Payment #
        query_all = """
            SELECT p.*, 
                   c.name as customer_name, 
                   v.name as vendor_name,
                   i.invoice_number, i.date as invoice_date, i.grand_total as invoice_total,
                   b.bill_number, b.date as bill_date, b.grand_total as bill_total
            FROM payments p
            LEFT JOIN customers c ON p.customer_id = c.id
            LEFT JOIN vendors v ON b.vendor_id = v.id -- Wait, p.vendor_id is not directly in payments for bills? 
                                                      -- Actually payment.py inserts vendor_id into payments.
                                                      -- Let's check schema or payment logic.
            LEFT JOIN bills b ON p.bill_id = b.id
            LEFT JOIN invoices i ON p.invoice_id = i.id
            -- Need to join vendor table correctly if vendor_id column exists or via bill
            -- Let's assume vendor_id exists in payments as per save_bill_payment
            WHERE p.payment_number = ?
        """
        # Note: vendor_id column exists in payments based on save_bill_payment logic
        
        # Refined query to be safer
        query_all = """
            SELECT p.*, 
                   c.name as customer_name, 
                   v.name as vendor_name,
                   i.invoice_number, i.date as invoice_date, i.grand_total as invoice_total,
                   b.bill_number, b.date as bill_date, b.grand_total as bill_total
            FROM payments p
            LEFT JOIN customers c ON p.customer_id = c.id
            LEFT JOIN vendors v ON p.vendor_id = v.id
            LEFT JOIN invoices i ON p.invoice_id = i.id
            LEFT JOIN bills b ON p.bill_id = b.id
            WHERE p.payment_number = ?
        """
        
        rows = execute_read_query(query_all, (payment_number,))
        if not rows:
            self.reject()
            return
            
        main_row = rows[0]
        total_amount = sum(r['amount'] for r in rows)
        
        # --- Header Info ---
        form_layout = QFormLayout()
        
        party_name = main_row['customer_name'] if main_row['customer_id'] else main_row['vendor_name']
        party_type = "Customer" if main_row['customer_id'] else "Vendor"
        
        form_layout.addRow("Payment #:", QLabel(main_row['payment_number']))
        form_layout.addRow("Date:", QLabel(main_row['date']))
        form_layout.addRow("Party:", QLabel(f"{party_name} ({party_type})"))
        form_layout.addRow("Total Amount:", QLabel(f"₹{total_amount:.2f}"))
        form_layout.addRow("Method:", QLabel(main_row['method']))
        if main_row['reference']:
            form_layout.addRow("Reference:", QLabel(main_row['reference']))
        
        layout.addLayout(form_layout)
        
        layout.addWidget(QLabel("<b>Allocation Breakdown</b>"))
        
        # --- Allocation Table ---
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Invoice/Bill #", "Date", "Total Amount", "Paid Amount"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        table.setRowCount(len(rows))
        
        for i, row in enumerate(rows):
            # Determine if Invoice or Bill
            doc_num = row['invoice_number'] or row['bill_number'] or "Unallocated / Credit"
            doc_date = row['invoice_date'] or row['bill_date'] or "-"
            doc_total = row['invoice_total'] or row['bill_total'] or 0.0
            
            if not row['invoice_id'] and not row['bill_id']:
                # Credit
                doc_total = 0.0 # Or N/A
            
            table.setItem(i, 0, QTableWidgetItem(doc_num))
            table.setItem(i, 1, QTableWidgetItem(str(doc_date)))
            table.setItem(i, 2, QTableWidgetItem(f"₹{doc_total:.2f}" if doc_total else "-"))
            table.setItem(i, 3, QTableWidgetItem(f"₹{row['amount']:.2f}"))
            
        layout.addWidget(table)
        
        if main_row['notes']:
            layout.addWidget(QLabel("<b>Notes:</b>"))
            notes = QTextEdit()
            notes.setPlainText(main_row['notes'])
            notes.setReadOnly(True)
            notes.setMaximumHeight(60)
            layout.addWidget(notes)
            
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

class RecordPaymentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Payment")
        self.resize(900, 700)
        # Enable Maximize Button
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
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
        
        # Credits Display
        self.lbl_credits = QLabel("Available Credits: ₹0.00")
        self.lbl_credits.setStyleSheet("color: green; font-weight: bold;")
        left_header.addWidget(self.lbl_credits)
        
        self.chk_use_credits = QCheckBox("Use Available Credits")
        self.chk_use_credits.setChecked(True)
        self.chk_use_credits.toggled.connect(self.update_summary)
        left_header.addWidget(self.chk_use_credits)
        
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
        
        # Notes
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
            self.lbl_credits.setText("Available Credits: ₹0.00")
            self.current_credits = 0.0
            return
            
        customer_id = self.customer_combo.currentData()
        self.invoices_data = get_unpaid_invoices(customer_id)
        
        # Fetch Credits
        self.current_credits = get_customer_credits(customer_id)
        self.lbl_credits.setText(f"Available Credits: ₹{self.current_credits:.2f}")
        
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
        
        credits_to_use = 0.0
        if self.chk_use_credits.isChecked() and hasattr(self, 'current_credits'):
            credits_to_use = self.current_credits
            
        total_available = recv + credits_to_use
        used = 0.0
        
        for r in range(self.table.rowCount()):
            spin = self.table.cellWidget(r, 4)
            if spin:
                used += spin.value()
            
        excess = total_available - used
        
        self.lbl_amount_used.setText(f"Amount Used: ₹{used:.2f}")
        self.lbl_amount_excess.setText(f"Amount Excess: ₹{excess:.2f}")
        
        if excess < 0:
             self.lbl_amount_excess.setStyleSheet("color: red;")
        else:
             self.lbl_amount_excess.setStyleSheet("color: green;")

    def auto_apply_payment(self):
        recv = self.amount_received_spin.value()
        credits_to_use = 0.0
        if self.chk_use_credits.isChecked() and hasattr(self, 'current_credits'):
            credits_to_use = self.current_credits
            
        remaining = recv + credits_to_use
        
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
        
        use_credits = self.chk_use_credits.isChecked()
        credits_available = self.current_credits if use_credits and hasattr(self, 'current_credits') else 0.0

        if recv <= 0:
            if not use_credits or credits_available <= 0:
                QMessageBox.warning(self, "Error", "Amount received must be greater than 0, or use available credits.")
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
            # Check if covered by credits
            credits_available = self.current_credits if self.chk_use_credits.isChecked() else 0.0
            if total_allocated > (recv + credits_available):
                QMessageBox.warning(self, "Error", "Total allocated amount cannot exceed amount received + credits.")
                return
            
        # Allow excess amount to be treated as credit
        # if not allocations:
        #      QMessageBox.warning(self, "Error", "Please allocate payment to at least one invoice.")
        #      return

        # Collect Custom Fields
        custom_fields_data = {}
        if hasattr(self, 'custom_fields_widgets'):
            for name, widget in self.custom_fields_widgets.items():
                custom_fields_data[name] = widget.text()

        data = {
            'customer_id': customer_id,
            'amount_received': recv,
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
            'send_thank_you': self.send_note_chk.isChecked(),
            'use_credits': self.chk_use_credits.isChecked()
        }
        
        try:
            save_payment(data)
            
            if self.send_note_chk.isChecked():
                QMessageBox.information(self, "Email", "Thank you note email queued (Simulated).")
                
            QMessageBox.information(self, "Success", "Payment recorded successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save payment: {str(e)}")
