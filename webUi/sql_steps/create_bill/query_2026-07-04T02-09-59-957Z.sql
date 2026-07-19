-- SQL COMMAND:

      INSERT INTO bills (bill_number, vendor_id, date, due_date, subtotal, tax_amount, grand_total, status, notes, order_number, payment_terms, outlet_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, 'Unpaid', ?, ?, ?, ?)
    
-- PARAMETERS:
["BIll-1212",1,"2026-07-08","2026-07-09",1403.13,252.5634,1655.6934,1]
