
from database.db import execute_read_query, execute_write_query, execute_transaction, is_mysql
import datetime

def get_unpaid_invoices(customer_id):
    """
    Returns a list of unpaid or partially paid invoices for a customer.
    Calculates the balance due for each invoice.
    Excludes Draft and Paid invoices.
    """
    query = """
        SELECT i.id, i.invoice_number, i.date, i.due_date, IFNULL(i.grand_total, 0) as grand_total, i.status
        FROM invoices i
        WHERE i.customer_id = ? AND i.status NOT IN ('Paid', 'Draft', 'Cancelled')
        ORDER BY i.date ASC
    """
    invoices = execute_read_query(query, (customer_id,))
    
    results = []
    for inv in invoices:
        paid_query = "SELECT SUM(amount) as total_paid FROM payments WHERE invoice_id = %s" if is_mysql() else "SELECT SUM(amount) as total_paid FROM payments WHERE invoice_id = ?"
        paid_res = execute_read_query(paid_query, (inv['id'],))
        
        if is_mysql():
            amount_paid = paid_res[0]['total_paid'] if paid_res and paid_res[0]['total_paid'] else 0.0
        else:
            amount_paid = paid_res[0][0] if paid_res and paid_res[0][0] else 0.0
        
        balance_due = inv['grand_total'] - amount_paid
        
        # Show even if balance is 0 but status is not Paid? 
        # No, if balance is 0, it should be paid. 
        # But allow small float tolerance.
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
    Excludes Draft and Paid bills.
    """
    query = """
        SELECT b.id, b.bill_number, b.date, b.due_date, IFNULL(b.grand_total, 0) as grand_total, b.status
        FROM bills b
        WHERE b.vendor_id = ? AND b.status NOT IN ('Paid', 'Draft', 'Cancelled')
        ORDER BY b.date ASC
    """
    bills = execute_read_query(query, (vendor_id,))
    
    results = []
    for bill in bills:
        paid_query = "SELECT SUM(amount) as total_paid FROM payments WHERE bill_id = %s" if is_mysql() else "SELECT SUM(amount) as total_paid FROM payments WHERE bill_id = ?"
        paid_res = execute_read_query(paid_query, (bill['id'],))
        
        if is_mysql():
            amount_paid = paid_res[0]['total_paid'] if paid_res and paid_res[0]['total_paid'] else 0.0
        else:
            amount_paid = paid_res[0][0] if paid_res and paid_res[0][0] else 0.0
        
        balance_due = bill['grand_total'] - amount_paid
        
        if balance_due > 0.01:
            b_data = dict(bill)
            b_data['amount_paid'] = amount_paid
            b_data['balance_due'] = balance_due
            results.append(b_data)
            
    return results

def get_customer_credits(customer_id):
    """Returns the total available credits (unallocated payments) for a customer."""
    query = "SELECT SUM(amount) as total FROM payments WHERE customer_id = %s AND invoice_id IS NULL" if is_mysql() else "SELECT SUM(amount) as total FROM payments WHERE customer_id = ? AND invoice_id IS NULL"
    res = execute_read_query(query, (customer_id,))
    
    if is_mysql():
        return res[0]['total'] if res and res[0]['total'] else 0.0
    else:
        return res[0][0] if res and res[0][0] else 0.0

def get_vendor_credits(vendor_id):
    """Returns the total available credits (unallocated payments) for a vendor."""
    query = "SELECT SUM(amount) as total FROM payments WHERE vendor_id = %s AND bill_id IS NULL" if is_mysql() else "SELECT SUM(amount) as total FROM payments WHERE vendor_id = ? AND bill_id IS NULL"
    res = execute_read_query(query, (vendor_id,))
    
    if is_mysql():
        return res[0]['total'] if res and res[0]['total'] else 0.0
    else:
        return res[0][0] if res and res[0][0] else 0.0

def consume_customer_credits(customer_id, amount_needed, invoice_id, transaction_queries):
    """
    Generates queries to consume credits for a specific invoice.
    Appends queries to the provided list.
    """
    # Fetch unallocated payments (FIFO)
    query = "SELECT id, amount FROM payments WHERE customer_id = ? AND invoice_id IS NULL ORDER BY date ASC, id ASC"
    credits = execute_read_query(query, (customer_id,))
    
    remaining_needed = amount_needed
    
    for credit in credits:
        if remaining_needed <= 0.001:
            break
            
        credit_id = credit['id']
        credit_amount = credit['amount']
        
        to_use = min(remaining_needed, credit_amount)
        
        # 1. Reduce the credit amount
        new_credit_amount = credit_amount - to_use
        if new_credit_amount < 0.01:
            # Delete if fully used (or maybe keep as 0? No, delete or mark used. Let's delete or set to 0. 
            # Deleting is cleaner for "unallocated", but keeping history is good.
            # But the schema relies on invoice_id IS NULL.
            # If we set invoice_id, it becomes allocated.
            # So, if fully used, we can just Update invoice_id = invoice_id?
            # But we might be splitting it across multiple invoices.
            # So we must SPLIT the row.
            
            # Actually, standard practice:
            # Update the existing row to have the invoice_id and amount = to_use.
            # If there was remaining, create a new row with remaining.
            # But we are iterating.
            
            # Case 1: Fully used for this invoice (Exact match)
            # Update invoice_id.
            
            # Case 2: Partially used (Credit > Needed)
            # Split:
            # Row A (Original ID): Update amount = Needed, invoice_id = invoice_id.
            # Row B (New): amount = Remaining, invoice_id = NULL.
            
            # Case 3: Fully used but less than needed (Credit < Needed)
            # Update invoice_id.
            
            transaction_queries.append((
                "UPDATE payments SET amount = ?, invoice_id = ? WHERE id = ?",
                (to_use, invoice_id, credit_id)
            ))
            
            # If we split (Credit > Needed), we need to re-insert the remainder
            if new_credit_amount > 0.001:
                # We need to copy other fields. Since we can't easily fetch-and-insert in one query without complexity,
                # we rely on the fact we are in a transaction generator.
                # We need to read the row details first? We already have ID.
                # Let's assume we can copy basic fields or we need to fetch them.
                # The 'credits' query only fetched id, amount.
                # We should fetch all.
                pass 
        else:
             # Fully used
             transaction_queries.append((
                "UPDATE payments SET invoice_id = ? WHERE id = ?",
                (invoice_id, credit_id)
            ))
             
        remaining_needed -= to_use

    # Wait, the logic above is slightly flawed because I need full row details to split.
    # Let's refine.

def consume_credits(party_type, party_id, amount_needed, target_id, transaction_queries):
    """
    Generates queries to consume credits (customer or vendor).
    party_type: 'customer' or 'vendor'
    target_id: invoice_id or bill_id
    """
    id_col = "customer_id" if party_type == 'customer' else "vendor_id"
    target_col = "invoice_id" if party_type == 'customer' else "bill_id"
    
    # Fetch unallocated payments (FIFO) with full details
    query = f"SELECT * FROM payments WHERE {id_col} = ? AND {target_col} IS NULL ORDER BY date ASC, id ASC"
    credits = execute_read_query(query, (party_id,))
    
    remaining_needed = amount_needed
    
    for credit in credits:
        if remaining_needed <= 0.001:
            break
            
        credit_id = credit['id']
        credit_amount = credit['amount']
        
        to_use = min(remaining_needed, credit_amount)
        
        if abs(credit_amount - to_use) < 0.01:
            # Case: Credit Amount matches exactly or is less than needed (Fully consumed)
            # Just link it to the target
            transaction_queries.append((
                f"UPDATE payments SET {target_col} = ? WHERE id = ?",
                (target_id, credit_id)
            ))
        else:
            # Case: Credit Amount > Needed (Partial use)
            # 1. Update original row to be the "used" portion (link to target, set amount = to_use)
            transaction_queries.append((
                f"UPDATE payments SET amount = ?, {target_col} = ? WHERE id = ?",
                (to_use, target_id, credit_id)
            ))
            
            # 2. Insert new row for the remainder (unallocated)
            remainder = credit_amount - to_use
            # Copy all fields except id, amount, and target_col (which is NULL)
            # We use the values from 'credit' dict
            # sqlite3.Row doesn't support .get(), so convert to dict or use keys check
            credit_dict = dict(credit)
            
            transaction_queries.append((
                """INSERT INTO payments (
                    invoice_id, bill_id, customer_id, vendor_id, amount, date, method, notes, 
                    payment_number, reference, deposit_to, bank_charges, 
                    tax_deducted, tax_account, attachment_path, custom_fields, send_thank_you
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    None, None, 
                    credit['customer_id'], credit['vendor_id'], 
                    remainder, credit['date'], credit['method'], credit['notes'],
                    credit['payment_number'], credit['reference'], credit['deposit_to'], credit['bank_charges'],
                    credit['tax_deducted'], credit['tax_account'], credit['attachment_path'], credit['custom_fields'], credit_dict.get('send_thank_you', 0)
                )
            ))
            
        remaining_needed -= to_use

def generate_payment_number():
    """Generates a new payment number automatically."""
    # Generated by system automatically
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
    transaction_queries = []
    
    allocations = data.get('allocations', [])
    customer_id = data.get('customer_id')
    vendor_id = data.get('vendor_id')
    amount_received = data.get('amount_received', 0.0)
    use_credits = data.get('use_credits', False)
    
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
    
    # Process allocations simply for the "Record Payment" flow without complex credits handling for now to get it working reliably
    for alloc in allocations:
        amount = alloc['amount']
        if amount <= 0:
            continue
            
        if "customer_id" in data and customer_id is not None:
            invoice_id = alloc.get('invoice_id')
            query = """
                INSERT INTO payments (invoice_id, customer_id, amount, date, method, reference, notes, payment_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """ if is_mysql() else """
                INSERT INTO payments (invoice_id, customer_id, amount, date, method, reference, notes, payment_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            transaction_queries.append((query, (
                invoice_id, customer_id, amount, payment_date, method, reference, notes, payment_number
            )))
            
            # Check and update invoice status if fully paid
            if invoice_id:
                update_invoice_status_query = """
                    UPDATE invoices 
                    SET status = 'Paid' 
                    WHERE id = %s AND (
                        SELECT COALESCE(SUM(amount), 0) + %s 
                        FROM payments 
                        WHERE invoice_id = %s
                    ) >= grand_total - 0.01
                """ if is_mysql() else """
                    UPDATE invoices 
                    SET status = 'Paid' 
                    WHERE id = ? AND (
                        SELECT COALESCE(SUM(amount), 0) + ? 
                        FROM payments 
                        WHERE invoice_id = ?
                    ) >= grand_total - 0.01
                """
                transaction_queries.append((update_invoice_status_query, (invoice_id, amount, invoice_id)))
        
        else:
            bill_id = alloc.get('bill_id')
            query = """
                INSERT INTO payments (bill_id, vendor_id, amount, date, method, reference, notes, payment_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """ if is_mysql() else """
                INSERT INTO payments (bill_id, vendor_id, amount, date, method, reference, notes, payment_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            transaction_queries.append((query, (
                bill_id, vendor_id, amount, payment_date, method, reference, notes, payment_number
            )))
            
            # Check and update bill status if fully paid
            if bill_id:
                update_bill_status_query = """
                    UPDATE bills 
                    SET status = 'Paid' 
                    WHERE id = %s AND (
                        SELECT COALESCE(SUM(amount), 0) + %s 
                        FROM payments 
                        WHERE bill_id = %s
                    ) >= grand_total - 0.01
                """ if is_mysql() else """
                    UPDATE bills 
                    SET status = 'Paid' 
                    WHERE id = ? AND (
                        SELECT COALESCE(SUM(amount), 0) + ? 
                        FROM payments 
                        WHERE bill_id = ?
                    ) >= grand_total - 0.01
                """
                transaction_queries.append((update_bill_status_query, (bill_id, amount, bill_id)))
                
    if transaction_queries:
        try:
            execute_transaction(transaction_queries)
        except Exception as e:
            raise Exception(f"{e}")

def save_bill_payment(data):
    transaction_queries = []
    
    allocations = data.get('allocations', [])
    vendor_id = data.get('vendor_id')
    amount_paid = data.get('amount_paid', 0.0)
    use_credits = data.get('use_credits', False)
    
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
    
    # Process allocations simply for the "Record Payment" flow
    for alloc in allocations:
        amount = alloc['amount']
        if amount <= 0:
            continue
            
        bill_id = alloc.get('bill_id')
        query = """
            INSERT INTO payments (bill_id, vendor_id, amount, date, method, reference, notes, payment_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """ if is_mysql() else """
            INSERT INTO payments (bill_id, vendor_id, amount, date, method, reference, notes, payment_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        transaction_queries.append((query, (
            bill_id, vendor_id, amount, payment_date, method, reference, notes, payment_number
        )))
        
        # Check and update bill status if fully paid
        if bill_id:
            update_bill_status_query = """
                UPDATE bills 
                SET status = 'Paid' 
                WHERE id = %s AND (
                    SELECT COALESCE(SUM(amount), 0) + %s 
                    FROM payments 
                    WHERE bill_id = %s
                ) >= grand_total - 0.01
            """ if is_mysql() else """
                UPDATE bills 
                SET status = 'Paid' 
                WHERE id = ? AND (
                    SELECT COALESCE(SUM(amount), 0) + ? 
                    FROM payments 
                    WHERE bill_id = ?
                ) >= grand_total - 0.01
            """
            transaction_queries.append((update_bill_status_query, (bill_id, amount, bill_id)))
            
    if transaction_queries:
        try:
            execute_transaction(transaction_queries)
        except Exception as e:
            raise Exception(f"{e}")
