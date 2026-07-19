-- ============================================================================
-- LedgerPro - Step 2 API Queries: Inventory & FIFO Stock Batches
-- ============================================================================

-- 1. Insert new stock batch (Purchase / Opening Stock)
INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id) 
VALUES (?, ?, ?, ?, ?);

-- 2. Fetch available stock batches in FIFO order (oldest purchase_date first)
SELECT id, item_id, quantity_remaining, purchase_rate, purchase_date 
FROM stock_batches 
WHERE item_id = ? AND quantity_remaining > 0 
ORDER BY purchase_date ASC, id ASC;

-- 3. Update batch remaining quantity after FIFO deduction
UPDATE stock_batches 
SET quantity_remaining = ? 
WHERE id = ?;

-- 4. Delete depleted stock batch (quantity_remaining = 0)
DELETE FROM stock_batches 
WHERE id = ? AND quantity_remaining <= 0;

-- 5. Update stock_on_hand in items master table
UPDATE items 
SET stock_on_hand = ? 
WHERE id = ?;

-- 6. Recalculate total available stock on hand from active FIFO batches
SELECT item_id, SUM(quantity_remaining) AS total_stock 
FROM stock_batches 
GROUP BY item_id;

-- 7. Query low-stock alert items (stock_on_hand <= reorder_point)
SELECT id, name, sku, stock_on_hand, reorder_point, unit 
FROM items 
WHERE track_inventory = 1 AND stock_on_hand <= reorder_point;

-- 8. Fetch total stock valuation by FIFO purchase rate
SELECT 
    i.id AS item_id,
    i.name,
    i.sku,
    COALESCE(SUM(sb.quantity_remaining * sb.purchase_rate), 0) AS batch_valuation
FROM items i
LEFT JOIN stock_batches sb ON i.id = sb.item_id
GROUP BY i.id;
