import os
import sys
import json
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo, QPrintDialog
from PySide6.QtPdf import QPdfDocument
from PySide6.QtGui import QPainter, QPageLayout, QPageSize
from PySide6.QtCore import QSize, QRectF, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox

from database.db import execute_read_query, execute_write_query

def get_available_printers():
    """Returns a list of all available system printer names."""
    try:
        printers = QPrinterInfo.availablePrinterNames()
        return printers if printers else []
    except Exception as e:
        print(f"Error fetching printer names: {e}")
        return []

def get_default_printer_name():
    """Returns the system default printer name."""
    try:
        def_printer = QPrinterInfo.defaultPrinterName()
        return def_printer if def_printer else ""
    except Exception as e:
        print(f"Error fetching default printer: {e}")
        return ""

def get_printer_settings():
    """Fetches printer settings from database."""
    settings = {
        'default_doc_printer': '(System Default)',
        'default_thermal_printer': '(System Default)',
        'print_action_default': 'dialog' # options: 'dialog', 'direct', 'system_dialog', 'preview'
    }
    try:
        rows = execute_read_query("SELECT `key`, value FROM settings WHERE `key` IN ('default_doc_printer', 'default_thermal_printer', 'print_action_default')")
        for row in rows:
            settings[row['key']] = row['value']
    except Exception as e:
        print(f"Error reading printer settings from DB: {e}")
    return settings

def save_printer_settings(doc_printer, thermal_printer, action_default):
    """Saves printer settings to database."""
    try:
        execute_write_query("REPLACE INTO settings (`key`, value) VALUES ('default_doc_printer', ?)", (doc_printer,))
        execute_write_query("REPLACE INTO settings (`key`, value) VALUES ('default_thermal_printer', ?)", (thermal_printer,))
        execute_write_query("REPLACE INTO settings (`key`, value) VALUES ('print_action_default', ?)", (action_default,))
        return True, "Printer settings saved successfully."
    except Exception as e:
        return False, f"Failed to save printer settings: {str(e)}"

def print_pdf_file(pdf_path, printer_name=None, copies=1, parent=None):
    """
    Directly prints a PDF file to a specified printer using QPdfDocument & QPrinter.
    Returns (success: bool, message: str)
    """
    if not os.path.exists(pdf_path):
        return False, f"PDF file not found: {pdf_path}"

    try:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # Select printer
        if printer_name and printer_name != "(System Default)" and printer_name in get_available_printers():
            printer.setPrinterName(printer_name)
        else:
            def_name = get_default_printer_name()
            if def_name:
                printer.setPrinterName(def_name)

        if not printer.isValid():
            return False, f"Printer '{printer_name or 'Default'}' is invalid or offline."

        if copies > 1:
            printer.setCopyCount(copies)

        # Load PDF
        doc = QPdfDocument()
        doc.load(pdf_path)

        page_count = doc.pageCount()
        if page_count == 0:
            return False, "PDF document has 0 pages or is corrupted."

        painter = QPainter()
        if not painter.begin(printer):
            return False, "Failed to initialize printer painter."

        printer_page_rect = printer.pageLayout().paintRectPixels(printer.resolution())

        for i in range(page_count):
            if i > 0:
                printer.newPage()

            # Render at high DPI equivalent quality for sharpness
            psize = doc.pagePointSize(i)
            render_w = int(psize.width() * 4)
            render_h = int(psize.height() * 4)

            img = doc.render(i, QSize(render_w, render_h))
            if not img.isNull():
                painter.drawImage(printer_page_rect, img)

        painter.end()
        return True, f"Successfully sent to printer '{printer.printerName()}'."

    except Exception as e:
        # Fallback for Windows shell print if QtPdf rendering encounters driver specific issues
        if sys.platform.startswith('win'):
            try:
                import win32api
                import win32print
                p_name = printer_name if (printer_name and printer_name != "(System Default)") else win32print.GetDefaultPrinter()
                win32api.ShellExecute(0, "printto", pdf_path, f'"{p_name}"', ".", 0)
                return True, f"Sent to printer '{p_name}' via Windows Print."
            except Exception as win_e:
                return False, f"Print error: {str(e)} (Fallback error: {str(win_e)})"
        return False, f"Failed to print PDF: {str(e)}"

def open_system_print_dialog(pdf_path, printer_name=None, parent=None):
    """
    Opens native/Qt QPrintDialog so the user can configure advanced print options before printing.
    """
    if not os.path.exists(pdf_path):
        QMessageBox.critical(parent, "Error", f"PDF file not found: {pdf_path}")
        return False

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    if printer_name and printer_name != "(System Default)" and printer_name in get_available_printers():
        printer.setPrinterName(printer_name)

    dialog = QPrintDialog(printer, parent)
    dialog.setWindowTitle("Print Document")
    
    if dialog.exec() == QPrintDialog.DialogCode.Accepted:
        try:
            doc = QPdfDocument()
            doc.load(pdf_path)
            
            painter = QPainter()
            if not painter.begin(printer):
                QMessageBox.critical(parent, "Error", "Failed to start printing engine.")
                return False

            printer_page_rect = printer.pageLayout().paintRectPixels(printer.resolution())
            for i in range(doc.pageCount()):
                if i > 0:
                    printer.newPage()
                psize = doc.pagePointSize(i)
                render_w = int(psize.width() * 4)
                render_h = int(psize.height() * 4)
                img = doc.render(i, QSize(render_w, render_h))
                if not img.isNull():
                    painter.drawImage(printer_page_rect, img)

            painter.end()
            QMessageBox.information(parent, "Print Success", f"Printed to {printer.printerName()}")
            return True
        except Exception as e:
            QMessageBox.critical(parent, "Print Error", str(e))
            return False
    return False

def open_pdf_in_viewer(pdf_path, parent=None):
    """Opens PDF in the operating system's default viewer."""
    if os.path.exists(pdf_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))
        return True
    else:
        if parent:
            QMessageBox.critical(parent, "Error", f"PDF file not found: {pdf_path}")
        return False

def handle_print_workflow(parent, pdf_path, doc_type="document", doc_title="Document"):
    """
    Central workflow handler for printing PDFs.
    Checks saved user settings and presents PrinterSelectionDialog or direct print based on preferences.
    """
    from ui.printer_dialog import PrinterSelectionDialog

    settings = get_printer_settings()
    default_action = settings.get('print_action_default', 'dialog')
    
    if doc_type in ['thermal_80', 'thermal_58']:
        target_printer = settings.get('default_thermal_printer', '(System Default)')
    else:
        target_printer = settings.get('default_doc_printer', '(System Default)')

    if default_action == 'direct':
        success, msg = print_pdf_file(pdf_path, printer_name=target_printer, parent=parent)
        if success:
            QMessageBox.information(parent, "Print Complete", msg)
        else:
            QMessageBox.warning(parent, "Print Failed", f"{msg}\nOpening Printer Selection Dialog...")
            dialog = PrinterSelectionDialog(pdf_path=pdf_path, doc_title=doc_title, doc_type=doc_type, parent=parent)
            dialog.exec()

    elif default_action == 'system_dialog':
        open_system_print_dialog(pdf_path, printer_name=target_printer, parent=parent)

    elif default_action == 'preview':
        open_pdf_in_viewer(pdf_path, parent=parent)

    else: # 'dialog' or default
        dialog = PrinterSelectionDialog(pdf_path=pdf_path, doc_title=doc_title, doc_type=doc_type, parent=parent)
        dialog.exec()
