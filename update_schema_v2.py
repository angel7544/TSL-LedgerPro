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
    # Check if DB exists
    if not os.path.exists(DB_FILE):
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # --- Invoices ---
    add_column_if_not_exists(cursor, "invoices", "order_number", "TEXT")
    add_column_if_not_exists(cursor, "invoices", "terms", "TEXT")
    add_column_if_not_exists(cursor, "invoices", "salesperson", "TEXT")
    add_column_if_not_exists(cursor, "invoices", "subject", "TEXT")
    add_column_if_not_exists(cursor, "invoices", "customer_notes", "TEXT") # Distinct from internal notes
    add_column_if_not_exists(cursor, "invoices", "terms_conditions", "TEXT")
    add_column_if_not_exists(cursor, "invoices", "round_off", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "invoices", "tds_amount", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "invoices", "tcs_amount", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "invoices", "attachment_path", "TEXT")

    # --- Bills ---
    add_column_if_not_exists(cursor, "bills", "order_number", "TEXT")
    add_column_if_not_exists(cursor, "bills", "payment_terms", "TEXT")
    add_column_if_not_exists(cursor, "bills", "reverse_charge", "INTEGER DEFAULT 0") # Boolean
    add_column_if_not_exists(cursor, "bills", "adjustment", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "bills", "tds_amount", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "bills", "tcs_amount", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "bills", "attachment_path", "TEXT")
    add_column_if_not_exists(cursor, "bills", "notes", "TEXT")
    add_column_if_not_exists(cursor, "bills", "discount_amount", "REAL DEFAULT 0") # Was missing in schema check? Let's add it.

    # --- Payments ---
    add_column_if_not_exists(cursor, "payments", "payment_number", "TEXT")
    add_column_if_not_exists(cursor, "payments", "deposit_to", "TEXT")
    add_column_if_not_exists(cursor, "payments", "bank_charges", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "payments", "tax_deducted", "REAL DEFAULT 0")
    add_column_if_not_exists(cursor, "payments", "tax_account", "TEXT")
    add_column_if_not_exists(cursor, "payments", "attachment_path", "TEXT")
    add_column_if_not_exists(cursor, "payments", "reference", "TEXT")
    add_column_if_not_exists(cursor, "payments", "send_thank_you", "INTEGER DEFAULT 0")
    
    # --- Custom Fields (JSON Store) ---
    add_column_if_not_exists(cursor, "invoices", "custom_fields", "TEXT")
    add_column_if_not_exists(cursor, "bills", "custom_fields", "TEXT")
    add_column_if_not_exists(cursor, "payments", "custom_fields", "TEXT")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
