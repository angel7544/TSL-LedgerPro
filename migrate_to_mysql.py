import sqlite3
import pymysql
import os

def migrate_sqlite_to_mysql(host, port, user, password, dbname):
    """
    Migrates data from the local SQLite database to the target MySQL database.
    Assumes the MySQL schema has already been created (e.g., via setup_mysql_database).
    """
    print(f"Starting migration from SQLite to MySQL ({host}:{port}/{dbname})...")
    
    # 1. Connect to SQLite
    base_dir = os.path.dirname(__file__)
    sqlite_db_path = os.path.join(base_dir, "ledgerpro.db")
    
    if not os.path.exists(sqlite_db_path):
        print(f"SQLite database not found at {sqlite_db_path}")
        return False
        
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # 2. Connect to MySQL
    try:
        mysql_conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return False

    mysql_cursor = mysql_conn.cursor()

    # Tables to migrate in order (respecting foreign key constraints ideally)
    tables = [
        "users",
        "customers",
        "vendors",
        "items",
        "stock_batches",
        "invoices",
        "invoice_items",
        "bills",
        "bill_items",
        "payments",
        "settings"
    ]

    try:
        # Disable foreign key checks during migration
        mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        for table in tables:
            print(f"Migrating table: {table}...")
            
            # Get SQLite data
            try:
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
            except sqlite3.OperationalError as e:
                print(f"  Skipping {table}: {e}")
                continue

            if not rows:
                print(f"  Table {table} is empty. Skipping.")
                continue

            # Get column names
            columns = rows[0].keys()
            col_names_str = ", ".join([f"`{c}`" for c in columns])
            placeholders = ", ".join(["%s"] * len(columns))
            
            insert_query = f"INSERT IGNORE INTO {table} ({col_names_str}) VALUES ({placeholders})"
            
            # Insert into MySQL
            data_to_insert = []
            for row in rows:
                # Convert row to tuple, handling None values appropriately
                data_to_insert.append(tuple(row[c] for c in columns))
                
            if data_to_insert:
                mysql_cursor.executemany(insert_query, data_to_insert)
                print(f"  Migrated {len(data_to_insert)} rows into {table}.")

        mysql_conn.commit()
        print("Migration completed successfully!")
        return True

    except Exception as e:
        print(f"Error during migration: {e}")
        mysql_conn.rollback()
        return False
    finally:
        try:
            mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            mysql_conn.commit()
        except:
            pass
            
        sqlite_conn.close()
        mysql_conn.close()

if __name__ == "__main__":
    print("=== Data Migration Utility ===")
    from config_manager import load_config
    config = load_config().get("database", {})
    
    host = input(f"MySQL Host (default: {config.get('host', 'localhost')}): ") or config.get('host', 'localhost')
    port = input(f"MySQL Port (default: {config.get('port', 3306)}): ") or config.get('port', 3306)
    user = input(f"MySQL User (default: {config.get('user', 'root')}): ") or config.get('user', 'root')
    password = input("MySQL Password: ") or config.get('password', '')
    db_name = input(f"Database Name (default: {config.get('database', 'ledgerpro')}): ") or config.get('database', 'ledgerpro')
    
    migrate_sqlite_to_mysql(host, int(port), user, password, db_name)
