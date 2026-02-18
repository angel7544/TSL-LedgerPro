import sqlite3
import os
import sys

def _resolve_paths():
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        db_dir = os.path.join(exe_dir, "data")
        os.makedirs(db_dir, exist_ok=True)
        db_name = os.path.join(db_dir, "ledgerpro.db")
        meipass = getattr(sys, "_MEIPASS", exe_dir)
        schema_file = os.path.join(meipass, "database", "schema.sql")
        return db_name, schema_file
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "ledgerpro.db"), os.path.join(base_dir, "schema.sql")

DB_NAME, SCHEMA_FILE = _resolve_paths()

def get_connection():
    # Increased timeout to 30 seconds to prevent "database is locked" errors
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME, timeout=30.0)
        # Enable WAL on creation too
        conn.execute("PRAGMA journal_mode=WAL;")
        with open(SCHEMA_FILE, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized.")
    else:
        # Check if tables exist
        conn = sqlite3.connect(DB_NAME, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Tables missing. Initializing schema...")
            with open(SCHEMA_FILE, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
        conn.close()
    run_migrations()

def run_migrations():
    # Only run migrations if not frozen (development) or if explicitly needed.
    # When frozen, migrations can be risky if import mechanisms fail.
    # But we need them for updates. Let's wrap them carefully.
    
    # V1
    try:
        import update_schema
        update_schema.migrate()
    except ImportError:
        pass # Likely frozen and module not found in standard way, or not bundled
    except Exception as e:
        print(f"Migration v1 failed: {e}")

    # V2
    try:
        import update_schema_v2
        update_schema_v2.migrate()
    except ImportError:
        pass
    except Exception as e:
        print(f"Migration v2 failed: {e}")

    # V3
    try:
        import update_schema_v3
        update_schema_v3.migrate()
    except ImportError:
        pass
    except Exception as e:
        print(f"Migration v3 failed: {e}")

    # V4
    try:
        import update_schema_v4
        update_schema_v4.migrate()
    except ImportError:
        pass
    except Exception as e:
        print(f"Migration v4 failed: {e}")

def execute_read_query(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    finally:
        conn.close()

def execute_write_query(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_row_id = cursor.lastrowid
        return last_row_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_transaction(operations):
    """
    Executes a list of queries in a single transaction.
    operations: list of (query, params) tuples.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for query, params in operations:
            cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
