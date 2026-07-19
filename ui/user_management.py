from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QDialog, QFormLayout, QFrame, QDialogButtonBox, QMenu, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from auth.auth_logic import (
    get_all_users, create_user_by_admin, update_user_role,
    update_password, delete_user, get_audit_logs, log_audit_action
)
from auth.session import Session
from ui.icons import get_icon

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New System User")
        self.setFixedWidth(420)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. John Doe")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. john@company.com")
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Enter password")
        
        self.role_combo = QComboBox()
        self.role_combo.addItem("Owner (Full Control)", "owner")
        self.role_combo.addItem("Manager (Operations & Reports)", "manager")
        self.role_combo.addItem("Staff (Basic Operations)", "staff")
        
        form_layout.addRow("Full Name:", self.name_input)
        form_layout.addRow("Email / Username:", self.email_input)
        form_layout.addRow("Initial Password:", self.pass_input)
        form_layout.addRow("Assigned Role:", self.role_combo)
        
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.handle_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def handle_accept(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.pass_input.text()
        role = self.role_combo.currentData()
        
        if not name or not email or not password:
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields.")
            return
            
        success = create_user_by_admin(name, email, password, role)
        if success:
            log_audit_action("CREATE_USER", "User Management", email, f"User '{name}' created with role '{role}'")
            QMessageBox.information(self, "Success", f"User '{name}' created successfully with role '{role.title()}'.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to create user. Email may already be registered.")

class EditRoleDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"Change Role - {user.get('name')}")
        self.setFixedWidth(380)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.role_combo = QComboBox()
        self.role_combo.addItem("Owner (Full Control)", "owner")
        self.role_combo.addItem("Manager (Operations & Reports)", "manager")
        self.role_combo.addItem("Staff (Basic Operations)", "staff")
        
        current_role = user.get('role', 'staff')
        index = self.role_combo.findData(current_role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
            
        form_layout.addRow(QLabel(f"User: <b>{user.get('name')}</b> ({user.get('email')})"))
        form_layout.addRow("New Role:", self.role_combo)
        
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.handle_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def handle_accept(self):
        new_role = self.role_combo.currentData()
        success = update_user_role(self.user['id'], new_role)
        if success:
            log_audit_action("UPDATE_ROLE", "User Management", self.user['id'], f"User '{self.user.get('name')}' role changed to '{new_role}'")
            QMessageBox.information(self, "Success", "User role updated successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update user role.")

class ResetPasswordDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"Reset Password - {user.get('name')}")
        self.setFixedWidth(380)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("New password")
        
        form_layout.addRow(QLabel(f"User: <b>{user.get('name')}</b>"))
        form_layout.addRow("New Password:", self.pass_input)
        
        layout.addLayout(form_layout)
        layout.addSpacing(15)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.handle_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def handle_accept(self):
        new_pass = self.pass_input.text()
        if not new_pass:
            QMessageBox.warning(self, "Error", "Password cannot be empty.")
            return
            
        success = update_password(self.user['id'], new_pass)
        if success:
            log_audit_action("RESET_PASSWORD", "User Management", self.user['id'], f"Password reset for user '{self.user.get('name')}'")
            QMessageBox.information(self, "Success", "Password reset successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to reset password.")


class UserManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        
        title = QLabel("User & Role Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B;")
        subtitle = QLabel("Manage system users, assign roles (Owner, Manager, Staff), and control access levels.")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B;")
        
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        self.add_user_btn = QPushButton(" Add New User")
        self.add_user_btn.setIcon(get_icon("add", "#FFFFFF", 16))
        self.add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
                padding: 10px 18px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        self.add_user_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_user_btn.clicked.connect(self.open_add_user_dialog)
        header_layout.addWidget(self.add_user_btn)
        
        layout.addLayout(header_layout)
        
        self.tabs = QTabWidget()
        
        # --- Tab 1: User Accounts ---
        self.users_tab = QWidget()
        users_tab_layout = QVBoxLayout(self.users_tab)
        users_tab_layout.setContentsMargins(0, 10, 0, 0)
        
        # Controls / Filter Bar
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users by name or email...")
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 6px;")
        self.search_input.textChanged.connect(self.filter_users)
        filter_layout.addWidget(self.search_input)
        filter_layout.addStretch()
        
        refresh_btn = QPushButton(" Refresh")
        refresh_btn.setIcon(get_icon("refresh", "#334155", 14))
        refresh_btn.setStyleSheet("padding: 8px 14px; background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: bold;")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_users)
        filter_layout.addWidget(refresh_btn)
        
        users_tab_layout.addLayout(filter_layout)
        
        # User Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Role", "Created At", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                padding: 10px;
                font-weight: bold;
                color: #475569;
                border: none;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        users_tab_layout.addWidget(self.table)
        self.tabs.addTab(self.users_tab, "User Accounts")

        # --- Tab 2: Audit Logs ---
        self.audit_tab = QWidget()
        audit_layout = QVBoxLayout(self.audit_tab)
        audit_layout.setContentsMargins(0, 10, 0, 0)
        
        audit_header = QHBoxLayout()
        audit_info = QLabel("Activity trail tracking system actions, user updates, and security events.")
        audit_info.setStyleSheet("color: #64748B; font-size: 13px;")
        audit_header.addWidget(audit_info)
        audit_header.addStretch()
        
        refresh_audit_btn = QPushButton(" Refresh Logs")
        refresh_audit_btn.setIcon(get_icon("refresh", "#334155", 14))
        refresh_audit_btn.setStyleSheet("padding: 8px 14px; background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: bold;")
        refresh_audit_btn.clicked.connect(self.load_audit_logs)
        audit_header.addWidget(refresh_audit_btn)
        
        audit_layout.addLayout(audit_header)
        
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(6)
        self.audit_table.setHorizontalHeaderLabels(["ID", "Timestamp", "User", "Action", "Module", "Details"])
        self.audit_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.audit_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                gridline-color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                padding: 10px;
                font-weight: bold;
                color: #475569;
                border: none;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        audit_layout.addWidget(self.audit_table)
        self.tabs.addTab(self.audit_tab, "Audit Activity Logs")

        layout.addWidget(self.tabs)
        
        self.all_users = []
        self.load_users()
        self.load_audit_logs()

    def refresh_data(self):
        self.load_users()
        self.load_audit_logs()

    def load_audit_logs(self):
        logs = get_audit_logs(limit=100)
        self.audit_table.setRowCount(len(logs))
        for row_idx, log in enumerate(logs):
            self.audit_table.setItem(row_idx, 0, QTableWidgetItem(str(log.get('id', ''))))
            self.audit_table.setItem(row_idx, 1, QTableWidgetItem(str(log.get('timestamp', ''))[:19]))
            self.audit_table.setItem(row_idx, 2, QTableWidgetItem(str(log.get('user_name', 'System'))))
            
            action_item = QTableWidgetItem(str(log.get('action', '')))
            action_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.audit_table.setItem(row_idx, 3, action_item)
            
            self.audit_table.setItem(row_idx, 4, QTableWidgetItem(str(log.get('module', ''))))
            self.audit_table.setItem(row_idx, 5, QTableWidgetItem(str(log.get('details', ''))))

    def load_users(self):
        self.all_users = get_all_users()
        self.filter_users()

    def filter_users(self):
        query = self.search_input.text().lower().strip()
        filtered = [
            u for u in self.all_users
            if query in u.get('name', '').lower() or query in u.get('email', '').lower() or query in u.get('role', '').lower()
        ]
        
        self.table.setRowCount(len(filtered))
        current_user = Session.get_instance().get_user()
        current_user_id = current_user.get('id') if current_user else None
        
        role_colors = {
            'owner': ('#7C3AED', '#F3E8FF'),   # Purple badge
            'manager': ('#2563EB', '#EFF6FF'), # Blue badge
            'staff': ('#059669', '#ECFDF5')    # Green badge
        }
        
        for row_idx, user in enumerate(filtered):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user['id'])))
            
            name_item = QTableWidgetItem(user.get('name', ''))
            name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row_idx, 1, name_item)
            
            self.table.setItem(row_idx, 2, QTableWidgetItem(user.get('email', '')))
            
            # Role Badge
            role_str = user.get('role', 'staff').lower()
            text_color, bg_color = role_colors.get(role_str, ('#334155', '#F1F5F9'))
            
            role_item = QTableWidgetItem(role_str.upper())
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            role_item.setForeground(QColor(text_color))
            role_item.setBackground(QColor(bg_color))
            role_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.table.setItem(row_idx, 3, role_item)
            
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(user.get('created_at', ''))[:10]))
            
            # Actions Container
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)
            
            edit_role_btn = QPushButton("Role")
            edit_role_btn.setStyleSheet("padding: 4px 8px; font-size: 12px; background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 4px;")
            edit_role_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_role_btn.clicked.connect(lambda _, u=user: self.open_edit_role_dialog(u))
            action_layout.addWidget(edit_role_btn)
            
            reset_pass_btn = QPushButton("Password")
            reset_pass_btn.setStyleSheet("padding: 4px 8px; font-size: 12px; background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 4px;")
            reset_pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            reset_pass_btn.clicked.connect(lambda _, u=user: self.open_reset_password_dialog(u))
            action_layout.addWidget(reset_pass_btn)
            
            # Don't allow user to delete themselves
            if user['id'] != current_user_id:
                del_btn = QPushButton("Delete")
                del_btn.setStyleSheet("padding: 4px 8px; font-size: 12px; background-color: #FEE2E2; color: #DC2626; border: 1px solid #FCA5A5; border-radius: 4px; font-weight: bold;")
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.clicked.connect(lambda _, u=user: self.handle_delete_user(u))
                action_layout.addWidget(del_btn)
                
            self.table.setCellWidget(row_idx, 5, action_widget)

    def open_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def open_edit_role_dialog(self, user):
        dialog = EditRoleDialog(user, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def open_reset_password_dialog(self, user):
        dialog = ResetPasswordDialog(user, self)
        dialog.exec()

    def handle_delete_user(self, user):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user account '{user.get('name')}' ({user.get('email')})?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success = delete_user(user['id'])
            if success:
                QMessageBox.information(self, "Deleted", "User account deleted successfully.")
                self.load_users()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete user account.")
