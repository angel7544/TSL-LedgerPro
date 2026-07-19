-- SQL COMMAND:

      SELECT p.*, c.name as customer_name, v.name as vendor_name, i.invoice_number, b.bill_number
      FROM payments p
      LEFT JOIN customers c ON p.customer_id = c.id
      LEFT JOIN vendors v ON p.vendor_id = v.id
      LEFT JOIN invoices i ON p.invoice_id = i.id
      LEFT JOIN bills b ON p.bill_id = b.id
      ORDER BY p.date DESC, p.id DESC
    
-- PARAMETERS:
[]
