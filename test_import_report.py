import csv
import sqlite3
import os
from database.db import execute_write_query, execute_read_query, execute_transaction
from datetime import datetime

# Mock QDate for the script
class QDate:
    @staticmethod
    def currentDate():
        return datetime.now()
    def toString(self, fmt):
        return self.strftime("%Y-%m-%d")

# Create a dummy CSV
csv_content = """Item ID,Item Name,SKU,HSN/SAC,Description,Rate,Account,Account Code,Taxable,Exemption Reason,Taxability Type,Product Type,Intra State Tax Name,Intra State Tax Rate,Intra State Tax Type,Inter State Tax Name,Inter State Tax Rate,Inter State Tax Type,Source,Reference ID,Last Sync Time,Status,Usage unit,Unit Name,Purchase Rate,Purchase Account,Purchase Account Code,Purchase Description,Inventory Account,Inventory Account Code,Inventory Valuation Method,Reorder Point,Vendor,Opening Stock,Opening Stock Value,Stock On Hand,Item Type,Sellable,Purchasable,Track Inventory
,Test Item 1,SKU001,1234,Desc 1,100.0,,,,,,,Output GST,5.0,,,,,,,,,pcs,pcs,50.0,,,,,,,10.0,Vendor A,20.0,1000.0,20.0,,,,
,Test Item 2,SKU002,5678,Desc 2,200.0,,,,,,,Output GST,12.0,,,,,,,,,pcs,pcs,150.0,,,,,,,5.0,Vendor B,0.0,0.0,10.0,,,,
"""

filename = "test_import.csv"
with open(filename, "w", newline="") as f:
    f.write(csv_content)

print("Created test CSV.")

# Simulate Import Logic
try:
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row.get('Item Name')
            if not name: continue
                
            sku = row.get('SKU', '')
            hsn = row.get('HSN/SAC', '')
            desc = row.get('Description', '')
            unit = row.get('Unit Name', 'pcs')
            
            def parse_float(val):
                if not val: return 0.0
                return float(str(val).replace('INR', '').replace(',', '').strip())

            selling_price = parse_float(row.get('Rate', '0'))
            purchase_price = parse_float(row.get('Purchase Rate', '0'))
            reorder_point = parse_float(row.get('Reorder Point', '0'))
            opening_stock = parse_float(row.get('Opening Stock', '0'))
            stock_on_hand_csv = parse_float(row.get('Stock On Hand', '0'))
            
            initial_stock = opening_stock if opening_stock > 0 else stock_on_hand_csv
            opening_value = parse_float(row.get('Opening Stock Value', '0'))
            
            gst_str = row.get('Intra State Tax Rate', '')
            if not gst_str: gst_str = row.get('Inter State Tax Rate', '0')
            gst_rate = parse_float(gst_str)

            vendor_name = row.get('Vendor', '').strip()
            vendor_id = None
            if vendor_name:
                v_rows = execute_read_query("SELECT id FROM vendors WHERE name = ?", (vendor_name,))
                if v_rows:
                    vendor_id = v_rows[0]['id']
                else:
                    vendor_id = execute_write_query("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))

            # Duplicate check
            existing = None
            if sku:
                existing = execute_read_query("SELECT id FROM items WHERE sku = ?", (sku,))
            else:
                existing = execute_read_query("SELECT id FROM items WHERE name = ?", (name,))
            
            if existing:
                print(f"Skipping duplicate: {name}")
                continue

            # Insert Item
            item_id = execute_write_query("""
                INSERT INTO items (name, sku, hsn_sac, description, unit, 
                                    selling_price, purchase_price, gst_rate, 
                                    reorder_point, stock_on_hand, opening_stock_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, sku, hsn, desc, unit, selling_price, purchase_price, gst_rate, reorder_point, initial_stock, opening_value))
            
            print(f"Inserted item: {name} with ID {item_id}")

            # Create Opening Stock Batch
            if initial_stock > 0:
                batch_rate = purchase_price
                if opening_value > 0 and opening_stock > 0:
                    batch_rate = opening_value / opening_stock
                
                execute_write_query("""
                    INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (item_id, initial_stock, batch_rate, datetime.now().strftime("%Y-%m-%d"), vendor_id))
                print(f"Created batch for {name}: {initial_stock} @ {batch_rate}")

except Exception as e:
    print(f"Error: {e}")

# Verify Valuation
from modules.reports_logic import get_stock_valuation
valuation = get_stock_valuation()
print("\nStock Valuation Report:")
for item in valuation:
    if item['sku'] in ['SKU001', 'SKU002']:
        print(f"{item['name']} (SKU: {item['sku']}): Stock={item['stock_on_hand']}, Price={item['purchase_price']}, Value={item['total_value']}")

# Clean up
os.remove(filename)
# Optionally remove inserted items to clean DB? 
# No, let's keep them as proof or delete them. I'll delete them to avoid pollution.
execute_write_query("DELETE FROM stock_batches WHERE item_id IN (SELECT id FROM items WHERE sku IN ('SKU001', 'SKU002'))")
execute_write_query("DELETE FROM items WHERE sku IN ('SKU001', 'SKU002')")
execute_write_query("DELETE FROM vendors WHERE name IN ('Vendor A', 'Vendor B')")
print("\nCleaned up test data.")
