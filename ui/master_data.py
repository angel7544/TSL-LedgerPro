from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QDialog, QFormLayout, QMessageBox,
    QFileDialog, QTabWidget, QCheckBox, QComboBox, QScrollArea, QFrame, QDoubleSpinBox
)
from PySide6.QtCore import QDate, Qt
from database.db import execute_read_query, execute_write_query, execute_transaction
import csv
import io
import datetime

class BaseCRUDPage(QWidget):
    def __init__(self, title, table_name, columns, form_fields):
        super().__init__()
        self.title = title
        self.table_name = table_name
        self.columns = columns # List of (display_name, db_column)
        self.form_fields = form_fields # List of (label, db_column, type)
        self.view_button_enabled = False
        
        self.layout = QVBoxLayout()
        
        # Header
        self.header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.add_btn = QPushButton(f"+ Add {title[:-1]}") # Remove 's'
        self.add_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 16px; border-radius: 6px;")
        self.add_btn.clicked.connect(lambda: self.open_form_dialog())
        
        self.header.addWidget(title_lbl)
        self.header.addStretch()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(f"Search {title[:-1]}...")
        self.search_bar.setFixedWidth(200)
        self.search_bar.textChanged.connect(self.filter_data)
        self.header.addWidget(self.search_bar)
        
        self.header.addWidget(self.add_btn)
        self.layout.addLayout(self.header)
        
        # Table
        self.table = QTableWidget()
        # Add 'Actions' column
        self.table.setColumnCount(len(columns) + 1)
        self.table.setHorizontalHeaderLabels([c[0] for c in columns] + ["Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        self.refresh_data()

    def refresh_data(self):
        cols = ", ".join([c[1] for c in self.columns])
        # We need ID for editing
        self.all_rows = execute_read_query(f"SELECT id, {cols} FROM {self.table_name} ORDER BY id DESC")
        self.filter_data()
        
    def filter_data(self):
        search_text = self.search_bar.text().lower()
        
        filtered_rows = []
        if not search_text:
            filtered_rows = self.all_rows
        else:
            for row in self.all_rows:
                # Search in all visible columns
                match = False
                for col in self.columns:
                    val = str(row[col[1]] or "").lower()
                    if search_text in val:
                        match = True
                        break
                if match:
                    filtered_rows.append(row)

        self.table.setRowCount(len(filtered_rows))
        
        formatters = getattr(self, "column_formatters", {})

        for r, row in enumerate(filtered_rows):
            for c, col in enumerate(self.columns):
                key = col[1]
                val = row[key]
                
                if key in formatters:
                    try:
                        text = formatters[key](val)
                    except:
                        text = str(val) if val is not None else ""
                else:
                    text = str(val) if val is not None else ""
                    
                item = QTableWidgetItem(text)
                
                # Align right for numbers
                if key in formatters or isinstance(val, (int, float)):
                     item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                     
                self.table.setItem(r, c, item)
            
            # Action Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            if getattr(self, "view_button_enabled", False):
                view_btn = QPushButton("View")
                view_btn.setStyleSheet("background-color: #06B6D4; color: white; border-radius: 4px; padding: 4px 8px;")
                view_btn.clicked.connect(lambda checked, row_data=row: self.open_view_dialog(row_data))
                action_layout.addWidget(view_btn)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("background-color: #F59E0B; color: white; border-radius: 4px; padding: 4px 8px;")
            edit_btn.clicked.connect(lambda checked, row_data=row: self.open_form_dialog(row_data))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #EF4444; color: white; border-radius: 4px; padding: 4px 8px;")
            delete_btn.clicked.connect(lambda checked, row_id=row['id']: self.delete_record(row_id))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            
            self.table.setCellWidget(r, len(self.columns), action_widget)

    def delete_record(self, record_id):
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f"Are you sure you want to delete this {self.title[:-1]}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                execute_write_query(f"DELETE FROM {self.table_name} WHERE id = ?", (record_id,))
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")

    def open_view_dialog(self, record_summary):
        self.open_form_dialog(record_summary)

    def open_form_dialog(self, record_summary=None):
        dialog = QDialog(self)
        mode = "Edit" if record_summary else "Add"
        dialog.setWindowTitle(f"{mode} {self.title[:-1]}")
        layout = QFormLayout(dialog)
        inputs = {}
        
        record = None
        if record_summary:
            # Fetch full record from DB to ensure all fields are available
            rows = execute_read_query(f"SELECT * FROM {self.table_name} WHERE id = ?", (record_summary['id'],))
            if rows:
                record = rows[0]
            else:
                QMessageBox.warning(self, "Error", "Record not found.")
                # We can't return here easily because we are in a lambda slot usually, 
                # but if we don't return, we crash.
                return

        for label, db_col, typ in self.form_fields:
            inp = QLineEdit()
            if record:
                # Use dict access for sqlite3.Row or standard dict
                try:
                    val = record[db_col]
                    inp.setText(str(val) if val is not None else "")
                except IndexError:
                    inp.setText("")
            layout.addRow(label, inp)
            inputs[db_col] = inp
            
        save_btn = QPushButton("Save")
        # Use record['id'] if record is available, else None
        record_id = record['id'] if record else None
        save_btn.clicked.connect(lambda: self.save_data(dialog, inputs, record_id))
        layout.addRow(save_btn)
        
        if dialog.exec():
            self.refresh_data()

    def save_data(self, dialog, inputs, record_id=None):
        data = {col: inp.text() for col, inp in inputs.items()}
        
        try:
            if record_id:
                # Update
                set_clause = ", ".join([f"{col} = ?" for col in data])
                values = tuple(data.values()) + (record_id,)
                execute_write_query(f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?", values)
            else:
                # Insert
                cols = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                values = tuple(data.values())
                execute_write_query(f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders})", values)
            
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", str(e))

class CustomersPage(BaseCRUDPage):
    def __init__(self):
        super().__init__("Customers", "customers", 
                         [("Name", "name"), ("Phone", "phone"), ("Email", "email"), ("GSTIN", "gstin"), ("State", "state"), ("Credits", "credits")],
                         [("Name", "name", "text"), ("Phone", "phone", "text"), ("Email", "email", "text"), 
                          ("Address", "address", "text"), ("GSTIN", "gstin", "text"), ("State", "state", "text")])

    def refresh_data(self):
        # Override to include credits calculation
        query = """
            SELECT c.*, 
            COALESCE((SELECT SUM(amount) FROM payments WHERE customer_id = c.id AND invoice_id IS NULL), 0) as credits
            FROM customers c
            ORDER BY c.id DESC
        """
        self.column_formatters = {
            'credits': lambda x: f"₹{float(x):.2f}"
        }
        self.all_rows = execute_read_query(query)
        self.filter_data()

class VendorsPage(BaseCRUDPage):
    def __init__(self):
        super().__init__("Vendors", "vendors",
                         [("Name", "name"), ("Phone", "phone"), ("GSTIN", "gstin"), ("State", "state"), ("Credits", "credits")],
                         [("Name", "name", "text"), ("Phone", "phone", "text"), ("Email", "email", "text"),
                          ("Address", "address", "text"), ("GSTIN", "gstin", "text"), ("State", "state", "text")])

    def refresh_data(self):
        # Override to include credits calculation
        query = """
            SELECT v.*, 
            COALESCE((SELECT SUM(amount) FROM payments WHERE vendor_id = v.id AND bill_id IS NULL), 0) as credits
            FROM vendors v
            ORDER BY v.id DESC
        """
        self.column_formatters = {
            'credits': lambda x: f"₹{float(x):.2f}"
        }
        self.all_rows = execute_read_query(query)
        self.filter_data()

class ItemsPage(BaseCRUDPage):
    def __init__(self):
        super().__init__("Items", "items",
                         [("Name", "name"), ("SKU", "sku"), ("Price", "selling_price"), ("Stock", "stock_on_hand"), ("Reorder", "reorder_point")],
                         [("Name", "name", "text"), ("SKU", "sku", "text"), ("HSN/SAC", "hsn_sac", "text"),
                          ("Description", "description", "text"), ("Unit", "unit", "text"), 
                          ("Selling Price", "selling_price", "number"), ("Purchase Price", "purchase_price", "number"),
                          ("GST Rate (%)", "gst_rate", "number"), ("Reorder Point", "reorder_point", "number")])
        self.view_button_enabled = True
        
        # Add Import/Export Buttons
        import_btn = QPushButton("Import CSV")
        import_btn.setStyleSheet("background-color: #10B981; color: white; padding: 8px 16px; border-radius: 6px; margin-right: 10px;")
        import_btn.clicked.connect(self.import_csv)
        
        export_btn = QPushButton("Export CSV")
        export_btn.setStyleSheet("background-color: #6366F1; color: white; padding: 8px 16px; border-radius: 6px; margin-right: 10px;")
        export_btn.clicked.connect(self.export_csv)
        
        count = self.header.count()
        self.header.insertWidget(count-1, export_btn)
        self.header.insertWidget(count-1, import_btn)

    def open_view_dialog(self, record_summary):
        self.open_form_dialog(record_summary, view_only=True)

    def open_form_dialog(self, record_summary=None, view_only=False):
        dialog = QDialog(self)
        mode = "View" if view_only else ("Edit" if record_summary else "Add")
        dialog.setWindowTitle(f"{mode} Item - Detailed View")
        dialog.resize(900, 700)
        
        layout = QVBoxLayout(dialog)
        
        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Data Containers
        self.item_inputs = {}
        
        # Fetch Record if Edit
        record = None
        if record_summary:
            rows = execute_read_query("SELECT * FROM items WHERE id = ?", (record_summary['id'],))
            if rows:
                record = rows[0]
        
        # --- Helper to create fields ---
        def add_row(form, label, key, widget, default=None):
            form.addRow(label, widget)
            self.item_inputs[key] = widget
            if record and key in record.keys() and record[key] is not None:
                val = record[key]
                if isinstance(widget, QLineEdit):
                    widget.setText(str(val))
                elif isinstance(widget, QDoubleSpinBox):
                    try: widget.setValue(float(val))
                    except: widget.setValue(0.0)
                elif isinstance(widget, QCheckBox):
                    widget.setChecked(bool(val))
                elif isinstance(widget, QComboBox):
                    index = widget.findText(str(val))
                    if index >= 0: widget.setCurrentIndex(index)
            elif default is not None:
                if isinstance(widget, QLineEdit): widget.setText(str(default))
                elif isinstance(widget, QCheckBox): widget.setChecked(bool(default))
        
        # --- Tab 1: General Info ---
        tab_general = QWidget()
        form_gen = QFormLayout(tab_general)
        
        add_row(form_gen, "Item Name *", "name", QLineEdit())
        add_row(form_gen, "SKU", "sku", QLineEdit())
        add_row(form_gen, "HSN/SAC", "hsn_sac", QLineEdit())
        add_row(form_gen, "Description", "description", QLineEdit())
        
        unit_cb = QComboBox()
        unit_cb.addItems(["pcs", "kg", "mtr", "box", "set", "ltr", "gm"])
        unit_cb.setEditable(True)
        add_row(form_gen, "Unit", "unit", unit_cb)
        
        item_type_cb = QComboBox()
        item_type_cb.addItems(["Goods", "Service"])
        add_row(form_gen, "Item Type", "item_type", item_type_cb, "Goods")
        
        prod_type_cb = QComboBox()
        prod_type_cb.addItems(["Inventory", "Non-Inventory", "Service", "Bundle"])
        prod_type_cb.setEditable(True)
        add_row(form_gen, "Product Type", "product_type", prod_type_cb, "Inventory")

        # Vendor Fetch
        vendor_cb = QComboBox()
        vendor_cb.addItem("Select Vendor", None)
        vendors = execute_read_query("SELECT id, name FROM vendors")
        selected_idx = 0
        for i, v in enumerate(vendors):
            vendor_cb.addItem(v['name'], v['id'])
            if record:
                try:
                    if record['vendor_id'] == v['id']:
                        selected_idx = i + 1
                except (KeyError, IndexError):
                    pass
        vendor_cb.setCurrentIndex(selected_idx)
        form_gen.addRow("Preferred Vendor", vendor_cb)
        self.item_inputs['vendor_cb'] = vendor_cb # Special handling
        
        tabs.addTab(tab_general, "General")
        
        # --- Tab 2: Pricing & Tax ---
        tab_price = QWidget()
        form_price = QFormLayout(tab_price)
        
        sb_sell = QDoubleSpinBox()
        sb_sell.setRange(0, 1000000)
        sb_sell.setDecimals(2)
        add_row(form_price, "Selling Price (Rate)", "selling_price", sb_sell)
        
        sb_cost = QDoubleSpinBox()
        sb_cost.setRange(0, 1000000)
        sb_cost.setDecimals(2)
        add_row(form_price, "Purchase Price", "purchase_price", sb_cost)
        
        chk_taxable = QCheckBox("Taxable Item")
        add_row(form_price, "", "taxable", chk_taxable, True)
        
        add_row(form_price, "Exemption Reason", "exemption_reason", QLineEdit())
        
        taxability_cb = QComboBox()
        taxability_cb.addItems(["Taxable", "Exempt", "Nil Rated", "Non-GST"])
        add_row(form_price, "Taxability Type", "taxability_type", taxability_cb, "Taxable")
        
        sb_gst = QDoubleSpinBox()
        sb_gst.setRange(0, 100)
        add_row(form_price, "GST Rate (%)", "gst_rate", sb_gst)
        
        # Detailed Tax Rates
        sb_intra = QDoubleSpinBox()
        sb_intra.setRange(0, 100)
        add_row(form_price, "Intra State Tax Rate", "intra_state_tax_rate", sb_intra)
        
        sb_inter = QDoubleSpinBox()
        sb_inter.setRange(0, 100)
        add_row(form_price, "Inter State Tax Rate", "inter_state_tax_rate", sb_inter)
        
        tabs.addTab(tab_price, "Pricing & Tax")
        
        # --- Tab 3: Inventory & Stock ---
        tab_stock = QWidget()
        form_stock = QFormLayout(tab_stock)
        
        chk_track = QCheckBox("Track Inventory")
        add_row(form_stock, "", "track_inventory", chk_track, True)
        
        sb_reorder = QDoubleSpinBox()
        sb_reorder.setRange(0, 100000)
        add_row(form_stock, "Reorder Point", "reorder_point", sb_reorder)
        
        val_method_cb = QComboBox()
        val_method_cb.addItems(["FIFO", "LIFO", "Weighted Average"]) # Currently only FIFO logic implemented
        add_row(form_stock, "Valuation Method", "inventory_valuation_method", val_method_cb, "FIFO")
        
        # Opening Stock Section (Group Box)
        stock_group = QFrame()
        stock_group.setFrameStyle(QFrame.StyledPanel)
        stock_layout = QFormLayout(stock_group)
        
        sb_opening = QDoubleSpinBox()
        sb_opening.setRange(0, 1000000)
        add_row(stock_layout, "Opening Stock Qty", "opening_stock", sb_opening)
        
        sb_opening_val = QDoubleSpinBox()
        sb_opening_val.setRange(0, 10000000)
        add_row(stock_layout, "Opening Stock Value (Total)", "opening_stock_value", sb_opening_val)
        
        # Stock On Hand (Read Only usually, but let's make it match opening stock logic if new)
        # Display current stock on hand
        lbl_stock = QLabel(str(record['stock_on_hand']) if record else "0.0")
        form_stock.addRow("Current Stock On Hand:", lbl_stock)
        
        form_stock.addRow("Opening Stock Details:", stock_group)
        
        tabs.addTab(tab_stock, "Inventory")
        
        # --- Tab 4: Accounts & Flags ---
        tab_acct = QWidget()
        form_acct = QFormLayout(tab_acct)
        
        add_row(form_acct, "Sales Account Code", "account_code", QLineEdit())
        add_row(form_acct, "Purchase Account Code", "purchase_account_code", QLineEdit())
        add_row(form_acct, "Inventory Account Code", "inventory_account_code", QLineEdit())
        add_row(form_acct, "Purchase Description", "purchase_description", QLineEdit())
        
        chk_sell = QCheckBox("Item is Sellable")
        add_row(form_acct, "", "is_sellable", chk_sell, True)
        
        chk_buy = QCheckBox("Item is Purchasable")
        add_row(form_acct, "", "is_purchasable", chk_buy, True)
        
        tabs.addTab(tab_acct, "Accounts/Other")
        
        if view_only:
            for widget in self.item_inputs.values():
                widget.setEnabled(False)
        
        # --- Buttons ---
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Item")
        save_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 8px;")
        cancel_btn = QPushButton("Cancel")
        
        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        
        layout.addLayout(btn_box)
        
        record_id = record['id'] if record else None
        if view_only:
            save_btn.setText("Close")
            cancel_btn.hide()
            save_btn.clicked.connect(dialog.accept)
        else:
            save_btn.clicked.connect(lambda: self.save_item_custom(dialog, record_id))
            cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

    def save_item_custom(self, dialog, record_id):
        try:
            # Gather Data
            data = {}
            # Text Fields
            for key in ['name', 'sku', 'hsn_sac', 'description', 'account_code', 
                       'purchase_account_code', 'inventory_account_code', 'purchase_description',
                       'exemption_reason']:
                data[key] = self.item_inputs[key].text()
                
            # Combos
            data['unit'] = self.item_inputs['unit'].currentText()
            data['item_type'] = self.item_inputs['item_type'].currentText()
            data['product_type'] = self.item_inputs['product_type'].currentText()
            data['taxability_type'] = self.item_inputs['taxability_type'].currentText()
            data['inventory_valuation_method'] = self.item_inputs['inventory_valuation_method'].currentText()
            
            # Numeric
            data['selling_price'] = self.item_inputs['selling_price'].value()
            data['purchase_price'] = self.item_inputs['purchase_price'].value()
            data['gst_rate'] = self.item_inputs['gst_rate'].value()
            data['intra_state_tax_rate'] = self.item_inputs['intra_state_tax_rate'].value()
            data['inter_state_tax_rate'] = self.item_inputs['inter_state_tax_rate'].value()
            data['reorder_point'] = self.item_inputs['reorder_point'].value()
            data['opening_stock'] = self.item_inputs['opening_stock'].value()
            data['opening_stock_value'] = self.item_inputs['opening_stock_value'].value()
            
            # Checkboxes (Integer)
            data['taxable'] = 1 if self.item_inputs['taxable'].isChecked() else 0
            data['track_inventory'] = 1 if self.item_inputs['track_inventory'].isChecked() else 0
            data['is_sellable'] = 1 if self.item_inputs['is_sellable'].isChecked() else 0
            data['is_purchasable'] = 1 if self.item_inputs['is_purchasable'].isChecked() else 0
            
            # Vendor
            vendor_data = self.item_inputs['vendor_cb'].currentData()
            data['vendor_id'] = vendor_data if vendor_data else None
            
            # Validation
            if not data['name']:
                QMessageBox.warning(dialog, "Validation", "Item Name is required.")
                return

            # Special Logic: If New Item and Opening Stock > 0, set stock_on_hand
            # If Edit, we generally don't overwrite stock_on_hand unless we want to support manual adjustment here
            # For now, let's allow updating stock_on_hand to match opening_stock if it's a NEW record.
            # If it's an EDIT, we leave stock_on_hand alone (it changes via transactions).
            
            if not record_id:
                # New Record
                data['stock_on_hand'] = data['opening_stock']
                
                cols = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                values = tuple(data.values())
                
                item_id = execute_write_query(f"INSERT INTO items ({cols}) VALUES ({placeholders})", values)
                
                # Create Batch for Opening Stock
                if data['opening_stock'] > 0:
                    # Calculate rate
                    rate = data['purchase_price']
                    if data['opening_stock_value'] > 0:
                        rate = data['opening_stock_value'] / data['opening_stock']
                    
                    execute_write_query("""
                        INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (item_id, data['opening_stock'], rate, QDate.currentDate().toString("yyyy-MM-dd"), data['vendor_id']))
                    
            else:
                # Update Record
                # Fetch old data to calculate difference
                old_record = execute_read_query("SELECT opening_stock, stock_on_hand FROM items WHERE id = ?", (record_id,))
                old_opening = 0.0
                if old_record:
                    old_opening = float(old_record[0]['opening_stock'] or 0.0)

                set_clause = ", ".join([f"{col} = ?" for col in data])
                values = tuple(data.values()) + (record_id,)
                execute_write_query(f"UPDATE items SET {set_clause} WHERE id = ?", values)
                
                # Handle Stock Correction if Opening Stock Changed
                new_opening = float(data['opening_stock'] or 0.0)
                diff = new_opening - old_opening
                
                if abs(diff) > 0.001: # Float comparison
                    # Update stock_on_hand
                    execute_write_query("UPDATE items SET stock_on_hand = stock_on_hand + ? WHERE id = ?", (diff, record_id))
                    
                    if diff > 0:
                        # Add Stock Batch
                        rate = data['purchase_price']
                        if data['opening_stock_value'] > 0 and new_opening > 0:
                             rate = data['opening_stock_value'] / new_opening
                             
                        execute_write_query("""
                            INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
                            VALUES (?, ?, ?, ?, ?)
                        """, (record_id, diff, rate, QDate.currentDate().toString("yyyy-MM-dd"), data['vendor_id']))
                    else:
                        # Reduce Stock Batch (FIFO logic but for correction)
                        qty_to_remove = abs(diff)
                        batches = execute_read_query("""
                            SELECT id, quantity_remaining 
                            FROM stock_batches 
                            WHERE item_id = ? AND quantity_remaining > 0 
                            ORDER BY purchase_date ASC, id ASC
                        """, (record_id,))
                        
                        for batch in batches:
                            if qty_to_remove <= 0:
                                break
                                
                            b_id = batch['id']
                            b_qty = batch['quantity_remaining']
                            
                            if b_qty <= qty_to_remove:
                                # Remove entire batch
                                execute_write_query("UPDATE stock_batches SET quantity_remaining = 0 WHERE id = ?", (b_id,))
                                qty_to_remove -= b_qty
                            else:
                                # Reduce batch
                                execute_write_query("UPDATE stock_batches SET quantity_remaining = ? WHERE id = ?", (b_qty - qty_to_remove, b_id))
                                qty_to_remove = 0
            
            dialog.accept()
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Failed to save item: {str(e)}")

    def import_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import Items CSV", "", "CSV Files (*.csv)")
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8-sig') as f:
                # Robust delimiter detection
                first_line = f.readline()
                f.seek(0)
                
                delimiters = [',', '\t', ';', '|']
                counts = {d: first_line.count(d) for d in delimiters}
                best_delimiter = max(counts, key=counts.get)
                
                dialect = None
                if counts[best_delimiter] > 0:
                    class SimpleDialect(csv.Dialect):
                        delimiter = best_delimiter
                        quotechar = '"'
                        doublequote = True
                        skipinitialspace = True
                        lineterminator = '\r\n'
                        quoting = csv.QUOTE_MINIMAL
                    dialect = SimpleDialect
                else:
                    # Fallback to sniffer
                    try:
                        sample = f.read(1024)
                        f.seek(0)
                        dialect = csv.Sniffer().sniff(sample)
                    except csv.Error:
                        dialect = csv.excel

                reader = csv.DictReader(f, dialect=dialect)
                
                # Verify headers
                if not reader.fieldnames:
                     QMessageBox.warning(self, "Import Error", "The CSV file appears to be empty or has no headers.")
                     return

                # Flexible header matching
                # Map expected headers to found headers
                header_map = {}
                found_headers = [h.strip() for h in reader.fieldnames] # Strip whitespace from headers
                
                def find_header(candidates):
                    for c in candidates:
                        for h in found_headers:
                            if h.lower() == c.lower():
                                return h
                    return None

                # Key mapping: Internal Key -> [List of possible CSV headers]
                key_mapping = {
                    'name': ['Item Name', 'Name', 'Product Name'],
                    'sku': ['SKU', 'Item Code'],
                    'hsn': ['HSN/SAC', 'HSN', 'SAC'],
                    'desc': ['Description', 'Desc'],
                    'unit': ['Unit Name', 'Usage unit', 'Unit'],
                    'selling_price': ['Rate', 'Selling Price', 'Price'],
                    'purchase_price': ['Purchase Rate', 'Purchase Price', 'Cost'],
                    'reorder_point': ['Reorder Point', 'Min Stock'],
                    'opening_stock': ['Opening Stock', 'Initial Stock'],
                    'opening_value': ['Opening Stock Value'],
                    'stock_on_hand': ['Stock On Hand', 'Qty'],
                    'intra_tax': ['Intra State Tax Rate', 'SGST', 'CGST'],
                    'inter_tax': ['Inter State Tax Rate', 'IGST'],
                    'vendor': ['Vendor', 'Supplier']
                }

                # Resolve headers
                resolved_headers = {}
                for key, candidates in key_mapping.items():
                    resolved_headers[key] = find_header(candidates)

                if not resolved_headers['name']:
                    debug_info = f"Detected delimiter: '{dialect.delimiter if hasattr(dialect, 'delimiter') else 'unknown'}'\n"
                    debug_info += f"First line start: {first_line[:50]}...\n"
                    debug_info += f"Found headers: {', '.join(found_headers)}"
                    
                    QMessageBox.critical(self, "Import Error", 
                                         f"Could not find a valid 'Item Name' column.\n\n{debug_info}")
                    return

                success_count = 0
                error_count = 0
                errors = []
                
                for row_idx, row in enumerate(reader, start=1):
                    # Strip keys in row to match stripped headers
                    clean_row = {k.strip(): v for k, v in row.items() if k}
                    
                    try:
                        name_col = resolved_headers['name']
                        name = clean_row.get(name_col, '').strip()
                        if not name: 
                            error_count += 1
                            errors.append(f"Row {row_idx}: Missing Name")
                            continue
                            
                        sku = clean_row.get(resolved_headers['sku'], '') if resolved_headers['sku'] else ''
                        hsn = clean_row.get(resolved_headers['hsn'], '') if resolved_headers['hsn'] else ''
                        desc = clean_row.get(resolved_headers['desc'], '') if resolved_headers['desc'] else ''
                        unit = clean_row.get(resolved_headers['unit'], 'pcs') if resolved_headers['unit'] else 'pcs'
                        
                        # Clean numeric fields
                        def parse_float(val):
                            if not val: return 0.0
                            return float(str(val).replace('INR', '').replace(',', '').strip())

                        selling_price = parse_float(clean_row.get(resolved_headers['selling_price'], '0')) if resolved_headers['selling_price'] else 0.0
                        purchase_price = parse_float(clean_row.get(resolved_headers['purchase_price'], '0')) if resolved_headers['purchase_price'] else 0.0
                        reorder_point = parse_float(clean_row.get(resolved_headers['reorder_point'], '0')) if resolved_headers['reorder_point'] else 0.0
                        opening_stock = parse_float(clean_row.get(resolved_headers['opening_stock'], '0')) if resolved_headers['opening_stock'] else 0.0
                        stock_on_hand_csv = parse_float(clean_row.get(resolved_headers['stock_on_hand'], '0')) if resolved_headers['stock_on_hand'] else 0.0
                        
                        # Use Stock On Hand if Opening Stock is 0
                        initial_stock = opening_stock if opening_stock > 0 else stock_on_hand_csv
                        opening_value = parse_float(clean_row.get(resolved_headers['opening_value'], '0')) if resolved_headers['opening_value'] else 0.0
                        
                        # GST Rate logic
                        gst_str = ''
                        if resolved_headers['intra_tax']:
                            gst_str = clean_row.get(resolved_headers['intra_tax'], '')
                        if not gst_str and resolved_headers['inter_tax']:
                            gst_str = clean_row.get(resolved_headers['inter_tax'], '')
                        gst_rate = parse_float(gst_str)

                        # Vendor logic
                        vendor_name = clean_row.get(resolved_headers['vendor'], '').strip() if resolved_headers['vendor'] else ''
                        vendor_id = None
                        if vendor_name:
                            v_rows = execute_read_query("SELECT id FROM vendors WHERE name = ?", (vendor_name,))
                            if v_rows:
                                vendor_id = v_rows[0]['id']
                            else:
                                # Create vendor
                                vendor_id = execute_write_query("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))

                        # Duplicate check
                        existing = None
                        if sku:
                            existing = execute_read_query("SELECT id FROM items WHERE sku = ?", (sku,))
                        else:
                            existing = execute_read_query("SELECT id FROM items WHERE name = ?", (name,))
                            
                        if existing:
                            error_count += 1
                            errors.append(f"Duplicate: {name} ({sku})")
                            continue
                            
                        # Insert Item
                        item_id = execute_write_query("""
                            INSERT INTO items (name, sku, hsn_sac, description, unit, 
                                             selling_price, purchase_price, gst_rate, 
                                             reorder_point, stock_on_hand, opening_stock_value)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (name, sku, hsn, desc, unit, selling_price, purchase_price, gst_rate, reorder_point, initial_stock, opening_value))
                        
                        # Create Opening Stock Batch if applicable
                        if initial_stock > 0:
                            # If Opening Stock Value is provided, calculate rate, else use Purchase Rate
                            batch_rate = purchase_price
                            if opening_value > 0 and opening_stock > 0:
                                batch_rate = opening_value / opening_stock
                                
                            execute_write_query("""
                                INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
                                VALUES (?, ?, ?, ?, ?)
                            """, (item_id, initial_stock, batch_rate, QDate.currentDate().toString("yyyy-MM-dd"), vendor_id))
                            
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Error row {row_idx} ({clean_row.get(resolved_headers['name'], 'Unknown')}): {str(e)}")
                        
                msg = f"Import Completed.\nSuccess: {success_count}\nSkipped/Errors: {error_count}"
                if errors:
                    msg += "\n\nDetails (First 10):\n" + "\n".join(errors[:10])
                QMessageBox.information(self, "Import Summary", msg)
                self.refresh_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Items", "", "CSV Files (*.csv)")
        if not filename: return
            
        try:
            items = execute_read_query("SELECT * FROM items")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Item Name", "SKU", "HSN/SAC", "Description", "Unit", 
                               "Rate", "Purchase Rate", "GST Rate", "Reorder Point", "Stock On Hand"])
                for item in items:
                    writer.writerow([
                        item['name'], item['sku'], item['hsn_sac'], item['description'], item['unit'],
                        item['selling_price'], item['purchase_price'], item['gst_rate'], 
                        item['reorder_point'], item['stock_on_hand']
                    ])
            QMessageBox.information(self, "Success", "Items exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))
