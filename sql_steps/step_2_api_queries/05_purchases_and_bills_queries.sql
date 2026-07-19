-- ============================================================================
-- LedgerPro - Step 2 API Queries: Purchase Bills & Vendor Purchases
-- ============================================================================

-- 1. Create Purchase Bill Header
INSERT INTO bills (
    bill_number, vendor_id, date, due_date, subtotal, tax_amount, 
    grand_total, status, order_number, payment_terms, reverse_charge, 
    adjustment, tds_amount, tcs_amount, attachment_path, notes, 
    discount_amount, custom_fields
) VALUES (
    ?, ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, 
    ?, ?
);

-- 2. Insert Bill Line Item
INSERT INTO bill_items (
    bill_id, item_id, quantity, rate, gst_percent, amount
) VALUES (
    ?, ?, ?, ?, ?, ?
);

-- 3. Fetch all purchase bills with vendor details
SELECT 
    b.id, b.bill_number, b.date, b.due_date, b.subtotal, b.tax_amount, 
    b.grand_total, b.status, b.created_at,
    v.id AS vendor_id, v.name AS vendor_name, v.phone AS vendor_phone
FROM bills b
JOIN vendors v ON b.vendor_id = v.id
ORDER BY b.date DESC, b.id DESC;

-- 4. Fetch bill header by ID
SELECT * FROM bills WHERE id = ?;

-- 5. Fetch bill line items
SELECT 
    bi.id, bi.bill_id, bi.item_id, bi.quantity, bi.rate, bi.gst_percent, bi.amount,
    itm.name AS item_name, itm.sku, itm.hsn_sac, itm.unit
FROM bill_items bi
JOIN items itm ON bi.item_id = itm.id
WHERE bi.bill_id = ?;

-- 6. Update purchase bill status (Draft, Unpaid, Paid, Partial)
UPDATE bills SET status = ? WHERE id = ?;

-- 7. Delete bill line items
DELETE FROM bill_items WHERE bill_id = ?;

-- 8. Delete bill header
DELETE FROM bills WHERE id = ?;
