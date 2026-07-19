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
    Returns a summary of stock valuation for all items using a single optimized query.
    """
    query = """
        SELECT 
            i.id AS item_id,
            i.name AS item_name,
            COALESCE(i.selling_price, 0) AS selling_price,
            COALESCE(i.sp1, 0) AS sp1,
            COALESCE(i.sp2, 0) AS sp2,
            COALESCE(i.sp3, 0) AS sp3,
            COALESCE(SUM(sb.quantity_remaining), 0) AS total_quantity,
            COALESCE(SUM(sb.quantity_remaining * sb.purchase_rate), 0) AS total_value
        FROM items i
        LEFT JOIN stock_batches sb ON i.id = sb.item_id AND sb.quantity_remaining > 0
        GROUP BY i.id, i.name, i.selling_price, i.sp1, i.sp2, i.sp3
    """
    rows = execute_read_query(query)
    summary = []
    
    for row in rows:
        total_qty = float(row['total_quantity'] or 0)
        total_value = float(row['total_value'] or 0.0)
        avg_cost = (total_value / total_qty) if total_qty > 0 else 0.0
        
        summary.append({
            "item_id": row['item_id'],
            "item_name": row['item_name'],
            "selling_price": float(row['selling_price'] or 0.0),
            "sp1": float(row['sp1'] or 0.0),
            "sp2": float(row['sp2'] or 0.0),
            "sp3": float(row['sp3'] or 0.0),
            "total_quantity": total_qty,
            "total_value": round(total_value, 2),
            "avg_cost": round(avg_cost, 2)
        })
        
    return summary

