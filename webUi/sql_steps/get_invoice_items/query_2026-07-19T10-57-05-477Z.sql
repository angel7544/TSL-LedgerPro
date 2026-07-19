-- SQL COMMAND:

      SELECT ii.*, it.name as item_name, it.sku as item_sku, it.hsn_sac as item_hsn
      FROM invoice_items ii 
      JOIN items it ON ii.item_id = it.id 
      WHERE ii.invoice_id = ?
    
-- PARAMETERS:
["1"]
