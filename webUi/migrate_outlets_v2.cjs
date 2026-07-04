const mysql = require('mysql2/promise');

async function run() {
  const c = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'admin@angel',
    database: 'ledgerpro'
  });

  console.log('Migrating outlets table...');

  try {
    await c.query("ALTER TABLE outlets ADD COLUMN pricing_type VARCHAR(50) NOT NULL DEFAULT 'Base'");
    console.log('Added pricing_type column to outlets table');
  } catch (e) {
    console.log(`pricing_type column exists or error: ${e.message}`);
  }

  try {
    await c.query("INSERT IGNORE INTO settings (\`key\`, value) VALUES ('sp1_label', 'Type 1 pricing'), ('sp2_label', 'Type 2 pricing'), ('sp3_label', 'Type 3 pricing')");
    console.log('Default pricing type labels registered in settings');
  } catch (e) {
    console.log(`Error registering pricing type labels: ${e.message}`);
  }

  await c.end();
  console.log('Migration v2 completed!');
}

run().catch(console.error);
