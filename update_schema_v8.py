from database.db import get_connection, is_mysql

def migrate():
    print("Running migration v8 (Database Indexes for Performance)...")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        indexes = [
            ("idx_stock_batches_item", "stock_batches", "(item_id, quantity_remaining)"),
            ("idx_items_sku", "items", "(sku)"),
            ("idx_items_name", "items", "(name)"),
            ("idx_invoices_customer_status", "invoices", "(customer_id, status, date)"),
            ("idx_invoice_items_inv_item", "invoice_items", "(invoice_id, item_id)"),
            ("idx_bills_vendor_status", "bills", "(vendor_id, status, date)"),
            ("idx_bill_items_bill_item", "bill_items", "(bill_id, item_id)"),
            ("idx_payments_inv_bill", "payments", "(invoice_id, bill_id)")
        ]
        
        for idx_name, table, cols in indexes:
            try:
                if is_mysql():
                    cursor.execute(f"CREATE INDEX {idx_name} ON {table} {cols}")
                else:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} {cols}")
            except Exception as e:
                # Ignore duplicate index creation error if already exists
                pass
                
        conn.commit()
        print("Migration v8 completed successfully.")
    except Exception as e:
        print(f"Migration v8 exception: {e}")
    finally:
        if not is_mysql():
            conn.close()

if __name__ == "__main__":
    migrate()
