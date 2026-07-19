from database.db import get_connection, is_mysql

def migrate():
    print("Running migration v7 (Audit logs table)...")
    conn = get_connection()
    try:
        if is_mysql():
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT,
                    user_name VARCHAR(255),
                    action VARCHAR(100) NOT NULL,
                    module VARCHAR(100) NOT NULL,
                    record_id VARCHAR(100),
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        else:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    user_name TEXT,
                    action TEXT NOT NULL,
                    module TEXT NOT NULL,
                    record_id TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        print("Migration v7 completed successfully.")
    except Exception as e:
        print(f"Migration v7 exception: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
