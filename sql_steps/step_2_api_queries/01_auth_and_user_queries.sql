-- ============================================================================
-- LedgerPro - Step 2 API Queries: Authentication & User Management
-- ============================================================================

-- 1. Get user by email (Authentication)
SELECT id, name, email, password_hash, role, created_at 
FROM users 
WHERE email = ?;

-- 2. Count owner role users (Initial signup check)
SELECT COUNT(*) AS cnt 
FROM users 
WHERE role = 'owner';

-- 3. Register / Signup new user
INSERT INTO users (name, email, password_hash, role) 
VALUES (?, ?, ?, ?);

-- 4. Get all users ordered by ID
SELECT id, name, email, role, created_at 
FROM users 
ORDER BY id ASC;

-- 5. Update user password
UPDATE users 
SET password_hash = ? 
WHERE id = ?;

-- 6. Update user role (Owner, Manager, Staff)
UPDATE users 
SET role = ? 
WHERE id = ?;

-- 7. Delete user account
DELETE FROM users 
WHERE id = ?;

-- 8. Fix empty/null roles migration fallback
UPDATE users 
SET role = 'owner' 
WHERE role IS NULL OR role = '';
