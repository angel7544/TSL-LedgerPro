import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(__file__), "ledgerpro.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

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
    try:
        import update_schema
    except Exception:
        pass
    try:
        import update_schema_v2
        update_schema_v2.migrate()
    except Exception:
        pass
    try:
        import update_schema_v3
        update_schema_v3.migrate()
    except Exception:
        pass

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
