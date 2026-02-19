
import os
import sys
import datetime
from database.db import execute_write_query, execute_read_query, init_db, DB_NAME
from modules.payment import get_unpaid_bills
from modules.invoice import create_bill, update_bill

def reproduce():
    # Use a test DB
    if os.path.exists("test_reproduce.db"):
        os.remove("test_reproduce.db")
    
    # Swap DB_NAME temporarily (hacky but works for script)
    import database.db
    database.db.DB_NAME = "test_reproduce.db"
    init_db()
    
    # 1. Create Vendor
    execute_write_query("INSERT INTO vendors (name) VALUES (?)", ("Test Vendor",))
    vendor_id = execute_read_query("SELECT id FROM vendors WHERE name='Test Vendor'")[0]['id']
    print(f"Vendor ID: {vendor_id}")
    
    # 2. Create Item
    execute_write_query("INSERT INTO items (name, purchase_price, is_purchasable) VALUES (?, ?, ?)", ("Test Item", 100, 1))
    item_id = execute_read_query("SELECT id FROM items WHERE name='Test Item'")[0]['id']
    print(f"Item ID: {item_id}")
    
    # 3. Create Bill (Draft)
    bill_data = {
        'vendor_id': vendor_id,
        'date': datetime.date.today().strftime("%Y-%m-%d"),
        'items': [
            {'item_id': item_id, 'quantity': 10, 'rate': 100, 'gst_percent': 0}
        ],
        'status': 'Draft'
    }
    bill_id = create_bill(bill_data)
    print(f"Created Bill ID: {bill_id} with status Draft")
    
    # 4. Check unpaid bills (Should NOT show because it's Draft)
    bills = get_unpaid_bills(vendor_id)
    print(f"Unpaid Bills (Draft): {len(bills)}")
    for b in bills:
        print(f" - {b['bill_number']}: {b['status']}")
        
    # 5. Mark as Sent (Due)
    execute_write_query("UPDATE bills SET status = 'Sent' WHERE id = ?", (bill_id,))
    print("Updated status to Sent")
    
    # 6. Check unpaid bills (Should SHOW)
    bills = get_unpaid_bills(vendor_id)
    print(f"Unpaid Bills (Sent): {len(bills)}")
    for b in bills:
        print(f" - {b['bill_number']}: {b['status']} | Grand Total: {b['grand_total']}")
        
    # 7. Mark as Paid
    execute_write_query("UPDATE bills SET status = 'Paid' WHERE id = ?", (bill_id,))
    print("Updated status to Paid")
    
    # 8. Check unpaid bills (Should NOT show)
    bills = get_unpaid_bills(vendor_id)
    print(f"Unpaid Bills (Paid): {len(bills)}")

if __name__ == "__main__":
    reproduce()
