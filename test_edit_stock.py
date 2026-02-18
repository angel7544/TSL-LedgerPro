
import sqlite3
import os
from database.db import execute_write_query, execute_read_query, execute_transaction

# Mock UI logic for testing
def simulate_edit_item(item_id, old_opening, new_opening, new_val=0, vendor_id=None):
    # This logic mimics what I added to save_item_custom
    
    # 1. Update Items table (informational)
    execute_write_query("UPDATE items SET opening_stock = ? WHERE id = ?", (new_opening, item_id))
    
    # 2. Handle Stock Correction
    diff = new_opening - old_opening
    
    if abs(diff) > 0.001:
        print(f"Correction needed: {diff}")
        execute_write_query("UPDATE items SET stock_on_hand = stock_on_hand + ? WHERE id = ?", (diff, item_id))
        
        if diff > 0:
            # Add Stock Batch
            rate = 100.0 # simplified
            execute_write_query("""
                INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
                VALUES (?, ?, ?, '2025-01-01', ?)
            """, (item_id, diff, rate, vendor_id))
        else:
            # Reduce Stock Batch
            qty_to_remove = abs(diff)
            batches = execute_read_query("""
                SELECT id, quantity_remaining 
                FROM stock_batches 
                WHERE item_id = ? AND quantity_remaining > 0 
                ORDER BY purchase_date ASC, id ASC
            """, (item_id,))
            
            for batch in batches:
                if qty_to_remove <= 0:
                    break
                    
                b_id = batch['id']
                b_qty = batch['quantity_remaining']
                
                if b_qty <= qty_to_remove:
                    execute_write_query("UPDATE stock_batches SET quantity_remaining = 0 WHERE id = ?", (b_id,))
                    qty_to_remove -= b_qty
                else:
                    execute_write_query("UPDATE stock_batches SET quantity_remaining = ? WHERE id = ?", (b_qty - qty_to_remove, b_id))
                    qty_to_remove = 0

def run_test():
    # Setup
    print("Setting up test item...")
    execute_write_query("DELETE FROM items WHERE name = 'TestItemEdit'")
    execute_write_query("DELETE FROM stock_batches WHERE item_id IN (SELECT id FROM items WHERE name = 'TestItemEdit')")
    
    # 1. Create Item with Opening Stock 10
    item_id = execute_write_query("""
        INSERT INTO items (name, stock_on_hand, opening_stock, purchase_price) 
        VALUES ('TestItemEdit', 10, 10, 100)
    """)
    execute_write_query("""
        INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date)
        VALUES (?, 10, 100, '2025-01-01')
    """, (item_id,))
    
    print(f"Created Item ID: {item_id}, Stock: 10")
    
    # 2. Simulate Edit: Change Opening Stock to 15
    print("Editing: Changing Opening Stock to 15...")
    simulate_edit_item(item_id, 10, 15)
    
    # Verify
    row = execute_read_query("SELECT stock_on_hand FROM items WHERE id = ?", (item_id,))[0]
    print(f"New Stock on Hand: {row['stock_on_hand']}")
    assert row['stock_on_hand'] == 15
    
    batches = execute_read_query("SELECT quantity_remaining FROM stock_batches WHERE item_id = ?", (item_id,))
    total_batch = sum(b['quantity_remaining'] for b in batches)
    print(f"Total in Batches: {total_batch}")
    assert total_batch == 15
    
    # 3. Simulate Edit: Change Opening Stock to 12
    print("Editing: Changing Opening Stock to 12...")
    simulate_edit_item(item_id, 15, 12)
    
    # Verify
    row = execute_read_query("SELECT stock_on_hand FROM items WHERE id = ?", (item_id,))[0]
    print(f"New Stock on Hand: {row['stock_on_hand']}")
    assert row['stock_on_hand'] == 12
    
    batches = execute_read_query("SELECT quantity_remaining FROM stock_batches WHERE item_id = ?", (item_id,))
    total_batch = sum(b['quantity_remaining'] for b in batches)
    print(f"Total in Batches: {total_batch}")
    assert total_batch == 12

    # Cleanup
    execute_write_query("DELETE FROM items WHERE id = ?", (item_id,))
    execute_write_query("DELETE FROM stock_batches WHERE item_id = ?", (item_id,))
    print("Test Passed!")

if __name__ == "__main__":
    run_test()
