-- SQL COMMAND:

      SELECT b.*, v.name as vendor_name 
      FROM bills b 
      JOIN vendors v ON b.vendor_id = v.id 
      ORDER BY b.date DESC, b.id DESC
    
-- PARAMETERS:
[]
