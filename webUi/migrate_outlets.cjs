const mysql = require('mysql2/promise');

async function run() {
  const c = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'admin@angel',
    database: 'ledgerpro'
  });

  console.log('Migrating database schema...');

  // Create Outlets Table
  await c.query(`
    CREATE TABLE IF NOT EXISTS outlets (
      id INT PRIMARY KEY AUTO_INCREMENT,
      name VARCHAR(255) NOT NULL,
      location VARCHAR(255)
    )
  `);

  // Insert default outlets
  await c.query(`
    INSERT IGNORE INTO outlets (id, name, location) VALUES 
    (1, 'Main Outlet', 'Headquarters'), 
    (2, 'North Branch', 'Delhi'), 
    (3, 'South Branch', 'Bangalore')
  `);

  // Add columns to existing tables
  const tablesWithOutlet = ['invoices', 'bills', 'users'];
  for (const t of tablesWithOutlet) {
    try {
      await c.query(`ALTER TABLE \`${t}\` ADD COLUMN outlet_id INT NOT NULL DEFAULT 1`);
      console.log(`Added outlet_id to table: ${t}`);
    } catch (e) {
      console.log(`Column outlet_id exists or error in ${t}: ${e.message}`);
    }
  }

  try {
    await c.query('ALTER TABLE items ADD COLUMN image_url TEXT');
    console.log('Added image_url to items table');
  } catch (e) {
    console.log(`image_url column exists or error in items: ${e.message}`);
  }

  try {
    await c.query("INSERT IGNORE INTO settings (\`key\`, value) VALUES ('company_logo', '')");
    console.log('Inserted default company_logo key');
  } catch (e) {
    console.log(`Error inserting company_logo setting: ${e.message}`);
  }

  await c.end();
  console.log('Migration script completed!');
}

run().catch(console.error);
