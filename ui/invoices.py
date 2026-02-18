from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QComboBox, 
    QDateEdit, QFormLayout, QDialog, QMessageBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QCheckBox, QFileDialog, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QDesktopServices
from database.db import execute_read_query, execute_write_query
from modules.invoice import create_invoice, update_invoice
from pdf.generator import generate_invoice_pdf
from ui.payments import RecordPaymentDialog
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
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        create_btn = QPushButton("+ New Invoice")
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
            
            self.table.setCellWidget(row_idx, 5, btn_widget)

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
            folder = os.path.join(os.getcwd(), "invoices_pdf")
            if not os.path.exists(folder):
                os.makedirs(folder)
                
            filename = os.path.join(folder, f"{self.invoice_data['invoice_number']}.pdf")
            generate_invoice_pdf(self.invoice_data, filename)
            
            # Open PDF
            QDesktopServices.openUrl(QUrl.fromLocalFile(filename))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")


class CreateInvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        self.invoice_data = invoice_data
        self.setWindowTitle("Edit Invoice" if invoice_data else "Create New Invoice")
        self.setFixedSize(900, 700)
        
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
        header_form.addRow("Customer:", self.customer_combo)
        
        # Invoice # (Auto-generated usually, but user might want to see/edit order #)
        self.order_number = QLineEdit()
        header_form.addRow("Order Number:", self.order_number)
        
        # Dates
        date_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30)) # Default net 30
        self.due_date.setCalendarPopup(True)
        
        date_layout.addWidget(QLabel("Date:"))
        date_layout.addWidget(self.date_edit)
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
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(6)
        self.items_table.setHorizontalHeaderLabels(["Item", "Qty", "Rate", "Disc %", "GST %", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setMinimumHeight(200)
        
        layout.addWidget(self.items_table)
        
        # Add Item Button
        add_item_btn = QPushButton("+ Add Line Item")
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
        
        # Load available items (including flags to control sellability)
        self.available_items = execute_read_query(
            "SELECT id, name, sku, selling_price, gst_rate, is_sellable FROM items"
        )

        # Populate if editing
        if self.invoice_data:
            self.populate_data()

    def populate_data(self):
        data = self.invoice_data
        
        # Header
        idx = self.customer_combo.findData(data['customer_id'])
        if idx >= 0:
            self.customer_combo.setCurrentIndex(idx)
            
        self.order_number.setText(data.get('order_number', ''))
        self.date_edit.setDate(QDate.fromString(data['date'], "yyyy-MM-dd"))
        if data.get('due_date'):
            self.due_date.setDate(QDate.fromString(data['due_date'], "yyyy-MM-dd"))
            
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

    def load_customers(self):
        customers = execute_read_query("SELECT id, name FROM customers")
        for c in customers:
            self.customer_combo.addItem(c['name'], c['id'])

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
        
        # Default values
        if item_data:
            # Find item in combo
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
            disc_val = str(item_data['discount_percent'])
        elif self.available_items:
            first_item = self.available_items[0]
            rate = str(first_item['selling_price'])
            gst = str(first_item['gst_rate'])
            qty_val = "1"
            disc_val = "0"
        else:
            rate = "0"
            gst = "0"
            qty_val = "1"
            disc_val = "0"

        combo.currentIndexChanged.connect(lambda idx, r=row: self.on_item_changed(r))
        
        qty = QLineEdit(qty_val)
        rate_edit = QLineEdit(rate)
        disc = QLineEdit(disc_val)
        gst_edit = QLineEdit(gst)
        total = QLabel("0.00")
        
        # Connect signals to recalculate
        qty.textChanged.connect(self.calculate_total)
        rate_edit.textChanged.connect(self.calculate_total)
        disc.textChanged.connect(self.calculate_total)
        gst_edit.textChanged.connect(self.calculate_total)
        
        self.items_table.setCellWidget(row, 0, combo)
        self.items_table.setCellWidget(row, 1, qty)
        self.items_table.setCellWidget(row, 2, rate_edit)
        self.items_table.setCellWidget(row, 3, disc)
        self.items_table.setCellWidget(row, 4, gst_edit)
        self.items_table.setCellWidget(row, 5, total)
        
        self.calculate_total()

    def on_item_changed(self, row):
        combo = self.items_table.cellWidget(row, 0)
        item_data = combo.currentData()
        if item_data:
            self.items_table.cellWidget(row, 2).setText(str(item_data['selling_price']))
            self.items_table.cellWidget(row, 4).setText(str(item_data['gst_rate']))
            self.calculate_total()

    def calculate_total(self):
        grand_total = 0.0
        try:
            for row in range(self.items_table.rowCount()):
                qty = float(self.items_table.cellWidget(row, 1).text() or 0)
                rate = float(self.items_table.cellWidget(row, 2).text() or 0)
                disc = float(self.items_table.cellWidget(row, 3).text() or 0)
                gst = float(self.items_table.cellWidget(row, 4).text() or 0)
                
                amount = (rate * (1 - disc/100)) * qty
                tax = amount * (gst/100)
                line_total = amount + tax
                
                self.items_table.cellWidget(row, 5).setText(f"{line_total:.2f}")
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
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Error", "Please select a customer")
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
                rate = float(self.items_table.cellWidget(row, 2).text())
                disc = float(self.items_table.cellWidget(row, 3).text())
                gst = float(self.items_table.cellWidget(row, 4).text())
                
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
                QMessageBox.information(self, "Success", "Invoice updated successfully")
            else:
                # Create
                create_invoice(invoice_data)
                QMessageBox.information(self, "Success", "Invoice created successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")
