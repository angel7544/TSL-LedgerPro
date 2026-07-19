import bcrypt
from database.db import execute_read_query, execute_write_query

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def login_user(email, password):
    """
    Verifies user credentials.
    Returns user dict if successful, None otherwise.
    """
    try:
        user_rows = execute_read_query("SELECT * FROM users WHERE email = ?", (email,))
        if not user_rows:
            return None
        
        user = dict(user_rows[0])
        if check_password(password, user['password_hash']):
            # Default role if not set or empty
            if not user.get('role'):
                user['role'] = 'owner'
            return user
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def signup_user(name, email, password, role='staff'):
    """
    Registers a new user.
    If no owner exists in the system, assigns 'owner' role.
    """
    hashed = hash_password(password)
    try:
        owner_res = execute_read_query("SELECT COUNT(*) as cnt FROM users WHERE role = 'owner'")
        owner_count = owner_res[0]['cnt'] if owner_res and isinstance(owner_res[0], dict) else (owner_res[0][0] if owner_res else 0)
        
        if owner_count == 0:
            assigned_role = 'owner'
        else:
            assigned_role = role if role in ['owner', 'manager', 'staff'] else 'staff'
            
        execute_write_query("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", 
                           (name, email, hashed, assigned_role))
        return True
    except Exception as e:
        print(f"Signup error: {e}")
        return False

def update_password(user_id, new_password):
    """Updates user password."""
    hashed = hash_password(new_password)
    try:
        execute_write_query("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
        return True
    except Exception as e:
        print(f"Update password error: {e}")
        return False

def get_all_users():
    """Retrieves all registered users."""
    try:
        rows = execute_read_query("SELECT id, name, email, role, created_at FROM users ORDER BY id ASC")
        users = []
        for r in rows:
            u = dict(r)
            if not u.get('role'):
                u['role'] = 'owner'
            users.append(u)
        return users
    except Exception as e:
        print(f"Get all users error: {e}")
        return []

def create_user_by_admin(name, email, password, role):
    """Admin endpoint to create a user with specified role."""
    if role not in ['owner', 'manager', 'staff']:
        role = 'staff'
    return signup_user(name, email, password, role=role)

def update_user_role(user_id, new_role):
    """Updates user role (owner, manager, staff)."""
    if new_role not in ['owner', 'manager', 'staff']:
        return False
    try:
        execute_write_query("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        return True
    except Exception as e:
        print(f"Update user role error: {e}")
        return False

def delete_user(user_id):
    """Deletes a user account."""
    try:
        execute_write_query("DELETE FROM users WHERE id = ?", (user_id,))
        return True
    except Exception as e:
        print(f"Delete user error: {e}")
        return False
