-- ============================================================================
-- LedgerPro - Step 4: Recreate SQLite Database (Drop & Fresh Creation)
-- ============================================================================

-- Drop Views
DROP VIEW IF EXISTS view_general_ledger;
DROP VIEW IF EXISTS view_vendor_ledger;
DROP VIEW IF EXISTS view_customer_ledger;
DROP VIEW IF EXISTS view_monthly_profit;
DROP VIEW IF EXISTS view_monthly_revenue;
DROP VIEW IF EXISTS view_payment_history;
DROP VIEW IF EXISTS view_inventory_status;
DROP VIEW IF EXISTS view_vendor_summary;
DROP VIEW IF EXISTS view_invoice_details;
DROP VIEW IF EXISTS view_customer_balance;
DROP VIEW IF EXISTS view_invoice_summary;

-- Drop Tables
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS bill_items;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS invoice_items;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS stock_batches;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS vendors;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS users;

-- Recreate Base Tables
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    gstin TEXT,
    state TEXT,
    customer_type TEXT DEFAULT 'Type 1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    gstin TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT UNIQUE,
    hsn_sac TEXT,
    gst_rate REAL DEFAULT 0,
    description TEXT,
    unit TEXT DEFAULT 'pcs',
    selling_price REAL DEFAULT 0,
    sp1 REAL DEFAULT 0,
    sp2 REAL DEFAULT 0,
    sp3 REAL DEFAULT 0,
    purchase_price REAL DEFAULT 0,
    reorder_point REAL DEFAULT 0,
    stock_on_hand REAL DEFAULT 0,
    opening_stock REAL DEFAULT 0,
    opening_stock_value REAL DEFAULT 0,
    account_code TEXT,
    purchase_account_code TEXT,
    inventory_account_code TEXT,
    taxable INTEGER DEFAULT 1,
    exemption_reason TEXT,
    taxability_type TEXT,
    product_type TEXT,
    intra_state_tax_rate REAL DEFAULT 0,
    inter_state_tax_rate REAL DEFAULT 0,
    purchase_description TEXT,
    inventory_valuation_method TEXT,
    item_type TEXT DEFAULT 'Goods',
    is_sellable INTEGER DEFAULT 1,
    is_purchasable INTEGER DEFAULT 1,
    track_inventory INTEGER DEFAULT 1,
    vendor_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE stock_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity_remaining REAL NOT NULL,
    purchase_rate REAL NOT NULL,
    purchase_date DATE NOT NULL,
    vendor_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Draft',
    notes TEXT,
    order_number TEXT,
    terms TEXT,
    salesperson TEXT,
    subject TEXT,
    customer_notes TEXT,
    terms_conditions TEXT,
    round_off REAL DEFAULT 0,
    tds_amount REAL DEFAULT 0,
    tcs_amount REAL DEFAULT 0,
    attachment_path TEXT,
    custom_fields TEXT,
    adjustment REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    rate REAL NOT NULL,
    discount_percent REAL DEFAULT 0,
    gst_percent REAL DEFAULT 0,
    amount REAL NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Draft',
    order_number TEXT,
    payment_terms TEXT,
    reverse_charge INTEGER DEFAULT 0,
    adjustment REAL DEFAULT 0,
    tds_amount REAL DEFAULT 0,
    tcs_amount REAL DEFAULT 0,
    attachment_path TEXT,
    notes TEXT,
    discount_amount REAL DEFAULT 0,
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    rate REAL NOT NULL,
    gst_percent REAL DEFAULT 0,
    amount REAL NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    bill_id INTEGER,
    customer_id INTEGER,
    vendor_id INTEGER,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    method TEXT,
    notes TEXT,
    payment_number TEXT,
    deposit_to TEXT,
    bank_charges REAL DEFAULT 0,
    tax_deducted REAL DEFAULT 0,
    tax_account TEXT,
    attachment_path TEXT,
    reference TEXT,
    send_thank_you INTEGER DEFAULT 0,
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name TEXT,
    action TEXT NOT NULL,
    module TEXT NOT NULL,
    record_id TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recreate SQLite Views
CREATE VIEW view_invoice_summary AS
SELECT i.id AS invoice_id, i.invoice_number, i.date AS invoice_date, i.due_date, c.id AS customer_id, c.name AS customer_name, c.phone AS customer_phone, c.gstin AS customer_gstin, i.subtotal, i.tax_amount, i.discount_amount, i.grand_total, i.status, COALESCE(SUM(p.amount), 0) AS total_paid, (i.grand_total - COALESCE(SUM(p.amount), 0)) AS balance_due, i.created_at
FROM invoices i JOIN customers c ON i.customer_id = c.id LEFT JOIN payments p ON i.id = p.invoice_id GROUP BY i.id;

CREATE VIEW view_customer_balance AS
SELECT c.id AS customer_id, c.name AS customer_name, c.email, c.phone, c.gstin, COALESCE(inv.total_invoiced, 0) AS total_invoiced, COALESCE(pay.total_paid, 0) AS total_paid, (COALESCE(inv.total_invoiced, 0) - COALESCE(pay.total_paid, 0)) AS outstanding_balance
FROM customers c LEFT JOIN (SELECT customer_id, SUM(grand_total) AS total_invoiced FROM invoices GROUP BY customer_id) inv ON c.id = inv.customer_id LEFT JOIN (SELECT customer_id, SUM(amount) AS total_paid FROM payments WHERE customer_id IS NOT NULL OR invoice_id IS NOT NULL GROUP BY customer_id) pay ON c.id = pay.customer_id;
