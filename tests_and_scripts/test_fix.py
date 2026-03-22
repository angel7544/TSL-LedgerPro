import sqlite3
import os
import sys

# Ensure we can import from the root directory
sys.path.append(os.getcwd())

from database.db import init_db, DB_NAME, execute_read_query

def check_column_exists(table, column):
    try:
        # Pragma table_info returns (cid, name, type, notnull, dflt_value, pk)
        columns = execute_read_query(f"PRAGMA table_info({table})")
        found = any(col['name'] == column for col in columns)
        return found
    except Exception as e:
        print(f"Error checking column {column} in {table}: {e}")
        return False

def test_fix():
    print(f"Testing database: {DB_NAME}")
    
    # Run migrations
    init_db()
    
    # Check for opening_stock in items
    if check_column_exists('items', 'opening_stock'):
        print("SUCCESS: column 'opening_stock' exists in 'items'")
    else:
        print("FAILURE: column 'opening_stock' MISSING in 'items'")

    # Check for adjustment in invoices (from v3)
    if check_column_exists('invoices', 'adjustment'):
        print("SUCCESS: column 'adjustment' exists in 'invoices'")
    else:
        print("FAILURE: column 'adjustment' MISSING in 'invoices'")

if __name__ == "__main__":
    test_fix()
