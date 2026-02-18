
import sys
from PySide6.QtWidgets import QApplication
from ui.reports import ReportsPage
from ui.dashboard import DashboardPage
from database.db import execute_write_query

def test_reports_page():
    print("Testing ReportsPage initialization...")
    try:
        page = ReportsPage()
        print("ReportsPage initialized successfully.")
    except Exception as e:
        print(f"ReportsPage initialization failed: {e}")
        raise

def test_dashboard_page():
    print("Testing DashboardPage initialization and refresh...")
    try:
        # Insert some dummy data for receivables/payables if needed
        execute_write_query("INSERT OR IGNORE INTO invoices (invoice_number, customer_id, date, due_date, grand_total, status) VALUES ('INV-TEST-DASH', 1, '2023-01-01', '2023-02-01', 1000.0, 'Sent')")
        execute_write_query("INSERT OR IGNORE INTO bills (bill_number, vendor_id, date, due_date, grand_total, status) VALUES ('BILL-TEST-DASH', 1, '2023-01-01', '2023-02-01', 500.0, 'Sent')")
        
        page = DashboardPage()
        page.refresh_data()
        print("DashboardPage initialized and refreshed successfully.")
    except Exception as e:
        print(f"DashboardPage initialization failed: {e}")
        raise

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        test_reports_page()
        test_dashboard_page()
        print("All tests passed.")
    except:
        sys.exit(1)
    
    sys.exit(0)
