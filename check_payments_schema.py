
import sqlite3
import os

DB_PATH = os.path.join("database", "ledgerpro.db")

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(payments)")
    columns = cursor.fetchall()
    print("Payments Table Columns:")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
