-- SQL COMMAND:

      SELECT COALESCE(SUM(amount), 0) as total_credits
      FROM payments
      WHERE customer_id = ? AND invoice_id IS NULL
    
-- PARAMETERS:
["1"]
