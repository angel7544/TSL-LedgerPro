-- ============================================================================
-- LedgerPro - Step 6: Seed Complete Organization Dataset
-- Admin, Manager, Staff Accounts, Master Data, Stock Batches & Sample Txns
-- ============================================================================

-- 1. Multi-Role User Accounts (Password: admin123 / manager123 / staff123)
INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES 
('Owner Admin', 'owner@br31tech.live', '$2b$12$e0MYzXy5ZJgU.Wv6rT5B2.K0k4J7p5l7e7g7h7i7j7k7l7m7n7o7p', 'owner'),
('Store Manager', 'manager@br31tech.live', '$2b$12$e0MYzXy5ZJgU.Wv6rT5B2.K0k4J7p5l7e7g7h7i7j7k7l7m7n7o7p', 'manager'),
('Billing Staff', 'staff@br31tech.live', '$2b$12$e0MYzXy5ZJgU.Wv6rT5B2.K0k4J7p5l7e7g7h7i7j7k7l7m7n7o7p', 'staff');

-- 2. Customer Profiles
INSERT OR IGNORE INTO customers (name, email, phone, address, gstin, state, customer_type) VALUES 
('Acme Corporation', 'billing@acme.com', '+91 9876543210', 'Suite 404, Cyber City, Mumbai', '27AAACA1234A1Z1', 'Maharashtra', 'Business B2B'),
('Walk-in Customer', 'retail@ledgerpro.com', '+91 9123456789', 'Counter Sales, Mumbai', '', 'Maharashtra', 'Consumer B2C');

-- 3. Vendor Profiles
INSERT OR IGNORE INTO vendors (name, email, phone, address, gstin, state) VALUES 
('Global Tech Distributors', 'sales@globaltech.com', '+91 9988776655', 'Industrial Estate, Pune', '27AABCG9876F1Z2', 'Maharashtra'),
('Logitech Electronics', 'orders@logitech.com', '+91 9811223344', 'Logistics Park, Delhi', '07AAACL5544E1Z9', 'Delhi');

-- 4. Master Items Catalog
INSERT OR IGNORE INTO items (name, sku, hsn_sac, gst_rate, unit, selling_price, purchase_price, reorder_point, stock_on_hand, track_inventory) VALUES 
('Wireless Optical Mouse', 'SKU-LOGI-WM01', '8471', 18.0, 'pcs', 650.00, 400.00, 10.0, 50.0, 1),
('Mechanical RGB Keyboard', 'SKU-LOGI-MK02', '8471', 18.0, 'pcs', 3500.00, 2200.00, 5.0, 25.0, 1),
('USB-C Fast Charging Cable', 'SKU-GEN-CBL01', '8544', 18.0, 'pcs', 299.00, 120.00, 20.0, 100.0, 1);

-- 5. FIFO Stock Batches Creation
INSERT OR IGNORE INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id) VALUES 
(1, 50.0, 400.00, '2026-07-01', 1),
(2, 25.0, 2200.00, '2026-07-05', 2),
(3, 100.0, 120.00, '2026-07-10', 1);

-- 6. Initial Sample Invoices
INSERT OR IGNORE INTO invoices (invoice_number, customer_id, date, subtotal, tax_amount, grand_total, status) VALUES 
('INV-2026-0001', 1, '2026-07-15', 4150.00, 747.00, 4897.00, 'Paid'),
('INV-2026-0002', 2, '2026-07-18', 650.00, 117.00, 767.00, 'Paid');

-- 7. Invoice Line Items
INSERT OR IGNORE INTO invoice_items (invoice_id, item_id, quantity, rate, gst_percent, amount) VALUES 
(1, 1, 1.0, 650.00, 18.0, 650.00),
(1, 2, 1.0, 3500.00, 18.0, 3500.00),
(2, 1, 1.0, 650.00, 18.0, 650.00);

-- 8. Sample Payments Received
INSERT OR IGNORE INTO payments (invoice_id, customer_id, amount, date, method, reference) VALUES 
(1, 1, 4897.00, '2026-07-15', 'UPI', 'UPI/987654/ACME'),
(2, 2, 767.00, '2026-07-18', 'Cash', 'POS-CASH-002');

-- 9. Initial Audit Log Activity Entries
INSERT INTO audit_logs (user_id, user_name, action, module, record_id, details) VALUES 
(1, 'Owner Admin', 'INITIAL_SEED', 'System Initialization', 'SYS-01', 'Populated initial organization seed data with multi-role accounts and stock batches.');
