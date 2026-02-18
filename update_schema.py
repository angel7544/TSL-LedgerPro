import sqlite3
import os
from database.db import DB_NAME

def migrate():
    # Check if DB exists before connecting
    if not os.path.exists(DB_NAME):
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    columns_to_add = [
        ("account_code", "TEXT"),
        ("purchase_account_code", "TEXT"),
        ("inventory_account_code", "TEXT"),
        ("taxable", "INTEGER DEFAULT 1"),
        ("exemption_reason", "TEXT"),
        ("taxability_type", "TEXT"),
        ("product_type", "TEXT"),
        ("intra_state_tax_rate", "REAL DEFAULT 0"),
        ("inter_state_tax_rate", "REAL DEFAULT 0"),
        ("purchase_description", "TEXT"),
        ("inventory_valuation_method", "TEXT"),
        ("item_type", "TEXT DEFAULT 'Goods'"),
        ("is_sellable", "INTEGER DEFAULT 1"),
        ("is_purchasable", "INTEGER DEFAULT 1"),
        ("track_inventory", "INTEGER DEFAULT 1"),
        ("opening_stock", "REAL DEFAULT 0"),
        ("vendor_id", "INTEGER")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE items ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"Column {col_name} already exists")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
