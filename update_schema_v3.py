import sqlite3
import os
from database.db import DB_NAME

DB_FILE = DB_NAME

def add_column_if_not_exists(cursor, table, column, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding column {column} to {table}: {e}")

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database file not found at {DB_FILE}")
        return

    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    cursor = conn.cursor()

    # --- Invoices Adjustment ---
    add_column_if_not_exists(cursor, "invoices", "adjustment", "REAL DEFAULT 0")

    conn.commit()
    conn.close()
    print("Migration v3 complete.")

if __name__ == "__main__":
    migrate()
