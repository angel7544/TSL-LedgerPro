import pymysql
import os
import sys

def setup_mysql_database(host, port, user, password, db_name):
    print(f"Connecting to MySQL at {host}:{port} as {user}...")
    try:
        # Connect to MySQL server (without selecting a database yet)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database if not exists
            print(f"Creating database '{db_name}' if it does not exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
        connection.commit()
        connection.select_db(db_name)
        
        # Now let's run the schema_mysql.sql
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema_mysql.sql')
        if not os.path.exists(schema_path):
            print(f"Error: Schema file not found at {schema_path}")
            return False
            
        with open(schema_path, 'r') as f:
            sql_script = f.read()
            
        # Execute the statements one by one
        print("Executing MySQL schema...")
        with connection.cursor() as cursor:
            statements = sql_script.split(';')
            for statement in statements:
                stmt = statement.strip()
                if stmt:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        # Ignore Duplicate Key (1061) or Table Exists (1050) errors
                        if getattr(e, 'args', None) and e.args[0] in (1061, 1050):
                            pass
                        else:
                            print(f"Statement execution note: {e}")
        
        connection.commit()
        print("MySQL Database setup completed successfully!")
        
        # Update config.json
        from config_manager import load_config, save_config
        config = load_config()
        config['database'] = {
            "type": "mysql",
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": db_name
        }
        save_config(config)
        print("Updated config.json to use MySQL.")
        return True
        
    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    print("=== MySQL Database Setup for LedgerPro ===")
    host = input("MySQL Host (default: localhost): ") or "localhost"
    port = input("MySQL Port (default: 3306): ") or "3306"
    user = input("MySQL User (default: root): ") or "root"
    password = input("MySQL Password: ")
    db_name = input("Database Name (default: ledgerpro): ") or "ledgerpro"
    
    setup_mysql_database(host, int(port), user, password, db_name)
