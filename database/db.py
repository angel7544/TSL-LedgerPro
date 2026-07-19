import sqlite3
import os
import sys
import re
try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

# Import our new config manager
try:
    from config_manager import load_config
except ImportError:
    # Fallback if run from an unexpected directory
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    try:
        from config_manager import load_config
    except ImportError:
        def load_config(): return {"database": {"type": "sqlite"}}

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

def get_config():
    return load_config().get("database", {"type": "sqlite"})

def is_mysql():
    return get_config().get("type") == "mysql" and pymysql is not None

def get_connection():
    conf = get_config()
    if is_mysql():
        conn = pymysql.connect(
            host=conf.get("host", "localhost"),
            port=int(conf.get("port", 3306)),
            user=conf.get("user", "root"),
            password=conf.get("password", ""),
            database=conf.get("database", "ledgerpro"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    else:
        # Increased timeout to 30 seconds to prevent "database is locked" errors
        conn = sqlite3.connect(DB_NAME, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

def translate_query(query):
    if not is_mysql():
        return query
        
    # Replace '?' with '%s' for parameterized queries
    q = query.replace('?', '%s')

    # SQLite strftime to MySQL
    q = re.sub(r"strftime\('%Y-%m',\s*([^)]+)\)", r"DATE_FORMAT(\1, '%Y-%m')", q)
    q = re.sub(r"strftime\('%m',\s*([^)]+)\)", r"MONTH(\1)", q)
    q = re.sub(r"strftime\('%Y',\s*([^)]+)\)", r"YEAR(\1)", q)
    
    # SQLite julianday to MySQL DATEDIFF
    q = re.sub(r"\(julianday\('now'\)\s*-\s*julianday\(([^)]+)\)\)", r"DATEDIFF(NOW(), \1)", q)
    q = re.sub(r"julianday\('now'\)\s*-\s*julianday\(([^)]+)\)", r"DATEDIFF(NOW(), \1)", q)
    
    # SQLite GROUP_CONCAT to MySQL
    q = re.sub(r"GROUP_CONCAT\(([^,]+),\s*'([^']+)'\)", r"GROUP_CONCAT(\1 SEPARATOR '\2')", q)

    # SQLite INSERT OR REPLACE / INSERT OR IGNORE syntax to MySQL
    q = re.sub(r"\bINSERT\s+OR\s+REPLACE\s+INTO\b", "REPLACE INTO", q, flags=re.IGNORECASE)
    q = re.sub(r"\bINSERT\s+OR\s+IGNORE\s+INTO\b", "INSERT IGNORE INTO", q, flags=re.IGNORECASE)

    # Escape any literal '%' signs that are not part of '%s' placeholders or already doubled '%%' for PyMySQL format safety
    q = re.sub(r'(?<!%)%(?![s%])', '%%', q)

    # Replace reserved word 'key' with backticks if used in SELECT or WHERE clause for settings table
    # Only replace if it's not already backticked and not part of a larger word
    q = re.sub(r"(?<!`)(\bkey\b)(?!`)", "`key`", q)

    return q

def init_db():
    if is_mysql():
        # Schema creation is handled by mysql_setup.py for MySQL, but run migrations to ensure role column
        print("Using MySQL backend.")
        run_migrations()
        return

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
    if not is_mysql():
        # V1
        try:
            import update_schema
            update_schema.migrate()
        except ImportError:
            pass 
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

        # V5
        try:
            import update_schema_v5
            update_schema_v5.migrate()
        except ImportError:
            pass
        except Exception as e:
            print(f"Migration v5 failed: {e}")

    # V6 (Runs on both SQLite and MySQL to ensure role column exists)
    try:
        import update_schema_v6
        update_schema_v6.migrate()
    except ImportError:
        pass
    except Exception as e:
        print(f"Migration v6 failed: {e}")

    # V7 (Audit logs table)
    try:
        import update_schema_v7
        update_schema_v7.migrate()
    except ImportError:
        pass
    except Exception as e:
        print(f"Migration v7 failed: {e}")

def execute_read_query(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(translate_query(query), params)
        result = cursor.fetchall()
        return result
    finally:
        conn.close()

def execute_write_query(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(translate_query(query), params)
        conn.commit()
        last_row_id = cursor.lastrowid
        return last_row_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_transaction(operations):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for query, params in operations:
            cursor.execute(translate_query(query), params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
