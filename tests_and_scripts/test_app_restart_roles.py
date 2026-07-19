import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import init_db, execute_write_query, execute_read_query, translate_query
from auth.auth_logic import create_user_by_admin, login_user
from update_schema_v6 import migrate

def test_app_restart_roles():
    print("=== Testing App Restarts & Role Persistence ===")
    init_db()
    
    # Clean up test user
    execute_write_query("DELETE FROM users WHERE email = 'persist_staff@test.com'")
    
    # Create staff user
    res = create_user_by_admin("Staff Persist", "persist_staff@test.com", "pass123", role="staff")
    assert res, "Failed to create staff user"
    
    u = login_user("persist_staff@test.com", "pass123")
    assert u['role'] == 'staff', f"Expected staff role, got {u['role']}"
    print("Created staff user successfully.")
    
    # Simulate app restart by running migration again
    print("Simulating app restart (running migration v6 again)...")
    migrate()
    
    # Verify user role is still 'staff' and wasn't changed to 'owner'
    u_after = login_user("persist_staff@test.com", "pass123")
    assert u_after['role'] == 'staff', f"BUG: Staff role was reset to '{u_after['role']}' after app restart!"
    print("PASSED: Staff user role persisted as 'staff' across app restart!")

    # Clean up test user
    execute_write_query("DELETE FROM users WHERE email = 'persist_staff@test.com'")

def test_strftime_translation():
    print("\n=== Testing Dashboard strftime Translation ===")
    q1 = "SELECT strftime('%Y-%m', date) as month, SUM(grand_total) as total FROM invoices WHERE strftime('%Y', date) = ?"
    t1 = translate_query(q1)
    print(f"Original SQL: {q1}\nTranslated SQL: {t1}")
    assert "DATE_FORMAT" in t1 and "YEAR" in t1 and "strftime" not in t1, f"Failed strftime translation: {t1}"
    print("PASSED: strftime query translation verified!")

if __name__ == "__main__":
    test_app_restart_roles()
    test_strftime_translation()
