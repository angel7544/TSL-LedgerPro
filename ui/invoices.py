from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox, 
    QDateEdit, QFormLayout, QDialog, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QCheckBox, QFileDialog, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QDesktopServices
from database.db import execute_read_query, execute_write_query
from modules.invoice import create_invoice, update_invoice, delete_invoice
from pdf.generator import generate_invoice_pdf
from ui.payments import RecordPaymentDialog
from ui.icons import get_icon
from auth.auth_logic import log_audit_action
import datetime
import os
import json

class InvoicesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Invoices")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        
        create_btn = QPushButton(" New Invoice")
        create_btn.setIcon(get_icon("add", "#FFFFFF", 16))
        create_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        create_btn.clicked.connect(self.open_create_dialog)
        
        pay_btn = QPushButton(" Record Payment")
        pay_btn.setIcon(get_icon("payments", "#FFFFFF", 16))
        pay_btn.setStyleSheet("background-color: #10B981; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        pay_btn.clicked.connect(self.open_payment_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(pay_btn)
        header_layout.addWidget(create_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Total", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        query = """
            SELECT i.id, i.invoice_number, c.name as customer_name, i.date, i.grand_total, i.status
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
        """
        rows = execute_read_query(query)
        self.table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(row['invoice_number']))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['customer_name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['date'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"₹{row['grand_total']:.2f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row['status']))
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("View")
            view_btn.clicked.connect(lambda checked, r=row['id']: self.view_invoice(r))
            btn_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=row['id']: self.edit_invoice(r))
            btn_layout.addWidget(edit_btn)
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("color: white; background-color: #EF4444;")
            del_btn.clicked.connect(lambda checked, r=row['id']: self.delete_invoice_ui(r))
            btn_layout.addWidget(del_btn)
            
            self.table.setCellWidget(row_idx, 5, btn_widget)

    def delete_invoice_ui(self, invoice_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this invoice? This will restore stock quantities.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                delete_invoice(invoice_id)
                log_audit_action("DELETE_INVOICE", "Invoices", invoice_id, "Invoice deleted (stock restored)")
                self.refresh_data()
                QMessageBox.information(self, "Success", "Invoice deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete invoice: {str(e)}")

    def edit_invoice(self, invoice_id):
        # Fetch full details
        inv_query = "SELECT * FROM invoices WHERE id = ?"
        inv_rows = execute_read_query(inv_query, (invoice_id,))
        if not inv_rows:
            return
            
        invoice = dict(inv_rows[0])
        
        # Fetch items
        items_query = """
            SELECT ii.*, i.name as item_name, i.selling_price as list_price, i.gst_rate as list_gst
            FROM invoice_items ii
            JOIN items i ON ii.item_id = i.id
            WHERE ii.invoice_id = ?
        """
        items = execute_read_query(items_query, (invoice_id,))
        invoice['items'] = [dict(item) for item in items]
        
        dialog = CreateInvoiceDialog(self, invoice_data=invoice)
        if dialog.exec():
            self.refresh_data()

    def view_invoice(self, invoice_id):
        # Fetch full details
        inv_query = """
            SELECT i.*, c.name as customer_name, c.address as customer_address, c.gstin as customer_gstin
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
        """
        inv_rows = execute_read_query(inv_query, (invoice_id,))
        if not inv_rows:
            return
            
        invoice = inv_rows[0]
        
        # Fetch items
        items_query = """
            SELECT ii.*, i.name as item_name
            FROM invoice_items ii
            JOIN items i ON ii.item_id = i.id
            WHERE ii.invoice_id = ?
        """
        items = execute_read_query(items_query, (invoice_id,))
        
        # Construct data for PDF
        invoice_data = dict(invoice)
        invoice_data['items'] = [dict(item) for item in items]
        invoice_data['items'] = [{
            'name': i['item_name'],
            'quantity': i['quantity'],
            'rate': i['rate'],
            'discount_percent': i['discount_percent'],
            'gst_percent': i['gst_percent'],
            'amount': i['amount']
        } for i in items]
        
        # Show Dialog
        dialog = ViewInvoiceDialog(invoice_data, self)
        dialog.exec()

    def open_create_dialog(self):
        dialog = CreateInvoiceDialog(self)
        if dialog.exec():
            self.refresh_data()

    def open_payment_dialog(self):
        dialog = RecordPaymentDialog(self)
        if dialog.exec():
            self.refresh_data()

class ViewInvoiceDialog(QDialog):
    def __init__(self, invoice_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Invoice #{invoice_data['invoice_number']}")
        self.setFixedSize(600, 700)
        self.invoice_data = invoice_data
        
        # Fetch company settings for PDF and Display
        settings = execute_read_query("SELECT key, value FROM settings")
        self.settings_dict = {row['key']: row['value'] for row in settings}
        self.invoice_data.update(self.settings_dict)
        self.invoice_data['logo_path'] = self.settings_dict.get('company_logo', '')
        
        layout = QVBoxLayout()
        
        # Details Area
        details = QTextEdit()
        details.setReadOnly(True)
        
        html = f"""
        <h2>Invoice #{invoice_data['invoice_number']}</h2>
        <p><b>Date:</b> {invoice_data['date']}<br>
        <b>Due Date:</b> {invoice_data.get('due_date', '')}</p>
        <p><b>Customer:</b> {invoice_data['customer_name']}<br>
        {invoice_data['customer_address'] or ''}<br>
        GSTIN: {invoice_data.get('customer_gstin', '')}</p>
        
        <table border="1" cellspacing="0" cellpadding="5" width="100%">
            <tr>
                <th>Item</th>
                <th>Qty</th>
                <th>Rate</th>
                <th>Total</th>
            </tr>
        """
        
        for item in invoice_data['items']:
            html += f"""
            <tr>
                <td>{item['name']}</td>
                <td>{item['quantity']}</td>
                <td>{item['rate']}</td>
                <td>{item['amount']}</td>
            </tr>
            """
            
        html += f"""
        </table>
        <h3 align="right">Total: ₹{invoice_data['grand_total']:.2f}</h3>
        """
        
        # Custom Fields Display
        if invoice_data.get('custom_fields'):
            try:
                custom_fields = json.loads(invoice_data['custom_fields'])
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
        print_btn = QPushButton(" Print A4 PDF")
        print_btn.setIcon(get_icon("print", "#1E293B", 16))
        print_btn.clicked.connect(self.print_pdf)

        print_thermal_80_btn = QPushButton(" POS 80mm (Excl. GST)")
        print_thermal_80_btn.setIcon(get_icon("pos_receipt", "#1E293B", 16))
        print_thermal_80_btn.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 4px; padding: 6px 10px; font-weight: 500;")
        print_thermal_80_btn.clicked.connect(lambda: self.print_thermal(80, gst_mode='exclusive'))

        print_thermal_80_incl_btn = QPushButton(" POS 80mm (Incl. GST)")
        print_thermal_80_incl_btn.setIcon(get_icon("pos_receipt", "#1E293B", 16))
        print_thermal_80_incl_btn.setStyleSheet("background-color: #EFF6FF; border: 1px solid #93C5FD; border-radius: 4px; padding: 6px 10px; font-weight: 500; color: #1D4ED8;")
        print_thermal_80_incl_btn.clicked.connect(lambda: self.print_thermal(80, gst_mode='inclusive'))

        print_thermal_58_btn = QPushButton(" POS 58mm (Excl. GST)")
        print_thermal_58_btn.setIcon(get_icon("pos_receipt", "#1E293B", 16))
        print_thermal_58_btn.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 4px; padding: 6px 10px; font-weight: 500;")
        print_thermal_58_btn.clicked.connect(lambda: self.print_thermal(58, gst_mode='exclusive'))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(print_thermal_80_btn)
        btn_layout.addWidget(print_thermal_80_incl_btn)
        btn_layout.addWidget(print_thermal_58_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def print_pdf(self):
        try:
            from modules.printer_service import handle_print_workflow
            folder = os.path.join(os.getcwd(), "invoices_pdf")
            if not os.path.exists(folder):
                os.makedirs(folder)
                
            inv_num = self.invoice_data['invoice_number']
            filename = os.path.join(folder, f"{inv_num.replace('/', '_')}.pdf")
            generate_invoice_pdf(self.invoice_data, filename)
            
            handle_print_workflow(self, filename, doc_type="invoice", doc_title=f"Invoice #{inv_num}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")

    def print_thermal(self, width_mm, gst_mode='exclusive'):
        try:
            from pdf.thermal_generator import generate_thermal_receipt
            from modules.printer_service import handle_print_workflow
            folder = os.path.join(os.getcwd(), "invoices_pdf")
            if not os.path.exists(folder):
                os.makedirs(folder)

            # Inject gst_mode into invoice_data copy
            data = dict(self.invoice_data)
            data['gst_mode'] = gst_mode

            mode_tag = 'incl' if gst_mode == 'inclusive' else 'excl'
            inv_clean = data['invoice_number'].replace('/', '_')
            filename = os.path.join(folder, f"receipt_{inv_clean}_{width_mm}mm_{mode_tag}.pdf")
            generate_thermal_receipt(data, paper_width_mm=width_mm, output_path=filename)

            doc_type_key = f"thermal_{width_mm}"
            handle_print_workflow(self, filename, doc_type=doc_type_key,
                                  doc_title=f"POS Receipt ({width_mm}mm {gst_mode}) #{data['invoice_number']}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate POS Receipt: {str(e)}")


class CreateInvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.setWindowTitle("Edit Invoice" if invoice_data else "Create New Invoice")
        self.resize(1150, 750)
        # Enable Maximize Button
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        
        main_layout = QVBoxLayout()
        
        # Scroll Area for long form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # --- Header Section ---
        header_form = QFormLayout()
        
        # Customer
        self.customer_combo = QComboBox()
        self.load_customers()
        self.customer_combo.currentIndexChanged.connect(self.on_customer_changed)
        header_form.addRow("Customer:", self.customer_combo)
        
        # Invoice # (Auto-generated usually, but user might want to see/edit order #)
        self.order_number = QLineEdit()
        header_form.addRow("Order Number:", self.order_number)
        
        # Dates & Due Date Presets (10, 15, 45 days, etc.)
        date_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.on_date_changed)
        
        self.due_preset_combo = QComboBox()
        self.due_preset_combo.addItem("Due on Receipt (0 Days)", 0)
        self.due_preset_combo.addItem("Net 7 Days", 7)
        self.due_preset_combo.addItem("Net 10 Days", 10)
        self.due_preset_combo.addItem("Net 15 Days", 15)
        self.due_preset_combo.addItem("Net 30 Days", 30)
        self.due_preset_combo.addItem("Net 45 Days", 45)
        self.due_preset_combo.addItem("Net 60 Days", 60)
        self.due_preset_combo.addItem("Custom Date", -1)
        self.due_preset_combo.setCurrentIndex(4) # Default Net 30
        self.due_preset_combo.currentIndexChanged.connect(self.on_due_preset_changed)
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30)) # Default net 30
        self.due_date.setCalendarPopup(True)
        self.due_date.dateChanged.connect(self.on_due_date_manual_changed)
        
        date_layout.addWidget(QLabel("Date:"))
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(QLabel("Payment Terms:"))
        date_layout.addWidget(self.due_preset_combo)
        date_layout.addWidget(QLabel("Due Date:"))
        date_layout.addWidget(self.due_date)
        header_form.addRow(date_layout)
        
        # Terms & Salesperson
        row2 = QHBoxLayout()
        self.terms = QLineEdit()
        self.salesperson = QLineEdit()
        row2.addWidget(QLabel("Terms:"))
        row2.addWidget(self.terms)
        row2.addWidget(QLabel("Salesperson:"))
        row2.addWidget(self.salesperson)
        header_form.addRow(row2)
        
        # Subject
        self.subject = QLineEdit()
        self.subject.setPlaceholderText("Let your customer know what this Invoice is for")
        header_form.addRow("Subject:", self.subject)
        
        layout.addLayout(header_form)
        
        # --- Items Table ---
        # Add an Info button for Rate Types
        info_layout = QHBoxLayout()
        info_layout.addStretch()
        info_btn = QPushButton(" Rate Types Info")
        info_btn.setIcon(get_icon("info", "#2563EB", 14))
        info_btn.setStyleSheet("background-color: transparent; color: #2563EB; text-decoration: underline; border: none; font-size: 12px; font-weight: bold;")
        info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        info_btn.clicked.connect(self.show_rate_types_info)
        info_layout.addWidget(info_btn)
        layout.addLayout(info_layout)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels(["Item", "Qty", "Rate Type", "Rate", "Disc %", "GST %", "Total", "Action"])
        
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.items_table.setColumnWidth(0, 320)
        self.items_table.setMinimumHeight(220)
        
        layout.addWidget(self.items_table)
        
        # Add Item Button
        add_item_btn = QPushButton(" Add Line Item")
        add_item_btn.setIcon(get_icon("add", "#2563EB", 16))
        add_item_btn.setStyleSheet("color: #2563EB; font-weight: bold; padding: 6px 12px; border: 1px solid #CBD5E1; border-radius: 4px; background: white;")
        add_item_btn.clicked.connect(self.add_item_row)
        layout.addWidget(add_item_btn)
        
        # --- Footer Section ---
        footer_layout = QHBoxLayout()
        
        # Left Side (Notes, Terms)
        left_footer = QVBoxLayout()
        
        left_footer.addWidget(QLabel("Customer Notes"))
        self.customer_notes = QTextEdit()
        self.customer_notes.setPlaceholderText("Thanks for your business.")
        self.customer_notes.setMaximumHeight(60)
        left_footer.addWidget(self.customer_notes)
        
        left_footer.addWidget(QLabel("Terms & Conditions"))
        self.terms_conditions = QTextEdit()
        self.terms_conditions.setPlaceholderText("Enter the terms and conditions...")
        self.terms_conditions.setMaximumHeight(60)
        left_footer.addWidget(self.terms_conditions)
        
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
        self.tds_amount = QDoubleSpinBox()
        self.tds_amount.setRange(0, 1000000)
        self.tds_amount.setPrefix("- ")
        
        self.tcs_amount = QDoubleSpinBox()
        self.tcs_amount.setRange(0, 1000000)
        self.tcs_amount.setPrefix("+ ")
        
        self.adjustment = QDoubleSpinBox()
        self.adjustment.setRange(-1000000, 1000000)
        self.adjustment.setPrefix("₹")
        self.adjustment.setToolTip("Adjustment (+/-)")

        self.round_off = QDoubleSpinBox()
        self.round_off.setRange(-10, 10)
        
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        right_footer.addRow("Sub Total:", self.subtotal_label)
        right_footer.addRow("TDS:", self.tds_amount)
        right_footer.addRow("TCS:", self.tcs_amount)
        right_footer.addRow("Adjustment:", self.adjustment)
        right_footer.addRow("Round Off:", self.round_off)
        right_footer.addRow("", self.total_label)
        
        # Connect signals for grand total calc
        self.tds_amount.valueChanged.connect(self.calculate_final_total)
        self.tcs_amount.valueChanged.connect(self.calculate_final_total)
        self.adjustment.valueChanged.connect(self.calculate_final_total)
        self.round_off.valueChanged.connect(self.calculate_final_total)
        
        footer_layout.addLayout(right_footer, stretch=1)
        
        layout.addLayout(footer_layout)
        
        # Set scroll widget
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Update Invoice" if self.invoice_data else "Save Invoice")
        save_btn.clicked.connect(self.save_invoice)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        
        self.items_data = [] 
        self.calculated_subtotal = 0.0 # Store for final calc
        self.custom_fields_widgets = {}
        self.load_custom_fields_ui(layout)
        
        # Load available items (including flags to control sellability)
        self.available_items = execute_read_query(
            "SELECT id, name, sku, selling_price, sp1, sp2, sp3, gst_rate, is_sellable FROM items"
        )

        if self.invoice_data:
            self.populate_data()
        else:
            self.add_item_row()

    def on_due_preset_changed(self):
        days = self.due_preset_combo.currentData()
        if days is not None and days >= 0:
            inv_date = self.date_edit.date()
            calc_due = inv_date.addDays(days)
            self.due_date.blockSignals(True)
            self.due_date.setDate(calc_due)
            self.due_date.blockSignals(False)

    def on_date_changed(self):
        self.on_due_preset_changed()

    def on_due_date_manual_changed(self):
        inv_date = self.date_edit.date()
        due_d = self.due_date.date()
        diff_days = inv_date.daysTo(due_d)
        
        idx = self.due_preset_combo.findData(diff_days)
        self.due_preset_combo.blockSignals(True)
        if idx >= 0:
            self.due_preset_combo.setCurrentIndex(idx)
        else:
            cust_idx = self.due_preset_combo.findData(-1)
            if cust_idx >= 0:
                self.due_preset_combo.setCurrentIndex(cust_idx)
        self.due_preset_combo.blockSignals(False)

    def populate_data(self):
        data = self.invoice_data
        
        # Header
        idx = self.customer_combo.findData(data['customer_id'])
        if idx >= 0:
            self.customer_combo.setCurrentIndex(idx)
            
        self.order_number.setText(data.get('order_number', ''))
        
        date_val = data['date']
        if isinstance(date_val, datetime.date):
            date_val = date_val.strftime("%Y-%m-%d")
        self.date_edit.setDate(QDate.fromString(str(date_val), "yyyy-MM-dd"))
        
        due_date_val = data.get('due_date')
        if due_date_val:
            if isinstance(due_date_val, datetime.date):
                due_date_val = due_date_val.strftime("%Y-%m-%d")
            self.due_date.setDate(QDate.fromString(str(due_date_val), "yyyy-MM-dd"))
            
        self.terms.setText(data.get('terms', ''))
        self.salesperson.setText(data.get('salesperson', ''))
        self.subject.setText(data.get('subject', ''))
        
        # Footer
        self.customer_notes.setText(data.get('customer_notes', ''))
        self.terms_conditions.setText(data.get('terms_conditions', ''))
        self.tds_amount.setValue(data.get('tds_amount', 0.0))
        self.tcs_amount.setValue(data.get('tcs_amount', 0.0))
        self.adjustment.setValue(data.get('adjustment', 0.0))
        self.round_off.setValue(data.get('round_off', 0.0))
        
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
        self.calculate_total()
            
    def load_custom_fields_ui(self, parent_layout):
        """Loads custom fields from settings and adds them to the UI."""
        settings = execute_read_query("SELECT value FROM settings WHERE key='custom_fields_invoice'")
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

    def show_rate_types_info(self):
        settings_rows = execute_read_query("SELECT `key`, value FROM settings WHERE `key` IN ('sp1_name', 'sp2_name', 'sp3_name')")
        settings_dict = {row['key']: row['value'] for row in settings_rows}
        sp1 = settings_dict.get('sp1_name', 'Type 1')
        sp2 = settings_dict.get('sp2_name', 'Type 2')
        sp3 = settings_dict.get('sp3_name', 'Type 3')
        msg = f"Rate Types defined in Settings:\n\nType 1: {sp1}\nType 2: {sp2}\nType 3: {sp3}"
        QMessageBox.information(self, "Rate Types Info", msg)

    def get_customer_price(self, item_data):
        if not item_data: return 0.0
        cust_data = self.customer_combo.currentData()
        if not cust_data: return item_data.get('selling_price', 0.0)
        
        c_type = cust_data.get('customer_type', 'Type 1')
        
        # Get custom names from settings
        settings_rows = execute_read_query("SELECT `key`, value FROM settings WHERE `key` IN ('sp1_name', 'sp2_name', 'sp3_name')")
        settings_dict = {row['key']: row['value'] for row in settings_rows}
        sp1_name = settings_dict.get('sp1_name', 'Type 1')
        sp2_name = settings_dict.get('sp2_name', 'Type 2')
        sp3_name = settings_dict.get('sp3_name', 'Type 3')
        
        if c_type == 'Type 1' or c_type == sp1_name: return item_data.get('sp1', item_data.get('selling_price', 0.0))
        elif c_type == 'Type 2' or c_type == sp2_name: return item_data.get('sp2', item_data.get('selling_price', 0.0))
        elif c_type == 'Type 3' or c_type == sp3_name: return item_data.get('sp3', item_data.get('selling_price', 0.0))
        return item_data.get('selling_price', 0.0)

    def on_customer_changed(self):
        # Update rate types for all currently added items
        cust_data = self.customer_combo.currentData()
        c_type = cust_data.get('customer_type', 'Type 1') if cust_data else 'Default'
        
        settings_rows = execute_read_query("SELECT `key`, value FROM settings WHERE `key` IN ('sp1_name', 'sp2_name', 'sp3_name')")
        settings_dict = {row['key']: row['value'] for row in settings_rows}
        sp1 = settings_dict.get('sp1_name', 'Type 1')
        sp2 = settings_dict.get('sp2_name', 'Type 2')
        sp3 = settings_dict.get('sp3_name', 'Type 3')
        
        for row in range(self.items_table.rowCount()):
            rate_type_combo = self.items_table.cellWidget(row, 2)
            if rate_type_combo:
                # Block signals to avoid double recalculation
                rate_type_combo.blockSignals(True)
                if c_type == 'Type 1' or c_type == sp1:
                    rate_type_combo.setCurrentIndex(1)
                elif c_type == 'Type 2' or c_type == sp2:
                    rate_type_combo.setCurrentIndex(2)
                elif c_type == 'Type 3' or c_type == sp3:
                    rate_type_combo.setCurrentIndex(3)
                else:
                    rate_type_combo.setCurrentIndex(0)
                rate_type_combo.blockSignals(False)
                
            combo = self.items_table.cellWidget(row, 0)
            item_data = combo.currentData()
            if item_data and rate_type_combo:
                rate_field = rate_type_combo.currentData()
                new_price = item_data.get(rate_field, item_data.get('selling_price', 0.0))
                self.items_table.cellWidget(row, 3).setText(str(new_price))
        self.calculate_total()

    def load_customers(self):
        customers = execute_read_query("SELECT id, name, customer_type FROM customers")
        for c in customers:
            self.customer_combo.addItem(c['name'], {'id': c['id'], 'customer_type': c.get('customer_type', 'Type 1')})

    def add_item_row(self, item_data=None):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setRowHeight(row, 38)
        
        combo_style = """
            QComboBox {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 13px;
                color: #0F172A;
                min-height: 26px;
            }
            QComboBox QAbstractItemView {
                min-width: 360px;
                background-color: white;
                selection-background-color: #2563EB;
                selection-color: white;
            }
        """
        line_edit_style = """
            QLineEdit {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 13px;
                color: #0F172A;
                min-height: 26px;
            }
        """
        
        # Item Combo
        combo = QComboBox()
        combo.setStyleSheet(combo_style)
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        for item in self.available_items:
            name = item['name']
            sku_text = ""
            if 'sku' in item.keys() and item['sku']:
                sku_text = f" ({item['sku']})"
            is_sellable = 1
            if 'is_sellable' in item.keys():
                try:
                    is_sellable = int(item['is_sellable'])
                except (ValueError, TypeError):
                    is_sellable = 1
            display_text = f"{name}{sku_text}"
            if not is_sellable:
                display_text = f"{display_text} [NOT SELLABLE]"
            combo.addItem(display_text, item)
            if not is_sellable:
                idx_added = combo.count() - 1
                combo.setItemData(idx_added, Qt.red, Qt.ForegroundRole)
        
        # Rate Type Combo
        rate_type_combo = QComboBox()
        rate_type_combo.setStyleSheet(combo_style)
        settings_rows = execute_read_query("SELECT `key`, value FROM settings WHERE `key` IN ('sp1_name', 'sp2_name', 'sp3_name')")
        settings_dict = {row['key']: row['value'] for row in settings_rows}
        sp1 = settings_dict.get('sp1_name', 'Type 1')
        sp2 = settings_dict.get('sp2_name', 'Type 2')
        sp3 = settings_dict.get('sp3_name', 'Type 3')
        
        rate_type_combo.addItem("Default", "selling_price")
        rate_type_combo.addItem(f"SP1 ({sp1})", "sp1")
        rate_type_combo.addItem(f"SP2 ({sp2})", "sp2")
        rate_type_combo.addItem(f"SP3 ({sp3})", "sp3")
        
        # Set default to Customer's Type if possible
        cust_data = self.customer_combo.currentData()
        c_type = cust_data.get('customer_type', 'Type 1') if cust_data else 'Default'
        if c_type == 'Type 1' or c_type == sp1:
            rate_type_combo.setCurrentIndex(1)
        elif c_type == 'Type 2' or c_type == sp2:
            rate_type_combo.setCurrentIndex(2)
        elif c_type == 'Type 3' or c_type == sp3:
            rate_type_combo.setCurrentIndex(3)
        else:
            rate_type_combo.setCurrentIndex(0)
 
        rate_type_combo.currentIndexChanged.connect(self.on_rate_type_changed)

        # Default values
        if item_data:
            # Robust Item Lookup & Fallback Addition
            idx = -1
            target_id = None
            if 'item_id' in item_data and item_data['item_id'] is not None:
                try: target_id = int(item_data['item_id'])
                except (ValueError, TypeError): pass
            elif 'id' in item_data and item_data['id'] is not None:
                try: target_id = int(item_data['id'])
                except (ValueError, TypeError): pass

            if target_id is not None:
                for i in range(combo.count()):
                    item_obj = combo.itemData(i)
                    if item_obj and 'id' in item_obj:
                        try:
                            if int(item_obj['id']) == target_id:
                                idx = i
                                break
                        except (ValueError, TypeError):
                            pass
                            
            if idx < 0 and target_id is not None:
                item_name = item_data.get('item_name', item_data.get('name', f"Item #{target_id}"))
                combo.addItem(item_name, {'id': target_id, 'name': item_name, 'selling_price': item_data.get('rate', 0.0), 'gst_rate': item_data.get('gst_percent', 0.0)})
                idx = combo.count() - 1
            
            combo.blockSignals(True)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            combo.blockSignals(False)
            
            rate = str(item_data['rate'])
            gst = str(item_data['gst_percent'])
            qty_val = str(item_data['quantity'])
            disc_val = str(item_data['discount_percent'])
            
            rate_type_combo.blockSignals(True)
            rate_type_combo.setCurrentIndex(0)
            rate_type_combo.blockSignals(False)
            
        elif self.available_items:
            first_item = self.available_items[0]
            rate = str(self.get_customer_price(first_item))
            gst = str(first_item['gst_rate'])
            qty_val = "1"
            disc_val = "0"
        else:
            rate = "0"
            gst = "0"
            qty_val = "1"
            disc_val = "0"

        combo.currentIndexChanged.connect(self.on_item_changed)
        
        qty = QLineEdit(qty_val)
        qty.setStyleSheet(line_edit_style)
        rate_edit = QLineEdit(rate)
        rate_edit.setStyleSheet(line_edit_style)
        disc = QLineEdit(disc_val)
        disc.setStyleSheet(line_edit_style)
        gst_edit = QLineEdit(gst)
        gst_edit.setStyleSheet(line_edit_style)
        
        total = QLabel("0.00")
        total.setStyleSheet("font-size: 13px; font-weight: bold; color: #0F172A;")
        
        # Connect signals to recalculate
        qty.textChanged.connect(self.calculate_total)
        rate_edit.textChanged.connect(self.calculate_total)
        disc.textChanged.connect(self.calculate_total)
        gst_edit.textChanged.connect(self.calculate_total)
        
        self.items_table.setCellWidget(row, 0, combo)
        self.items_table.setCellWidget(row, 1, qty)
        self.items_table.setCellWidget(row, 2, rate_type_combo)
        self.items_table.setCellWidget(row, 3, rate_edit)
        self.items_table.setCellWidget(row, 4, disc)
        self.items_table.setCellWidget(row, 5, gst_edit)
        self.items_table.setCellWidget(row, 6, total)
        
        # Remove Button
        remove_btn = QPushButton("")
        remove_btn.setIcon(get_icon("delete", "#EF4444", 16))
        remove_btn.setToolTip("Remove Item Row")
        remove_btn.setStyleSheet("border: none; background: transparent; padding: 4px;")
        remove_btn.clicked.connect(self.remove_item_row)
        self.items_table.setCellWidget(row, 7, remove_btn)
        
        self.calculate_total()

    def remove_item_row(self):
        row = self.get_sender_row()
        if row >= 0:
            self.items_table.removeRow(row)
            self.calculate_total()

    def get_sender_row(self):
        sender = self.sender()
        if not sender: return -1
        
        # Try finding by position first (faster)
        pos = sender.parent().mapTo(self.items_table.viewport(), sender.pos())
        index = self.items_table.indexAt(pos)
        if index.isValid():
            return index.row()
            
        # Fallback search
        for r in range(self.items_table.rowCount()):
            for c in range(self.items_table.columnCount()):
                if self.items_table.cellWidget(r, c) == sender:
                    return r
        return -1

    def on_rate_type_changed(self):
        row = self.get_sender_row()
        if row < 0: return
        
        combo = self.items_table.cellWidget(row, 0)
        item_data = combo.currentData()
        if item_data:
            rate_type_combo = self.items_table.cellWidget(row, 2)
            rate_field = rate_type_combo.currentData()
            new_price = item_data.get(rate_field, item_data.get('selling_price', 0.0))
            self.items_table.cellWidget(row, 3).setText(str(new_price))
            self.calculate_total()

    def on_item_changed(self):
        row = self.get_sender_row()
        if row < 0: return
        
        combo = self.items_table.cellWidget(row, 0)
        item_data = combo.currentData()
        if item_data:
            rate_type_combo = self.items_table.cellWidget(row, 2)
            rate_field = rate_type_combo.currentData()
            new_price = item_data.get(rate_field, item_data.get('selling_price', 0.0))
            self.items_table.cellWidget(row, 3).setText(str(new_price))
            self.items_table.cellWidget(row, 5).setText(str(item_data['gst_rate']))
            self.calculate_total()

    def calculate_total(self):
        grand_total = 0.0
        for row in range(self.items_table.rowCount()):
            try:
                qty_w = self.items_table.cellWidget(row, 1)
                rate_w = self.items_table.cellWidget(row, 3)
                disc_w = self.items_table.cellWidget(row, 4)
                gst_w = self.items_table.cellWidget(row, 5)
                total_w = self.items_table.cellWidget(row, 6)
                
                if not (qty_w and rate_w and disc_w and gst_w and total_w): continue
                
                qty = float(qty_w.text() or 0)
                rate = float(rate_w.text() or 0)
                disc = float(disc_w.text() or 0)
                gst = float(gst_w.text() or 0)
                
                amount = (rate * (1 - disc/100)) * qty
                tax = amount * (gst/100)
                line_total = amount + tax
                
                total_w.setText(f"{line_total:.2f}")
                grand_total += line_total
            except ValueError:
                pass
            
        self.calculated_subtotal = grand_total
        self.subtotal_label.setText(f"{grand_total:.2f}")
        self.calculate_final_total()

    def calculate_final_total(self):
        total = self.calculated_subtotal
        total -= self.tds_amount.value()
        total += self.tcs_amount.value()
        total += self.adjustment.value()
        total += self.round_off.value()
        self.total_label.setText(f"Total: ₹{total:.2f}")

    def attach_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Attachment", "", "All Files (*)")
        if path:
            self.attachment_path = path
            self.attach_label.setText(os.path.basename(path))

    def save_invoice(self):
        customer_data = self.customer_combo.currentData()
        if not customer_data:
            QMessageBox.warning(self, "Error", "Please select a customer")
            return
        customer_id = customer_data['id']
            
        items = []
        for row in range(self.items_table.rowCount()):
            combo = self.items_table.cellWidget(row, 0)
            idx = combo.currentIndex()
            if idx < 0:
                continue
            item_data = combo.itemData(idx)
            if not item_data:
                continue
            is_sellable = 1
            if 'is_sellable' in item_data.keys():
                try:
                    is_sellable = int(item_data['is_sellable'])
                except (ValueError, TypeError):
                    is_sellable = 1
            if not is_sellable:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Item '{item_data['name']}' is marked as not inactive(sellable) in Items."
                )
                return
                
            try:
                qty = float(self.items_table.cellWidget(row, 1).text())
                rate = float(self.items_table.cellWidget(row, 3).text())
                disc = float(self.items_table.cellWidget(row, 4).text())
                gst = float(self.items_table.cellWidget(row, 5).text())
                
                items.append({
                    "item_id": item_data['id'],
                    "quantity": qty,
                    "rate": rate,
                    "discount_percent": disc,
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

        invoice_data = {
            "customer_id": customer_id,
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "due_date": self.due_date.date().toString("yyyy-MM-dd"),
            "items": items,
            "order_number": self.order_number.text(),
            "terms": self.terms.text(),
            "salesperson": self.salesperson.text(),
            "subject": self.subject.text(),
            "customer_notes": self.customer_notes.toPlainText(),
            "terms_conditions": self.terms_conditions.toPlainText(),
            "tds_amount": self.tds_amount.value(),
            "tcs_amount": self.tcs_amount.value(),
            "adjustment": self.adjustment.value(),
            "round_off": self.round_off.value(),
            "attachment_path": self.attachment_path,
            "custom_fields": json.dumps(custom_fields_data)
        }
        
        try:
            if self.invoice_data:
                # Update
                invoice_data['status'] = self.invoice_data.get('status', 'Due') # Preserve status or default
                update_invoice(self.invoice_data['id'], invoice_data)
                log_audit_action("UPDATE_INVOICE", "Invoices", self.invoice_data['id'], f"Invoice #{self.invoice_data.get('invoice_number')} updated")
                QMessageBox.information(self, "Success", "Invoice updated successfully")
            else:
                # Create
                new_inv_id = create_invoice(invoice_data)
                log_audit_action("CREATE_INVOICE", "Invoices", new_inv_id or "", f"New invoice created for customer ID {customer_id}")
                QMessageBox.information(self, "Success", "Invoice created successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")
