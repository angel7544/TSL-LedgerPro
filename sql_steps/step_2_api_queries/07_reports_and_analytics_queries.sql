-- ============================================================================
-- LedgerPro - Step 2 API Queries: Reports & Dashboard Analytics
-- ============================================================================

-- 1. Dashboard Metrics: Total Sales Revenue
SELECT COALESCE(SUM(grand_total), 0) AS total_sales FROM invoices WHERE status != 'Cancelled';

-- 2. Dashboard Metrics: Total Outstanding Customer Receivable Balance
SELECT COALESCE(SUM(outstanding_balance), 0) AS total_receivables FROM view_customer_balance;

-- 3. Dashboard Metrics: Total Purchase Expenses
SELECT COALESCE(SUM(grand_total), 0) AS total_expenses FROM bills WHERE status != 'Cancelled';

-- 4. Dashboard Metrics: Total Outstanding Vendor Payable Balance
SELECT COALESCE(SUM(vendor_payable_balance), 0) AS total_payables FROM view_vendor_summary;

-- 5. Top Selling Products Report
SELECT 
    itm.id, itm.name, itm.sku,
    SUM(ii.quantity) AS total_quantity_sold,
    SUM(ii.amount) AS total_revenue_generated
FROM invoice_items ii
JOIN items itm ON ii.item_id = itm.id
JOIN invoices i ON ii.invoice_id = i.id
WHERE i.status != 'Cancelled'
GROUP BY itm.id, itm.name, itm.sku
ORDER BY total_revenue_generated DESC
LIMIT 10;

-- 6. GST Sales Tax Summary (B2B & B2C)
SELECT 
    i.invoice_number, i.date, c.name AS customer_name, c.gstin AS customer_gstin,
    i.subtotal AS taxable_value, i.tax_amount AS total_gst, i.grand_total
FROM invoices i
JOIN customers c ON i.customer_id = c.id
WHERE i.date BETWEEN ? AND ? AND i.status != 'Cancelled';

-- 7. Cost of Goods Sold (COGS) & Net Profit Summary
SELECT 
    (SELECT COALESCE(SUM(grand_total), 0) FROM invoices WHERE date BETWEEN ? AND ?) AS total_revenue,
    (SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE date BETWEEN ? AND ?) AS total_cogs,
    ((SELECT COALESCE(SUM(grand_total), 0) FROM invoices WHERE date BETWEEN ? AND ?) - 
     (SELECT COALESCE(SUM(grand_total), 0) FROM bills WHERE date BETWEEN ? AND ?)) AS net_margin;

-- 8. Customer Account Statement / Ledger Query
SELECT * FROM view_customer_ledger WHERE customer_id = ? ORDER BY txn_date ASC;

-- 9. Vendor Account Statement / Ledger Query
SELECT * FROM view_vendor_ledger WHERE vendor_id = ? ORDER BY txn_date ASC;

-- 10. General Ledger Activity Feed Query
SELECT * FROM view_general_ledger ORDER BY txn_date DESC LIMIT 100;
