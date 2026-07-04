const mysql = require('mysql2/promise');

async function run() {
  const c = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'admin@angel',
    database: 'ledgerpro'
  });

  console.log('Adding branch-specific branding fields to outlets table...');
  const columns = [
    { name: 'logo_url', type: 'TEXT' },
    { name: 'address', type: 'TEXT' },
    { name: 'gstin', type: 'VARCHAR(100)' },
    { name: 'state', type: 'VARCHAR(100)' },
    { name: 'phone', type: 'VARCHAR(50)' },
    { name: 'email', type: 'VARCHAR(100)' }
  ];

  for (const col of columns) {
    try {
      await c.query(`ALTER TABLE outlets ADD COLUMN ${col.name} ${col.type}`);
      console.log(`Added column ${col.name} to outlets table`);
    } catch (e) {
      console.log(`Column ${col.name} already exists or error: ${e.message}`);
    }
  }

  await c.end();
  console.log('Migration v3 completed!');
}

run().catch(console.error);
