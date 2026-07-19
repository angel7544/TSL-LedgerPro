-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    gstin VARCHAR(50),
    state VARCHAR(100),
    customer_type VARCHAR(50) DEFAULT 'Type 1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vendors Table
CREATE TABLE IF NOT EXISTS vendors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    gstin VARCHAR(50),
    state VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Items Table
CREATE TABLE IF NOT EXISTS items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    hsn_sac VARCHAR(50),
    gst_rate DOUBLE DEFAULT 0,
    description TEXT,
    unit VARCHAR(50) DEFAULT 'pcs',
    selling_price DOUBLE DEFAULT 0,
    sp1 DOUBLE DEFAULT 0,
    sp2 DOUBLE DEFAULT 0,
    sp3 DOUBLE DEFAULT 0,
    purchase_price DOUBLE DEFAULT 0,
    reorder_point DOUBLE DEFAULT 0,
    stock_on_hand DOUBLE DEFAULT 0,
    opening_stock DOUBLE DEFAULT 0,
    opening_stock_value DOUBLE DEFAULT 0,
    account_code VARCHAR(100),
    purchase_account_code VARCHAR(100),
    inventory_account_code VARCHAR(100),
    taxable TINYINT DEFAULT 1,
    exemption_reason TEXT,
    taxability_type VARCHAR(100),
    product_type VARCHAR(100),
    intra_state_tax_rate DOUBLE DEFAULT 0,
    inter_state_tax_rate DOUBLE DEFAULT 0,
    purchase_description TEXT,
    inventory_valuation_method VARCHAR(100),
    item_type VARCHAR(50) DEFAULT 'Goods',
    is_sellable TINYINT DEFAULT 1,
    is_purchasable TINYINT DEFAULT 1,
    track_inventory TINYINT DEFAULT 1,
    vendor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock Batches Table (FIFO)
CREATE TABLE IF NOT EXISTS stock_batches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    quantity_remaining DOUBLE NOT NULL,
    purchase_rate DOUBLE NOT NULL,
    purchase_date DATE NOT NULL,
    vendor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Invoices Table
CREATE TABLE IF NOT EXISTS invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal DOUBLE DEFAULT 0,
    tax_amount DOUBLE DEFAULT 0,
    discount_amount DOUBLE DEFAULT 0,
    grand_total DOUBLE DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Draft',
    notes TEXT,
    order_number VARCHAR(100),
    terms TEXT,
    salesperson VARCHAR(100),
    subject TEXT,
    customer_notes TEXT,
    terms_conditions TEXT,
    round_off DOUBLE DEFAULT 0,
    tds_amount DOUBLE DEFAULT 0,
    tcs_amount DOUBLE DEFAULT 0,
    attachment_path TEXT,
    custom_fields TEXT,
    adjustment DOUBLE DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Invoice Items Table
CREATE TABLE IF NOT EXISTS invoice_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity DOUBLE NOT NULL,
    rate DOUBLE NOT NULL,
    discount_percent DOUBLE DEFAULT 0,
    gst_percent DOUBLE DEFAULT 0,
    amount DOUBLE NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- Bills Table (Purchases)
CREATE TABLE IF NOT EXISTS bills (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bill_number VARCHAR(100) NOT NULL,
    vendor_id INT NOT NULL,
    date DATE NOT NULL,
    due_date DATE,
    subtotal DOUBLE DEFAULT 0,
    tax_amount DOUBLE DEFAULT 0,
    grand_total DOUBLE DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Draft',
    order_number VARCHAR(100),
    payment_terms VARCHAR(100),
    reverse_charge TINYINT DEFAULT 0,
    adjustment DOUBLE DEFAULT 0,
    tds_amount DOUBLE DEFAULT 0,
    tcs_amount DOUBLE DEFAULT 0,
    attachment_path TEXT,
    notes TEXT,
    discount_amount DOUBLE DEFAULT 0,
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Bill Items Table
CREATE TABLE IF NOT EXISTS bill_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity DOUBLE NOT NULL,
    rate DOUBLE NOT NULL,
    gst_percent DOUBLE DEFAULT 0,
    amount DOUBLE NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT,
    bill_id INT,
    customer_id INT,
    vendor_id INT,
    amount DOUBLE NOT NULL,
    date DATE NOT NULL,
    method VARCHAR(100),
    notes TEXT,
    payment_number VARCHAR(100),
    deposit_to VARCHAR(100),
    bank_charges DOUBLE DEFAULT 0,
    tax_deducted DOUBLE DEFAULT 0,
    tax_account VARCHAR(100),
    attachment_path TEXT,
    reference VARCHAR(100),
    send_thank_you TINYINT DEFAULT 0,
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Settings Table
CREATE TABLE IF NOT EXISTS settings (
    `key` VARCHAR(100) PRIMARY KEY,
    value TEXT
);

-- Insert Default Settings
INSERT IGNORE INTO settings (`key`, value) VALUES ('company_name', 'My Company');
INSERT IGNORE INTO settings (`key`, value) VALUES ('company_address', '123 Business St');
INSERT IGNORE INTO settings (`key`, value) VALUES ('company_gstin', '');
INSERT IGNORE INTO settings (`key`, value) VALUES ('company_state', '');
INSERT IGNORE INTO settings (`key`, value) VALUES ('invoice_prefix', 'INV-');

-- Performance Indexes
CREATE INDEX idx_stock_batches_item ON stock_batches (item_id, quantity_remaining);
CREATE INDEX idx_items_sku ON items (sku);
CREATE INDEX idx_items_name ON items (name);
CREATE INDEX idx_invoices_customer_status ON invoices (customer_id, status, date);
CREATE INDEX idx_invoice_items_inv_item ON invoice_items (invoice_id, item_id);
CREATE INDEX idx_bills_vendor_status ON bills (vendor_id, status, date);
CREATE INDEX idx_bill_items_bill_item ON bill_items (bill_id, item_id);
CREATE INDEX idx_payments_inv_bill ON payments (invoice_id, bill_id);

