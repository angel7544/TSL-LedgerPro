-- ============================================================================
-- LedgerPro - Step 3: Multi-Role Access Control (RBAC) & Organization Schema
-- ============================================================================

-- 1. User Roles Matrix & Policies:
--    - Owner:   Full Administrative access (User management, Audit logs, Company settings, Financial reports)
--    - Manager: Operations management (Invoices, Bills, Inventory adjustments, Customer/Vendor master)
--    - Staff:   Counter Billing & POS transactions (Create invoices, view stock levels)

-- Ensure role column constraints in users table
-- SQLite Schema alteration:
-- ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'staff';

-- MySQL Schema alteration:
-- ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'staff';

-- 2. Role Constraint Verification & Updates
UPDATE users 
SET role = 'owner' 
WHERE role IS NULL OR role = '' OR role NOT IN ('owner', 'manager', 'staff');

-- 3. Audit Logging Table DDL for RBAC Enforcement Tracking
-- SQLite:
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

-- MySQL:
-- CREATE TABLE IF NOT EXISTS audit_logs (
--     id INT PRIMARY KEY AUTO_INCREMENT,
--     user_id INT,
--     user_name VARCHAR(255),
--     action VARCHAR(100) NOT NULL,
--     module VARCHAR(100) NOT NULL,
--     record_id VARCHAR(100),
--     details TEXT,
--     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Multi-Organization Profile Settings Keys
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('organization_name', 'The Space Labs');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('organization_tagline', 'Leading Enterprise Solutions');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('organization_currency', 'INR');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('organization_country', 'India');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('thermal_printer_size', '80mm');
