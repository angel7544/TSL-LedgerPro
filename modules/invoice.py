from database.db import execute_read_query, execute_transaction, execute_write_query
from modules.gst import calculate_gst
from modules.stock_fifo import reduce_stock_fifo, add_stock
import datetime

def generate_invoice_number():
    """Generates a new invoice number."""
    settings = execute_read_query("SELECT value FROM settings WHERE key='invoice_prefix'")
    prefix = settings[0]['value'] if settings else "INV-"
    
    rows = execute_read_query("SELECT invoice_number FROM invoices WHERE invoice_number LIKE ?", (f"{prefix}%",))
    max_num = 0
    for row in rows:
        inv = row['invoice_number'] or ""
        if not inv.startswith(prefix):
            continue
        suffix = inv[len(prefix):]
        if suffix.isdigit():
            num = int(suffix)
            if num > max_num:
                max_num = num
    next_num = max_num + 1
        
    return f"{prefix}{next_num:04d}"

def create_invoice(data):
    """
    Creates a new invoice, updates stock, and saves to database.
    
    Args:
        data (dict): Invoice data including customer_id, date, items, etc.
        
    Returns:
        int: The ID of the created invoice.
    """
    customer_id = data['customer_id']
    date = data['date']
    due_date = data.get('due_date')
    notes = data.get('notes', '')
    
    # New Fields
    order_number = data.get('order_number', '')
    terms = data.get('terms', '')
    salesperson = data.get('salesperson', '')
    subject = data.get('subject', '')
    customer_notes = data.get('customer_notes', '')
    terms_conditions = data.get('terms_conditions', '')
    round_off = data.get('round_off', 0.0)
    tds_amount = data.get('tds_amount', 0.0)
    tcs_amount = data.get('tcs_amount', 0.0)
    adjustment = data.get('adjustment', 0.0)
    status = data.get('status', 'Due')
    attachment_path = data.get('attachment_path', '')
    custom_fields = data.get('custom_fields', '{}') # JSON string
    
    items = data['items']
    
    # Get company state and customer state
    company_state_row = execute_read_query("SELECT value FROM settings WHERE key='company_state'")
    company_state = company_state_row[0]['value'] if company_state_row else ""
    
    customer_row = execute_read_query("SELECT state FROM customers WHERE id=?", (customer_id,))
    customer_state = customer_row[0]['state'] if customer_row else ""
    
    invoice_number = generate_invoice_number()
    
    subtotal = 0.0
    total_tax = 0.0
    discount_amount = 0.0
    grand_total = 0.0
    
    invoice_items_data = []
    stock_reductions = []
    
    for item in items:
        item_id = item['item_id']
        qty = item['quantity']
        rate = item['rate']
        discount_percent = item.get('discount_percent', 0)
        gst_percent = item.get('gst_percent', 0)
        
        # Calculate line item amount
        # Discount is applied on rate
        discounted_rate = rate * (1 - discount_percent / 100)
        line_discount = (rate - discounted_rate) * qty
        discount_amount += line_discount
        
        taxable_val = discounted_rate * qty
        
        # Calculate GST
        gst_res = calculate_gst(taxable_val, gst_percent, company_state, customer_state)
        tax = gst_res['total_tax']
        line_total = gst_res['grand_total']
        
        subtotal += taxable_val
        total_tax += tax
        grand_total += line_total
        
        invoice_items_data.append({
            "item_id": item_id,
            "quantity": qty,
            "rate": rate,
            "discount_percent": discount_percent,
            "gst_percent": gst_percent,
            "amount": line_total
        })
        
        # Prepare stock reduction
        stock_reductions.append((item_id, qty))

    # Apply adjustments to grand_total
    grand_total -= tds_amount
    grand_total += tcs_amount
    grand_total += adjustment
    grand_total += round_off

    # Create invoice record
    inv_query = """
        INSERT INTO invoices (
            invoice_number, customer_id, date, due_date, subtotal, tax_amount, discount_amount, grand_total, notes,
            order_number, terms, salesperson, subject, customer_notes, terms_conditions, round_off, tds_amount, tcs_amount, adjustment, status, attachment_path, custom_fields
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    inv_params = (
        invoice_number, customer_id, date, due_date, subtotal, total_tax, discount_amount, grand_total, notes,
        order_number, terms, salesperson, subject, customer_notes, terms_conditions, round_off, tds_amount, tcs_amount, adjustment, status, attachment_path, custom_fields
    )
    
    # We need to execute invoice creation first to get ID
    # But ideally we want everything in a transaction.
    # Since execute_transaction takes a list of queries, we can't easily get the ID in the middle.
    # So we will do it in steps, but if stock reduction fails, we have an issue.
    # A better approach with execute_transaction is hard here without a proper ORM or advanced DB wrapper.
    # So we will do:
    # 1. Create Invoice
    # 2. Add Items
    # 3. Reduce Stock
    # If step 3 fails, we technically have an invoice created but stock not reduced.
    # For this task, we will proceed sequentially.
    
    invoice_id = execute_write_query(inv_query, inv_params)
    
    item_queries = []
    for item_data in invoice_items_data:
        q = """
            INSERT INTO invoice_items (invoice_id, item_id, quantity, rate, discount_percent, gst_percent, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        p = (invoice_id, item_data['item_id'], item_data['quantity'], item_data['rate'], 
             item_data['discount_percent'], item_data['gst_percent'], item_data['amount'])
        item_queries.append((q, p))
        
    if item_queries:
        execute_transaction(item_queries)
        
    # Reduce stock
    for item_id, qty in stock_reductions:
        reduce_stock_fifo(item_id, qty)
        
    return invoice_id

def update_invoice(invoice_id, data):
    """
    Updates an existing invoice and adjusts stock accordingly.
    """
    # 1. Get existing items to calculate stock difference
    old_items_query = "SELECT item_id, quantity FROM invoice_items WHERE invoice_id = ?"
    old_items = execute_read_query(old_items_query, (invoice_id,))
    old_items_map = {item['item_id']: item['quantity'] for item in old_items}
    
    # 2. Prepare new data
    new_items = data['items']
    new_items_map = {item['item_id']: item['quantity'] for item in new_items}
    
    # 3. Calculate Stock Adjustments
    # Items to reduce (new > old or new item)
    to_reduce = []
    # Items to add back (new < old or removed item)
    to_add = []
    
    # Check new items
    for item in new_items:
        item_id = item['item_id']
        new_qty = item['quantity']
        old_qty = old_items_map.get(item_id, 0)
        
        diff = new_qty - old_qty
        if diff > 0:
            to_reduce.append((item_id, diff))
        elif diff < 0:
            to_add.append((item_id, -diff))
            
    # Check removed items
    for item_id, old_qty in old_items_map.items():
        if item_id not in new_items_map:
            to_add.append((item_id, old_qty))
            
    # 4. Apply Stock Changes
    for item_id, qty in to_reduce:
        reduce_stock_fifo(item_id, qty)
        
    for item_id, qty in to_add:
        # We need purchase price to add back. 
        # Since we don't know the exact batch cost, use current purchase_price from items table
        item_row = execute_read_query("SELECT purchase_price FROM items WHERE id=?", (item_id,))
        rate = item_row[0]['purchase_price'] if item_row else 0
        add_stock(item_id, qty, rate, data['date'])
        
    # 5. Update Invoice Record
    # Calculate totals first (same logic as create_invoice)
    # ... (Reuse logic or refactor. For now, copy-paste logic for safety and speed)
    customer_id = data['customer_id']
    company_state_row = execute_read_query("SELECT value FROM settings WHERE key='company_state'")
    company_state = company_state_row[0]['value'] if company_state_row else ""
    customer_row = execute_read_query("SELECT state FROM customers WHERE id=?", (customer_id,))
    customer_state = customer_row[0]['state'] if customer_row else ""
    
    subtotal = 0.0
    total_tax = 0.0
    discount_amount = 0.0
    grand_total = 0.0
    invoice_items_data = []
    
    for item in new_items:
        item_id = item['item_id']
        qty = item['quantity']
        rate = item['rate']
        discount_percent = item.get('discount_percent', 0)
        gst_percent = item.get('gst_percent', 0)
        
        discounted_rate = rate * (1 - discount_percent / 100)
        line_discount = (rate - discounted_rate) * qty
        discount_amount += line_discount
        taxable_val = discounted_rate * qty
        gst_res = calculate_gst(taxable_val, gst_percent, company_state, customer_state)
        tax = gst_res['total_tax']
        line_total = gst_res['grand_total']
        
        subtotal += taxable_val
        total_tax += tax
        grand_total += line_total
        
        invoice_items_data.append({
            "item_id": item_id,
            "quantity": qty,
            "rate": rate,
            "discount_percent": discount_percent,
            "gst_percent": gst_percent,
            "amount": line_total
        })

    # Apply adjustments to grand_total
    grand_total -= data.get('tds_amount', 0.0)
    grand_total += data.get('tcs_amount', 0.0)
    grand_total += data.get('adjustment', 0.0)
    grand_total += data.get('round_off', 0.0)

    # Update Query
    inv_query = """
        UPDATE invoices SET
            customer_id=?, date=?, due_date=?, subtotal=?, tax_amount=?, discount_amount=?, grand_total=?, notes=?,
            order_number=?, terms=?, salesperson=?, subject=?, customer_notes=?, terms_conditions=?, 
            round_off=?, tds_amount=?, tcs_amount=?, adjustment=?, status=?, attachment_path=?, custom_fields=?
        WHERE id=?
    """
    inv_params = (
        customer_id, data['date'], data.get('due_date'), subtotal, total_tax, discount_amount, grand_total, data.get('notes', ''),
        data.get('order_number', ''), data.get('terms', ''), data.get('salesperson', ''), data.get('subject', ''), 
        data.get('customer_notes', ''), data.get('terms_conditions', ''), data.get('round_off', 0.0), 
        data.get('tds_amount', 0.0), data.get('tcs_amount', 0.0), data.get('adjustment', 0.0), 
        data.get('status', 'Due'), data.get('attachment_path', ''), data.get('custom_fields', '{}'),
        invoice_id
    )
    execute_write_query(inv_query, inv_params)
    
    # 6. Delete old items and insert new
    execute_write_query("DELETE FROM invoice_items WHERE invoice_id=?", (invoice_id,))
    
    item_queries = []
    for item_data in invoice_items_data:
        q = """
            INSERT INTO invoice_items (invoice_id, item_id, quantity, rate, discount_percent, gst_percent, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        p = (invoice_id, item_data['item_id'], item_data['quantity'], item_data['rate'], 
             item_data['discount_percent'], item_data['gst_percent'], item_data['amount'])
        item_queries.append((q, p))
        
    if item_queries:
        execute_transaction(item_queries)
        
    return invoice_id

def generate_bill_number():
    """Generates a new bill number."""
    # Get prefix from settings
    settings = execute_read_query("SELECT value FROM settings WHERE key='bill_prefix'")
    prefix = settings[0]['value'] if settings else "BILL-"
    
    # Find last bill number
    last_bill = execute_read_query("SELECT bill_number FROM bills ORDER BY id DESC LIMIT 1")
    if last_bill:
        last_num_str = last_bill[0]['bill_number'].replace(prefix, "")
        try:
            next_num = int(last_num_str) + 1
        except ValueError:
            next_num = 1
    else:
        next_num = 1
        
    return f"{prefix}{next_num:04d}"

def create_bill(data):
    """
    Creates a new bill (purchase), updates stock, and saves to database.
    
    Args:
        data (dict): Bill data including vendor_id, date, items, etc.
        
    Returns:
        int: The ID of the created bill.
    """
    vendor_id = data['vendor_id']
    date = data['date']
    due_date = data.get('due_date')
    status = data.get('status', 'Draft')
    
    # New Fields
    bill_number = data.get('bill_number') or generate_bill_number()
    order_number = data.get('order_number', '')
    payment_terms = data.get('payment_terms', '')
    reverse_charge = data.get('reverse_charge', 0)
    adjustment = data.get('adjustment', 0.0)
    tds_amount = data.get('tds_amount', 0.0)
    tcs_amount = data.get('tcs_amount', 0.0)
    attachment_path = data.get('attachment_path', '')
    notes = data.get('notes', '')
    discount_amount = data.get('discount_amount', 0.0)
    custom_fields = data.get('custom_fields', '{}') # JSON string
    
    items = data['items']
    
    # bill_number logic handled above
    
    subtotal = 0.0
    total_tax = 0.0
    grand_total = 0.0
    
    bill_items_data = []
    stock_additions = []
    
    for item in items:
        item_id = item['item_id']
        qty = item['quantity']
        rate = item['rate']
        gst_percent = item.get('gst_percent', 0)
        
        # Calculate line item amount
        taxable_val = rate * qty
        tax = taxable_val * (gst_percent / 100)
        line_total = taxable_val + tax
        
        subtotal += taxable_val
        total_tax += tax
        grand_total += line_total
        
        bill_items_data.append({
            "item_id": item_id,
            "quantity": qty,
            "rate": rate,
            "gst_percent": gst_percent,
            "amount": line_total
        })
        
        # Prepare stock addition
        stock_additions.append((item_id, qty, rate))

    # Apply adjustments to grand_total
    grand_total -= discount_amount
    grand_total -= tds_amount
    grand_total += tcs_amount
    grand_total += adjustment

    # Create bill record
    bill_query = """
        INSERT INTO bills (
            bill_number, vendor_id, date, due_date, subtotal, tax_amount, grand_total, status,
            order_number, payment_terms, reverse_charge, adjustment, tds_amount, tcs_amount, attachment_path, notes, discount_amount, custom_fields
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    bill_params = (
        bill_number, vendor_id, date, due_date, subtotal, total_tax, grand_total, status,
        order_number, payment_terms, reverse_charge, adjustment, tds_amount, tcs_amount, attachment_path, notes, discount_amount, custom_fields
    )
    
    bill_id = execute_write_query(bill_query, bill_params)
    
    item_queries = []
    for item_data in bill_items_data:
        q = """
            INSERT INTO bill_items (bill_id, item_id, quantity, rate, gst_percent, amount)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        p = (bill_id, item_data['item_id'], item_data['quantity'], item_data['rate'], 
             item_data['gst_percent'], item_data['amount'])
        item_queries.append((q, p))
        
    if item_queries:
        execute_transaction(item_queries)
        
    # Add stock
    for item_id, qty, rate in stock_additions:
        add_stock(item_id, qty, rate, date, vendor_id)
        
    return bill_id

def update_bill(bill_id, data):
    """
    Updates an existing bill and adjusts stock accordingly.
    """
    # 1. Get existing items to calculate stock difference
    old_items_query = "SELECT item_id, quantity FROM bill_items WHERE bill_id = ?"
    old_items = execute_read_query(old_items_query, (bill_id,))
    old_items_map = {item['item_id']: item['quantity'] for item in old_items}
    
    # 2. Prepare new data
    new_items = data['items']
    new_items_map = {item['item_id']: item['quantity'] for item in new_items}
    
    # 3. Calculate Stock Adjustments
    # Items to add (new > old or new item) - Since it's a bill (purchase), adding more means more stock
    to_add = []
    # Items to reduce (new < old or removed item) - reducing bill qty means reducing stock
    to_reduce = []
    
    # Check new items
    for item in new_items:
        item_id = item['item_id']
        new_qty = item['quantity']
        old_qty = old_items_map.get(item_id, 0)
        
        diff = new_qty - old_qty
        if diff > 0:
            to_add.append((item_id, diff, item['rate']))
        elif diff < 0:
            to_reduce.append((item_id, -diff))
            
    # Check removed items
    for item_id, old_qty in old_items_map.items():
        if item_id not in new_items_map:
            to_reduce.append((item_id, old_qty))
            
    # 4. Apply Stock Changes
    for item_id, qty, rate in to_add:
        add_stock(item_id, qty, rate, data['date'], data['vendor_id'])
        
    for item_id, qty in to_reduce:
        reduce_stock_fifo(item_id, qty)
        
    # 5. Update Bill Record
    vendor_id = data['vendor_id']
    subtotal = 0.0
    total_tax = 0.0
    grand_total = 0.0
    bill_items_data = []
    
    for item in new_items:
        item_id = item['item_id']
        qty = item['quantity']
        rate = item['rate']
        gst_percent = item.get('gst_percent', 0)
        
        taxable_val = rate * qty
        tax = taxable_val * (gst_percent / 100)
        line_total = taxable_val + tax
        
        subtotal += taxable_val
        total_tax += tax
        grand_total += line_total
        
        bill_items_data.append({
            "item_id": item_id,
            "quantity": qty,
            "rate": rate,
            "gst_percent": gst_percent,
            "amount": line_total
        })

    # Apply adjustments to grand_total
    grand_total -= data.get('discount_amount', 0.0)
    grand_total -= data.get('tds_amount', 0.0)
    grand_total += data.get('tcs_amount', 0.0)
    grand_total += data.get('adjustment', 0.0)

    # Update Query
    bill_query = """
        UPDATE bills SET
            vendor_id=?, date=?, due_date=?, subtotal=?, tax_amount=?, grand_total=?, status=?,
            order_number=?, payment_terms=?, reverse_charge=?, adjustment=?, tds_amount=?, tcs_amount=?, 
            attachment_path=?, notes=?, discount_amount=?, custom_fields=?
        WHERE id=?
    """
    bill_params = (
        vendor_id, data['date'], data.get('due_date'), subtotal, total_tax, grand_total, data.get('status', 'Draft'),
        data.get('order_number', ''), data.get('payment_terms', ''), data.get('reverse_charge', 0), 
        data.get('adjustment', 0.0), data.get('tds_amount', 0.0), data.get('tcs_amount', 0.0), 
        data.get('attachment_path', ''), data.get('notes', ''), data.get('discount_amount', 0.0), 
        data.get('custom_fields', '{}'),
        bill_id
    )
    execute_write_query(bill_query, bill_params)
    
    # 6. Delete old items and insert new
    execute_write_query("DELETE FROM bill_items WHERE bill_id=?", (bill_id,))
    
    item_queries = []
    for item_data in bill_items_data:
        q = """
            INSERT INTO bill_items (bill_id, item_id, quantity, rate, gst_percent, amount)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        p = (bill_id, item_data['item_id'], item_data['quantity'], item_data['rate'], 
             item_data['gst_percent'], item_data['amount'])
        item_queries.append((q, p))
        
    if item_queries:
        execute_transaction(item_queries)
        
    return bill_id
