-- SQL COMMAND:

      SELECT b.*, v.name as vendor_name, 
             COALESCE((SELECT SUM(amount) FROM payments WHERE bill_id = b.id), 0) as paid_amount,
             (b.grand_total - COALESCE((SELECT SUM(amount) FROM payments WHERE bill_id = b.id), 0)) as balance_due
      FROM bills b 
      JOIN vendors v ON b.vendor_id = v.id 
      ORDER BY b.date DESC, b.id DESC
    
-- PARAMETERS:
[]
