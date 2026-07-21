import json
from PySide6.QtWidgets import (
    QGroupBox, QFormLayout, QLineEdit, QComboBox, QDateEdit, QLabel, QVBoxLayout, QWidget
)
from PySide6.QtCore import QDate
from database.db import execute_read_query

def load_custom_fields_config(module_name):
    """
    Loads custom fields definitions from settings for module ('invoice', 'bill', 'payment').
    Returns list of dicts: [{'name': '...', 'type': '...', 'default': '...'}, ...]
    """
    key = f"custom_fields_{module_name.lower()}"
    try:
        rows = execute_read_query("SELECT value FROM settings WHERE `key` = ?", (key,))
        if rows and rows[0]['value']:
            return json.loads(rows[0]['value'])
    except Exception as e:
        print(f"Error loading custom fields for {module_name}: {e}")
    return []

class CustomFieldsWidget(QGroupBox):
    """
    Dynamic Form Widget that renders configured Custom Fields for Invoices, Bills, or Payments.
    """
    def __init__(self, module_name, initial_json='{}', parent=None):
        super().__init__("Custom Fields / अतिरिक्त फ़ील्ड्स", parent)
        self.module_name = module_name.lower()
        self.field_inputs = {}
        
        # Parse initial values if editing an existing record
        self.initial_values = {}
        if initial_json:
            try:
                if isinstance(initial_json, str):
                    self.initial_values = json.loads(initial_json)
                elif isinstance(initial_json, dict):
                    self.initial_values = initial_json
            except Exception as e:
                print(f"Error parsing initial custom_fields JSON: {e}")

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #F8FAFC;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        self.init_ui()

    def init_ui(self):
        form_layout = QFormLayout(self)
        form_layout.setSpacing(10)
        
        configs = load_custom_fields_config(self.module_name)
        if not configs:
            self.setVisible(False)
            return

        self.setVisible(True)

        for cfg in configs:
            fname = cfg.get('name', '').strip()
            ftype = cfg.get('type', 'Text').strip()
            fdefault = cfg.get('default', '').strip()

            if not fname:
                continue

            current_val = self.initial_values.get(fname, fdefault)

            if ftype == "Date":
                input_widget = QDateEdit()
                input_widget.setCalendarPopup(True)
                if current_val:
                    qd = QDate.fromString(current_val, "yyyy-MM-dd")
                    if qd.isValid():
                        input_widget.setDate(qd)
                    else:
                        input_widget.setDate(QDate.currentDate())
                else:
                    input_widget.setDate(QDate.currentDate())
                input_widget.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px; background: white;")

            elif ftype == "Dropdown":
                input_widget = QComboBox()
                input_widget.setStyleSheet("padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px; background: white;")
                # If default contains comma-separated options: e.g. "Option A, Option B"
                options = [opt.strip() for opt in fdefault.split(",") if opt.strip()] if "," in fdefault else [fdefault] if fdefault else []
                if not options:
                    options = ["Default", "Option 1", "Option 2"]
                input_widget.addItems(options)
                if current_val in options:
                    input_widget.setCurrentText(current_val)

            else: # Text or Number
                input_widget = QLineEdit()
                input_widget.setText(str(current_val))
                input_widget.setPlaceholderText(f"Enter {fname}")
                input_widget.setStyleSheet("padding: 6px; border: 1px solid #CBD5E1; border-radius: 4px; background: white;")

            form_layout.addRow(f"{fname}:", input_widget)
            self.field_inputs[fname] = (ftype, input_widget)

    def get_custom_fields_dict(self):
        """Returns a dict of custom field values."""
        result = {}
        for fname, (ftype, widget) in self.field_inputs.items():
            if ftype == "Date":
                result[fname] = widget.date().toString("yyyy-MM-dd")
            elif ftype == "Dropdown":
                result[fname] = widget.currentText()
            else:
                result[fname] = widget.text().strip()
        return result

    def get_custom_fields_json(self):
        """Returns JSON string representation of custom fields."""
        return json.dumps(self.get_custom_fields_dict())
