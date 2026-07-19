STYLESHEET = """
QMainWindow {
    background-color: #F8FAFC;
}

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 14px;
    color: #1E293B;
}

/* Sidebar */
#Sidebar {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
    min-width: 255px;
    max-width: 255px;
}

#Sidebar QPushButton {
    background-color: transparent;
    color: #475569;
    border: none;
    text-align: left;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    margin: 3px 10px;
    min-height: 38px;
}

#Sidebar QPushButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

#Sidebar QPushButton:checked {
    background-color: #EFF6FF;
    color: #2563EB;
    font-weight: 700;
}

/* Sidebar ScrollArea */
#SidebarScroll {
    border: none;
    background: transparent;
}

#SidebarScroll > QWidget > QWidget {
    background: transparent;
}

/* Header Bar */
#Header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    min-height: 60px;
    max-height: 60px;
}

#Header QLabel {
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
}

/* Content Area */
#ContentArea {
    background-color: #F8FAFC;
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
    color: #475569;
    padding: 10px 12px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    font-weight: 700;
    font-size: 13px;
}

/* Buttons */
QPushButton.PrimaryButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    padding: 9px 18px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.PrimaryButton:hover {
    background-color: #1D4ED8;
}

QPushButton.SecondaryButton {
    background-color: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    padding: 9px 18px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 13px;
}

QPushButton.SecondaryButton:hover {
    background-color: #F8FAFC;
    border-color: #94A3B8;
}

/* Inputs */
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #2563EB;
    font-size: 13px;
    color: #0F172A;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QTextEdit:focus {
    border-color: #2563EB;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    background-color: #FFFFFF;
    padding: 12px;
}

QTabBar::tab {
    background: #F1F5F9;
    color: #64748B;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    padding: 9px 18px;
    font-weight: 600;
    font-size: 13px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background: #FFFFFF;
    color: #2563EB;
    border-top: 2px solid #2563EB;
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
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #F1F5F9;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #CBD5E1;
    min-width: 24px;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""
