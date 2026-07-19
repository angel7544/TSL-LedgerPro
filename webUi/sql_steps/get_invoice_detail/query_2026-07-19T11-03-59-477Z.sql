-- SQL COMMAND:

      SELECT i.*, 
             c.name as customer_name, c.email as customer_email, c.phone as customer_phone, c.address as customer_address, c.gstin as customer_gstin, c.state as customer_state,
             o.name as outlet_name, o.logo_url as outlet_logo_url, o.address as outlet_address, o.gstin as outlet_gstin, o.state as outlet_state, o.phone as outlet_phone, o.email as outlet_email, o.upi_id as outlet_upi_id
      FROM invoices i 
      JOIN customers c ON i.customer_id = c.id 
      LEFT JOIN outlets o ON i.outlet_id = o.id
      WHERE i.id = ?
    
-- PARAMETERS:
["1"]
