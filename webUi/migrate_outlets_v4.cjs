const mysql = require('mysql2/promise');

async function run() {
  const c = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'admin@angel',
    database: 'ledgerpro'
  });

  console.log('Adding upi_id fields to database schema...');
  try {
    await c.query('ALTER TABLE outlets ADD COLUMN upi_id VARCHAR(150)');
    console.log('Added upi_id column to outlets table');
  } catch (e) {
    console.log(`outlets upi_id column already exists or error: ${e.message}`);
  }

  try {
    await c.query("INSERT IGNORE INTO settings (\`key\`, value) VALUES ('company_upi_id', '')");
    console.log('Inserted company_upi_id key in settings table');
  } catch (e) {
    console.log(`settings table insertion error: ${e.message}`);
  }

  await c.end();
  console.log('Migration v4 completed!');
}

run().catch(console.error);
