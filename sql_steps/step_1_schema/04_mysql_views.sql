-- ============================================================================
-- LedgerPro - Step 1: MySQL Database Views
-- Database Views for Reporting, Analytics & Accounting (MySQL Syntax)
-- Engine: MySQL 8.0 / MariaDB
-- ============================================================================

-- 1. Invoice Summary View
CREATE OR REPLACE VIEW view_invoice_summary AS
SELECT 
    i.id AS invoice_id,
    i.invoice_number,
    i.date AS invoice_date,
    i.due_date,
    c.id AS customer_id,
    c.name AS customer_name,
    c.phone AS customer_phone,
    c.gstin AS customer_gstin,
    i.subtotal,
    i.tax_amount,
    i.discount_amount,
    i.grand_total,
    i.status,
    IFNULL(SUM(p.amount), 0) AS total_paid,
    (i.grand_total - IFNULL(SUM(p.amount), 0)) AS balance_due,
    i.created_at
FROM invoices i
JOIN customers c ON i.customer_id = c.id
LEFT JOIN payments p ON i.id = p.invoice_id
GROUP BY i.id, i.invoice_number, i.date, i.due_date, c.id, c.name, c.phone, c.gstin, i.subtotal, i.tax_amount, i.discount_amount, i.grand_total, i.status, i.created_at;

-- 2. Customer Balance View
CREATE OR REPLACE VIEW view_customer_balance AS
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    c.email,
    c.phone,
    c.gstin,
    IFNULL(inv.total_invoiced, 0) AS total_invoiced,
    IFNULL(pay.total_paid, 0) AS total_paid,
    (IFNULL(inv.total_invoiced, 0) - IFNULL(pay.total_paid, 0)) AS outstanding_balance
FROM customers c
LEFT JOIN (
    SELECT customer_id, SUM(grand_total) AS total_invoiced
    FROM invoices
    GROUP BY customer_id
) inv ON c.id = inv.customer_id
LEFT JOIN (
    SELECT customer_id, SUM(amount) AS total_paid
    FROM payments
    WHERE customer_id IS NOT NULL OR invoice_id IS NOT NULL
    GROUP BY customer_id
) pay ON c.id = pay.customer_id;

-- 3. Invoice Details View
CREATE OR REPLACE VIEW view_invoice_details AS
SELECT 
    ii.id AS line_item_id,
    i.id AS invoice_id,
    i.invoice_number,
    i.date AS invoice_date,
    c.name AS customer_name,
    itm.id AS item_id,
    itm.name AS item_name,
    itm.sku AS item_sku,
    ii.quantity,
    ii.rate,
    ii.discount_percent,
    ii.gst_percent,
    ii.amount AS item_total
FROM invoice_items ii
JOIN invoices i ON ii.invoice_id = i.id
JOIN customers c ON i.customer_id = c.id
JOIN items itm ON ii.item_id = itm.id;

-- 4. Vendor Summary View
CREATE OR REPLACE VIEW view_vendor_summary AS
SELECT 
    v.id AS vendor_id,
    v.name AS vendor_name,
    v.email,
    v.phone,
    v.gstin,
    IFNULL(b.total_billed, 0) AS total_purchased,
    IFNULL(p.total_paid, 0) AS total_paid_to_vendor,
    (IFNULL(b.total_billed, 0) - IFNULL(p.total_paid, 0)) AS vendor_payable_balance
FROM vendors v
LEFT JOIN (
    SELECT vendor_id, SUM(grand_total) AS total_billed
    FROM bills
    GROUP BY vendor_id
) b ON v.id = b.vendor_id
LEFT JOIN (
    SELECT vendor_id, SUM(amount) AS total_paid
    FROM payments
    WHERE vendor_id IS NOT NULL OR bill_id IS NOT NULL
    GROUP BY vendor_id
) p ON v.id = p.vendor_id;

-- 5. Inventory Status View
CREATE OR REPLACE VIEW view_inventory_status AS
SELECT 
    id AS item_id,
    name AS item_name,
    sku,
    hsn_sac,
    unit,
    selling_price,
    purchase_price,
    stock_on_hand,
    reorder_point,
    (stock_on_hand * purchase_price) AS inventory_value,
    CASE 
        WHEN stock_on_hand <= 0 THEN 'OUT_OF_STOCK'
        WHEN stock_on_hand <= reorder_point THEN 'LOW_STOCK'
        ELSE 'IN_STOCK'
    END AS stock_status
FROM items;

-- 6. Payment History View
CREATE OR REPLACE VIEW view_payment_history AS
SELECT 
    p.id AS payment_id,
    p.payment_number,
    p.date AS payment_date,
    p.amount,
    p.method,
    p.reference,
    p.invoice_id,
    i.invoice_number,
    p.bill_id,
    b.bill_number,
    COALESCE(c.name, v.name, 'N/A') AS party_name,
    CASE 
        WHEN p.invoice_id IS NOT NULL OR p.customer_id IS NOT NULL THEN 'INWARD_RECEIPT'
        WHEN p.bill_id IS NOT NULL OR p.vendor_id IS NOT NULL THEN 'OUTWARD_PAYMENT'
        ELSE 'GENERAL'
    END AS payment_type
FROM payments p
LEFT JOIN invoices i ON p.invoice_id = i.id
LEFT JOIN bills b ON p.bill_id = b.id
LEFT JOIN customers c ON COALESCE(p.customer_id, i.customer_id) = c.id
LEFT JOIN vendors v ON COALESCE(p.vendor_id, b.vendor_id) = v.id;

-- 7. Monthly Revenue View
CREATE OR REPLACE VIEW view_monthly_revenue AS
SELECT 
    DATE_FORMAT(date, '%Y-%m') AS month_year,
    COUNT(id) AS total_invoices,
    SUM(subtotal) AS gross_sales,
    SUM(tax_amount) AS total_tax_collected,
    SUM(discount_amount) AS total_discounts,
    SUM(grand_total) AS net_revenue
FROM invoices
WHERE status != 'Cancelled'
GROUP BY DATE_FORMAT(date, '%Y-%m');

-- 8. Monthly Profit View
CREATE OR REPLACE VIEW view_monthly_profit AS
SELECT 
    rev.month_year,
    IFNULL(rev.net_revenue, 0) AS total_sales,
    IFNULL(exp.total_purchases, 0) AS total_purchases,
    (IFNULL(rev.net_revenue, 0) - IFNULL(exp.total_purchases, 0)) AS estimated_gross_profit
FROM (
    SELECT DATE_FORMAT(date, '%Y-%m') AS month_year, SUM(grand_total) AS net_revenue
    FROM invoices WHERE status != 'Cancelled'
    GROUP BY DATE_FORMAT(date, '%Y-%m')
) rev
LEFT JOIN (
    SELECT DATE_FORMAT(date, '%Y-%m') AS month_year, SUM(grand_total) AS total_purchases
    FROM bills WHERE status != 'Cancelled'
    GROUP BY DATE_FORMAT(date, '%Y-%m')
) exp ON rev.month_year = exp.month_year;

-- 9. Customer Ledger View
CREATE OR REPLACE VIEW view_customer_ledger AS
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    'INVOICE' AS entry_type,
    i.invoice_number AS doc_ref,
    i.date AS txn_date,
    i.grand_total AS debit_amount,
    0.0 AS credit_amount
FROM invoices i
JOIN customers c ON i.customer_id = c.id
UNION ALL
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    'PAYMENT_RECEIPT' AS entry_type,
    COALESCE(p.payment_number, CONCAT('PAY-', p.id)) AS doc_ref,
    p.date AS txn_date,
    0.0 AS debit_amount,
    p.amount AS credit_amount
FROM payments p
JOIN invoices i ON p.invoice_id = i.id
JOIN customers c ON i.customer_id = c.id;

-- 10. Vendor Ledger View
CREATE OR REPLACE VIEW view_vendor_ledger AS
SELECT 
    v.id AS vendor_id,
    v.name AS vendor_name,
    'PURCHASE_BILL' AS entry_type,
    b.bill_number AS doc_ref,
    b.date AS txn_date,
    b.grand_total AS credit_amount,
    0.0 AS debit_amount
FROM bills b
JOIN vendors v ON b.vendor_id = v.id
UNION ALL
SELECT 
    v.id AS vendor_id,
    v.name AS vendor_name,
    'VENDOR_PAYMENT' AS entry_type,
    COALESCE(p.payment_number, CONCAT('VPAY-', p.id)) AS doc_ref,
    p.date AS txn_date,
    p.amount AS credit_amount,
    0.0 AS debit_amount
FROM payments p
JOIN bills b ON p.bill_id = b.id
JOIN vendors v ON b.vendor_id = v.id;

-- 11. General Ledger View
CREATE OR REPLACE VIEW view_general_ledger AS
SELECT 
    'SALES_INVOICE' AS module,
    i.id AS record_id,
    i.invoice_number AS ref_code,
    i.date AS txn_date,
    c.name AS party_name,
    i.grand_total AS debit,
    0.0 AS credit,
    i.status
FROM invoices i
JOIN customers c ON i.customer_id = c.id
UNION ALL
SELECT 
    'PURCHASE_BILL' AS module,
    b.id AS record_id,
    b.bill_number AS ref_code,
    b.date AS txn_date,
    v.name AS party_name,
    0.0 AS debit,
    b.grand_total AS credit,
    b.status
FROM bills b
JOIN vendors v ON b.vendor_id = v.id
UNION ALL
SELECT 
    'PAYMENT' AS module,
    p.id AS record_id,
    COALESCE(p.payment_number, CONCAT('PAY-', p.id)) AS ref_code,
    p.date AS txn_date,
    COALESCE(c.name, v.name, 'N/A') AS party_name,
    CASE WHEN p.bill_id IS NOT NULL OR p.vendor_id IS NOT NULL THEN p.amount ELSE 0.0 END AS debit,
    CASE WHEN p.invoice_id IS NOT NULL OR p.customer_id IS NOT NULL THEN p.amount ELSE 0.0 END AS credit,
    'Completed' AS status
FROM payments p
LEFT JOIN customers c ON p.customer_id = c.id
LEFT JOIN vendors v ON p.vendor_id = v.id;
