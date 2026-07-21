import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QCheckBox, QGroupBox, QFrame, QMessageBox, QListView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.icons import get_icon
from modules.printer_service import (
    get_available_printers, get_default_printer_name,
    get_printer_settings, save_printer_settings,
    print_pdf_file, open_system_print_dialog, open_pdf_in_viewer
)

class PrinterSelectionDialog(QDialog):
    def __init__(self, pdf_path, doc_title="Document", doc_type="document", parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.doc_title = doc_title
        self.doc_type = doc_type
        
        self.setWindowTitle(f"Print - {doc_title}")
        self.setFixedWidth(520)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Box
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon("print", "#2563EB", 32).pixmap(32, 32))
        
        text_layout = QVBoxLayout()
        title_lbl = QLabel(f"Print: {self.doc_title}")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        
        doc_type_str = "A4 Document"
        if self.doc_type == "thermal_80":
            doc_type_str = "80mm POS Thermal Receipt"
        elif self.doc_type == "thermal_58":
            doc_type_str = "58mm POS Thermal Receipt"
        elif self.doc_type == "bill":
            doc_type_str = "Purchase Bill PDF"
        elif self.doc_type == "report":
            doc_type_str = "Report PDF"

        file_lbl = QLabel(f"Type: {doc_type_str} | File: {os.path.basename(self.pdf_path)}")
        file_lbl.setStyleSheet("font-size: 12px; color: #64748B;")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(file_lbl)
        
        header_layout.addWidget(icon_lbl)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Printer Settings Group
        settings_group = QGroupBox("Printer Configuration")
        settings_group.setStyleSheet("font-weight: bold; color: #1E293B;")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)
        
        # Printer Dropdown Label + Combo
        printer_lbl = QLabel("Select Printer Service:")
        printer_lbl.setStyleSheet("font-weight: normal; color: #334155;")
        
        self.printer_combo = QComboBox()
        self.printer_combo.setView(QListView())
        self.printer_combo.setMaxVisibleItems(8)
        self.printer_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                color: #0F172A;
                font-weight: 500;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #94A3B8;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                background: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                color: #0F172A;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
                padding: 4px;
                outline: 0px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 28px;
                padding: 4px 8px;
            }
        """)
        
        printers = get_available_printers()
        default_sys_printer = get_default_printer_name()
        
        self.printer_combo.addItem("(System Default)", "(System Default)")
        for p in printers:
            label = f"{p} (Default)" if p == default_sys_printer else p
            self.printer_combo.addItem(label, p)

        # Preselect configured printer preference if available
        saved_settings = get_printer_settings()
        if self.doc_type in ["thermal_80", "thermal_58"]:
            pref = saved_settings.get('default_thermal_printer', '(System Default)')
        else:
            pref = saved_settings.get('default_doc_printer', '(System Default)')

        idx = self.printer_combo.findData(pref)
        if idx >= 0:
            self.printer_combo.setCurrentIndex(idx)
            
        group_layout.addWidget(printer_lbl)
        group_layout.addWidget(self.printer_combo)
        
        # Copies Row
        copies_layout = QHBoxLayout()
        copies_lbl = QLabel("Number of Copies:")
        copies_lbl.setStyleSheet("font-weight: normal; color: #334155;")
        
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 99)
        self.copies_spin.setValue(1)
        self.copies_spin.setFixedWidth(80)
        self.copies_spin.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 6px; font-weight: normal;")
        
        copies_layout.addWidget(copies_lbl)
        copies_layout.addWidget(self.copies_spin)
        copies_layout.addStretch()
        group_layout.addLayout(copies_layout)
        
        # Default Printer Checkbox
        self.set_default_chk = QCheckBox(f"Save as default printer for {doc_type_str}s")
        self.set_default_chk.setStyleSheet("font-weight: normal; color: #475569; margin-top: 5px;")
        group_layout.addWidget(self.set_default_chk)
        
        settings_group.setLayout(group_layout)
        layout.addWidget(settings_group)
        
        # Action Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        primary_btn_row = QHBoxLayout()
        
        # Print Direct Button
        print_btn = QPushButton(" Print Direct")
        print_btn.setIcon(get_icon("print", "#FFFFFF", 16))
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB; color: white; border-radius: 6px; padding: 10px 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        print_btn.clicked.connect(self.do_direct_print)
        
        # System Print Dialog Button
        sys_dialog_btn = QPushButton(" System Print Dialog...")
        sys_dialog_btn.setIcon(get_icon("settings", "#1E293B", 16))
        sys_dialog_btn.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9; color: #0F172A; border: 1px solid #CBD5E1; border-radius: 6px; padding: 10px 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        sys_dialog_btn.clicked.connect(self.do_system_dialog)
        
        primary_btn_row.addWidget(print_btn)
        primary_btn_row.addWidget(sys_dialog_btn)
        btn_layout.addLayout(primary_btn_row)
        
        secondary_btn_row = QHBoxLayout()
        
        # View PDF Button
        view_pdf_btn = QPushButton(" View / Save PDF")
        view_pdf_btn.setIcon(get_icon("view", "#334155", 14))
        view_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; color: #334155; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 14px; font-weight: 500;
            }
            QPushButton:hover { background-color: #F8FAFC; }
        """)
        view_pdf_btn.clicked.connect(self.do_view_pdf)
        
        # Cancel Button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; color: #64748B; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 14px; font-weight: 500;
            }
            QPushButton:hover { background-color: #F8FAFC; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        secondary_btn_row.addWidget(view_pdf_btn)
        secondary_btn_row.addStretch()
        secondary_btn_row.addWidget(cancel_btn)
        btn_layout.addLayout(secondary_btn_row)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def get_selected_printer(self):
        return self.printer_combo.currentData()

    def check_save_default_printer(self):
        if self.set_default_chk.isChecked():
            selected = self.get_selected_printer()
            saved = get_printer_settings()
            if self.doc_type in ["thermal_80", "thermal_58"]:
                doc_p = saved.get('default_doc_printer', '(System Default)')
                therm_p = selected
            else:
                doc_p = selected
                therm_p = saved.get('default_thermal_printer', '(System Default)')
            act = saved.get('print_action_default', 'dialog')
            save_printer_settings(doc_p, therm_p, act)

    def do_direct_print(self):
        printer_name = self.get_selected_printer()
        copies = self.copies_spin.value()
        self.check_save_default_printer()
        
        success, msg = print_pdf_file(self.pdf_path, printer_name=printer_name, copies=copies, parent=self)
        if success:
            QMessageBox.information(self, "Print Direct", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Print Direct Error", msg)

    def do_system_dialog(self):
        printer_name = self.get_selected_printer()
        self.check_save_default_printer()
        self.accept()
        open_system_print_dialog(self.pdf_path, printer_name=printer_name, parent=self.parent())

    def do_view_pdf(self):
        self.check_save_default_printer()
        open_pdf_in_viewer(self.pdf_path, parent=self)
        self.accept()
