STYLESHEET = """
QMainWindow {
    background-color: #F5F7FA;
}

QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: #334155;
}

/* Sidebar */
#Sidebar {
    background-color: #1E293B;
    color: #FFFFFF;
    min-width: 220px;
    max-width: 220px;
}

#Sidebar QPushButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    text-align: left;
    padding: 12px 20px;
    font-weight: 500;
    border-radius: 8px;
    margin: 4px 10px;
}

#Sidebar QPushButton:hover {
    background-color: #334155;
    color: #FFFFFF;
}

#Sidebar QPushButton:checked {
    background-color: #2563EB;
    color: #FFFFFF;
}

/* Header */
#Header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    min-height: 60px;
}

#Header QLabel {
    font-size: 16px;
    font-weight: 600;
    color: #1E293B;
}

/* Content Area */
#ContentArea {
    background-color: #F5F7FA;
    padding: 20px;
}

/* Cards */
.Card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 20px;
}

/* Tables */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    selection-background-color: #EFF6FF;
    selection-color: #1E293B;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    font-weight: 600;
}

/* Buttons */
QPushButton.PrimaryButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #1D4ED8;
}

QPushButton.SecondaryButton {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
}

QPushButton.SecondaryButton:hover {
    background-color: #F8FAFC;
    border-color: #94A3B8;
}

/* Inputs */
QLineEdit, QComboBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #2563EB;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #2563EB;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F1F5F9;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
