
import sys
import datetime
from database.db import execute_write_query, execute_read_query, execute_transaction
from modules.payment import save_payment, get_customer_credits, save_bill_payment, get_vendor_credits

def test_credit_consumption():
    print("Testing Credit Consumption Flow...")
    
    # --- Customer Test ---
    print("\n--- Customer Test ---")
    cust_name = f"Credit User {datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query("INSERT INTO customers (name) VALUES (?)", (cust_name,))
    cust_id = execute_read_query("SELECT id FROM customers WHERE name = ?", (cust_name,))[0]['id']
    
    # 1. Create Invoice A (1000)
    inv_num = f"INV-CREDIT-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO invoices (invoice_number, customer_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (inv_num, cust_id, '2023-01-01', 1000.0, 'Sent')
    )
    inv_id = execute_read_query("SELECT id FROM invoices WHERE invoice_number = ?", (inv_num,))[0]['id']
    print(f"Created Invoice {inv_num} (1000.0)")
    
    # 2. Create Advance Payment (500)
    print("Creating Advance Payment of 500...")
    save_payment({
        'customer_id': cust_id,
        'amount_received': 500.0,
        'date': '2023-01-02',
        'method': 'Cash',
        'reference': 'ADV-1',
        'allocations': [] # No allocation = Credit
    })
    
    credits = get_customer_credits(cust_id)
    print(f"Credits Available: {credits} (Expected 500.0)")
    
    # 3. Pay Invoice A using 500 Cash + 500 Credit
    print("Paying Invoice A with 500 Cash + Credits...")
    save_payment({
        'customer_id': cust_id,
        'amount_received': 500.0,
        'date': '2023-01-03',
        'method': 'Cash',
        'reference': 'PAY-MIX',
        'allocations': [{'invoice_id': inv_id, 'amount': 1000.0}],
        'use_credits': True
    })
    
    # Verify Invoice Status
    status = execute_read_query("SELECT status FROM invoices WHERE id = ?", (inv_id,))[0]['status']
    print(f"Invoice Status: {status} (Expected 'Paid')")
    
    # Verify Credits Consumed
    credits = get_customer_credits(cust_id)
    print(f"Credits Remaining: {credits} (Expected 0.0)")
    
    if status == 'Paid' and credits == 0.0:
        print("SUCCESS: Customer Credit + Cash payment worked.")
    else:
        print("FAIL: Customer Credit logic failed.")

    # --- Vendor Test (Partial Credit Use) ---
    print("\n--- Vendor Test ---")
    vend_name = f"Credit Vendor {datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query("INSERT INTO vendors (name) VALUES (?)", (vend_name,))
    vend_id = execute_read_query("SELECT id FROM vendors WHERE name = ?", (vend_name,))[0]['id']
    
    # 1. Create Bill B (1000)
    bill_num = f"BILL-CREDIT-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill_num, vend_id, '2023-01-01', 1000.0, 'Sent')
    )
    bill_id = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill_num,))[0]['id']
    print(f"Created Bill {bill_num} (1000.0)")
    
    # 2. Create Advance Payment (2000)
    print("Creating Advance Payment of 2000...")
    save_bill_payment({
        'vendor_id': vend_id,
        'amount_paid': 2000.0,
        'date': '2023-01-02',
        'method': 'Bank Transfer',
        'reference': 'ADV-V-1',
        'allocations': []
    })
    
    credits = get_vendor_credits(vend_id)
    print(f"Credits Available: {credits} (Expected 2000.0)")
    
    # 3. Pay Bill B using ONLY Credits (1000)
    print("Paying Bill B with Credits only...")
    save_bill_payment({
        'vendor_id': vend_id,
        'amount_paid': 0.0,
        'date': '2023-01-03',
        'method': 'Bank Transfer',
        'reference': 'PAY-CREDIT-ONLY',
        'allocations': [{'bill_id': bill_id, 'amount': 1000.0}],
        'use_credits': True
    })
    
    # Verify Bill Status
    status = execute_read_query("SELECT status FROM bills WHERE id = ?", (bill_id,))[0]['status']
    print(f"Bill Status: {status} (Expected 'Paid')")
    
    # Verify Credits Remaining
    credits = get_vendor_credits(vend_id)
    print(f"Credits Remaining: {credits} (Expected 1000.0)")
    
    if status == 'Paid' and abs(credits - 1000.0) < 0.01:
        print("SUCCESS: Vendor Partial Credit payment worked.")
    else:
        print("FAIL: Vendor Credit logic failed.")

if __name__ == "__main__":
    try:
        test_credit_consumption()
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
