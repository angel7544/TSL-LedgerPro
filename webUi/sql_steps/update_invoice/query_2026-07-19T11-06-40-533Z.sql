-- SQL COMMAND:

      UPDATE invoices SET
        customer_id = ?, date = ?, due_date = ?, subtotal = ?, tax_amount = ?, grand_total = ?, status = ?, notes = ?, order_number = ?, terms = ?, salesperson = ?, subject = ?, round_off = ?, outlet_id = ?, customer_notes = ?, terms_conditions = ?, tds_amount = ?, tcs_amount = ?, adjustment = ?
      WHERE id = ?
    
-- PARAMETERS:
[1,"2026-07-01","2026-07-17",12348.288,2222.69184,14571.68984,"Due","1"]
