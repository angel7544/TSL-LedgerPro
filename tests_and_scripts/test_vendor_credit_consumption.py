
import sys
import datetime
from database.db import execute_write_query, execute_read_query
from modules.payment import save_bill_payment, get_vendor_credits

def test_vendor_credit_consumption():
    print("Testing Vendor Credit Consumption Flow...")
    
    # 1. Setup Vendor
    vendor_name = f"Credit Consume Vendor {datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))
    vend_res = execute_read_query("SELECT id FROM vendors WHERE name = ?", (vendor_name,))
    vend_id = vend_res[0]['id']
    print(f"Created Vendor: {vendor_name} (ID: {vend_id})")
    
    # 2. Create Bill 1 (500)
    bill1_num = f"BILL-1-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill1_num, vend_id, '2023-01-01', 500.0, 'Sent')
    )
    bill1_id = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill1_num,))[0]['id']
    print(f"Created Bill 1: {bill1_num} (ID: {bill1_id}) Amount: 500.0")
    
    # 3. Pay Bill 1 with 1000 (Excess 500)
    print("Paying Bill 1 with 1000 Cash (Creating 500 Credit)...")
    save_bill_payment({
        'vendor_id': vend_id,
        'amount_paid': 1000.0,
        'date': '2023-01-02',
        'method': 'Cash',
        'allocations': [{'bill_id': bill1_id, 'amount': 500.0}]
    })
    
    # 4. Verify Credit
    credits = get_vendor_credits(vend_id)
    print(f"Credits Available: {credits} (Expected 500.0)")
    if abs(credits - 500.0) > 0.01:
        print("FAIL: Credits incorrect after excess payment.")
        return
        
    # 5. Create Bill 2 (300)
    bill2_num = f"BILL-2-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill2_num, vend_id, '2023-01-03', 300.0, 'Sent')
    )
    bill2_id = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill2_num,))[0]['id']
    print(f"Created Bill 2: {bill2_num} (ID: {bill2_id}) Amount: 300.0")
    
    # 6. Pay Bill 2 using Credits (Full coverage)
    print("Paying Bill 2 using Credits...")
    save_bill_payment({
        'vendor_id': vend_id,
        'amount_paid': 0.0, # No new cash
        'date': '2023-01-04',
        'method': 'Cash',
        'allocations': [{'bill_id': bill2_id, 'amount': 300.0}],
        'use_credits': True
    })
    
    # 7. Verify Bill 2 Status
    status = execute_read_query("SELECT status FROM bills WHERE id = ?", (bill2_id,))[0]['status']
    print(f"Bill 2 Status: {status} (Expected 'Paid')")
    if status != 'Paid':
        print("FAIL: Bill 2 not paid.")
        return

    # 8. Verify Credit Remaining (500 - 300 = 200)
    credits = get_vendor_credits(vend_id)
    print(f"Credits Remaining: {credits} (Expected 200.0)")
    if abs(credits - 200.0) > 0.01:
        print("FAIL: Credits incorrect after Bill 2 payment.")
        return

    # 9. Create Bill 3 (300) - To test mixed payment
    bill3_num = f"BILL-3-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill3_num, vend_id, '2023-01-05', 300.0, 'Sent')
    )
    bill3_id = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill3_num,))[0]['id']
    print(f"Created Bill 3: {bill3_num} (ID: {bill3_id}) Amount: 300.0")
    
    # 10. Pay Bill 3 using remaining 200 Credits + 100 Cash
    print("Paying Bill 3 using Credits (200) + Cash (100)...")
    save_bill_payment({
        'vendor_id': vend_id,
        'amount_paid': 100.0, # Cash needed
        'date': '2023-01-06',
        'method': 'Cash',
        'allocations': [{'bill_id': bill3_id, 'amount': 300.0}], # Full allocation
        'use_credits': True
    })
    
    # 11. Verify Bill 3 Status
    status = execute_read_query("SELECT status FROM bills WHERE id = ?", (bill3_id,))[0]['status']
    print(f"Bill 3 Status: {status} (Expected 'Paid')")
    if status != 'Paid':
        print("FAIL: Bill 3 not paid.")
        return

    # 12. Verify Credit Remaining (200 - 200 = 0)
    credits = get_vendor_credits(vend_id)
    print(f"Credits Remaining: {credits} (Expected 0.0)")
    if abs(credits - 0.0) > 0.01:
        print("FAIL: Credits incorrect after Bill 3 payment.")
        return
        
    print("SUCCESS: All Vendor Credit tests passed.")

if __name__ == "__main__":
    try:
        test_vendor_credit_consumption()
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
