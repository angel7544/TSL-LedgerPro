import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth.auth_logic import login_user, create_user_by_admin
from database.db import execute_write_query, init_db

def test_admin_verification_logic():
    print("=== Testing Admin Authentication Verification for DB Setup ===")
    init_db()
    
    # Ensure test owner and staff accounts
    execute_write_query("DELETE FROM users WHERE email IN ('admin_verify_owner@test.com', 'admin_verify_staff@test.com')")
    create_user_by_admin("Owner Tester", "admin_verify_owner@test.com", "ownerpass", role="owner")
    create_user_by_admin("Staff Tester", "admin_verify_staff@test.com", "staffpass", role="staff")
    
    # Verify owner credentials return valid owner user
    u_owner = login_user("admin_verify_owner@test.com", "ownerpass")
    assert u_owner is not None and u_owner.get('role') == 'owner', "Owner authentication failed"
    print("Owner verification PASSED.")
    
    # Verify staff credentials return staff user (which fails admin verification check)
    u_staff = login_user("admin_verify_staff@test.com", "staffpass")
    assert u_staff is not None and u_staff.get('role') == 'staff', "Staff authentication failed"
    assert u_staff.get('role') not in ['owner', 'admin'], "Staff role must not pass admin check"
    print("Staff non-admin check PASSED.")
    
    # Cleanup
    execute_write_query("DELETE FROM users WHERE email IN ('admin_verify_owner@test.com', 'admin_verify_staff@test.com')")
    print("All Admin DB Setup Verification tests PASSED!")

if __name__ == "__main__":
    test_admin_verification_logic()
