from database.db import execute_write_query, execute_read_query
from modules.invoice import create_bill
from pdf.generator import generate_price_list_pdf
import os
import datetime

def test_bill_creation():
    print("Testing Bill Creation...")
    
    # Ensure a vendor exists
    execute_write_query("INSERT OR IGNORE INTO vendors (name) VALUES ('Test Vendor')")
    vendor = execute_read_query("SELECT id FROM vendors WHERE name='Test Vendor' LIMIT 1")[0]
    
    # Ensure an item exists
    execute_write_query("INSERT OR IGNORE INTO items (name, purchase_price, selling_price, stock_on_hand) VALUES ('Test Item Bill', 100, 150, 0)")
    item = execute_read_query("SELECT id FROM items WHERE name='Test Item Bill' LIMIT 1")[0]
    
    bill_data = {
        "vendor_id": vendor['id'],
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "items": [
            {
                "item_id": item['id'],
                "quantity": 10,
                "rate": 100,
                "gst_percent": 18
            }
        ],
        "status": "Paid"
    }
    
    try:
        bill_id = create_bill(bill_data)
        print(f"Bill created successfully. ID: {bill_id}")
        
        # Verify stock update
        stock = execute_read_query("SELECT stock_on_hand FROM items WHERE id=?", (item['id'],))
        print(f"Current Stock: {stock[0]['stock_on_hand']} (Should be 10)")
        
        # Verify bill record
        bill = execute_read_query("SELECT grand_total FROM bills WHERE id=?", (bill_id,))
        print(f"Bill Total: {bill[0]['grand_total']} (Should be 1180.0)")
        
    except Exception as e:
        print(f"Bill creation failed: {e}")

def test_pdf_generation():
    print("\nTesting PDF Generation...")
    items = [
        {"name": "Item A", "sku": "SKU001", "selling_price": 100.0},
        {"name": "Item B", "sku": "SKU002", "selling_price": 200.0},
        {"name": "Item C", "sku": None, "selling_price": 300.0}
    ]
    
    filename = "test_price_list.pdf"
    try:
        generate_price_list_pdf(items, filename)
        if os.path.exists(filename):
            print(f"PDF generated successfully at {filename}")
            # os.remove(filename) # Keep it for manual check if needed
        else:
            print("PDF file not found after generation.")
    except Exception as e:
        print(f"PDF generation failed: {e}")

if __name__ == "__main__":
    test_bill_creation()
    test_pdf_generation()
