-- SQL COMMAND:

      SELECT i.id, i.invoice_number, i.date, i.due_date, i.grand_total, i.status,
             (i.grand_total - COALESCE(SUM(p.amount), 0)) as balance_due
      FROM invoices i
      LEFT JOIN payments p ON i.id = p.invoice_id
      WHERE i.customer_id = ? AND i.status != 'Draft'
      GROUP BY i.id, i.invoice_number, i.date, i.due_date, i.grand_total, i.status
      HAVING balance_due > 0.01
      ORDER BY i.date ASC, i.id ASC
    
-- PARAMETERS:
["1"]
