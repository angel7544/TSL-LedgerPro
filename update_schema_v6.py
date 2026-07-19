from database.db import get_connection, is_mysql

def migrate():
    print("Running migration v6 (Multi-role support for users)...")
    conn = get_connection()
    try:
        if is_mysql():
            cursor = conn.cursor()
            # Check if role column exists in MySQL users table
            cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
            col = cursor.fetchone()
            if not col:
                print("Adding 'role' column to MySQL 'users' table...")
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'staff'")
                conn.commit()
                # On initial creation only, migrate pre-existing accounts to 'owner'
                cursor.execute("UPDATE users SET role = 'owner' WHERE role IS NULL OR role = '' OR role = 'staff'")
                conn.commit()
            else:
                # Fix any NULL or empty roles without touching existing 'staff' or 'manager' users
                cursor.execute("UPDATE users SET role = 'owner' WHERE role IS NULL OR role = ''")
                conn.commit()
        else:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'role' not in columns:
                print("Adding 'role' column to SQLite 'users' table...")
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'staff'")
                conn.commit()
                # On initial creation only, migrate pre-existing accounts to 'owner'
                cursor.execute("UPDATE users SET role = 'owner' WHERE role IS NULL OR role = '' OR role = 'staff'")
                conn.commit()
            else:
                # Fix any NULL or empty roles without touching existing 'staff' or 'manager' users
                cursor.execute("UPDATE users SET role = 'owner' WHERE role IS NULL OR role = ''")
                conn.commit()

        print("Migration v6 completed successfully.")
    except Exception as e:
        print(f"Migration v6 exception: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
