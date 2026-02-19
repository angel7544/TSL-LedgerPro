from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QFormLayout, QMessageBox, QFileDialog, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QDialog,
    QDialogButtonBox, QGroupBox
)
from PySide6.QtCore import Qt
from database.db import execute_read_query, execute_write_query
from auth.auth_logic import update_password, check_password
from auth.session import Session
import shutil
import datetime
import os
import json

from PySide6.QtGui import QPixmap

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        # --- Tab 1: Company Profile ---
        self.profile_tab = QWidget()
        self.init_profile_tab()
        self.tabs.addTab(self.profile_tab, "Company Profile")
        
        # --- Tab 2: Security ---
        self.security_tab = QWidget()
        self.init_security_tab()
        self.tabs.addTab(self.security_tab, "Security")
        
        # --- Tab 3: Custom Fields ---
        self.custom_fields_tab = QWidget()
        self.init_custom_fields_tab()
        self.tabs.addTab(self.custom_fields_tab, "Custom Fields")
        
        # --- Tab 4: Database ---
        self.database_tab = QWidget()
        self.init_database_tab()
        self.tabs.addTab(self.database_tab, "Database")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
        self.load_settings()

    def init_profile_tab(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.company_name = QLineEdit()
        self.gstin = QLineEdit()
        self.address = QLineEdit()
        self.state = QLineEdit()
        self.website = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.invoice_prefix = QLineEdit()
        self.payment_prefix = QLineEdit()
        
        # Logo Section
        self.logo_path = ""
        self.logo_label = QLabel("No Logo Selected")
        self.logo_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setFixedSize(150, 80) # Fixed size for preview area
        
        self.logo_btn = QPushButton("Upload Logo")
        self.logo_btn.clicked.connect(self.upload_logo)
        
        form_layout.addRow("Company Name:", self.company_name)
        form_layout.addRow("GSTIN:", self.gstin)
        form_layout.addRow("Address:", self.address)
        form_layout.addRow("State:", self.state)
        form_layout.addRow("Website:", self.website)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Phone:", self.phone)
        form_layout.addRow("Invoice Prefix:", self.invoice_prefix)
        form_layout.addRow("Payment Prefix:", self.payment_prefix)
        form_layout.addRow("Logo:", self.logo_btn)
        form_layout.addRow("", self.logo_label)
        
        save_btn = QPushButton("Save Profile")
        save_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 10px; border-radius: 6px;")
        save_btn.clicked.connect(self.save_profile)
        
        layout.addLayout(form_layout)
        layout.addWidget(save_btn)
        layout.addStretch()
        self.profile_tab.setLayout(layout)

    def init_security_tab(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Current Password:", self.current_password)
        form_layout.addRow("New Password:", self.new_password)
        form_layout.addRow("Confirm Password:", self.confirm_password)
        
        change_btn = QPushButton("Update Password")
        change_btn.setStyleSheet("background-color: #DC2626; color: white; padding: 10px; border-radius: 6px;")
        change_btn.clicked.connect(self.change_password)
        
        layout.addLayout(form_layout)
        layout.addWidget(change_btn)
        layout.addStretch()
        self.security_tab.setLayout(layout)

    def init_custom_fields_tab(self):
        layout = QVBoxLayout()
        
        # Module Selector
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("Select Module:"))
        self.module_combo = QComboBox()
        self.module_combo.addItems(["Invoices", "Bills", "Payments"])
        self.module_combo.currentIndexChanged.connect(self.load_custom_fields)
        top_layout.addWidget(self.module_combo)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Fields Table
        self.fields_table = QTableWidget()
        self.fields_table.setColumnCount(3)
        self.fields_table.setHorizontalHeaderLabels(["Field Name", "Type", "Default Value"])
        self.fields_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.fields_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Field")
        add_btn.clicked.connect(self.add_custom_field_row)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_custom_field_row)
        save_fields_btn = QPushButton("Save Fields")
        save_fields_btn.setStyleSheet("background-color: #2563EB; color: white;")
        save_fields_btn.clicked.connect(self.save_custom_fields)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_fields_btn)
        
        layout.addLayout(btn_layout)
        self.custom_fields_tab.setLayout(layout)

    def init_database_tab(self):
        layout = QVBoxLayout()
        
        # Backup / Restore
        backup_group = QGroupBox("Backup & Restore")
        backup_layout = QVBoxLayout()
        
        backup_btn = QPushButton("Backup Database (Export)")
        backup_btn.clicked.connect(self.backup_db)
        
        import_btn = QPushButton("Import Database (Restore)")
        import_btn.setStyleSheet("background-color: #F59E0B; color: white;")
        import_btn.clicked.connect(self.import_db)
        
        backup_layout.addWidget(backup_btn)
        backup_layout.addWidget(import_btn)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Danger Zone
        danger_group = QGroupBox("Danger Zone")
        danger_layout = QVBoxLayout()
        
        clear_inv_btn = QPushButton("Clear All Invoices")
        clear_inv_btn.setStyleSheet("color: red;")
        clear_inv_btn.clicked.connect(self.clear_invoices)
        
        clear_bill_btn = QPushButton("Clear All Bills (Purchases)")
        clear_bill_btn.setStyleSheet("color: red;")
        clear_bill_btn.clicked.connect(self.clear_bills)
        
        clear_pay_btn = QPushButton("Clear All Payments")
        clear_pay_btn.setStyleSheet("color: red;")
        clear_pay_btn.clicked.connect(self.clear_payments)
        
        reset_btn = QPushButton("Reset Entire Database")
        reset_btn.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 10px;")
        reset_btn.clicked.connect(self.reset_db)
        
        danger_layout.addWidget(clear_inv_btn)
        danger_layout.addWidget(clear_bill_btn)
        danger_layout.addWidget(clear_pay_btn)
        danger_layout.addWidget(reset_btn)
        danger_group.setLayout(danger_layout)
        layout.addWidget(danger_group)
        
        layout.addStretch()
        self.database_tab.setLayout(layout)

    def import_db(self):
        from database.db import DB_NAME
        
        confirm = QMessageBox.question(
            self, "Confirm Restore", 
            "Restoring a database will OVERWRITE the current database. All current data will be lost. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "SQLite Database (*.db);;All Files (*)")
        if file_path:
            try:
                # Close current connection if possible? 
                # SQLite usually allows overwriting if no active transaction lock.
                # But safer to just copy.
                shutil.copy(file_path, DB_NAME)
                QMessageBox.information(self, "Success", "Database restored successfully. Please restart the application.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore database: {str(e)}")

    def clear_invoices(self):
        confirm = QMessageBox.question(self, "Confirm", "Delete ALL Invoices? This cannot be undone.\n\nWARNING: Stock quantities will NOT be restored. Use this only if you want to clear sales history but keep current stock levels, or if you plan to reset stock separately.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                execute_write_query("DELETE FROM invoice_items")
                execute_write_query("DELETE FROM invoices")
                # Also need to clear invoice_id from payments or delete those payments?
                # Ideally we should delete payments associated with invoices.
                execute_write_query("DELETE FROM payments WHERE invoice_id IS NOT NULL")
                QMessageBox.information(self, "Success", "All invoices and related payments deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def clear_bills(self):
        confirm = QMessageBox.question(self, "Confirm", "Delete ALL Bills? This cannot be undone.\n\nWARNING: Stock quantities will NOT be reduced. You will retain stock added by these bills.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                execute_write_query("DELETE FROM bill_items")
                execute_write_query("DELETE FROM bills")
                # Delete payments associated with bills
                execute_write_query("DELETE FROM payments WHERE bill_id IS NOT NULL")
                QMessageBox.information(self, "Success", "All bills and related payments deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def clear_payments(self):
        confirm = QMessageBox.question(self, "Confirm", "Delete ALL Payments? This cannot be undone.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                execute_write_query("DELETE FROM payments")
                # Reset invoice/bill statuses?
                # Yes, if payments are gone, invoices are likely Due/Sent.
                execute_write_query("UPDATE invoices SET status = 'Sent' WHERE status = 'Paid'")
                execute_write_query("UPDATE bills SET status = 'Sent' WHERE status = 'Paid'")
                QMessageBox.information(self, "Success", "All payments deleted. Invoice/Bill statuses updated.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


    def backup_db(self):
        from database.db import DB_NAME
        if not os.path.exists(DB_NAME):
            QMessageBox.warning(self, "Error", "Database file not found.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Backup", f"backup_{datetime.date.today()}.db", "SQLite Database (*.db)")
        if file_path:
            try:
                shutil.copy(DB_NAME, file_path)
                QMessageBox.information(self, "Success", "Backup created successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to backup database: {str(e)}")

    def reset_db(self):
        confirm = QMessageBox.question(
            self, "DANGER: Reset Database", 
            "Are you sure you want to RESET the database? This will delete ALL data (Invoices, Bills, Payments, Customers, etc.) permanently. This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # Confirm again
            confirm2 = QMessageBox.question(
                self, "Confirm Reset", 
                "Really? All data will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm2 == QMessageBox.StandardButton.Yes:
                from database.db import DB_NAME, init_db
                try:
                    if os.path.exists(DB_NAME):
                        os.remove(DB_NAME)
                    
                    init_db()
                    QMessageBox.information(self, "Success", "Database has been reset. Please restart the application.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to reset database: {str(e)}")

    def load_settings(self):
        settings = execute_read_query("SELECT key, value FROM settings")
        self.settings_data = {row['key']: row['value'] for row in settings}
        
        # Profile
        self.company_name.setText(self.settings_data.get('company_name', ''))
        self.gstin.setText(self.settings_data.get('company_gstin', ''))
        self.address.setText(self.settings_data.get('company_address', ''))
        self.state.setText(self.settings_data.get('company_state', ''))
        self.website.setText(self.settings_data.get('company_website', ''))
        self.email.setText(self.settings_data.get('company_email', ''))
        self.phone.setText(self.settings_data.get('company_phone', ''))
        self.invoice_prefix.setText(self.settings_data.get('invoice_prefix', 'INV-'))
        self.payment_prefix.setText(self.settings_data.get('payment_prefix', 'PAY-'))
        
        logo = self.settings_data.get('company_logo', '')
        if logo and os.path.exists(logo):
            self.logo_path = logo
            # Show Preview
            pix = QPixmap(logo).scaled(140, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pix)
            self.logo_label.setText("") # Clear text
        else:
            self.logo_label.setText("No Logo Selected")
            self.logo_label.clear()
            self.logo_label.setText("No Logo Selected")
            
        # Custom Fields
        self.load_custom_fields()

    def upload_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            assets_dir = "assets"
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)
            
            filename = os.path.basename(file_path)
            dest_path = os.path.join(assets_dir, filename)
            
            try:
                shutil.copy(file_path, dest_path)
                self.logo_path = dest_path
                
                # Show Preview
                pix = QPixmap(dest_path).scaled(140, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_label.setPixmap(pix)
                self.logo_label.setText("")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload logo: {str(e)}")

    def save_profile(self):
        try:
            updates = [
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_name', self.company_name.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_gstin', self.gstin.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_address', self.address.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_state', self.state.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_website', self.website.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_email', self.email.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_phone', self.phone.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('invoice_prefix', self.invoice_prefix.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('payment_prefix', self.payment_prefix.text())),
                ("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('company_logo', self.logo_path))
            ]
            for query, params in updates:
                execute_write_query(query, params)
            
            # Refresh local data
            self.load_settings()
            QMessageBox.information(self, "Success", "Profile settings saved!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def change_password(self):
        current = self.current_password.text()
        new_pass = self.new_password.text()
        confirm = self.confirm_password.text()
        
        if not current or not new_pass or not confirm:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
            
        if new_pass != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
            
        user = Session.get_instance().get_user()
        if not user:
            QMessageBox.critical(self, "Error", "User session not found. Please login again.")
            return

        # Verify current password
        # Need to fetch latest hash from DB to be safe
        user_db = execute_read_query("SELECT password_hash FROM users WHERE id = ?", (user['id'],))
        if not user_db:
             QMessageBox.critical(self, "Error", "User not found in database.")
             return
             
        if not check_password(current, user_db[0]['password_hash']):
            QMessageBox.critical(self, "Error", "Current password is incorrect")
            return
            
        if update_password(user['id'], new_pass):
            QMessageBox.information(self, "Success", "Password updated successfully!")
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to update password")

    def load_custom_fields(self):
        module = self.module_combo.currentText().lower() # invoices, bills, payments
        if module == "invoices":
            key = "custom_fields_invoice"
        elif module == "bills":
            key = "custom_fields_bill"
        else:
            key = "custom_fields_payment"
            
        json_str = self.settings_data.get(key, '[]')
        try:
            fields = json.loads(json_str)
        except:
            fields = []
            
        self.fields_table.setRowCount(len(fields))
        for r, field in enumerate(fields):
            self.fields_table.setItem(r, 0, QTableWidgetItem(field.get('name', '')))
            self.fields_table.setItem(r, 1, QTableWidgetItem(field.get('type', 'Text')))
            self.fields_table.setItem(r, 2, QTableWidgetItem(field.get('default', '')))

    def add_custom_field_row(self):
        row = self.fields_table.rowCount()
        self.fields_table.insertRow(row)
        self.fields_table.setItem(row, 0, QTableWidgetItem("New Field"))
        self.fields_table.setItem(row, 1, QTableWidgetItem("Text"))
        self.fields_table.setItem(row, 2, QTableWidgetItem(""))

    def remove_custom_field_row(self):
        row = self.fields_table.currentRow()
        if row >= 0:
            self.fields_table.removeRow(row)

    def save_custom_fields(self):
        module = self.module_combo.currentText().lower()
        if module == "invoices":
            key = "custom_fields_invoice"
        elif module == "bills":
            key = "custom_fields_bill"
        else:
            key = "custom_fields_payment"
            
        fields = []
        for r in range(self.fields_table.rowCount()):
            name = self.fields_table.item(r, 0).text()
            if not name.strip(): continue
            
            fields.append({
                'name': name,
                'type': self.fields_table.item(r, 1).text(),
                'default': self.fields_table.item(r, 2).text()
            })
            
        json_str = json.dumps(fields)
        
        try:
            execute_write_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, json_str))
            
            # Update local cache
            self.settings_data[key] = json_str
            
            QMessageBox.information(self, "Success", f"Custom fields for {module} saved!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def backup_db(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy("database/ledgerpro.db", f"backup_ledgerpro_{timestamp}.db")
            QMessageBox.information(self, "Success", f"Backup created: backup_ledgerpro_{timestamp}.db")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
