import bcrypt
from database.db import execute_read_query, execute_write_query

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    # If hashed is bytes, decode it; if it's str, encode it for bcrypt
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
        
        user = user_rows[0]
        # user['password_hash'] should be the hash string from DB
        if check_password(password, user['password_hash']):
            return dict(user)
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def signup_user(name, email, password):
    """
    Registers a new user.
    Returns True if successful, raises error if email exists.
    """
    hashed = hash_password(password)
    try:
        execute_write_query("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                           (name, email, hashed))
        return True
    except Exception as e:
        # Likely unique constraint violation
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
