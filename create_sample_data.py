import random
from datetime import datetime, timedelta
import sqlite3
from database.db import execute_write_query, execute_read_query

def create_customers():
    customers = [
        ("Acme Corp", "contact@acme.com", "123-456-7890", "123 Main St, NY", "27AAAAA0000A1Z5", "Maharashtra"),
        ("Globex Inc", "info@globex.com", "987-654-3210", "456 Oak Ave, CA", "29BBBBB1111B1Z6", "Karnataka"),
        ("Soylent Corp", "sales@soylent.com", "555-123-4567", "789 Pine Ln, TX", "33CCCCC2222C1Z7", "Tamil Nadu"),
        ("Umbrella Corp", "support@umbrella.com", "444-987-6543", "321 Elm Dr, FL", "07DDDDD3333D1Z8", "Delhi"),
        ("Stark Ind", "tony@stark.com", "111-222-3333", "10880 Malibu Point, CA", "19EEEEE4444E1Z9", "West Bengal")
    ]
    ids = []
    for c in customers:
        try:
            # Check if exists by name to avoid duplicates in logic (though DB allows it)
            existing = execute_read_query("SELECT id FROM customers WHERE name=?", (c[0],))
            if existing:
                ids.append(existing[0]['id'])
            else:
                query = "INSERT INTO customers (name, email, phone, address, gstin, state) VALUES (?, ?, ?, ?, ?, ?)"
                ids.append(execute_write_query(query, c))
        except Exception as e:
            print(f"Error creating customer {c[0]}: {e}")
    return ids

def create_vendors():
    vendors = [
        ("Wayne Enterprises", "bruce@wayne.com", "999-888-7777", "1007 Mountain Dr, Gotham", "27FFFFF5555F1Z0", "Maharashtra"),
        ("Cyberdyne Systems", "skynet@cyberdyne.com", "888-777-6666", "2144 Pico Blvd, CA", "29GGGGG6666G1Z1", "Karnataka"),
        ("Massive Dynamic", "bell@massive.com", "777-666-5555", "650 Fifth Ave, NY", "33HHHHH7777H1Z2", "Tamil Nadu"),
        ("Aperture Science", "glados@aperture.com", "666-555-4444", "40000 Science Dr, OH", "07IIIII8888I1Z3", "Delhi"),
        ("Black Mesa", "gordon@blackmesa.com", "555-444-3333", "New Mexico", "19JJJJJ9999J1Z4", "West Bengal")
    ]
    ids = []
    for v in vendors:
        try:
            existing = execute_read_query("SELECT id FROM vendors WHERE name=?", (v[0],))
            if existing:
                ids.append(existing[0]['id'])
            else:
                query = "INSERT INTO vendors (name, email, phone, address, gstin, state) VALUES (?, ?, ?, ?, ?, ?)"
                ids.append(execute_write_query(query, v))
        except Exception as e:
            print(f"Error creating vendor {v[0]}: {e}")
    return ids

def create_items():
    items = [
        ("Laptop", "ELEC001", "8471", 18.0, "High performance laptop", "pcs", 50000.0, 40000.0, 10, 50),
        ("Mouse", "ELEC002", "8471", 18.0, "Wireless mouse", "pcs", 500.0, 300.0, 20, 100),
        ("Keyboard", "ELEC003", "8471", 18.0, "Mechanical keyboard", "pcs", 1500.0, 1000.0, 15, 80),
        ("Monitor", "ELEC004", "8528", 18.0, "24 inch monitor", "pcs", 10000.0, 8000.0, 5, 30),
        ("Printer", "ELEC005", "8443", 18.0, "Laser printer", "pcs", 12000.0, 9000.0, 5, 20),
        ("Desk Chair", "FURN001", "9401", 12.0, "Ergonomic chair", "pcs", 8000.0, 5000.0, 10, 25),
        ("Office Desk", "FURN002", "9403", 12.0, "Wooden desk", "pcs", 15000.0, 10000.0, 5, 10),
        ("Notebook", "STAT001", "4820", 5.0, "A4 notebook", "pcs", 100.0, 50.0, 50, 200),
        ("Pen", "STAT002", "9608", 5.0, "Ballpoint pen", "pcs", 20.0, 10.0, 100, 500),
        ("Stapler", "STAT003", "8472", 12.0, "Heavy duty stapler", "pcs", 300.0, 150.0, 20, 50)
    ]
    ids = []
    for i in items:
        try:
            # Check by SKU
            existing = execute_read_query("SELECT id FROM items WHERE sku=?", (i[1],))
            if existing:
                ids.append(existing[0]['id'])
            else:
                query = """
                    INSERT INTO items (name, sku, hsn_sac, gst_rate, description, unit, selling_price, purchase_price, reorder_point, stock_on_hand)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                ids.append(execute_write_query(query, i))
        except Exception as e:
            print(f"Error creating item {i[0]}: {e}")
    return ids

def create_invoices(customer_ids, item_ids):
    # Create ~10 invoices
    today = datetime.now().date()
    
    for i in range(10):
        try:
            cust_id = random.choice(customer_ids)
            days_ago = random.randint(0, 90) # Up to 3 months ago
            inv_date = today - timedelta(days=days_ago)
            due_date = inv_date + timedelta(days=30)
            
            # Determine status
            days_overdue = (today - due_date).days
            if days_overdue > 0:
                status = "Overdue"
            elif days_ago > 5:
                status = "Sent"
            else:
                status = "Draft"
            
            # Invoice items
            num_items = random.randint(1, 5)
            selected_items = random.sample(item_ids, num_items)
            
            subtotal = 0
            tax_total = 0
            
            # Generate unique invoice number
            inv_num = f"INV-SAMPLE-{i+1:04d}-{random.randint(100, 999)}"
            
            inv_query = """
                INSERT INTO invoices (invoice_number, customer_id, date, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """
            inv_id = execute_write_query(inv_query, (inv_num, cust_id, inv_date, due_date, status))
            
            # Add items
            for item_id in selected_items:
                item = execute_read_query("SELECT selling_price, gst_rate FROM items WHERE id=?", (item_id,))[0]
                qty = random.randint(1, 10)
                rate = item['selling_price']
                gst = item['gst_rate']
                amount = qty * rate
                
                subtotal += amount
                tax_total += amount * (gst / 100)
                
                item_query = """
                    INSERT INTO invoice_items (invoice_id, item_id, quantity, rate, gst_percent, amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                execute_write_query(item_query, (inv_id, item_id, qty, rate, gst, amount))
                
            grand_total = subtotal + tax_total
            
            # Update invoice totals
            update_query = """
                UPDATE invoices SET subtotal=?, tax_amount=?, grand_total=? WHERE id=?
            """
            execute_write_query(update_query, (subtotal, tax_total, grand_total, inv_id))
            
            # Add Payment if old enough (to show paid/partial)
            if days_ago > 60:
                # Mark as Paid
                execute_write_query("UPDATE invoices SET status='Paid' WHERE id=?", (inv_id,))
                
                pay_query = """
                    INSERT INTO payments (invoice_id, amount, date, method, payment_number)
                    VALUES (?, ?, ?, ?, ?)
                """
                pay_date = inv_date + timedelta(days=random.randint(1, 20))
                pay_num = f"PAY-{random.randint(1000, 9999)}"
                execute_write_query(pay_query, (inv_id, grand_total, pay_date, "Bank Transfer", pay_num))
                
        except Exception as e:
            print(f"Error creating invoice {i}: {e}")

def create_bills(vendor_ids, item_ids):
    today = datetime.now().date()
    
    for i in range(5):
        try:
            vend_id = random.choice(vendor_ids)
            days_ago = random.randint(0, 60)
            bill_date = today - timedelta(days=days_ago)
            due_date = bill_date + timedelta(days=30)
            
            status = "Overdue" if (today - due_date).days > 0 else "Draft"
            if days_ago > 10 and status == "Draft":
                status = "Sent" # Or 'Received' for bills usually
            
            subtotal = 0
            tax_total = 0
            
            bill_num = f"BILL-SAMPLE-{i+1:04d}-{random.randint(100, 999)}"
            bill_query = """
                INSERT INTO bills (bill_number, vendor_id, date, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """
            bill_id = execute_write_query(bill_query, (bill_num, vend_id, bill_date, due_date, status))
            
            num_items = random.randint(1, 3)
            selected_items = random.sample(item_ids, num_items)
            
            for item_id in selected_items:
                item = execute_read_query("SELECT purchase_price, gst_rate FROM items WHERE id=?", (item_id,))[0]
                qty = random.randint(10, 50)
                rate = item['purchase_price']
                gst = item['gst_rate']
                amount = qty * rate
                
                subtotal += amount
                tax_total += amount * (gst / 100)
                
                item_query = """
                    INSERT INTO bill_items (bill_id, item_id, quantity, rate, gst_percent, amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                execute_write_query(item_query, (bill_id, item_id, qty, rate, gst, amount))
                
            grand_total = subtotal + tax_total
            update_query = "UPDATE bills SET subtotal=?, tax_amount=?, grand_total=? WHERE id=?"
            execute_write_query(update_query, (subtotal, tax_total, grand_total, bill_id))
            
             # Add Payment if old enough
            if days_ago > 45:
                 # Mark as Paid
                execute_write_query("UPDATE bills SET status='Paid' WHERE id=?", (bill_id,))
                
                pay_query = """
                    INSERT INTO payments (bill_id, amount, date, method, payment_number)
                    VALUES (?, ?, ?, ?, ?)
                """
                pay_date = bill_date + timedelta(days=random.randint(1, 20))
                pay_num = f"PAY-BILL-{random.randint(1000, 9999)}"
                execute_write_query(pay_query, (bill_id, grand_total, pay_date, "Bank Transfer", pay_num))
                
        except Exception as e:
            print(f"Error creating bill {i}: {e}")

def main():
    print("Creating sample data...")
    cust_ids = create_customers()
    print(f"Created/Found {len(cust_ids)} customers")
    vend_ids = create_vendors()
    print(f"Created/Found {len(vend_ids)} vendors")
    item_ids = create_items()
    print(f"Created/Found {len(item_ids)} items")
    
    if cust_ids and item_ids:
        create_invoices(cust_ids, item_ids)
        print("Created sample invoices")
    
    if vend_ids and item_ids:
        create_bills(vend_ids, item_ids)
        print("Created sample bills")
        
    print("Done!")

if __name__ == "__main__":
    main()
