import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db import translate_query, init_db, execute_read_query, execute_write_query
from auth.auth_logic import (
    signup_user, login_user, get_all_users, update_user_role,
    delete_user, create_user_by_admin
)
from auth.session import Session

def test_query_translation():
    print("=== Testing Query Translation ===")
    
    # Mock MySQL config check if needed or test translation logic directly
    import database.db as db_mod
    original_is_mysql = db_mod.is_mysql
    db_mod.is_mysql = lambda: True
    try:
        q1 = "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)"
        t1 = translate_query(q1)
        print(f"Original: {q1}\nTranslated: {t1}")
        assert "REPLACE INTO settings (`key`, value) VALUES (%s, %s)" in t1 or "REPLACE INTO settings (`key`, value)" in t1, f"Failed t1: {t1}"

        q2 = "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)"
        t2 = translate_query(q2)
        print(f"Original: {q2}\nTranslated: {t2}")
        assert "INSERT IGNORE INTO settings (`key`, value)" in t2, f"Failed t2: {t2}"
        print("Query translation tests PASSED!")
    finally:
        db_mod.is_mysql = original_is_mysql

def test_role_and_user_mgmt():
    print("\n=== Testing Role and User Management ===")
    init_db()
    
    # Clean up test users
    execute_write_query("DELETE FROM users WHERE email LIKE '%@testrole.com'")
    
    # Create first user -> should be owner
    res1 = signup_user("Test Owner", "owner@testrole.com", "pass123", role="owner")
    assert res1, "Failed to create owner user"
    
    u_owner = login_user("owner@testrole.com", "pass123")
    assert u_owner is not None, "Owner login failed"
    assert u_owner.get('role') == 'owner', f"Expected owner role, got {u_owner.get('role')}"
    print("First user assigned 'owner' role: OK")

    # Session test with owner
    Session.get_instance().set_user(u_owner)
    assert Session.get_instance().is_owner(), "Session.is_owner should be True"
    assert Session.get_instance().can_access_module("Users"), "Owner should access Users module"

    # Create manager user
    res2 = create_user_by_admin("Test Manager", "manager@testrole.com", "pass123", role="manager")
    assert res2, "Failed to create manager user"

    u_mgr = login_user("manager@testrole.com", "pass123")
    assert u_mgr is not None, "Manager login failed"
    assert u_mgr.get('role') == 'manager', f"Expected manager role, got {u_mgr.get('role')}"
    print("Manager user created and logged in: OK")

    # Session test with manager
    Session.get_instance().set_user(u_mgr)
    assert not Session.get_instance().is_owner(), "Session.is_owner should be False for manager"
    assert Session.get_instance().is_manager(), "Session.is_manager should be True for manager"
    assert not Session.get_instance().can_access_module("Users"), "Manager should NOT access Users module"
    assert Session.get_instance().can_access_module("Invoices"), "Manager should access Invoices module"

    # Create staff user
    res3 = create_user_by_admin("Test Staff", "staff@testrole.com", "pass123", role="staff")
    assert res3, "Failed to create staff user"

    u_staff = login_user("staff@testrole.com", "pass123")
    assert u_staff is not None, "Staff login failed"
    assert u_staff.get('role') == 'staff', f"Expected staff role, got {u_staff.get('role')}"
    print("Staff user created and logged in: OK")

    # Session test with staff
    Session.get_instance().set_user(u_staff)
    assert not Session.get_instance().is_manager(), "Session.is_manager should be False for staff"
    assert not Session.get_instance().can_access_module("Reports"), "Staff should NOT access Reports module"
    assert Session.get_instance().can_access_module("Invoices"), "Staff should access Invoices module"

    # Test Role Update
    res_update = update_user_role(u_staff['id'], 'manager')
    assert res_update, "Failed to update staff role to manager"
    u_staff_updated = login_user("staff@testrole.com", "pass123")
    assert u_staff_updated.get('role') == 'manager', "Failed role update check"
    print("User role update: OK")

    # Test Get All Users
    all_u = get_all_users()
    emails = [u['email'] for u in all_u]
    assert "owner@testrole.com" in emails, "Owner missing from get_all_users"
    print(f"Total users fetched: {len(all_u)}: OK")

    # Clean up test users
    execute_write_query("DELETE FROM users WHERE email LIKE '%@testrole.com'")
    print("Role and User Management tests PASSED!")

if __name__ == "__main__":
    test_query_translation()
    test_role_and_user_mgmt()
