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
