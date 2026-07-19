-- SQL COMMAND:

      SELECT bi.*, i.name as item_name, i.sku as item_sku, i.hsn_sac as item_hsn
      FROM bill_items bi 
      JOIN items i ON bi.item_id = i.id 
      WHERE bi.bill_id = ?
    
-- PARAMETERS:
["1"]
