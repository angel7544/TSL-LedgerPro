
import sys
from database.db import execute_write_query, execute_read_query
from modules.payment import get_unpaid_invoices, save_payment, get_unpaid_bills, save_bill_payment
import datetime

def test_payment_flow():
    print("Testing Payment Flow...")
    
    # 1. Setup: Create a test customer and invoice
    execute_write_query("INSERT OR IGNORE INTO customers (name) VALUES ('Payment Test Customer')")
    cust_res = execute_read_query("SELECT id FROM customers WHERE name = 'Payment Test Customer'")
    cust_id = cust_res[0]['id']
    
    # Create Invoice 1 (1000.00)
    inv_num = f"INV-PAY-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO invoices (invoice_number, customer_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (inv_num, cust_id, '2023-01-01', 1000.0, 'Sent')
    )
    inv_res = execute_read_query("SELECT id FROM invoices WHERE invoice_number = ?", (inv_num,))
    inv_id = inv_res[0]['id']
    
    print(f"Created Invoice {inv_num} (ID: {inv_id}) for Customer {cust_id}")
    
    # 2. Check Unpaid Invoices (Should be 1000)
    unpaid = get_unpaid_invoices(cust_id)
    target_inv = next((i for i in unpaid if i['id'] == inv_id), None)
    if not target_inv:
        print("Error: Invoice not found in unpaid list")
        return
        
    print(f"Initial Balance Due: {target_inv['balance_due']} (Expected 1000.0)")
    
    # 3. Record Partial Payment (400)
    print("Recording partial payment of 400...")
    payment_data = {
        'customer_id': cust_id,
        'date': '2023-01-02',
        'method': 'Cash',
        'reference': 'REF1',
        'allocations': [{'invoice_id': inv_id, 'amount': 400.0}]
    }
    save_payment(payment_data)
    
    # 4. Check Balance Due (Should be 600)
    unpaid = get_unpaid_invoices(cust_id)
    target_inv = next((i for i in unpaid if i['id'] == inv_id), None)
    if not target_inv:
        print("Error: Invoice not found after partial payment")
        return
        
    print(f"Balance Due after 400 payment: {target_inv['balance_due']} (Expected 600.0)")
    if abs(target_inv['balance_due'] - 600.0) > 0.01:
        print("FAIL: Balance calculation incorrect")
        
    # 5. Record Remaining Payment (600)
    print("Recording remaining payment of 600...")
    payment_data['allocations'] = [{'invoice_id': inv_id, 'amount': 600.0}]
    save_payment(payment_data)
    
    # 6. Check Status (Should be Paid and not in unpaid list)
    unpaid = get_unpaid_invoices(cust_id)
    target_inv = next((i for i in unpaid if i['id'] == inv_id), None)
    
    if target_inv:
        print(f"Error: Invoice still in unpaid list with balance {target_inv['balance_due']}")
    else:
        print("Success: Invoice removed from unpaid list (Fully Paid)")
        
    # Verify Status in DB
    final_status = execute_read_query("SELECT status FROM invoices WHERE id = ?", (inv_id,))[0]['status']
    print(f"Final Invoice Status: {final_status} (Expected 'Paid')")

def test_bill_payment_flow():
    print("Testing Bill Payment Flow...")
    
    execute_write_query("INSERT OR IGNORE INTO vendors (name) VALUES ('Payment Test Vendor')")
    vend_res = execute_read_query("SELECT id FROM vendors WHERE name = 'Payment Test Vendor'")
    vend_id = vend_res[0]['id']
    
    bill_num = f"BILL-PAY-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill_num, vend_id, '2023-01-01', 500.0, 'Draft')
    )
    bill_res = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill_num,))
    bill_id = bill_res[0]['id']
    
    execute_write_query("UPDATE bills SET status = 'Sent' WHERE id = ?", (bill_id,))
    
    unpaid = get_unpaid_bills(vend_id)
    target_bill = next((b for b in unpaid if b['id'] == bill_id), None)
    if not target_bill:
        print("Error: Bill not found in unpaid list")
        return
        
    print(f"Initial Bill Balance Due: {target_bill['balance_due']} (Expected 500.0)")
    
    print("Recording bill payment of 500...")
    payment_data = {
        'vendor_id': vend_id,
        'date': '2023-01-05',
        'method': 'Bank Transfer',
        'reference': 'BPAY1',
        'allocations': [{'bill_id': bill_id, 'amount': 500.0}]
    }
    save_bill_payment(payment_data)
    
    unpaid = get_unpaid_bills(vend_id)
    target_bill = next((b for b in unpaid if b['id'] == bill_id), None)
    
    if target_bill:
        print(f"Error: Bill still in unpaid list with balance {target_bill['balance_due']}")
    else:
        print("Success: Bill removed from unpaid list (Fully Paid)")
        
    final_status = execute_read_query("SELECT status FROM bills WHERE id = ?", (bill_id,))[0]['status']
    print(f"Final Bill Status: {final_status} (Expected 'Paid')")

if __name__ == "__main__":
    try:
        test_payment_flow()
        test_bill_payment_flow()
    except Exception as e:
        print(f"Test Failed: {e}")
