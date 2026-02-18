
from database.db import execute_read_query, execute_write_query, execute_transaction
import datetime

def get_unpaid_invoices(customer_id):
    """
    Returns a list of unpaid or partially paid invoices for a customer.
    Calculates the balance due for each invoice.
    """
    query = """
        SELECT i.id, i.invoice_number, i.date, i.due_date, i.grand_total, i.status
        FROM invoices i
        WHERE i.customer_id = ? AND i.status != 'Paid'
        ORDER BY i.date ASC
    """
    invoices = execute_read_query(query, (customer_id,))
    
    results = []
    for inv in invoices:
        paid_query = "SELECT SUM(amount) FROM payments WHERE invoice_id = ?"
        paid_res = execute_read_query(paid_query, (inv['id'],))
        amount_paid = paid_res[0][0] if paid_res and paid_res[0][0] else 0.0
        
        balance_due = inv['grand_total'] - amount_paid
        
        if balance_due > 0.01:
            inv_data = dict(inv)
            inv_data['amount_paid'] = amount_paid
            inv_data['balance_due'] = balance_due
            results.append(inv_data)
            
    return results

def get_unpaid_bills(vendor_id):
    """
    Returns a list of unpaid or partially paid bills for a vendor.
    Calculates the balance due for each bill.
    """
    query = """
        SELECT b.id, b.bill_number, b.date, b.due_date, b.grand_total, b.status
        FROM bills b
        WHERE b.vendor_id = ? AND b.status != 'Paid'
        ORDER BY b.date ASC
    """
    bills = execute_read_query(query, (vendor_id,))
    
    results = []
    for bill in bills:
        paid_query = "SELECT SUM(amount) FROM payments WHERE bill_id = ?"
        paid_res = execute_read_query(paid_query, (bill['id'],))
        amount_paid = paid_res[0][0] if paid_res and paid_res[0][0] else 0.0
        
        balance_due = bill['grand_total'] - amount_paid
        
        if balance_due > 0.01:
            b_data = dict(bill)
            b_data['amount_paid'] = amount_paid
            b_data['balance_due'] = balance_due
            results.append(b_data)
            
    return results

def generate_payment_number():
    """Generates a new payment number."""
    settings = execute_read_query("SELECT value FROM settings WHERE key='payment_prefix'")
    prefix = settings[0]['value'] if settings else "PAY-"
    
    last_pay = execute_read_query("SELECT payment_number FROM payments ORDER BY id DESC LIMIT 1")
    if last_pay and last_pay[0]['payment_number']:
        last_num_str = last_pay[0]['payment_number'].replace(prefix, "")
        try:
            next_num = int(last_num_str) + 1
        except ValueError:
            next_num = 1
    else:
        next_num = 1
        
    return f"{prefix}{next_num:04d}"

def save_payment(data):
    """
    Saves a payment against invoices and updates invoice statuses.
    Handles unallocated amounts as credits (invoice_id=NULL).
    """
    allocations = data.get('allocations', [])
    customer_id = data.get('customer_id')
    total_received = data.get('amount_received', 0.0)
    
    payment_date = data.get('date', datetime.date.today().strftime("%Y-%m-%d"))
    method = data.get('method', 'Cash')
    reference = data.get('reference', '')
    notes = data.get('notes', '')
    
    payment_number = data.get('payment_number') or generate_payment_number()
    deposit_to = data.get('deposit_to', '')
    bank_charges = data.get('bank_charges', 0.0)
    tax_deducted = data.get('tax_deducted', 0.0)
    tax_account = data.get('tax_account', '')
    attachment_path = data.get('attachment_path', '')
    send_thank_you = 1 if data.get('send_thank_you') else 0
    custom_fields = data.get('custom_fields', '{}')
    
    transaction_queries = []
    
    total_allocated = 0.0
    
    # Process allocations
    for i, alloc in enumerate(allocations):
        invoice_id = alloc['invoice_id']
        amount = alloc['amount']
        
        if amount <= 0:
            continue
            
        total_allocated += amount
            
        current_bank_charges = bank_charges if i == 0 else 0.0
        current_tax_deducted = tax_deducted if i == 0 else 0.0
        current_tax_account = tax_account if i == 0 else ''
            
        transaction_queries.append((
            """INSERT INTO payments (
                invoice_id, customer_id, amount, date, method, notes, 
                payment_number, reference, deposit_to, bank_charges, 
                tax_deducted, tax_account, attachment_path, custom_fields, send_thank_you
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                invoice_id, customer_id, amount, payment_date, method, notes,
                payment_number, reference, deposit_to, current_bank_charges,
                current_tax_deducted, current_tax_account, attachment_path, custom_fields, send_thank_you
            )
        ))
        
        inv_res = execute_read_query("SELECT grand_total FROM invoices WHERE id = ?", (invoice_id,))
        if not inv_res:
            continue
        grand_total = inv_res[0]['grand_total']
        
        paid_res = execute_read_query("SELECT SUM(amount) FROM payments WHERE invoice_id = ?", (invoice_id,))
        previously_paid = paid_res[0][0] if paid_res and paid_res[0][0] else 0.0
        
        new_total_paid = previously_paid + amount
        
        if new_total_paid >= grand_total - 0.01:
            transaction_queries.append((
                "UPDATE invoices SET status = 'Paid' WHERE id = ?",
                (invoice_id,)
            ))
            
    # Handle Unallocated / Excess Amount (Credit)
    excess_amount = total_received - total_allocated
    if excess_amount > 0.01:
        # Only apply bank charges/tax if not applied in allocations
        apply_charges = (len(allocations) == 0)
        current_bank_charges = bank_charges if apply_charges else 0.0
        current_tax_deducted = tax_deducted if apply_charges else 0.0
        current_tax_account = tax_account if apply_charges else ''
        
        transaction_queries.append((
            """INSERT INTO payments (
                invoice_id, customer_id, amount, date, method, notes, 
                payment_number, reference, deposit_to, bank_charges, 
                tax_deducted, tax_account, attachment_path, custom_fields, send_thank_you
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                None, customer_id, excess_amount, payment_date, method, notes,
                payment_number, reference, deposit_to, current_bank_charges,
                current_tax_deducted, current_tax_account, attachment_path, custom_fields, send_thank_you
            )
        ))
            
    if transaction_queries:
        execute_transaction(transaction_queries)

def save_bill_payment(data):
    """
    Saves a payment against bills and updates bill statuses.
    """
    allocations = data.get('allocations', [])
    # if not allocations: return # Allow credits now? Wait, user asked for customer credits. Vendor credits implied?
    # Let's support vendor credits too for consistency.
    vendor_id = data.get('vendor_id')
    total_paid = data.get('amount_paid', 0.0) # Using 'amount_paid' key for bills?
    # Actually ui/payments.py RecordPaymentDialog handles customers. 
    # ui/bills.py might handle bill payments? Or does RecordPaymentDialog handle both?
    # RecordPaymentDialog seems customer focused.
    # Let's stick to customer credits for now as per request.
    
    if not allocations and not vendor_id:
        return
        
    payment_date = data.get('date', datetime.date.today().strftime("%Y-%m-%d"))
    method = data.get('method', 'Cash')
    reference = data.get('reference', '')
    notes = data.get('notes', '')
    
    payment_number = data.get('payment_number') or generate_payment_number()
    deposit_to = data.get('deposit_to', '')
    bank_charges = data.get('bank_charges', 0.0)
    tax_deducted = data.get('tax_deducted', 0.0)
    tax_account = data.get('tax_account', '')
    attachment_path = data.get('attachment_path', '')
    custom_fields = data.get('custom_fields', '{}')
    
    transaction_queries = []
    
    for i, alloc in enumerate(allocations):
        bill_id = alloc['bill_id']
        amount = alloc['amount']
        
        if amount <= 0:
            continue
            
        current_bank_charges = bank_charges if i == 0 else 0.0
        current_tax_deducted = tax_deducted if i == 0 else 0.0
        current_tax_account = tax_account if i == 0 else ''
            
        transaction_queries.append((
            """INSERT INTO payments (
                bill_id, vendor_id, amount, date, method, notes, 
                payment_number, reference, deposit_to, bank_charges, 
                tax_deducted, tax_account, attachment_path, custom_fields
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                bill_id, vendor_id, amount, payment_date, method, notes,
                payment_number, reference, deposit_to, current_bank_charges,
                current_tax_deducted, current_tax_account, attachment_path, custom_fields
            )
        ))
        
        bill_res = execute_read_query("SELECT grand_total FROM bills WHERE id = ?", (bill_id,))
        if not bill_res:
            continue
        grand_total = bill_res[0]['grand_total']
        
        paid_res = execute_read_query("SELECT SUM(amount) FROM payments WHERE bill_id = ?", (bill_id,))
        previously_paid = paid_res[0][0] if paid_res and paid_res[0][0] else 0.0
        
        new_total_paid = previously_paid + amount
        
        if new_total_paid >= grand_total - 0.01:
            transaction_queries.append((
                "UPDATE bills SET status = 'Paid' WHERE id = ?",
                (bill_id,)
            ))
            
    if transaction_queries:
        execute_transaction(transaction_queries)
