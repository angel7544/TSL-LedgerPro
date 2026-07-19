import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import init_db, execute_write_query
from auth.auth_logic import log_audit_action, get_audit_logs
from pdf.thermal_generator import generate_thermal_receipt

def test_thermal_receipt_generation():
    print("=== Testing Thermal POS Receipt Generator (80mm & 58mm) ===")
    sample_invoice = {
        'company_name': 'The Space Labs POS',
        'company_address': '123 Tech Street\nCity, State 400001',
        'company_phone': '+91 9876543210',
        'company_gstin': '27AAAAA0000A1Z5',
        'invoice_number': 'INV-TEST-POS-001',
        'date': '2026-07-19',
        'salesperson': 'Admin Cashier',
        'customer_name': 'Walk-in Customer',
        'subtotal': 1500.00,
        'tax_amount': 270.00,
        'discount_amount': 50.00,
        'grand_total': 1720.00,
        'items': [
            {'name': 'Wireless Optical Mouse', 'quantity': 2, 'rate': 500.0, 'amount': 1000.0},
            {'name': 'USB-C Fast Cable 2m', 'quantity': 1, 'rate': 500.0, 'amount': 500.0}
        ]
    }
    
    file_80 = generate_thermal_receipt(sample_invoice, paper_width_mm=80)
    assert os.path.exists(file_80), f"Failed 80mm receipt generation: {file_80}"
    print(f"Generated 80mm receipt: {file_80} - OK")

    file_58 = generate_thermal_receipt(sample_invoice, paper_width_mm=58)
    assert os.path.exists(file_58), f"Failed 58mm receipt generation: {file_58}"
    print(f"Generated 58mm receipt: {file_58} - OK")

def test_audit_logging():
    print("\n=== Testing Audit Logging Engine ===")
    init_db()
    
    # Log test action
    log_audit_action("TEST_ACTION", "Test Module", "REC-101", "Testing v3.5.0 audit logger")
    
    logs = get_audit_logs(limit=10)
    actions = [l.get('action') for l in logs]
    assert "TEST_ACTION" in actions, "Audit log record not found"
    print("Audit log creation & retrieval PASSED!")

if __name__ == "__main__":
    test_thermal_receipt_generation()
    test_audit_logging()
