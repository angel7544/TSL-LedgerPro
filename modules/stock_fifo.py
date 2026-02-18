from database.db import execute_read_query, execute_transaction, execute_write_query

def add_stock(item_id, quantity, rate, date, vendor_id=None):
    """
    Adds a new stock batch to the inventory.
    """
    query = """
        INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_write_query(query, (item_id, quantity, rate, date, vendor_id))
    
    # Update master stock
    execute_write_query("UPDATE items SET stock_on_hand = stock_on_hand + ? WHERE id = ?", (quantity, item_id))

def reduce_stock_fifo(item_id, quantity_sold):
    """
    Reduces stock using FIFO method and calculates the Cost of Goods Sold (COGS).
    
    Args:
        item_id (int): The ID of the item being sold.
        quantity_sold (float): The quantity being sold.
        
    Returns:
        float: The total cost of goods sold for this transaction.
    """
    remaining_to_sell = quantity_sold
    total_cogs = 0.0
    updates = []
    
    # Fetch batches with remaining quantity, ordered by date (FIFO)
    batches = execute_read_query("""
        SELECT id, quantity_remaining, purchase_rate 
        FROM stock_batches 
        WHERE item_id = ? AND quantity_remaining > 0 
        ORDER BY purchase_date ASC, id ASC
    """, (item_id,))
    
    for batch in batches:
        if remaining_to_sell <= 0:
            break

        batch_id = batch['id']
        qty_available = batch['quantity_remaining']
        cost_price = batch['purchase_rate']
        
        if qty_available <= remaining_to_sell:
            # Consume this entire batch
            sold_from_batch = qty_available
            total_cogs += sold_from_batch * cost_price
            remaining_to_sell -= sold_from_batch
            
            # Update batch to 0
            updates.append(("UPDATE stock_batches SET quantity_remaining = 0 WHERE id = ?", (batch_id,)))
            
        else:
            # Consume part of this batch
            sold_from_batch = remaining_to_sell
            total_cogs += sold_from_batch * cost_price
            new_qty = qty_available - sold_from_batch
            remaining_to_sell = 0
            
            # Update batch with remaining quantity
            updates.append(("UPDATE stock_batches SET quantity_remaining = ? WHERE id = ?", (new_qty, batch_id)))
            
    if updates:
        execute_transaction(updates)

    # Always update master stock
    execute_write_query("UPDATE items SET stock_on_hand = stock_on_hand - ? WHERE id = ?", (quantity_sold, item_id))

    if remaining_to_sell > 0:
        # Not enough stock available. 
        # In a strict system, we might raise an error. 
        # For now, we'll assume the remaining uses the last known purchase price or 0 if no history.
        # But let's just log a warning or return what we have.
        print(f"Warning: Not enough stock for item {item_id}. Missing {remaining_to_sell}")
        
    return total_cogs

def get_stock_valuation_summary():
    """
    Returns a summary of stock valuation for all items.
    """
    items = execute_read_query("SELECT id, name FROM items")
    summary = []
    
    for item in items:
        item_id = item['id']
        batches = execute_read_query("""
            SELECT quantity_remaining, purchase_rate 
            FROM stock_batches 
            WHERE item_id = ? AND quantity_remaining > 0
        """, (item_id,))
        
        total_qty = 0
        total_value = 0.0
        
        for batch in batches:
            qty = batch['quantity_remaining']
            rate = batch['purchase_rate']
            total_qty += qty
            total_value += qty * rate
            
        avg_cost = (total_value / total_qty) if total_qty > 0 else 0.0
        
        summary.append({
            "item_id": item_id,
            "item_name": item['name'],
            "total_quantity": total_qty,
            "total_value": round(total_value, 2),
            "avg_cost": round(avg_cost, 2)
        })
        
    return summary
