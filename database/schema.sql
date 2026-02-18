-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    gstin TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vendors Table
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

-- Items Table
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT UNIQUE,
    hsn_sac TEXT,
    gst_rate REAL DEFAULT 0,
    description TEXT,
    unit TEXT DEFAULT 'pcs',
    selling_price REAL DEFAULT 0,
    purchase_price REAL DEFAULT 0,
    reorder_point REAL DEFAULT 0,
    stock_on_hand REAL DEFAULT 0,
    opening_stock_value REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock Batches Table (FIFO)
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

-- Invoices Table
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
    status TEXT DEFAULT 'Draft', -- Draft, Sent, Paid, Overdue
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Invoice Items Table
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

-- Bills Table (Purchases)
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_number TEXT NOT NULL,
    vendor_id INTEGER NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    grand_total REAL DEFAULT 0,
    status TEXT DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Bill Items Table
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

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    bill_id INTEGER,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    method TEXT, -- Cash, Bank, UPI, etc.
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (bill_id) REFERENCES bills(id)
);

-- Settings Table
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Insert Default Settings
INSERT OR IGNORE INTO settings (key, value) VALUES ('company_name', 'My Company');
INSERT OR IGNORE INTO settings (key, value) VALUES ('company_address', '123 Business St');
INSERT OR IGNORE INTO settings (key, value) VALUES ('company_gstin', '');
INSERT OR IGNORE INTO settings (key, value) VALUES ('company_state', '');
INSERT OR IGNORE INTO settings (key, value) VALUES ('invoice_prefix', 'INV-');
