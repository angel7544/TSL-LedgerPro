const mysql = require('mysql2/promise');
async function run() {
  const c = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'admin@angel',
    database: 'ledgerpro'
  });
  try {
    const id = 1;
    const sqlBill = `
      SELECT b.*, 
             v.name as vendor_name, v.email as vendor_email, v.phone as vendor_phone, v.address as vendor_address, v.gstin as vendor_gstin, v.state as vendor_state,
             o.name as outlet_name, o.logo_url as outlet_logo_url, o.address as outlet_address, o.gstin as outlet_gstin, o.state as outlet_state, o.phone as outlet_phone, o.email as outlet_email
      FROM bills b 
      JOIN vendors v ON b.vendor_id = v.id 
      LEFT JOIN outlets o ON b.outlet_id = o.id
      WHERE b.id = ?
    `;
    const [billRows] = await c.query(sqlBill, [id]);
    console.log('Bill rows:', billRows);
    
    const sqlItems = `
      SELECT bi.*, i.name as item_name, i.sku as item_sku, i.hsn_sac as item_hsn
      FROM bill_items bi 
      JOIN items i ON bi.item_id = i.id 
      WHERE bi.bill_id = ?
    `;
    const [itemRows] = await c.query(sqlItems, [id]);
    console.log('Item rows:', itemRows);
  } catch(e) {
    console.error('ERROR:', e.message);
  }
  await c.end();
}
run();
