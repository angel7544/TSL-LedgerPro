from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QMessageBox, QLabel, QComboBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from config_manager import load_config, save_config

class DBConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Database Configuration")
        self.setFixedSize(400, 350)
        
        self.config = load_config()
        db_config = self.config.get("database", {})
        
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Select your database backend. SQLite is local, MySQL is network-based.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        form_layout = QFormLayout()
        
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["sqlite", "mysql"])
        self.db_type_combo.setCurrentText(db_config.get("type", "sqlite"))
        self.db_type_combo.currentTextChanged.connect(self.toggle_fields)
        
        self.host_input = QLineEdit(db_config.get("host", "localhost"))
        self.port_input = QLineEdit(str(db_config.get("port", 3306)))
        self.user_input = QLineEdit(db_config.get("user", "root"))
        self.password_input = QLineEdit(db_config.get("password", ""))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.dbname_input = QLineEdit(db_config.get("database", "ledgerpro"))
        
        form_layout.addRow("Database Type:", self.db_type_combo)
        form_layout.addRow("Host:", self.host_input)
        form_layout.addRow("Port:", self.port_input)
        form_layout.addRow("User:", self.user_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Database Name:", self.dbname_input)
        
        layout.addLayout(form_layout)
        
        self.toggle_fields(self.db_type_combo.currentText())
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        test_btn = QPushButton("Test Connection / Setup MySQL")
        test_btn.clicked.connect(self.test_connection)
        
        migrate_btn = QPushButton("Migrate Data to MySQL")
        migrate_btn.clicked.connect(self.migrate_data)
        
        save_btn = QPushButton("Save && Close")
        save_btn.setStyleSheet("background-color: #2563EB; color: white; padding: 8px;")
        save_btn.clicked.connect(self.save_config)
        
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(migrate_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addStretch()
        layout.addLayout(btn_layout)
        
    def toggle_fields(self, db_type):
        is_mysql = (db_type == "mysql")
        self.host_input.setEnabled(is_mysql)
        self.port_input.setEnabled(is_mysql)
        self.user_input.setEnabled(is_mysql)
        self.password_input.setEnabled(is_mysql)
        self.dbname_input.setEnabled(is_mysql)
        
    def test_connection(self):
        if self.db_type_combo.currentText() == "sqlite":
            QMessageBox.information(self, "Test", "SQLite uses a local file and is ready by default.")
            return
            
        host = self.host_input.text()
        port = int(self.port_input.text() or 3306)
        user = self.user_input.text()
        password = self.password_input.text()
        dbname = self.dbname_input.text()
        
        try:
            from mysql_setup import setup_mysql_database
            success = setup_mysql_database(host, port, user, password, dbname)
            if success:
                QMessageBox.information(self, "Success", "MySQL connection successful and database is ready!")
            else:
                QMessageBox.critical(self, "Error", "Failed to setup MySQL database. Check console logs.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not test connection: {str(e)}")

    def migrate_data(self):
        if self.db_type_combo.currentText() == "sqlite":
            QMessageBox.warning(self, "Warning", "Please select MySQL as the database type to migrate data.")
            return
            
        host = self.host_input.text()
        port = int(self.port_input.text() or 3306)
        user = self.user_input.text()
        password = self.password_input.text()
        dbname = self.dbname_input.text()
        
        reply = QMessageBox.question(self, 'Confirm Migration', 
                                     'This will copy data from your local SQLite database to the specified MySQL database. Existing data in MySQL may be overwritten or duplicated. Continue?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from migrate_to_mysql import migrate_sqlite_to_mysql
                success = migrate_sqlite_to_mysql(host, port, user, password, dbname)
                if success:
                    QMessageBox.information(self, "Success", "Data migrated successfully to MySQL!")
                else:
                    QMessageBox.critical(self, "Error", "Migration failed. Check console for details.")
            except ImportError:
                 QMessageBox.critical(self, "Error", "Migration script not found.")
            except Exception as e:
                 QMessageBox.critical(self, "Error", f"Migration failed: {str(e)}")

    def save_config(self):
        db_type = self.db_type_combo.currentText()
        self.config["database"] = {
            "type": db_type,
            "host": self.host_input.text(),
            "port": int(self.port_input.text() or 3306),
            "user": self.user_input.text(),
            "password": self.password_input.text(),
            "database": self.dbname_input.text()
        }
        try:
            save_config(self.config)
            QMessageBox.information(self, "Saved", "Database configuration saved! Please restart the application if you changed the backend.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {str(e)}")
