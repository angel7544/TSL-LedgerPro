from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QMessageBox, QFileDialog, QInputDialog, QLineEdit
)
from PySide6.QtCore import QDate
from modules.stock_fifo import get_stock_valuation_summary, add_stock, reduce_stock_fifo
from database.db import execute_read_query, execute_write_query
import csv

class StockPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Stock Valuation (FIFO)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search items...")
        self.search_bar.setFixedWidth(200)
        self.search_bar.textChanged.connect(self.filter_data)

        import_btn = QPushButton("Import Stock CSV")
        import_btn.setStyleSheet("background-color: #10B981; color: white; padding: 8px 16px; border-radius: 6px; margin-right: 10px;")
        import_btn.clicked.connect(self.import_stock_csv)

        export_btn = QPushButton("Export to CSV")
        export_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px 16px; border-radius: 6px;")
        export_btn.clicked.connect(self.export_csv)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.search_bar)
        header.addWidget(import_btn)
        header.addWidget(export_btn)
        layout.addLayout(header)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Item Name", "Qty Available", "FIFO Value", "Avg Cost"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        self.stock_data = get_stock_valuation_summary()
        self.filter_data()

    def filter_data(self):
        search_text = self.search_bar.text().lower()
        filtered_data = [
            item for item in self.stock_data 
            if search_text in item['item_name'].lower()
        ]
        
        self.table.setRowCount(len(filtered_data))
        
        for r, item in enumerate(filtered_data):
            self.table.setItem(r, 0, QTableWidgetItem(item['item_name']))
            self.table.setItem(r, 1, QTableWidgetItem(str(item['total_quantity'])))
            self.table.setItem(r, 2, QTableWidgetItem(f"₹{item['total_value']:.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"₹{item['avg_cost']:.2f}"))

    def import_stock_csv(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import Stock CSV", "", "CSV Files (*.csv)")
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
                    try:
                        sample = f.read(1024)
                        f.seek(0)
                        dialect = csv.Sniffer().sniff(sample)
                    except csv.Error:
                        dialect = csv.excel

                reader = csv.DictReader(f, dialect=dialect)
                
                if not reader.fieldnames:
                     QMessageBox.warning(self, "Import Error", "The CSV file appears to be empty or has no headers.")
                     return

                # Header Mapping
                found_headers = [h.strip() for h in reader.fieldnames]
                
                def find_header(candidates):
                    for c in candidates:
                        for h in found_headers:
                            if h.lower() == c.lower():
                                return h
                    return None

                name_col = find_header(['Item Name', 'Name', 'Product Name'])
                sku_col = find_header(['SKU', 'Item SKU', 'Product Code'])
                stock_col = find_header(['Stock On Hand', 'Qty', 'Quantity', 'Stock'])
                
                if (not name_col and not sku_col) or not stock_col:
                    QMessageBox.critical(self, "Import Error", 
                                         f"Could not find valid identifiers ('Item Name' or 'SKU') and 'Stock On Hand' column.\nFound: {found_headers}")
                    return

                success_count = 0
                error_count = 0
                errors = []
                
                for row_idx, row in enumerate(reader, start=1):
                    clean_row = {k.strip(): v for k, v in row.items() if k}
                    
                    item_name = clean_row.get(name_col, '').strip() if name_col else ''
                    item_sku = clean_row.get(sku_col, '').strip() if sku_col else ''
                    
                    if not item_name and not item_sku:
                        continue
                    
                    identifier = item_sku if item_sku else item_name
                        
                    try:
                        qty_str = clean_row.get(stock_col, '')
                        if not qty_str or not str(qty_str).strip():
                            continue # Skip empty stock values to avoid accidental zeroing
                            
                        new_qty = float(str(qty_str).replace(',', '').strip())
                        
                        # Find Item
                        items = []
                        if item_sku:
                             items = execute_read_query("SELECT id, stock_on_hand, purchase_price FROM items WHERE sku = ?", (item_sku,))
                        
                        if not items and item_name:
                             items = execute_read_query("SELECT id, stock_on_hand, purchase_price FROM items WHERE name = ?", (item_name,))

                        if not items:
                            error_count += 1
                            errors.append(f"Item not found: {identifier}")
                            continue
                            
                        item = items[0]
                        item_id = item['id']
                        current_qty = item['stock_on_hand']
                        purchase_price = item['purchase_price']
                        
                        if new_qty > current_qty:
                            # Add Stock
                            diff = new_qty - current_qty
                            add_stock(item_id, diff, purchase_price, QDate.currentDate().toString("yyyy-MM-dd"))
                        elif new_qty < current_qty:
                            # Reduce Stock
                            diff = current_qty - new_qty
                            reduce_stock_fifo(item_id, diff)
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Error row {row_idx} ({identifier}): {str(e)}")

                msg = f"Stock Import Completed.\nSuccess: {success_count}\nSkipped/Errors: {error_count}"
                if errors:
                    msg += "\n\nDetails (First 10):\n" + "\n".join(errors[:10])
                QMessageBox.information(self, "Import Summary", msg)
                self.refresh_data()

        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Stock Report", "", "CSV Files (*.csv)")
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Item Name", "Quantity", "Total Value", "Avg Cost"])
                for item in self.stock_data:
                    writer.writerow([item['item_name'], item['total_quantity'], item['total_value'], item['avg_cost']])
