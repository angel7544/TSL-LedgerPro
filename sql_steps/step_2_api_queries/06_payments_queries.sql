-- ============================================================================
-- LedgerPro - Step 2 API Queries: Payment Receipts & Settlements
-- ============================================================================

-- 1. Record customer payment against invoice
INSERT INTO payments (
    invoice_id, customer_id, amount, date, method, notes, 
    payment_number, deposit_to, bank_charges, tax_deducted, 
    tax_account, attachment_path, reference, send_thank_you, custom_fields
) VALUES (
    ?, ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, 
    ?, ?, ?, ?, ?
);

-- 2. Record vendor payment against purchase bill
INSERT INTO payments (
    bill_id, vendor_id, amount, date, method, notes, 
    payment_number, deposit_to, bank_charges, tax_deducted, 
    tax_account, attachment_path, reference, send_thank_you, custom_fields
) VALUES (
    ?, ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, 
    ?, ?, ?, ?, ?
);

-- 3. Calculate total payments received for an invoice
SELECT SUM(amount) AS total_paid FROM payments WHERE invoice_id = ?;

-- 4. Calculate total payments made for a purchase bill
SELECT SUM(amount) AS total_paid FROM payments WHERE bill_id = ?;

-- 5. Fetch payment history list
SELECT 
    p.id, p.payment_number, p.date, p.amount, p.method, p.reference, p.notes,
    p.invoice_id, i.invoice_number,
    p.bill_id, b.bill_number,
    COALESCE(c.name, v.name) AS party_name
FROM payments p
LEFT JOIN invoices i ON p.invoice_id = i.id
LEFT JOIN bills b ON p.bill_id = b.id
LEFT JOIN customers c ON COALESCE(p.customer_id, i.customer_id) = c.id
LEFT JOIN vendors v ON COALESCE(p.vendor_id, b.vendor_id) = v.id
ORDER BY p.date DESC, p.id DESC;

-- 6. Delete payment record
DELETE FROM payments WHERE id = ?;
