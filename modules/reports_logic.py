from database.db import execute_read_query
import datetime

def get_sales_report(start_date, end_date):
    """
    Returns sales data within a date range.
    """
    query = """
        SELECT i.invoice_number, c.name as customer_name, i.date, i.grand_total, i.status
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.date BETWEEN ? AND ?
        ORDER BY i.date DESC
    """
    return execute_read_query(query, (start_date, end_date))

def get_purchase_report(start_date, end_date):
    """
    Returns purchase data within a date range.
    """
    query = """
        SELECT b.bill_number, v.name as vendor_name, b.date, b.grand_total, b.status
        FROM bills b
        JOIN vendors v ON b.vendor_id = v.id
        WHERE b.date BETWEEN ? AND ?
        ORDER BY b.date DESC
    """
    return execute_read_query(query, (start_date, end_date))

def get_gst_report(start_date, end_date):
    """
    Returns GST collected (Output Tax) and paid (Input Tax).
    """
    # Output Tax (Sales)
    sales_query = """
        SELECT SUM(tax_amount) as total_output_tax
        FROM invoices
        WHERE date BETWEEN ? AND ?
    """
    sales_res = execute_read_query(sales_query, (start_date, end_date))
    sales_tax = sales_res[0]['total_output_tax'] if sales_res and sales_res[0]['total_output_tax'] else 0.0
    
    # Input Tax (Purchases)
    purchase_query = """
        SELECT SUM(tax_amount) as total_input_tax
        FROM bills
        WHERE date BETWEEN ? AND ?
    """
    purchase_res = execute_read_query(purchase_query, (start_date, end_date))
    purchase_tax = purchase_res[0]['total_input_tax'] if purchase_res and purchase_res[0]['total_input_tax'] else 0.0
    
    return {
        "output_tax": sales_tax,
        "input_tax": purchase_tax,
        "net_gst_payable": sales_tax - purchase_tax
    }

def get_outstanding_invoices():
    """
    Returns invoices that are not fully paid.
    """
    # Assuming 'Paid' status means fully paid.
    # In a real system, we'd check payments against invoice total.
    query = """
        SELECT i.invoice_number, c.name as customer_name, i.date, i.due_date, i.grand_total, i.status
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.status != 'Paid'
        ORDER BY i.due_date ASC
    """
    return execute_read_query(query)

def get_stock_valuation():
    """
    Returns stock valuation report.
    """
    query = """
        SELECT
            i.name,
            i.sku,
            i.stock_on_hand,
            i.purchase_price,
            COALESCE(SUM(sb.quantity_remaining * sb.purchase_rate), 0) as batch_value,
            COALESCE(SUM(sb.quantity_remaining), 0) as batch_qty
        FROM items i
        LEFT JOIN stock_batches sb ON i.id = sb.item_id
        GROUP BY i.id
    """
    rows = execute_read_query(query)
    
    results = []
    for row in rows:
        val = row['batch_value']
        # Fallback to simple valuation if no batches
        if row['batch_qty'] == 0 and row['stock_on_hand'] > 0:
            val = row['stock_on_hand'] * row['purchase_price']
            
        results.append({
            'name': row['name'],
            'sku': row['sku'],
            'stock_on_hand': row['stock_on_hand'],
            'purchase_price': row['purchase_price'],
            'total_value': val
        })
    return results

def get_monthly_sales_data(year):
    """
    Returns monthly sales totals for a given year.
    """
    query = """
        SELECT strftime('%m', date) as month, SUM(grand_total) as total
        FROM invoices
        WHERE strftime('%Y', date) = ?
        GROUP BY month
        ORDER BY month
    """
    rows = execute_read_query(query, (str(year),))
    
    # Initialize all months with 0
    monthly_data = {m: 0.0 for m in range(1, 13)}
    
    for row in rows:
        month_idx = int(row['month'])
        monthly_data[month_idx] = row['total']
        
    return [monthly_data[m] for m in range(1, 13)]

def get_monthly_purchase_data(year):
    """
    Returns monthly purchase totals for a given year.
    """
    query = """
        SELECT strftime('%m', date) as month, SUM(grand_total) as total
        FROM bills
        WHERE strftime('%Y', date) = ?
        GROUP BY month
        ORDER BY month
    """
    rows = execute_read_query(query, (str(year),))
    
    # Initialize all months with 0
    monthly_data = {m: 0.0 for m in range(1, 13)}
    
    for row in rows:
        month_idx = int(row['month'])
        monthly_data[month_idx] = row['total']
        
    return [monthly_data[m] for m in range(1, 13)]

def get_ar_aging_report():
    """
    Returns AR Aging report data (Customer Invoices).
    Buckets: Current, 1-15, 16-30, 31-60, 60+ days overdue.
    """
    # SQLite julianday returns fractional days, so we subtract due_date from now
    query = """
        SELECT 
            i.invoice_number, 
            c.name as customer_name, 
            i.date, 
            i.due_date, 
            i.grand_total, 
            i.status,
            (julianday('now') - julianday(i.due_date)) as days_overdue,
            (i.grand_total - COALESCE((SELECT SUM(amount) FROM payments WHERE invoice_id = i.id), 0)) as balance_due
        FROM invoices i
        JOIN customers c ON i.customer_id = c.id
        WHERE i.status != 'Paid'
        ORDER BY days_overdue DESC
    """
    rows = execute_read_query(query)
    
    buckets = {
        "Current": [],
        "1-15 Days": [],
        "16-30 Days": [],
        "31-60 Days": [],
        "60+ Days": []
    }
    
    for row in rows:
        # If fully paid but status mismatch, skip
        if row['balance_due'] <= 0.01: # Tolerance for float
             continue
             
        # If no due date, treat as current
        if not row['due_date']:
            days = 0
        else:
            days = row['days_overdue']
            
        entry = {
            "invoice_number": row['invoice_number'],
            "customer_name": row['customer_name'],
            "date": row['date'],
            "due_date": row['due_date'],
            "amount": row['balance_due'], # Use balance due
            "days_overdue": int(days) if days > 0 else 0,
            "status": row['status']
        }
        
        if days <= 0:
            buckets["Current"].append(entry)
        elif days <= 15:
            buckets["1-15 Days"].append(entry)
        elif days <= 30:
            buckets["16-30 Days"].append(entry)
        elif days <= 60:
            buckets["31-60 Days"].append(entry)
        else:
            buckets["60+ Days"].append(entry)
            
    return buckets

def get_cash_flow_data(fiscal_year_start):
    """
    Returns monthly cash flow data for a fiscal year (April to March).
    
    Args:
        fiscal_year_start (int): The starting year of the fiscal year (e.g., 2025 for FY 2025-26).
        
    Returns:
        dict: {
            'months': ['Apr', 'May', ...],
            'incoming': [val1, val2, ...],
            'outgoing': [val1, val2, ...],
            'net_cash': [val1, val2, ...],
            'opening_balance': float,
            'closing_balance': float,
            'total_incoming': float,
            'total_outgoing': float
        }
    """
    start_date = f"{fiscal_year_start}-04-01"
    end_date = f"{fiscal_year_start + 1}-03-31"
    
    # 1. Calculate Opening Balance (Cash on Hand before Start Date)
    # Incoming (Invoices paid) - Outgoing (Bills paid)
    opening_query = """
        SELECT 
            SUM(CASE WHEN invoice_id IS NOT NULL THEN amount ELSE 0 END) as total_in,
            SUM(CASE WHEN bill_id IS NOT NULL THEN amount ELSE 0 END) as total_out
        FROM payments
        WHERE date < ?
    """
    opening_res = execute_read_query(opening_query, (start_date,))
    opening_in = opening_res[0]['total_in'] if opening_res and opening_res[0]['total_in'] else 0.0
    opening_out = opening_res[0]['total_out'] if opening_res and opening_res[0]['total_out'] else 0.0
    opening_balance = opening_in - opening_out
    
    # 2. Get Monthly Data for the Fiscal Year
    monthly_data = []
    months = []
    incoming_data = []
    outgoing_data = []
    net_cash_data = []
    
    current_balance = opening_balance
    total_incoming = 0.0
    total_outgoing = 0.0
    
    # Generate months list (Apr to Mar)
    month_dates = []
    for i in range(12):
        if i < 9: # Apr (4) to Dec (12)
            month_num = i + 4
            year = fiscal_year_start
        else: # Jan (1) to Mar (3)
            month_num = i - 8
            year = fiscal_year_start + 1
            
        month_str = f"{year}-{month_num:02d}"
        month_name = datetime.date(year, month_num, 1).strftime("%b\n%Y")
        months.append(month_name)
        month_dates.append(month_str)

    # Fetch data grouped by month
    # We'll fetch all payments in the range and process in python for simplicity
    payments_query = """
        SELECT strftime('%Y-%m', date) as month, 
               invoice_id, 
               bill_id, 
               SUM(amount) as total
        FROM payments
        WHERE date BETWEEN ? AND ?
        GROUP BY month, invoice_id IS NOT NULL
    """
    rows = execute_read_query(payments_query, (start_date, end_date))
    
    # Organize data
    # Structure: {'YYYY-MM': {'in': 0, 'out': 0}}
    data_map = {m: {'in': 0.0, 'out': 0.0} for m in month_dates}
    
    for row in rows:
        m = row['month']
        if m in data_map:
            if row['invoice_id']: # Incoming
                data_map[m]['in'] += row['total']
            elif row['bill_id']: # Outgoing
                data_map[m]['out'] += row['total']
    
    # Build result lists
    running_balance = opening_balance
    cash_flow_trend = [] # To store running balance for chart
    
    for m in month_dates:
        inc = data_map[m]['in']
        out = data_map[m]['out']
        
        total_incoming += inc
        total_outgoing += out
        
        incoming_data.append(inc)
        outgoing_data.append(out)
        
        running_balance += (inc - out)
        cash_flow_trend.append(running_balance)
        
    return {
        'months': months,
        'incoming': incoming_data,
        'outgoing': outgoing_data,
        'balance_trend': cash_flow_trend,
        'opening_balance': opening_balance,
        'closing_balance': running_balance,
        'total_incoming': total_incoming,
        'total_outgoing': total_outgoing,
        'fiscal_year': f"{fiscal_year_start}-{fiscal_year_start+1}"
    }

def get_ap_aging_report():
    """
    Returns AP Aging report data (Vendor Bills).
    Buckets: Current, 1-15, 16-30, 31-60, 60+ days overdue.
    """
    query = """
        SELECT 
            b.bill_number, 
            v.name as vendor_name, 
            b.date, 
            b.due_date, 
            b.grand_total, 
            b.status,
            (julianday('now') - julianday(b.due_date)) as days_overdue,
            (b.grand_total - COALESCE((SELECT SUM(amount) FROM payments WHERE bill_id = b.id), 0)) as balance_due
        FROM bills b
        JOIN vendors v ON b.vendor_id = v.id
        WHERE b.status != 'Paid'
        ORDER BY days_overdue DESC
    """
    rows = execute_read_query(query)
    
    buckets = {
        "Current": [],
        "1-15 Days": [],
        "16-30 Days": [],
        "31-60 Days": [],
        "60+ Days": []
    }
    
    for row in rows:
        if row['balance_due'] <= 0.01:
             continue

        if not row['due_date']:
            days = 0
        else:
            days = row['days_overdue']
            
        entry = {
            "bill_number": row['bill_number'],
            "vendor_name": row['vendor_name'],
            "date": row['date'],
            "due_date": row['due_date'],
            "amount": row['balance_due'], # Use balance due
            "days_overdue": int(days) if days > 0 else 0,
            "status": row['status']
        }
        
        if days <= 0:
            buckets["Current"].append(entry)
        elif days <= 15:
            buckets["1-15 Days"].append(entry)
        elif days <= 30:
            buckets["16-30 Days"].append(entry)
        elif days <= 60:
            buckets["31-60 Days"].append(entry)
        else:
            buckets["60+ Days"].append(entry)
            
    return buckets

