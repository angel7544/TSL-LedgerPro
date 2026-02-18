import sqlite3
import os
from database.db import DB_NAME

def migrate():
    if not os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE payments ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
        print("Added customer_id to payments")
    except sqlite3.OperationalError:
        pass # Already exists

    try:
        cursor.execute("ALTER TABLE payments ADD COLUMN vendor_id INTEGER REFERENCES vendors(id)")
        print("Added vendor_id to payments")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()