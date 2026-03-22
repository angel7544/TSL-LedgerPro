
import sys
import datetime
from database.db import execute_write_query, execute_read_query
from modules.payment import save_bill_payment

def test_vendor_credits():
    print("Testing Vendor Credits Flow...")
    
    # 1. Setup: Create a test vendor
    vendor_name = f"Credit Test Vendor {datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))
    vend_res = execute_read_query("SELECT id FROM vendors WHERE name = ?", (vendor_name,))
    vend_id = vend_res[0]['id']
    print(f"Created Vendor: {vendor_name} (ID: {vend_id})")
    
    # 2. Create a Bill (Amount: 500)
    bill_num = f"BILL-CREDIT-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill_num, vend_id, '2023-01-01', 500.0, 'Sent')
    )
    bill_res = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill_num,))
    bill_id = bill_res[0]['id']
    print(f"Created Bill: {bill_num} (ID: {bill_id}) Amount: 500.0")
    
    # 3. Record Payment with Excess Amount (Paid: 700, Allocated: 500, Excess: 200)
    print("Recording payment of 700 (Allocating 500 to bill)...")
    payment_data = {
        'vendor_id': vend_id,
        'amount_paid': 700.0,
        'date': '2023-01-05',
        'method': 'Bank Transfer',
        'reference': 'BPAY-CREDIT',
        'allocations': [{'bill_id': bill_id, 'amount': 500.0}]
    }
    save_bill_payment(payment_data)
    
    # 4. Verify Bill Status
    bill_status = execute_read_query("SELECT status FROM bills WHERE id = ?", (bill_id,))[0]['status']
    print(f"Bill Status: {bill_status} (Expected 'Paid')")
    if bill_status != 'Paid':
        print("FAIL: Bill status is not Paid")
    
    # 5. Verify Vendor Credits
    # Query from VendorsPage logic
    query = """
        SELECT v.*, 
        COALESCE((SELECT SUM(amount) FROM payments WHERE vendor_id = v.id AND bill_id IS NULL), 0) as credits
        FROM vendors v
        WHERE v.id = ?
    """
    row = execute_read_query(query, (vend_id,))
    credits = row[0]['credits']
    print(f"Vendor Credits: {credits} (Expected 200.0)")
    
    if abs(credits - 200.0) < 0.01:
        print("SUCCESS: Vendor credits calculated correctly.")
    else:
        print("FAIL: Vendor credits incorrect.")

    # 6. Test Payment with NO Bill (Advance Payment)
    print("\nRecording Advance Payment of 300 (No allocation)...")
    payment_data_advance = {
        'vendor_id': vend_id,
        'amount_paid': 300.0,
        'date': '2023-01-06',
        'method': 'Cash',
        'reference': 'ADVANCE',
        'allocations': []
    }
    save_bill_payment(payment_data_advance)
    
    row = execute_read_query(query, (vend_id,))
    credits = row[0]['credits']
    print(f"Vendor Credits after Advance: {credits} (Expected 500.0 [200+300])")
    
    if abs(credits - 500.0) < 0.01:
        print("SUCCESS: Advance payment added to credits.")
    else:
        print("FAIL: Advance payment credits incorrect.")

if __name__ == "__main__":
    try:
        test_vendor_credits()
    except Exception as e:
        print(f"Test Failed: {e}")
