-- ============================================================================
-- LedgerPro - Step 4: Recreate MySQL Database (Drop & Fresh Creation)
-- Engine: MySQL 8.0 / MariaDB
-- ============================================================================

DROP DATABASE IF EXISTS ledgerpro;
CREATE DATABASE ledgerpro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ledgerpro;

-- 1. Users Table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'staff',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Customers Table
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    gstin VARCHAR(50),
    state VARCHAR(100),
    customer_type VARCHAR(50) DEFAULT 'Type 1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Vendors Table
CREATE TABLE vendors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    gstin VARCHAR(50),
    state VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Items Table
CREATE TABLE items (
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Stock Batches Table
CREATE TABLE stock_batches (
    id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    quantity_remaining DOUBLE NOT NULL,
    purchase_rate DOUBLE NOT NULL,
    purchase_date DATE NOT NULL,
    vendor_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Invoices Table
CREATE TABLE invoices (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Invoice Items Table
CREATE TABLE invoice_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity DOUBLE NOT NULL,
    rate DOUBLE NOT NULL,
    discount_percent DOUBLE DEFAULT 0,
    gst_percent DOUBLE DEFAULT 0,
    amount DOUBLE NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Bills Table
CREATE TABLE bills (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Bill Items Table
CREATE TABLE bill_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity DOUBLE NOT NULL,
    rate DOUBLE NOT NULL,
    gst_percent DOUBLE DEFAULT 0,
    amount DOUBLE NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Payments Table
CREATE TABLE payments (
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
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE SET NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Settings Table
CREATE TABLE settings (
    `key` VARCHAR(100) PRIMARY KEY,
    value TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Audit Logs Table
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    user_name VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    module VARCHAR(100) NOT NULL,
    record_id VARCHAR(100),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- MySQL Views Creation
CREATE OR REPLACE VIEW view_invoice_summary AS
SELECT i.id AS invoice_id, i.invoice_number, i.date AS invoice_date, i.due_date, c.id AS customer_id, c.name AS customer_name, c.phone AS customer_phone, c.gstin AS customer_gstin, i.subtotal, i.tax_amount, i.discount_amount, i.grand_total, i.status, IFNULL(SUM(p.amount), 0) AS total_paid, (i.grand_total - IFNULL(SUM(p.amount), 0)) AS balance_due, i.created_at
FROM invoices i JOIN customers c ON i.customer_id = c.id LEFT JOIN payments p ON i.id = p.invoice_id GROUP BY i.id, i.invoice_number, i.date, i.due_date, c.id, c.name, c.phone, c.gstin, i.subtotal, i.tax_amount, i.discount_amount, i.grand_total, i.status, i.created_at;

CREATE OR REPLACE VIEW view_customer_balance AS
SELECT c.id AS customer_id, c.name AS customer_name, c.email, c.phone, c.gstin, IFNULL(inv.total_invoiced, 0) AS total_invoiced, IFNULL(pay.total_paid, 0) AS total_paid, (IFNULL(inv.total_invoiced, 0) - IFNULL(pay.total_paid, 0)) AS outstanding_balance
FROM customers c LEFT JOIN (SELECT customer_id, SUM(grand_total) AS total_invoiced FROM invoices GROUP BY customer_id) inv ON c.id = inv.customer_id LEFT JOIN (SELECT customer_id, SUM(amount) AS total_paid FROM payments WHERE customer_id IS NOT NULL OR invoice_id IS NOT NULL GROUP BY customer_id) pay ON c.id = pay.customer_id;
