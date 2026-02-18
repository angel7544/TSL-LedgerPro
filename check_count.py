from database.db import execute_read_query
print(f"Invoices: {len(execute_read_query('SELECT * FROM invoices'))}")
print(f"Bills: {len(execute_read_query('SELECT * FROM bills'))}")
