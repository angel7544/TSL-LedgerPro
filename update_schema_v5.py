import sqlite3
import os
from database.db import DB_NAME

def migrate():
    if not os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Add selling prices to items
    for sp in ['sp1', 'sp2', 'sp3']:
        try:
            cursor.execute(f"ALTER TABLE items ADD COLUMN {sp} REAL DEFAULT 0")
            print(f"Added {sp} to items")
        except sqlite3.OperationalError:
            pass # Already exists

    # Add customer_type to customers
    try:
        cursor.execute("ALTER TABLE customers ADD COLUMN customer_type TEXT DEFAULT 'Type 1'")
        print("Added customer_type to customers")
    except sqlite3.OperationalError:
        pass # Already exists

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
