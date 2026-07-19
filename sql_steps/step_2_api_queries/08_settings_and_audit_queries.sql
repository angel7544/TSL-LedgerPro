-- ============================================================================
-- LedgerPro - Step 2 API Queries: Company Settings & Audit Logs
-- ============================================================================

-- ----------------------------------------------------------------------------
-- SETTINGS
-- ----------------------------------------------------------------------------

-- 1. Fetch setting value by key
SELECT `value` FROM settings WHERE `key` = ?;

-- 2. Fetch all system settings
SELECT `key`, `value` FROM settings;

-- 3. Upsert setting (Insert or Replace)
-- SQLite:
INSERT OR REPLACE INTO settings (`key`, `value`) VALUES (?, ?);
-- MySQL:
-- REPLACE INTO settings (`key`, `value`) VALUES (?, ?);

-- ----------------------------------------------------------------------------
-- AUDIT LOGS
-- ----------------------------------------------------------------------------

-- 1. Insert Audit Log Entry
INSERT INTO audit_logs (user_id, user_name, action, module, record_id, details) 
VALUES (?, ?, ?, ?, ?, ?);

-- 2. Fetch recent audit logs (Admin Monitoring)
SELECT id, user_id, user_name, action, module, record_id, details, timestamp 
FROM audit_logs 
ORDER BY id DESC 
LIMIT ?;

-- 3. Filter audit logs by module or user
SELECT id, user_id, user_name, action, module, record_id, details, timestamp 
FROM audit_logs 
WHERE module = ? OR user_name = ? 
ORDER BY id DESC;
