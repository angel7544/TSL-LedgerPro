
import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), "database", "ledgerpro.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if customer_id exists
        cursor.execute("PRAGMA table_info(payments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'customer_id' not in columns:
            print("Adding customer_id to payments table...")
            cursor.execute("ALTER TABLE payments ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
            
            # Backfill customer_id
            print("Backfilling customer_id...")
            cursor.execute("""
                UPDATE payments 
                SET customer_id = (SELECT customer_id FROM invoices WHERE invoices.id = payments.invoice_id)
                WHERE invoice_id IS NOT NULL
            """)
            
        if 'vendor_id' not in columns:
            print("Adding vendor_id to payments table...")
            cursor.execute("ALTER TABLE payments ADD COLUMN vendor_id INTEGER REFERENCES vendors(id)")
            
            # Backfill vendor_id
            print("Backfilling vendor_id...")
            cursor.execute("""
                UPDATE payments 
                SET vendor_id = (SELECT vendor_id FROM bills WHERE bills.id = payments.bill_id)
                WHERE bill_id IS NOT NULL
            """)
            
        conn.commit()
        print("Migration v4 completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration v4 failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
