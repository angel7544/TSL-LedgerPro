import sqlite3
import os

DB_PATH = os.path.join("database", "ledgerpro.db")

try:
    print(f"Connecting to {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['invoices', 'bills', 'items', 'payments', 'customers', 'settings']
    
    for table in tables:
        print(f"\n{table.capitalize()} Columns:")
        try:
            cursor.execute(f'PRAGMA table_info({table})')
            columns = cursor.fetchall()
            if columns:
                for row in columns:
                    print(f"  {row[1]} ({row[2]})")
            else:
                print(f"  Table {table} not found or empty.")
        except Exception as e:
            print(f"  Error reading table {table}: {e}")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
