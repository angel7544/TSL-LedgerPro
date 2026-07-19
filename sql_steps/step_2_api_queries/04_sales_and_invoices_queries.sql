-- ============================================================================
-- LedgerPro - Step 2 API Queries: Sales Invoices & Billing
-- ============================================================================

-- 1. Create Sales Invoice Header
INSERT INTO invoices (
    invoice_number, customer_id, date, due_date, subtotal, tax_amount, 
    discount_amount, grand_total, status, notes, order_number, terms, 
    salesperson, subject, customer_notes, terms_conditions, round_off, 
    tds_amount, tcs_amount, attachment_path, custom_fields, adjustment
) VALUES (
    ?, ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?
);

-- 2. Insert Invoice Line Item
INSERT INTO invoice_items (
    invoice_id, item_id, quantity, rate, discount_percent, gst_percent, amount
) VALUES (
    ?, ?, ?, ?, ?, ?, ?
);

-- 3. Fetch all invoices with customer details
SELECT 
    i.id, i.invoice_number, i.date, i.due_date, i.subtotal, i.tax_amount, 
    i.discount_amount, i.grand_total, i.status, i.created_at,
    c.id AS customer_id, c.name AS customer_name, c.phone AS customer_phone
FROM invoices i
JOIN customers c ON i.customer_id = c.id
ORDER BY i.date DESC, i.id DESC;

-- 4. Fetch invoice by ID
SELECT * FROM invoices WHERE id = ?;

-- 5. Fetch invoice line items for print / display
SELECT 
    ii.id, ii.invoice_id, ii.item_id, ii.quantity, ii.rate, ii.discount_percent, 
    ii.gst_percent, ii.amount,
    itm.name AS item_name, itm.sku, itm.hsn_sac, itm.unit
FROM invoice_items ii
JOIN items itm ON ii.item_id = itm.id
WHERE ii.invoice_id = ?;

-- 6. Update invoice status (Draft, Sent, Paid, Partial, Overdue)
UPDATE invoices SET status = ? WHERE id = ?;

-- 7. Delete invoice line items
DELETE FROM invoice_items WHERE invoice_id = ?;

-- 8. Delete invoice header
DELETE FROM invoices WHERE id = ?;

-- 9. Get next available invoice sequence number
SELECT invoice_number FROM invoices ORDER BY id DESC LIMIT 1;
