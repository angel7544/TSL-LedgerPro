import bcrypt
from database.db import execute_read_query, execute_write_query, init_db
import sys

def create_admin_user():
    # Ensure DB is initialized
    init_db()
    
    email = "admin@br31tech.live"
    password = "admin123"
    name = "Administrator"
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Check if user exists
    existing = execute_read_query("SELECT id FROM users WHERE email = ?", (email,))
    
    if existing:
        print(f"User '{email}' already exists. Updating password...")
        execute_write_query("UPDATE users SET password_hash = ? WHERE email = ?", (hashed, email))
        print("Password updated successfully.")
    else:
        print(f"Creating user '{email}'...")
        execute_write_query("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", 
                           (name, email, hashed))
        print("User created successfully.")

if __name__ == "__main__":
    create_admin_user()
