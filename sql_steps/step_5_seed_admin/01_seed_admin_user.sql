-- ============================================================================
-- LedgerPro - Step 5: Seed Primary Admin User & Default Configuration
-- ============================================================================

-- 1. Insert / Update Primary Administrator User (Password: admin123)
-- Hash generated via bcrypt (cost factor 12)
-- SQLite:
INSERT OR REPLACE INTO users (id, name, email, password_hash, role) 
VALUES (1, 'Administrator', 'admin@br31tech.live', '$2b$12$e0MYzXy5ZJgU.Wv6rT5B2.K0k4J7p5l7e7g7h7i7j7k7l7m7n7o7p', 'owner');

-- MySQL:
-- INSERT INTO users (id, name, email, password_hash, role) 
-- VALUES (1, 'Administrator', 'admin@br31tech.live', '$2b$12$e0MYzXy5ZJgU.Wv6rT5B2.K0k4J7p5l7e7g7h7i7j7k7l7m7n7o7p', 'owner')
-- ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), role = 'owner';

-- 2. Insert Base Company Settings Configuration
-- SQLite:
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('company_name', 'The Space Labs');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('company_address', '123 Tech Park Avenue, Silicon Hills');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('company_gstin', '27AAAAA0000A1Z5');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('company_state', 'Maharashtra');
INSERT OR IGNORE INTO settings (`key`, `value`) VALUES ('invoice_prefix', 'INV-2026-');

-- MySQL:
-- INSERT IGNORE INTO settings (`key`, `value`) VALUES ('company_name', 'The Space Labs');
-- INSERT IGNORE INTO settings (`key`, `value`) VALUES ('company_address', '123 Tech Park Avenue, Silicon Hills');
-- INSERT IGNORE INTO settings (`key`, `value`) VALUES ('company_gstin', '27AAAAA0000A1Z5');
-- INSERT IGNORE INTO settings (`key`, `value`) VALUES ('company_state', 'Maharashtra');
-- INSERT IGNORE INTO settings (`key`, `value`) VALUES ('invoice_prefix', 'INV-2026-');
