-- SQL COMMAND:

      SELECT i.*, c.name as customer_name, c.state as customer_state 
      FROM invoices i 
      JOIN customers c ON i.customer_id = c.id 
      ORDER BY i.date DESC, i.id DESC
    
-- PARAMETERS:
[]
