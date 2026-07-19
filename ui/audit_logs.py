from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDateEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
import csv
import datetime
from database.db import execute_read_query, is_mysql
from ui.icons import get_icon

class AuditLogsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Header Title & Actions ---
        header_layout = QHBoxLayout()
        title = QLabel("Audit Trail & Activity Logs")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(get_icon("refresh", "#2563EB", 16))
        refresh_btn.setStyleSheet("background-color: #F1F5F9; color: #1E293B; border: 1px solid #CBD5E1; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        refresh_btn.clicked.connect(self.refresh_data)
        
        export_btn = QPushButton("Export CSV")
        export_btn.setIcon(get_icon("save", "#FFFFFF", 16))
        export_btn.setStyleSheet("background-color: #10B981; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        export_btn.clicked.connect(self.export_to_csv)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(export_btn)
        layout.addLayout(header_layout)
        
        # --- Filters Toolbar ---
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 10, 0, 10)
        
        # Search Box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by user, action, record ID, or details...")
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 13px;")
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Module Filter
        self.module_combo = QComboBox()
        self.module_combo.addItem("All Modules", "")
        modules = ["Auth", "User Management", "Customers", "Vendors", "Items", "Invoices", "Purchases", "Payments", "Stock", "Settings"]
        for m in modules:
            self.module_combo.addItem(m, m)
        self.module_combo.currentIndexChanged.connect(self.apply_filters)
        self.module_combo.setStyleSheet("padding: 6px; border: 1px solid #CBD5E1; border-radius: 6px;")
        
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input, stretch=2)
        filter_layout.addWidget(QLabel("Module:"))
        filter_layout.addWidget(self.module_combo, stretch=1)
        
        layout.addLayout(filter_layout)
        
        # --- Audit Logs Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Log ID", "Timestamp", "User Name", "User ID", "Action", "Module", "Record ID", "Details"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #E2E8F0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #E2E8F0;
            }
        """)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.all_logs = []
        self.refresh_data()

    def refresh_data(self):
        try:
            query = "SELECT id, user_id, user_name, action, module, record_id, details, timestamp FROM audit_logs ORDER BY id DESC LIMIT 500"
            rows = execute_read_query(query)
            self.all_logs = [dict(r) for r in rows]
            self.apply_filters()
        except Exception as e:
            print(f"Error fetching audit logs: {e}")

    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        selected_module = self.module_combo.currentData()
        
        filtered = []
        for log in self.all_logs:
            # Module check
            if selected_module and log.get('module') != selected_module:
                continue
                
            # Search check
            if search_text:
                combined = f"{log.get('user_name', '')} {log.get('action', '')} {log.get('record_id', '')} {log.get('details', '')}".lower()
                if search_text not in combined:
                    continue
                    
            filtered.append(log)
            
        self.table.setRowCount(len(filtered))
        for r, log in enumerate(filtered):
            self.table.setItem(r, 0, QTableWidgetItem(str(log.get('id', ''))))
            self.table.setItem(r, 1, QTableWidgetItem(str(log.get('timestamp', ''))))
            self.table.setItem(r, 2, QTableWidgetItem(str(log.get('user_name', 'System'))))
            self.table.setItem(r, 3, QTableWidgetItem(str(log.get('user_id', '-'))))
            
            # Action styling badge item
            action_item = QTableWidgetItem(str(log.get('action', '')))
            action = str(log.get('action', ''))
            if "DELETE" in action or "RESTORE" in action:
                action_item.setForeground(Qt.GlobalColor.red)
            elif "CREATE" in action or "INSERT" in action or "ADD" in action:
                action_item.setForeground(Qt.GlobalColor.darkGreen)
            elif "UPDATE" in action or "EDIT" in action:
                action_item.setForeground(Qt.GlobalColor.blue)
            self.table.setItem(r, 4, action_item)
            
            self.table.setItem(r, 5, QTableWidgetItem(str(log.get('module', ''))))
            self.table.setItem(r, 6, QTableWidgetItem(str(log.get('record_id', ''))))
            self.table.setItem(r, 7, QTableWidgetItem(str(log.get('details', ''))))

    def export_to_csv(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Export Info", "No audit log entries to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Audit Logs CSV", "audit_logs.csv", "CSV Files (*.csv)")
        if not file_path:
            return
            
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Log ID", "Timestamp", "User Name", "User ID", "Action", "Module", "Record ID", "Details"])
                for r in range(self.table.rowCount()):
                    row_data = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(8)]
                    writer.writerow(row_data)
            QMessageBox.information(self, "Success", f"Audit logs successfully exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {e}")
