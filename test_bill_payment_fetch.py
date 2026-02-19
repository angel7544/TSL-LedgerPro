
import sys
import datetime
from database.db import execute_write_query, execute_read_query
from modules.payment import get_unpaid_bills

def test_fetch():
    print("Testing Bill Fetching...")
    
    # 1. Create Vendor
    vendor_name = f"Fetch Test Vendor {datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))
    vend_id = execute_read_query("SELECT id FROM vendors WHERE name = ?", (vendor_name,))[0]['id']
    
    # 2. Create Bill (Status: Sent)
    bill_num = f"BILL-SENT-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill_num, vend_id, '2023-01-01', 500.0, 'Sent')
    )
    print(f"Created Bill {bill_num} with status 'Sent'")
    
    # 3. Fetch Unpaid Bills
    bills = get_unpaid_bills(vend_id)
    print(f"Fetched {len(bills)} bills.")
    found = False
    for b in bills:
        print(f" - {b['bill_number']} ({b['status']})")
        if b['bill_number'] == bill_num:
            found = True
            
    if found:
        print("SUCCESS: Sent bill was fetched.")
    else:
        print("FAIL: Sent bill was NOT fetched.")

    # 4. Create Bill (Status: Draft)
    bill_draft = f"BILL-DRAFT-{datetime.datetime.now().strftime('%H%M%S')}"
    execute_write_query(
        "INSERT INTO bills (bill_number, vendor_id, date, grand_total, status) VALUES (?, ?, ?, ?, ?)",
        (bill_draft, vend_id, '2023-01-02', 500.0, 'Draft')
    )
    # Get ID
    bill_draft_id = execute_read_query("SELECT id FROM bills WHERE bill_number = ?", (bill_draft,))[0]['id']
    print(f"Created Bill {bill_draft} with status 'Draft' (ID: {bill_draft_id})")
    
    # 5. Fetch Unpaid Bills (Draft should be fetched)
    bills = get_unpaid_bills(vend_id)
    found_draft = False
    for b in bills:
        if b['bill_number'] == bill_draft:
            found_draft = True
            
    if found_draft:
        print("NOTE: Draft bill was fetched (Current behavior).")
    else:
        print("NOTE: Draft bill was NOT fetched.")
        
    # 6. Update status to 'Sent' (Mark as Due)
    print("Marking Draft bill as Due (Sent)...")
    execute_write_query("UPDATE bills SET status = 'Sent' WHERE id = ?", (bill_draft_id,))
    
    # 7. Fetch again
    bills = get_unpaid_bills(vend_id)
    found_sent = False
    for b in bills:
        if b['bill_number'] == bill_draft:
            print(f" - Found {b['bill_number']} with status {b['status']}")
            found_sent = True
            
    if found_sent:
        print("SUCCESS: Updated Sent bill was fetched.")
    else:
        print("FAIL: Updated Sent bill was NOT fetched.")

if __name__ == "__main__":
    test_fetch()
