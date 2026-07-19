-- ============================================================================
-- LedgerPro - Step 1: SQLite Base Database Schema
-- Baseline Schema combining initial setup & migrations v1-v7
-- Engine: SQLite 3 (PRAGMA journal_mode=WAL)
-- ============================================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'staff', -- owner, manager, staff
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
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

-- 3. Vendors Table
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    gstin TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Items Master Table
CREATE TABLE IF NOT EXISTS items (
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

-- 5. Stock Batches Table (FIFO Inventory Management)
CREATE TABLE IF NOT EXISTS stock_batches (
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

-- 6. Invoices Table (Sales)
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Draft', -- Draft, Sent, Paid, Overdue, Partial
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

-- 7. Invoice Items Table
CREATE TABLE IF NOT EXISTS invoice_items (
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

-- 8. Bills Table (Purchases)
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Draft', -- Draft, Unpaid, Paid, Partial
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

-- 9. Bill Items Table
CREATE TABLE IF NOT EXISTS bill_items (
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

-- 10. Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    bill_id INTEGER,
    customer_id INTEGER,
    vendor_id INTEGER,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    method TEXT, -- Cash, Bank Transfer, UPI, Cheque, Credit Card
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

-- 11. Settings Table (Key-Value configuration)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- 12. Audit Logs Table (Activity Monitoring)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name TEXT,
    action TEXT NOT NULL,
    module TEXT NOT NULL,
    record_id TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
