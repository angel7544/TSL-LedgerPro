-- SQL COMMAND:

      SELECT b.*, 
             v.name as vendor_name, v.email as vendor_email, v.phone as vendor_phone, v.address as vendor_address, v.gstin as vendor_gstin, v.state as vendor_state,
             o.name as outlet_name, o.logo_url as outlet_logo_url, o.address as outlet_address, o.gstin as outlet_gstin, o.state as outlet_state, o.phone as outlet_phone, o.email as outlet_email
      FROM bills b 
      JOIN vendors v ON b.vendor_id = v.id 
      LEFT JOIN outlets o ON b.outlet_id = o.id
      WHERE b.id = ?
    
-- PARAMETERS:
["1"]
