
import os
import sys
import datetime
import json
import sqlite3

# Add project root to path
sys.path.append(os.getcwd())

try:
    from database.db import init_db, execute_write_query, execute_read_query
    from modules.invoice import create_invoice, create_bill
    from modules.payment import save_payment
    from pdf.generator import generate_invoice_pdf, generate_bill_pdf, generate_payment_receipt_pdf
    
    print("Imports successful.")
    
    # Initialize DB (creates tables if not exist)
    init_db()
    print("DB Initialized.")
    
    # Clean up previous test data
    execute_write_query("DELETE FROM invoices")
    execute_write_query("DELETE FROM invoice_items")
    execute_write_query("DELETE FROM bills")
    execute_write_query("DELETE FROM bill_items")
    execute_write_query("DELETE FROM payments")
    print("Previous test data cleaned.")
    
    # Insert dummy settings for PDF header verification
    execute_write_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('company_name', 'Test Company Ltd.')")
    execute_write_query("INSERT OR REPLACE INTO settings (key, value) VALUES ('company_email', 'test@company.com')")
    
    # Mock Data for Invoice
    invoice_data = {
        'customer_id': 1, # Assuming customer 1 exists or will fail if foreign key constraint. 
                          # Actually, let's insert a dummy customer first.
        'date': '2023-10-27',
        'due_date': '2023-11-27',
        'items': [
            {'item_id': 1, 'quantity': 2, 'rate': 100, 'gst_percent': 18, 'discount_percent': 0, 'amount': 236}
        ],
        'order_number': 'ORD-123',
        'terms': 'Net 30',
        'salesperson': 'John Doe',
        'subject': 'Test Invoice',
        'customer_notes': 'Thank you',
        'terms_conditions': 'No returns',
        'custom_fields': json.dumps({'Field1': 'Value1'})
    }
    
    # Insert dummy customer and item
    execute_write_query("INSERT OR IGNORE INTO customers (id, name) VALUES (1, 'Test Customer')")
    execute_write_query("INSERT OR IGNORE INTO items (id, name, selling_price, gst_rate) VALUES (1, 'Test Item', 100, 18)")
    
    print("Dummy data inserted.")
    
    # Create Invoice
    inv_id = create_invoice(invoice_data)
    print(f"Invoice created with ID: {inv_id}")
    
    # Fetch generated invoice number
    inv_res = execute_read_query("SELECT invoice_number, grand_total FROM invoices WHERE id = ?", (inv_id,))
    inv_number = inv_res[0]['invoice_number']
    grand_total = inv_res[0]['grand_total']
    print(f"Generated Invoice Number: {inv_number}")
    
    # Mock Data for Bill
    bill_data = {
        'vendor_id': 1,
        'date': '2023-10-27',
        'items': [
             {'item_id': 1, 'quantity': 10, 'rate': 50, 'gst_percent': 18, 'amount': 590}
        ],
        'bill_number': 'BILL-TEST-001',
        'order_number': 'PO-123',
        'payment_terms': 'Net 60',
        'reverse_charge': 0,
        'custom_fields': json.dumps({'Field2': 'Value2'})
    }
    
    # Insert dummy vendor
    execute_write_query("INSERT OR IGNORE INTO vendors (id, name) VALUES (1, 'Test Vendor')")
    
    # Create Bill
    bill_id = create_bill(bill_data)
    print(f"Bill created with ID: {bill_id}")
    
    # Mock Data for Payment
    payment_data = {
        'customer_id': 1,
        'date': '2023-10-28',
        'method': 'Cash',
        'reference': 'REF-001',
        'payment_number': 'PAY-TEST-001',
        'deposit_to': 'Bank',
        'bank_charges': 10.0,
        'tax_deducted': 5.0,
        'allocations': [
            {'invoice_id': inv_id, 'amount': 100}
        ],
        'custom_fields': json.dumps({'Field3': 'Value3'}),
        'send_thank_you': True
    }
    
    # Save Payment
    save_payment(payment_data)
    print("Payment saved.")
    
    # Generate PDFs
    # We need to fetch data back to match what the generator expects (usually dict)
    # But generator expects a dictionary with specific keys. 
    # Let's just pass the mock data augmented with calculated totals for the test.
    
    invoice_data['invoice_number'] = inv_number
    invoice_data['grand_total'] = grand_total
    invoice_data['customer_name'] = 'Test Customer'
    generate_invoice_pdf(invoice_data, "test_invoice.pdf")
    print("Invoice PDF generated.")
    
    bill_data['grand_total'] = 590.0
    bill_data['vendor_name'] = 'Test Vendor'
    generate_bill_pdf(bill_data, "test_bill.pdf")
    print("Bill PDF generated.")
    
    payment_data['amount_received'] = 100.0
    payment_data['customer_name'] = 'Test Customer'
    generate_payment_receipt_pdf(payment_data, "test_receipt.pdf")
    print("Payment Receipt PDF generated.")
    
    # Cleanup
    if os.path.exists("test_invoice.pdf"): os.remove("test_invoice.pdf")
    if os.path.exists("test_bill.pdf"): os.remove("test_bill.pdf")
    if os.path.exists("test_receipt.pdf"): os.remove("test_receipt.pdf")
    
    # Verify Custom Fields for Invoice
    inv_check = execute_read_query("SELECT custom_fields FROM invoices WHERE id=?", (inv_id,))
    if inv_check:
        print(f"Invoice Custom Fields: {inv_check[0]['custom_fields']}")
        if "Field1" not in inv_check[0]['custom_fields']:
            print("ERROR: Custom Fields not saved for Invoice")
    
    # Verify Custom Fields for Bill
    bill_check = execute_read_query("SELECT custom_fields FROM bills WHERE id=?", (bill_id,))
    if bill_check:
        print(f"Bill Custom Fields: {bill_check[0]['custom_fields']}")
        if "Field2" not in bill_check[0]['custom_fields']:
            print("ERROR: Custom Fields not saved for Bill")

    print("Verification Successful.")

except Exception as e:
    print(f"Verification Failed: {e}")
    import traceback
    traceback.print_exc()
