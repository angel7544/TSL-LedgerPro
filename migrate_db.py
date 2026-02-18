import sqlite3
import os

DB_NAME = "database/ledgerpro.db"

def migrate():
    if not os.path.exists(DB_NAME):
        print("Database does not exist. Run main.py first.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(items)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Add purchase_price
    if 'purchase_price' not in columns:
        print("Adding purchase_price to items...")
        cursor.execute("ALTER TABLE items ADD COLUMN purchase_price REAL DEFAULT 0")
        
    # Add stock_on_hand
    if 'stock_on_hand' not in columns:
        print("Adding stock_on_hand to items...")
        cursor.execute("ALTER TABLE items ADD COLUMN stock_on_hand REAL DEFAULT 0")
        
    # Add reorder_point
    if 'reorder_point' not in columns:
        print("Adding reorder_point to items...")
        cursor.execute("ALTER TABLE items ADD COLUMN reorder_point REAL DEFAULT 0")
        
    # Add opening_stock_value (optional, but good for reference)
    if 'opening_stock_value' not in columns:
        print("Adding opening_stock_value to items...")
        cursor.execute("ALTER TABLE items ADD COLUMN opening_stock_value REAL DEFAULT 0")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
