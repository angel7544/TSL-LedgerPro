import express from 'express';
import cors from 'cors';
import mysql from 'mysql2/promise';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import multer from 'multer';
import csv from 'csv-parser';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());

// Setup Multer for CSV Upload
const upload = multer({ dest: 'uploads/' });

const JWT_SECRET = 'ledgerpro_super_secret_token_key';

// Load MySQL database configuration from config.json
let pool;
try {
  const configPath = path.join(__dirname, '..', 'config.json');
  const rawConfig = fs.readFileSync(configPath, 'utf-8');
  const config = JSON.parse(rawConfig);
  
  if (config.database && config.database.type === 'mysql') {
    pool = mysql.createPool({
      host: config.database.host || 'localhost',
      port: config.database.port || 3306,
      user: config.database.user || 'root',
      password: config.database.password || '',
      database: config.database.database || 'ledgerpro',
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0
    });
    console.log(`MySQL Connection Pool established on ${config.database.host}:${config.database.port}`);
  } else {
    throw new Error('Database config is not mysql or missing');
  }
} catch (error) {
  console.error('Failed to read config.json or configure MySQL Pool. Ensure config.json is present in project root.', error);
  // Fallback default config
  pool = mysql.createPool({
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: '',
    database: 'ledgerpro',
    waitForConnections: true,
    connectionLimit: 5
  });
}

// Ensure database table directories for sql execution output files (User rule)
const sqlStepsDir = path.join(__dirname, 'sql_steps');
if (!fs.existsSync(sqlStepsDir)) {
  fs.mkdirSync(sqlStepsDir, { recursive: true });
}

function logSqlStep(stepName, query, params) {
  try {
    const stepDir = path.join(sqlStepsDir, stepName);
    if (!fs.existsSync(stepDir)) {
      fs.mkdirSync(stepDir, { recursive: true });
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = path.join(stepDir, `query_${timestamp}.sql`);
    const content = `-- SQL COMMAND:\n${query}\n-- PARAMETERS:\n${JSON.stringify(params || [])}\n`;
    fs.writeFileSync(filename, content);
  } catch (err) {
    console.error('Error logging SQL step:', err);
  }
}

// Authentication Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = (authHeader && authHeader.split(' ')[1]) || req.query.token;
  if (!token) return res.status(401).json({ error: 'Access token required' });
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Invalid or expired token' });
    req.user = user;
    next();
  });
};

// ==================== AUTHENTICATION ROUTES ====================

app.post('/api/auth/register', async (req, res) => {
  const { name, email, password } = req.body;
  if (!name || !email || !password) {
    return res.status(400).json({ error: 'All fields are required' });
  }
  try {
    const passwordHash = await bcrypt.hash(password, 10);
    const sql = 'INSERT INTO users (name, email, password_hash, role, outlet_id) VALUES (?, ?, ?, ?, ?)';
    logSqlStep('auth_register', sql, [name, email, '***']);
    await pool.query(sql, [name, email, passwordHash, 'Admin', 1]);
    res.json({ success: true, message: 'User registered successfully!' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message || 'Registration failed' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }
  try {
    const sql = 'SELECT * FROM users WHERE email = ?';
    logSqlStep('auth_login', sql, [email]);
    const [rows] = await pool.query(sql, [email]);
    if (rows.length === 0) {
      return res.status(400).json({ error: 'Invalid email or password' });
    }
    const user = rows[0];
    const validPass = await bcrypt.compare(password, user.password_hash);
    if (!validPass) {
      return res.status(400).json({ error: 'Invalid email or password' });
    }
    const token = jwt.sign({ id: user.id, name: user.name, email: user.email, role: user.role, outlet_id: user.outlet_id }, JWT_SECRET, { expiresIn: '8h' });
    res.json({ token, user: { id: user.id, name: user.name, email: user.email, role: user.role, outlet_id: user.outlet_id } });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/auth/me', authenticateToken, async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT id, name, email, role, outlet_id FROM users WHERE id = ?', [req.user.id]);
    if (rows.length > 0) {
      res.json({ user: rows[0] });
    } else {
      res.status(404).json({ error: 'User not found' });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== SETTINGS ROUTES ====================

app.get('/api/settings', async (req, res) => {
  try {
    const sql = 'SELECT * FROM settings';
    logSqlStep('get_settings', sql);
    const [rows] = await pool.query(sql);
    const settings = {};
    rows.forEach(row => {
      settings[row.key] = row.value;
    });
    res.json(settings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/settings', authenticateToken, async (req, res) => {
  const settings = req.body;
  try {
    for (const [key, val] of Object.entries(settings)) {
      const sql = 'INSERT INTO settings (`key`, value) VALUES (?, ?) ON DUPLICATE KEY UPDATE value = ?';
      logSqlStep('update_settings', sql, [key, val, val]);
      await pool.query(sql, [key, val, val]);
    }
    res.json({ success: true, message: 'Settings updated successfully' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== CUSTOMERS ROUTES ====================

app.get('/api/customers', authenticateToken, async (req, res) => {
  try {
    const sql = 'SELECT * FROM customers ORDER BY name ASC';
    logSqlStep('get_customers', sql);
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/customers', authenticateToken, async (req, res) => {
  const { name, email, phone, address, gstin, state, customer_type } = req.body;
  try {
    const sql = 'INSERT INTO customers (name, email, phone, address, gstin, state, customer_type) VALUES (?, ?, ?, ?, ?, ?, ?)';
    logSqlStep('create_customer', sql, [name, email, phone, address, gstin, state, customer_type]);
    const [result] = await pool.query(sql, [name, email, phone, address, gstin, state, customer_type || 'Type 1']);
    res.json({ id: result.insertId, name, email, phone, address, gstin, state, customer_type });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.put('/api/customers/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { name, email, phone, address, gstin, state, customer_type } = req.body;
  try {
    const sql = 'UPDATE customers SET name=?, email=?, phone=?, address=?, gstin=?, state=?, customer_type=? WHERE id=?';
    logSqlStep('update_customer', sql, [name, email, phone, address, gstin, state, customer_type, id]);
    await pool.query(sql, [name, email, phone, address, gstin, state, customer_type, id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/customers/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  try {
    const sql = 'DELETE FROM customers WHERE id = ?';
    logSqlStep('delete_customer', sql, [id]);
    await pool.query(sql, [id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== VENDORS ROUTES ====================

app.get('/api/vendors', authenticateToken, async (req, res) => {
  try {
    const sql = 'SELECT * FROM vendors ORDER BY name ASC';
    logSqlStep('get_vendors', sql);
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/vendors', authenticateToken, async (req, res) => {
  const { name, email, phone, address, gstin, state } = req.body;
  try {
    const sql = 'INSERT INTO vendors (name, email, phone, address, gstin, state) VALUES (?, ?, ?, ?, ?, ?)';
    logSqlStep('create_vendor', sql, [name, email, phone, address, gstin, state]);
    const [result] = await pool.query(sql, [name, email, phone, address, gstin, state]);
    res.json({ id: result.insertId, name, email, phone, address, gstin, state });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.put('/api/vendors/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { name, email, phone, address, gstin, state } = req.body;
  try {
    const sql = 'UPDATE vendors SET name=?, email=?, phone=?, address=?, gstin=?, state=? WHERE id=?';
    logSqlStep('update_vendor', sql, [name, email, phone, address, gstin, state, id]);
    await pool.query(sql, [name, email, phone, address, gstin, state, id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/vendors/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  try {
    const sql = 'DELETE FROM vendors WHERE id = ?';
    logSqlStep('delete_vendor', sql, [id]);
    await pool.query(sql, [id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== ITEMS ROUTES ====================

app.get('/api/items', authenticateToken, async (req, res) => {
  try {
    const sql = 'SELECT * FROM items ORDER BY name ASC';
    logSqlStep('get_items', sql);
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/items', authenticateToken, async (req, res) => {
  const { name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, purchase_price, reorder_point, opening_stock, image_url, is_sellable } = req.body;
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    const sqlInsertItem = `
      INSERT INTO items (name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, purchase_price, reorder_point, opening_stock, stock_on_hand, image_url, is_sellable)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const isSellableVal = is_sellable === undefined ? 1 : (is_sellable ? 1 : 0);
    logSqlStep('create_item', sqlInsertItem, [name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, purchase_price, reorder_point, opening_stock, opening_stock, image_url, isSellableVal]);
    const [itemResult] = await connection.query(sqlInsertItem, [
      name, sku, hsn_sac, gst_rate || 0, description, unit || 'pcs', selling_price || 0, sp1 || 0, sp2 || 0, sp3 || 0, purchase_price || 0, reorder_point || 0, opening_stock || 0, opening_stock || 0, image_url || null, isSellableVal
    ]);
    const itemId = itemResult.insertId;

    if (opening_stock && opening_stock > 0) {
      const sqlInsertBatch = `
        INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date)
        VALUES (?, ?, ?, CURDATE())
      `;
      logSqlStep('create_item_opening_batch', sqlInsertBatch, [itemId, opening_stock, purchase_price]);
      await connection.query(sqlInsertBatch, [itemId, opening_stock, purchase_price || 0]);
    }

    await connection.commit();
    res.json({ id: itemId, name, sku });
  } catch (err) {
    await connection.rollback();
    res.status(500).json({ error: err.message });
  } finally {
    connection.release();
  }
});

app.put('/api/items/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, purchase_price, reorder_point, image_url, is_sellable } = req.body;
  try {
    const isSellableVal = is_sellable === undefined ? 1 : (is_sellable ? 1 : 0);
    const sql = 'UPDATE items SET name=?, sku=?, hsn_sac=?, gst_rate=?, description=?, unit=?, selling_price=?, sp1=?, sp2=?, sp3=?, purchase_price=?, reorder_point=?, image_url=?, is_sellable=? WHERE id=?';
    logSqlStep('update_item', sql, [name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, purchase_price, reorder_point, image_url, isSellableVal, id]);
    await pool.query(sql, [name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, purchase_price, reorder_point, image_url || null, isSellableVal, id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/items/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  try {
    const sql = 'DELETE FROM items WHERE id = ?';
    logSqlStep('delete_item', sql, [id]);
    await pool.query(sql, [id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Helper to detect CSV Delimiter
function detectSeparator(filePath) {
  try {
    const fd = fs.openSync(filePath, 'r');
    const buffer = Buffer.alloc(4096);
    const bytesRead = fs.readSync(fd, buffer, 0, 4096, 0);
    fs.closeSync(fd);
    const content = buffer.toString('utf8', 0, bytesRead);
    const firstLine = content.split('\n')[0];
    const commas = (firstLine.match(/,/g) || []).length;
    const tabs = (firstLine.match(/\t/g) || []).length;
    const semicolons = (firstLine.match(/;/g) || []).length;

    if (tabs > commas && tabs > semicolons) return '\t';
    if (semicolons > commas && semicolons > tabs) return ';';
    return ',';
  } catch (err) {
    return ',';
  }
}

// CSV Key mapping similar to python desktop app
const keyMapping = {
  name: ['Item Name', 'Name', 'Product Name'],
  sku: ['SKU', 'Item Code'],
  hsn: ['HSN/SAC', 'HSN', 'SAC'],
  desc: ['Description', 'Desc'],
  unit: ['Unit Name', 'Usage unit', 'Unit'],
  selling_price: ['Rate', 'Selling Price', 'Price'],
  sp1: ['SP1', 'Selling Price 1'],
  sp2: ['SP2', 'Selling Price 2'],
  sp3: ['SP3', 'Selling Price 3'],
  purchase_price: ['Purchase Rate', 'Purchase Price', 'Cost'],
  reorder_point: ['Reorder Point', 'Min Stock'],
  opening_stock: ['Opening Stock', 'Initial Stock'],
  opening_value: ['Opening Stock Value'],
  stock_on_hand: ['Stock On Hand', 'Qty'],
  intra_tax: ['Intra State Tax Rate', 'SGST', 'CGST'],
  inter_tax: ['Inter State Tax Rate', 'IGST'],
  vendor: ['Vendor', 'Supplier']
};

function parseNumber(val) {
  if (val === undefined || val === null || val === '') return 0.0;
  return parseFloat(String(val).replace(/INR/g, '').replace(/,/g, '').trim()) || 0.0;
}

// CSV Import Route for Items
app.post('/api/items/import', authenticateToken, upload.single('file'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  const filePath = req.file.path;
  const separator = detectSeparator(filePath);
  const results = [];
  const connection = await pool.getConnection();

  fs.createReadStream(filePath)
    .pipe(csv({ separator }))
    .on('data', (data) => results.push(data))
    .on('end', async () => {
      try {
        await connection.beginTransaction();
        
        if (results.length === 0) {
          throw new Error('CSV is empty or missing headers');
        }

        // Clean headers and resolve mappings
        const firstRow = results[0];
        const cleanKeys = Object.keys(firstRow).map(k => k.trim());
        const resolvedHeaders = {};

        for (const [key, candidates] of Object.entries(keyMapping)) {
          let resolvedHeader = null;
          for (const c of candidates) {
            for (const h of cleanKeys) {
              if (h.toLowerCase() === c.toLowerCase()) {
                resolvedHeader = h;
                break;
              }
            }
            if (resolvedHeader) break;
          }
          resolvedHeaders[key] = resolvedHeader;
        }

        if (!resolvedHeaders.name) {
          throw new Error('Could not find a valid "Item Name" column in CSV.');
        }

        let successCount = 0;
        let skippedCount = 0;

        for (const row of results) {
          const cleanRow = {};
          for (const [k, v] of Object.entries(row)) {
            if (k) cleanRow[k.trim()] = v;
          }

          const name = (cleanRow[resolvedHeaders.name] || '').trim();
          if (!name) continue;

          const sku = cleanRow[resolvedHeaders.sku] || '';
          const hsn = cleanRow[resolvedHeaders.hsn] || '';
          const desc = cleanRow[resolvedHeaders.desc] || '';
          const unit = cleanRow[resolvedHeaders.unit] || 'pcs';

          const selling_price = parseNumber(cleanRow[resolvedHeaders.selling_price]);
          const sp1 = parseNumber(cleanRow[resolvedHeaders.sp1]);
          const sp2 = parseNumber(cleanRow[resolvedHeaders.sp2]);
          const sp3 = parseNumber(cleanRow[resolvedHeaders.sp3]);
          const purchase_price = parseNumber(cleanRow[resolvedHeaders.purchase_price]);
          const reorder_point = parseNumber(cleanRow[resolvedHeaders.reorder_point]);
          const opening_stock = parseNumber(cleanRow[resolvedHeaders.opening_stock]);
          const stock_on_hand_csv = parseNumber(cleanRow[resolvedHeaders.stock_on_hand]);

          const initial_stock = opening_stock > 0 ? opening_stock : stock_on_hand_csv;
          const opening_value = parseNumber(cleanRow[resolvedHeaders.opening_value]);

          let gst_rate = 0.0;
          if (resolvedHeaders.intra_tax && cleanRow[resolvedHeaders.intra_tax]) {
            gst_rate = parseNumber(cleanRow[resolvedHeaders.intra_tax]);
          } else if (resolvedHeaders.inter_tax && cleanRow[resolvedHeaders.inter_tax]) {
            gst_rate = parseNumber(cleanRow[resolvedHeaders.inter_tax]);
          }

          const vendor_name = resolvedHeaders.vendor ? (cleanRow[resolvedHeaders.vendor] || '').trim() : '';
          let vendor_id = null;
          if (vendor_name) {
            const [vRows] = await connection.query("SELECT id FROM vendors WHERE name = ?", [vendor_name]);
            if (vRows.length > 0) {
              vendor_id = vRows[0].id;
            } else {
              const [vResult] = await connection.query("INSERT INTO vendors (name) VALUES (?)", [vendor_name]);
              vendor_id = vResult.insertId;
            }
          }

          // Duplicate check
          let existing = [];
          if (sku) {
            const [rows] = await connection.query("SELECT id FROM items WHERE sku = ?", [sku]);
            existing = rows;
          } else {
            const [rows] = await connection.query("SELECT id FROM items WHERE name = ?", [name]);
            existing = rows;
          }

          if (existing.length > 0) {
            skippedCount++;
            continue;
          }

          // Insert Item
          const insertSql = `
            INSERT INTO items (name, sku, hsn_sac, description, unit, selling_price, sp1, sp2, sp3, purchase_price, gst_rate, reorder_point, stock_on_hand, opening_stock_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          `;
          const [itemResult] = await connection.query(insertSql, [
            name, sku, hsn, desc, unit, selling_price, sp1, sp2, sp3, purchase_price, gst_rate, reorder_point, initial_stock, opening_value
          ]);
          const itemId = itemResult.insertId;

          // Create stock batch
          if (initial_stock > 0) {
            let batch_rate = purchase_price;
            if (opening_value > 0 && opening_stock > 0) {
              batch_rate = opening_value / opening_stock;
            }
            await connection.query(`
              INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id)
              VALUES (?, ?, ?, CURDATE(), ?)
            `, [itemId, initial_stock, batch_rate, vendor_id]);
          }

          successCount++;
        }

        await connection.commit();
        fs.unlinkSync(filePath);
        res.json({ success: true, message: `Import finished. Success: ${successCount}. Skipped: ${skippedCount}` });
      } catch (err) {
        await connection.rollback();
        fs.unlinkSync(filePath);
        res.status(500).json({ error: err.message });
      } finally {
        connection.release();
      }
    });
});

// ==================== INVOICES ROUTES ====================

app.get('/api/invoices', authenticateToken, async (req, res) => {
  try {
    const sql = `
      SELECT i.*, c.name as customer_name, c.state as customer_state 
      FROM invoices i 
      JOIN customers c ON i.customer_id = c.id 
      ORDER BY i.date DESC, i.id DESC
    `;
    logSqlStep('get_invoices', sql);
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/invoices/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  try {
    const sqlInv = `
      SELECT i.*, 
             c.name as customer_name, c.email as customer_email, c.phone as customer_phone, c.address as customer_address, c.gstin as customer_gstin, c.state as customer_state,
             o.name as outlet_name, o.logo_url as outlet_logo_url, o.address as outlet_address, o.gstin as outlet_gstin, o.state as outlet_state, o.phone as outlet_phone, o.email as outlet_email, o.upi_id as outlet_upi_id
      FROM invoices i 
      JOIN customers c ON i.customer_id = c.id 
      LEFT JOIN outlets o ON i.outlet_id = o.id
      WHERE i.id = ?
    `;
    logSqlStep('get_invoice_detail', sqlInv, [id]);
    const [invRows] = await pool.query(sqlInv, [id]);
    if (invRows.length === 0) return res.status(404).json({ error: 'Invoice not found' });

    const sqlItems = `
      SELECT ii.*, it.name as item_name, it.sku as item_sku, it.hsn_sac as item_hsn
      FROM invoice_items ii 
      JOIN items it ON ii.item_id = it.id 
      WHERE ii.invoice_id = ?
    `;
    logSqlStep('get_invoice_items', sqlItems, [id]);
    const [itemRows] = await pool.query(sqlItems, [id]);

    res.json({ invoice: invRows[0], items: itemRows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Create Invoice (including GST breakdown, customer state logic, FIFO inventory reduce)
app.post('/api/invoices', authenticateToken, async (req, res) => {
  const { customer_id, date, due_date, items, notes, order_number, terms, salesperson, subject, round_off, outlet_id } = req.body;
  if (!customer_id || !items || items.length === 0) {
    return res.status(400).json({ error: 'Customer and items are required' });
  }

  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    // 1. Get Company details for GST calculation (Intra vs Inter state)
    const [settingsRows] = await connection.query("SELECT * FROM settings");
    const settings = {};
    settingsRows.forEach(r => settings[r.key] = r.value);
    const sellerState = (settings['company_state'] || '').trim().toLowerCase();

    // 2. Get Customer details
    const [custRows] = await connection.query("SELECT * FROM customers WHERE id = ?", [customer_id]);
    if (custRows.length === 0) throw new Error('Customer not found');
    const customer = custRows[0];
    const buyerState = (customer.state || '').trim().toLowerCase();
    
    const isIntraState = sellerState && buyerState && sellerState === buyerState;

    let subtotal = 0;
    let totalTax = 0;
    const processedItems = [];

    // 3. Process items and calculate GST
    for (const entry of items) {
      const { item_id, quantity, rate, discount_percent } = entry;
      const [itemRows] = await connection.query("SELECT * FROM items WHERE id = ?", [item_id]);
      if (itemRows.length === 0) throw new Error(`Item ${item_id} not found`);
      const item = itemRows[0];

      const itemRate = rate !== undefined ? rate : item.selling_price;
      const itemGstRate = item.gst_rate || 0;

      const baseAmount = itemRate * quantity;
      const discountAmount = (baseAmount * (discount_percent || 0)) / 100;
      const taxableAmount = baseAmount - discountAmount;

      // GST Calculation
      const gstAmount = (taxableAmount * itemGstRate) / 100;

      subtotal += taxableAmount;
      totalTax += gstAmount;

      processedItems.push({
        item_id,
        quantity,
        rate: itemRate,
        discount_percent: discount_percent || 0,
        gst_percent: itemGstRate,
        amount: taxableAmount + gstAmount
      });

      // 4. Reduce stock using FIFO method
      if (item.track_inventory) {
        let remainingToSell = quantity;
        
        // Fetch batches (FIFO order)
        const [batches] = await connection.query(`
          SELECT id, quantity_remaining, purchase_rate 
          FROM stock_batches 
          WHERE item_id = ? AND quantity_remaining > 0 
          ORDER BY purchase_date ASC, id ASC
        `, [item_id]);

        for (const batch of batches) {
          if (remainingToSell <= 0) break;
          const qtyAvailable = batch.quantity_remaining;
          
          if (qtyAvailable <= remainingToSell) {
            remainingToSell -= qtyAvailable;
            await connection.query("UPDATE stock_batches SET quantity_remaining = 0 WHERE id = ?", [batch.id]);
          } else {
            const newQty = qtyAvailable - remainingToSell;
            remainingToSell = 0;
            await connection.query("UPDATE stock_batches SET quantity_remaining = ? WHERE id = ?", [newQty, batch.id]);
          }
        }

        // Update main item stock
        await connection.query("UPDATE items SET stock_on_hand = stock_on_hand - ? WHERE id = ?", [quantity, item_id]);
      }
    }

    const grandTotal = subtotal + totalTax;

    // Generate invoice number
    const prefix = settings['invoice_prefix'] || 'INV-';
    const [countRows] = await connection.query("SELECT COUNT(*) as cnt FROM invoices");
    const invNumber = `${prefix}${(countRows[0].cnt + 1).toString().padStart(5, '0')}`;

    const { order_number, terms, subject, customer_notes, terms_conditions, tds_amount, tcs_amount, adjustment, status } = req.body;
    const finalGrandTotal = grandTotal - (parseFloat(tds_amount) || 0) + (parseFloat(tcs_amount) || 0) + (parseFloat(adjustment) || 0) + (parseFloat(round_off) || 0);

    // 5. Insert Invoice
    const sqlInsertInvoice = `
      INSERT INTO invoices (invoice_number, customer_id, date, due_date, subtotal, tax_amount, grand_total, status, notes, order_number, terms, salesperson, subject, round_off, outlet_id, customer_notes, terms_conditions, tds_amount, tcs_amount, adjustment)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const invStatus = status || 'Unpaid';
    logSqlStep('create_invoice', sqlInsertInvoice, [invNumber, customer_id, date, due_date, subtotal, totalTax, finalGrandTotal, invStatus, round_off || 0, outlet_id || 1]);
    const [invResult] = await connection.query(sqlInsertInvoice, [
      invNumber, customer_id, date || new Date(), due_date, subtotal, totalTax, finalGrandTotal, invStatus, notes, order_number, terms, salesperson, subject, parseFloat(round_off) || 0, parseInt(outlet_id) || 1, customer_notes, terms_conditions, parseFloat(tds_amount) || 0, parseFloat(tcs_amount) || 0, parseFloat(adjustment) || 0
    ]);
    const invoiceId = invResult.insertId;

    // 6. Insert Invoice Items
    for (const pi of processedItems) {
      const sqlInsertItem = `
        INSERT INTO invoice_items (invoice_id, item_id, quantity, rate, discount_percent, gst_percent, amount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `;
      await connection.query(sqlInsertItem, [
        invoiceId, pi.item_id, pi.quantity, pi.rate, pi.discount_percent, pi.gst_percent, pi.amount
      ]);
    }

    await connection.commit();
    res.json({ success: true, invoiceId, invoiceNumber: invNumber });

  } catch (err) {
    await connection.rollback();
    console.error(err);
    res.status(500).json({ error: err.message });
  } finally {
    connection.release();
  }
});

// Update Invoice status
app.put('/api/invoices/:id/status', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { status } = req.body;
  try {
    const sql = 'UPDATE invoices SET status = ? WHERE id = ?';
    logSqlStep('update_invoice_status', sql, [status, id]);
    await pool.query(sql, [status, id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/invoices/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    // 1. Check for payments
    const [payments] = await connection.query("SELECT id FROM payments WHERE invoice_id = ?", [id]);
    if (payments.length > 0) {
      return res.status(400).json({ error: "Cannot delete invoice with recorded payments. Please delete payments first." });
    }

    // 2. Get items to restore stock
    const [invItems] = await connection.query("SELECT item_id, quantity FROM invoice_items WHERE invoice_id = ?", [id]);

    // Reverse Stock: Add back quantity
    for (const item of invItems) {
      const [itemDef] = await connection.query("SELECT purchase_price FROM items WHERE id = ?", [item.item_id]);
      const rate = itemDef.length > 0 ? itemDef[0].purchase_price : 0;

      // Add stock batch
      const insertBatchSql = "INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date) VALUES (?, ?, ?, CURDATE())";
      logSqlStep("delete_invoice_restore_batch", insertBatchSql, [item.item_id, item.quantity, rate]);
      await connection.query(insertBatchSql, [item.item_id, item.quantity, rate]);

      // Update main stock level
      const updateStockSql = "UPDATE items SET stock_on_hand = stock_on_hand + ? WHERE id = ?";
      logSqlStep("delete_invoice_update_item_stock", updateStockSql, [item.quantity, item.item_id]);
      await connection.query(updateStockSql, [item.quantity, item.item_id]);
    }

    // 3. Delete records
    logSqlStep("delete_invoice_items", "DELETE FROM invoice_items WHERE invoice_id = ?", [id]);
    await connection.query("DELETE FROM invoice_items WHERE invoice_id = ?", [id]);

    logSqlStep("delete_invoice_record", "DELETE FROM invoices WHERE id = ?", [id]);
    await connection.query("DELETE FROM invoices WHERE id = ?", [id]);

    await connection.commit();
    res.json({ success: true });
  } catch (err) {
    await connection.rollback();
    res.status(500).json({ error: err.message });
  } finally {
    connection.release();
  }
});

// ==================== BILLS ROUTES ====================

app.get('/api/bills', authenticateToken, async (req, res) => {
  try {
    const sql = `
      SELECT b.*, v.name as vendor_name, 
             COALESCE((SELECT SUM(amount) FROM payments WHERE bill_id = b.id), 0) as paid_amount,
             (b.grand_total - COALESCE((SELECT SUM(amount) FROM payments WHERE bill_id = b.id), 0)) as balance_due
      FROM bills b 
      JOIN vendors v ON b.vendor_id = v.id 
      ORDER BY b.date DESC, b.id DESC
    `;
    logSqlStep('get_bills', sql);
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/bills/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  try {
    const sqlBill = `
      SELECT b.*, 
             v.name as vendor_name, v.email as vendor_email, v.phone as vendor_phone, v.address as vendor_address, v.gstin as vendor_gstin, v.state as vendor_state,
             o.name as outlet_name, o.logo_url as outlet_logo_url, o.address as outlet_address, o.gstin as outlet_gstin, o.state as outlet_state, o.phone as outlet_phone, o.email as outlet_email
      FROM bills b 
      JOIN vendors v ON b.vendor_id = v.id 
      LEFT JOIN outlets o ON b.outlet_id = o.id
      WHERE b.id = ?
    `;
    logSqlStep('get_bill_detail', sqlBill, [id]);
    const [billRows] = await pool.query(sqlBill, [id]);
    if (billRows.length === 0) return res.status(404).json({ error: 'Bill not found' });

    const sqlItems = `
      SELECT bi.*, i.name as item_name, i.sku as item_sku, i.hsn_sac as item_hsn
      FROM bill_items bi 
      JOIN items i ON bi.item_id = i.id 
      WHERE bi.bill_id = ?
    `;
    logSqlStep('get_bill_items', sqlItems, [id]);
    const [itemRows] = await pool.query(sqlItems, [id]);

    res.json({ bill: billRows[0], items: itemRows });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/bills/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    // 1. Check for payments
    const [payments] = await connection.query("SELECT id FROM payments WHERE bill_id = ?", [id]);
    if (payments.length > 0) {
      return res.status(400).json({ error: "Cannot delete bill with recorded payments. Please delete payments first." });
    }

    // 2. Get items to reduce stock
    const [billItems] = await connection.query("SELECT item_id, quantity FROM bill_items WHERE bill_id = ?", [id]);

    // Reverse Stock: Reduce stock level since purchase is deleted
    for (const item of billItems) {
      let remainingToReduce = item.quantity;

      // Find stock batches for this item that can be reduced/removed (usually latest batches first, or FIFO order)
      const [batches] = await connection.query(
        "SELECT id, quantity_remaining FROM stock_batches WHERE item_id = ? AND quantity_remaining > 0 ORDER BY purchase_date DESC, id DESC",
        [item.item_id]
      );

      for (const batch of batches) {
        if (remainingToReduce <= 0) break;
        if (batch.quantity_remaining <= remainingToReduce) {
          remainingToReduce -= batch.quantity_remaining;
          await connection.query("DELETE FROM stock_batches WHERE id = ?", [batch.id]);
        } else {
          const newQty = batch.quantity_remaining - remainingToReduce;
          remainingToReduce = 0;
          await connection.query("UPDATE stock_batches SET quantity_remaining = ? WHERE id = ?", [newQty, batch.id]);
        }
      }

      // Update main stock level
      const updateStockSql = "UPDATE items SET stock_on_hand = GREATEST(0, stock_on_hand - ?) WHERE id = ?";
      logSqlStep("delete_bill_reduce_item_stock", updateStockSql, [item.quantity, item.item_id]);
      await connection.query(updateStockSql, [item.quantity, item.item_id]);
    }

    // 3. Delete records
    logSqlStep("delete_bill_items", "DELETE FROM bill_items WHERE bill_id = ?", [id]);
    await connection.query("DELETE FROM bill_items WHERE bill_id = ?", [id]);

    logSqlStep("delete_bill_record", "DELETE FROM bills WHERE id = ?", [id]);
    await connection.query("DELETE FROM bills WHERE id = ?", [id]);

    await connection.commit();
    res.json({ success: true });
  } catch (err) {
    await connection.rollback();
    res.status(500).json({ error: err.message });
  } finally {
    connection.release();
  }
});

app.put('/api/bills/:id/status', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { status } = req.body;
  try {
    const sql = 'UPDATE bills SET status = ? WHERE id = ?';
    logSqlStep('update_bill_status', sql, [status, id]);
    await pool.query(sql, [status, id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/bills', authenticateToken, async (req, res) => {
  const { bill_number, vendor_id, date, due_date, items, notes, order_number, payment_terms, outlet_id, reverse_charge, adjustment, tds_amount, tcs_amount, discount_amount, status } = req.body;
  if (!bill_number || !vendor_id || !items || items.length === 0) {
    return res.status(400).json({ error: 'Bill number, vendor, and items are required' });
  }

  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    let subtotal = 0;
    let totalTax = 0;
    const processedItems = [];

    for (const entry of items) {
      const { item_id, quantity, rate } = entry;
      const [itemRows] = await connection.query("SELECT * FROM items WHERE id = ?", [item_id]);
      if (itemRows.length === 0) throw new Error(`Item ${item_id} not found`);
      const item = itemRows[0];

      const itemRate = rate !== undefined ? rate : item.purchase_price;
      const gstRate = item.gst_rate || 0;

      const baseAmount = itemRate * quantity;
      const gstAmount = (baseAmount * gstRate) / 100;

      subtotal += baseAmount;
      totalTax += gstAmount;

      processedItems.push({
        item_id,
        quantity,
        rate: itemRate,
        gst_percent: gstRate,
        amount: baseAmount + gstAmount
      });

      // Update Stock (FIFO batch entry)
      const batchSql = 'INSERT INTO stock_batches (item_id, quantity_remaining, purchase_rate, purchase_date, vendor_id, outlet_id) VALUES (?, ?, ?, ?, ?, ?)';
      await connection.query(batchSql, [item_id, quantity, itemRate, date || new Date(), vendor_id, parseInt(outlet_id) || 1]);

      // Update main stock level
      await connection.query("UPDATE items SET stock_on_hand = stock_on_hand + ?, purchase_price = ? WHERE id = ?", [quantity, itemRate, item_id]);
    }

    const grandTotal = subtotal + totalTax;
    const finalGrandTotal = grandTotal - (parseFloat(tds_amount) || 0) + (parseFloat(tcs_amount) || 0) + (parseFloat(adjustment) || 0) - (parseFloat(discount_amount) || 0);

    // Insert Bill
    const sqlInsertBill = `
      INSERT INTO bills (bill_number, vendor_id, date, due_date, subtotal, tax_amount, grand_total, status, notes, order_number, payment_terms, outlet_id, reverse_charge, adjustment, tds_amount, tcs_amount, discount_amount)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const billStatus = status || 'Unpaid';
    logSqlStep('create_bill', sqlInsertBill, [bill_number, vendor_id, date, due_date, subtotal, totalTax, finalGrandTotal, billStatus, outlet_id || 1]);
    const [billResult] = await connection.query(sqlInsertBill, [
      bill_number, vendor_id, date || new Date(), due_date, subtotal, totalTax, finalGrandTotal, billStatus, notes, order_number, payment_terms, parseInt(outlet_id) || 1, reverse_charge ? 1 : 0, parseFloat(adjustment) || 0, parseFloat(tds_amount) || 0, parseFloat(tcs_amount) || 0, parseFloat(discount_amount) || 0
    ]);
    const billId = billResult.insertId;

    // Insert Bill Items
    for (const pi of processedItems) {
      const sqlInsertItem = `
        INSERT INTO bill_items (bill_id, item_id, quantity, rate, gst_percent, amount)
        VALUES (?, ?, ?, ?, ?, ?)
      `;
      await connection.query(sqlInsertItem, [
        billId, pi.item_id, pi.quantity, pi.rate, pi.gst_percent, pi.amount
      ]);
    }

    await connection.commit();
    res.json({ success: true, billId });

  } catch (err) {
    await connection.rollback();
    res.status(500).json({ error: err.message });
  } finally {
    connection.release();
  }
});

// ==================== PAYMENTS ROUTES ====================

app.get('/api/payments', authenticateToken, async (req, res) => {
  try {
    const sql = `
      SELECT p.*, c.name as customer_name, v.name as vendor_name, i.invoice_number, b.bill_number
      FROM payments p
      LEFT JOIN customers c ON p.customer_id = c.id
      LEFT JOIN vendors v ON p.vendor_id = v.id
      LEFT JOIN invoices i ON p.invoice_id = i.id
      LEFT JOIN bills b ON p.bill_id = b.id
      ORDER BY p.date DESC, p.id DESC
    `;
    logSqlStep('get_payments', sql);
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/payments', authenticateToken, async (req, res) => {
  const { 
    customer_id, vendor_id, amount, date, method, notes, 
    payment_number, deposit_to, bank_charges, reference, 
    allocations, use_credits 
  } = req.body;

  if (!amount && (!allocations || allocations.length === 0)) {
    return res.status(400).json({ error: 'Amount is required' });
  }

  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    const pNum = payment_number || `PAY-${Date.now()}`;
    const pDate = date || new Date();

    // 1. Process allocations
    let totalAllocated = 0;
    if (allocations && allocations.length > 0) {
      for (const alloc of allocations) {
        if (alloc.amount <= 0) continue;
        totalAllocated += alloc.amount;

        const sqlInsertPay = `
          INSERT INTO payments (invoice_id, bill_id, customer_id, vendor_id, amount, date, method, notes, payment_number, deposit_to, bank_charges, reference)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `;
        await connection.query(sqlInsertPay, [
          alloc.invoice_id || null, alloc.bill_id || null, customer_id || null, vendor_id || null, alloc.amount, pDate, method, notes, pNum, deposit_to, bank_charges || 0, reference
        ]);

        // Adjust Invoice status
        if (alloc.invoice_id) {
          const [invRows] = await connection.query("SELECT grand_total FROM invoices WHERE id = ?", [alloc.invoice_id]);
          if (invRows.length > 0) {
            const grandTotal = invRows[0].grand_total;
            const [payRows] = await connection.query("SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?", [alloc.invoice_id]);
            const totalPaid = payRows[0].paid || 0;
            const newStatus = totalPaid >= grandTotal - 0.01 ? 'Paid' : totalPaid > 0 ? 'Partially Paid' : 'Unpaid';
            await connection.query("UPDATE invoices SET status = ? WHERE id = ?", [newStatus, alloc.invoice_id]);
          }
        }

        // Adjust Bill status
        if (alloc.bill_id) {
          const [billRows] = await connection.query("SELECT grand_total FROM bills WHERE id = ?", [alloc.bill_id]);
          if (billRows.length > 0) {
            const grandTotal = billRows[0].grand_total;
            const [payRows] = await connection.query("SELECT SUM(amount) as paid FROM payments WHERE bill_id = ?", [alloc.bill_id]);
            const totalPaid = payRows[0].paid || 0;
            const newStatus = totalPaid >= grandTotal - 0.01 ? 'Paid' : totalPaid > 0 ? 'Partially Paid' : 'Unpaid';
            await connection.query("UPDATE bills SET status = ? WHERE id = ?", [newStatus, alloc.bill_id]);
          }
        }
      }
    }

    // 2. Handle Excess Amount (creates a credit row with invoice_id/bill_id = NULL)
    const excess = amount - totalAllocated;
    if (excess > 0.01) {
      const sqlInsertExcess = `
        INSERT INTO payments (invoice_id, bill_id, customer_id, vendor_id, amount, date, method, notes, payment_number, deposit_to, bank_charges, reference)
        VALUES (NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `;
      await connection.query(sqlInsertExcess, [
        customer_id || null, vendor_id || null, excess, pDate, method, notes, pNum, deposit_to, bank_charges || 0, reference
      ]);
    }

    await connection.commit();
    res.json({ success: true });
  } catch (err) {
    await connection.rollback();
    res.status(500).json({ error: err.message });
  } finally {
    connection.release();
  }
});

// ==================== STOCK FIFO & LEDGER ====================

app.get('/api/stock/valuation', authenticateToken, async (req, res) => {
  try {
    const [items] = await pool.query("SELECT id, name, selling_price, sp1, sp2, sp3, stock_on_hand FROM items");
    const summary = [];

    for (const item of items) {
      const [batches] = await pool.query(`
        SELECT quantity_remaining, purchase_rate 
        FROM stock_batches 
        WHERE item_id = ? AND quantity_remaining > 0
      `, [item.id]);

      let totalQty = 0;
      let totalValue = 0;

      batches.forEach(b => {
        totalQty += b.quantity_remaining;
        totalValue += b.quantity_remaining * b.purchase_rate;
      });

      const avgCost = totalQty > 0 ? (totalValue / totalQty) : 0;

      summary.push({
        item_id: item.id,
        item_name: item.name,
        selling_price: item.selling_price || 0,
        sp1: item.sp1 || 0,
        sp2: item.sp2 || 0,
        sp3: item.sp3 || 0,
        total_quantity: totalQty,
        total_value: parseFloat(totalValue.toFixed(2)),
        avg_cost: parseFloat(avgCost.toFixed(2))
      });
    }

    res.json(summary);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/stock/batches', authenticateToken, async (req, res) => {
  try {
    const sql = `
      SELECT sb.*, i.name as item_name, v.name as vendor_name
      FROM stock_batches sb
      JOIN items i ON sb.item_id = i.id
      LEFT JOIN vendors v ON sb.vendor_id = v.id
      ORDER BY sb.purchase_date DESC, sb.id DESC
    `;
    const [rows] = await pool.query(sql);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ==================== REPORTS ROUTES ====================

// Dashboard analytics endpoint
app.get('/api/reports/dashboard', authenticateToken, async (req, res) => {
  const { outlet_id } = req.query;
  const hasOutlet = outlet_id && outlet_id !== 'all';
  try {
    let salesSql = "SELECT SUM(grand_total) as total FROM invoices WHERE status != 'Draft'";
    const salesParams = [];
    if (hasOutlet) {
      salesSql += " AND outlet_id = ?";
      salesParams.push(parseInt(outlet_id));
    }
    const [salesResult] = await pool.query(salesSql, salesParams);

    let purchaseSql = "SELECT SUM(grand_total) as total FROM bills WHERE status != 'Draft'";
    const purchaseParams = [];
    if (hasOutlet) {
      purchaseSql += " AND outlet_id = ?";
      purchaseParams.push(parseInt(outlet_id));
    }
    const [purchaseResult] = await pool.query(purchaseSql, purchaseParams);
    
    // Receivables (Unpaid + Partially Paid Invoices)
    let recSql = "SELECT id, grand_total FROM invoices WHERE status != 'Paid'";
    const recParams = [];
    if (hasOutlet) {
      recSql += " AND outlet_id = ?";
      recParams.push(parseInt(outlet_id));
    }
    const [invoices] = await pool.query(recSql, recParams);
    let outstandingReceivables = 0;
    for (const inv of invoices) {
      const [pay] = await pool.query("SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?", [inv.id]);
      const paid = pay[0].paid || 0;
      outstandingReceivables += (inv.grand_total - paid);
    }

    // Stock value
    let stockSql = "SELECT quantity_remaining, purchase_rate FROM stock_batches WHERE quantity_remaining > 0";
    const stockParams = [];
    if (hasOutlet) {
      stockSql += " AND outlet_id = ?";
      stockParams.push(parseInt(outlet_id));
    }
    const [batches] = await pool.query(stockSql, stockParams);
    let stockValue = 0;
    batches.forEach(b => stockValue += b.quantity_remaining * b.purchase_rate);

    // Low stock items count
    const [lowStock] = await pool.query("SELECT COUNT(*) as count FROM items WHERE stock_on_hand <= reorder_point");

    // Monthly Sales Chart Data
    let monthlySql = `
      SELECT DATE_FORMAT(date, '%Y-%m') as month, SUM(grand_total) as total 
      FROM invoices 
      WHERE status != 'Draft'
    `;
    const monthlyParams = [];
    if (hasOutlet) {
      monthlySql += " AND outlet_id = ?";
      monthlyParams.push(parseInt(outlet_id));
    }
    monthlySql += `
      GROUP BY month 
      ORDER BY month DESC 
      LIMIT 6
    `;
    const [monthlySales] = await pool.query(monthlySql, monthlyParams);

    res.json({
      sales: salesResult[0].total || 0,
      purchases: purchaseResult[0].total || 0,
      receivables: outstandingReceivables,
      stockValue,
      lowStockCount: lowStock[0].count,
      monthlySales: monthlySales.reverse()
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GST summary report
app.get('/api/reports/gst-summary', authenticateToken, async (req, res) => {
  const { startDate, endDate } = req.query;
  try {
    let salesQuery = `
      SELECT ii.gst_percent, SUM(ii.amount - (ii.rate * ii.quantity * (1 - ii.discount_percent/100))) as tax_collected
      FROM invoice_items ii
      JOIN invoices i ON ii.invoice_id = i.id
      WHERE i.status != 'Draft'
    `;
    let purchaseQuery = `
      SELECT bi.gst_percent, SUM(bi.amount - (bi.rate * bi.quantity)) as tax_paid
      FROM bill_items bi
      JOIN bills b ON bi.bill_id = b.id
      WHERE b.status != 'Draft'
    `;

    const params = [];
    if (startDate && endDate) {
      salesQuery += ` AND i.date BETWEEN ? AND ?`;
      purchaseQuery += ` AND b.date BETWEEN ? AND ?`;
      params.push(startDate, endDate);
    }

    salesQuery += ` GROUP BY ii.gst_percent`;
    purchaseQuery += ` GROUP BY bi.gst_percent`;

    const [salesTax] = await pool.query(salesQuery, params);
    const [purchaseTax] = await pool.query(purchaseQuery, params);

    res.json({ salesTax, purchaseTax });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// AR aging report
app.get('/api/reports/aging/receivables', authenticateToken, async (req, res) => {
  try {
    const [invoices] = await pool.query(`
      SELECT i.id, i.invoice_number, i.grand_total, i.date, i.due_date, c.name as customer_name, DATEDIFF(CURDATE(), i.due_date) as days_overdue
      FROM invoices i
      JOIN customers c ON i.customer_id = c.id
      WHERE i.status != 'Paid' AND i.status != 'Draft'
    `);

    const aging = {
      current: 0,
      thirty: 0,
      sixty: 0,
      ninety: 0,
      ninetyPlus: 0,
      details: []
    };

    for (const inv of invoices) {
      const [pay] = await pool.query("SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?", [inv.id]);
      const balance = inv.grand_total - (pay[0].paid || 0);

      if (balance <= 0) continue;

      const overdue = inv.days_overdue || 0;
      if (overdue <= 0) {
        aging.current += balance;
      } else if (overdue <= 30) {
        aging.thirty += balance;
      } else if (overdue <= 60) {
        aging.sixty += balance;
      } else if (overdue <= 90) {
        aging.ninety += balance;
      } else {
        aging.ninetyPlus += balance;
      }

      aging.details.push({
        invoice_number: inv.invoice_number,
        customer_name: inv.customer_name,
        date: inv.date,
        due_date: inv.due_date,
        balance,
        days_overdue: overdue
      });
    }

    res.json(aging);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET customer's unpaid invoices with outstanding balances
app.get('/api/payments/unpaid-invoices/:customerId', authenticateToken, async (req, res) => {
  const { customerId } = req.params;
  try {
    const [invoices] = await pool.query(
      "SELECT id, invoice_number, date, due_date, grand_total, status FROM invoices WHERE customer_id = ? AND status NOT IN ('Paid', 'Draft', 'Cancelled') ORDER BY date ASC",
      [customerId]
    );
    const results = [];
    for (const inv of invoices) {
      const [payRows] = await pool.query("SELECT SUM(amount) as paid FROM payments WHERE invoice_id = ?", [inv.id]);
      const paid = payRows[0].paid || 0;
      const balance = inv.grand_total - paid;
      if (balance > 0.01) {
        results.push({
          id: inv.id,
          invoice_number: inv.invoice_number,
          date: inv.date,
          due_date: inv.due_date,
          grand_total: inv.grand_total,
          status: inv.status,
          amount_paid: paid,
          balance_due: balance
        });
      }
    }
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET customer's available credit balance
app.get('/api/payments/credits/:customerId', authenticateToken, async (req, res) => {
  const { customerId } = req.params;
  try {
    const [rows] = await pool.query("SELECT SUM(amount) as total FROM payments WHERE customer_id = ? AND invoice_id IS NULL", [customerId]);
    res.json({ credits: rows[0].total || 0.0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET vendor's unpaid bills with outstanding balances
app.get('/api/payments/unpaid-bills/:vendorId', authenticateToken, async (req, res) => {
  const { vendorId } = req.params;
  try {
    const [bills] = await pool.query(
      "SELECT id, bill_number, date, due_date, grand_total, status FROM bills WHERE vendor_id = ? AND status NOT IN ('Paid', 'Draft', 'Cancelled') ORDER BY date ASC",
      [vendorId]
    );
    const results = [];
    for (const bill of bills) {
      const [payRows] = await pool.query("SELECT SUM(amount) as paid FROM payments WHERE bill_id = ?", [bill.id]);
      const paid = payRows[0].paid || 0;
      const balance = bill.grand_total - paid;
      if (balance > 0.01) {
        results.push({
          id: bill.id,
          bill_number: bill.bill_number,
          date: bill.date,
          due_date: bill.due_date,
          grand_total: bill.grand_total,
          status: bill.status,
          amount_paid: paid,
          balance_due: balance
        });
      }
    }
    res.json(results);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET vendor's available credit balance
app.get('/api/payments/vendor-credits/:vendorId', authenticateToken, async (req, res) => {
  const { vendorId } = req.params;
  try {
    const [rows] = await pool.query("SELECT SUM(amount) as total FROM payments WHERE vendor_id = ? AND bill_id IS NULL", [vendorId]);
    res.json({ credits: rows[0].total || 0.0 });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST to update MySQL connection configurations dynamically
app.post('/api/settings/db-config', async (req, res) => {
  const { host, port, user, password, database, type } = req.body;
  try {
    const configPath = path.join(__dirname, '..', 'config.json');
    const config = {
      database: {
        type: type || 'mysql',
        host: host || 'localhost',
        port: parseInt(port) || 3306,
        user: user || 'root',
        password: password || '',
        database: database || 'ledgerpro'
      }
    };
    fs.writeFileSync(configPath, JSON.stringify(config, null, 4));
    res.json({ success: true, message: 'Database configurations updated successfully!' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET database SQL backup download stream
app.get('/api/settings/backup', authenticateToken, async (req, res) => {
  try {
    const [tables] = await pool.query("SHOW TABLES");
    let dump = `-- LEDGERPRO DATABASE BACKUP\n-- DATE: ${new Date().toISOString()}\n\n`;
    
    for (const tableRow of tables) {
      const tableName = Object.values(tableRow)[0];
      const [createRows] = await pool.query(`SHOW CREATE TABLE \`${tableName}\``);
      const createSql = createRows[0]['Create Table'];
      dump += `DROP TABLE IF EXISTS \`${tableName}\`;\n${createSql};\n\n`;

      const [rows] = await pool.query(`SELECT * FROM \`${tableName}\``);
      if (rows.length > 0) {
        dump += `INSERT INTO \`${tableName}\` VALUES \n`;
        const valueStrings = rows.map(row => {
          const values = Object.values(row).map(val => {
            if (val === null) return 'NULL';
            if (typeof val === 'number') return val;
            if (val instanceof Date) return `'${val.toISOString().slice(0, 19).replace('T', ' ')}'`;
            return `'${String(val).replace(/'/g, "\\'")}'`;
          });
          return `(${values.join(', ')})`;
        });
        dump += valueStrings.join(',\n') + ';\n\n';
      }
    }
    
    res.setHeader('Content-disposition', 'attachment; filename=ledgerpro_backup.sql');
    res.setHeader('Content-type', 'text/plain');
    res.write(dump);
    res.end();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET list of outlets/branches
app.get('/api/outlets', authenticateToken, async (req, res) => {
  try {
    const [rows] = await pool.query("SELECT * FROM outlets ORDER BY id");
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST to create a new outlet (Admin only)
app.post('/api/outlets', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  const { name, location, pricing_type, logo_url, address, gstin, state, phone, email, upi_id } = req.body;
  if (!name) return res.status(400).json({ error: 'Name is required' });
  try {
    const sql = 'INSERT INTO outlets (name, location, pricing_type, logo_url, address, gstin, state, phone, email, upi_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
    logSqlStep('create_outlet', sql, [name, location, pricing_type, logo_url, address, gstin, state, phone, email, upi_id]);
    const [result] = await pool.query(sql, [name, location, pricing_type || 'Base', logo_url || null, address || null, gstin || null, state || null, phone || null, email || null, upi_id || null]);
    res.json({ id: result.insertId, name, location, pricing_type: pricing_type || 'Base' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PUT to edit an outlet (Admin only)
app.put('/api/outlets/:id', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  const { name, location, pricing_type, logo_url, address, gstin, state, phone, email, upi_id } = req.body;
  try {
    const sql = 'UPDATE outlets SET name = ?, location = ?, pricing_type = ?, logo_url = ?, address = ?, gstin = ?, state = ?, phone = ?, email = ?, upi_id = ? WHERE id = ?';
    logSqlStep('update_outlet', sql, [name, location, pricing_type, logo_url, address, gstin, state, phone, email, upi_id, req.params.id]);
    await pool.query(sql, [name, location, pricing_type, logo_url || null, address || null, gstin || null, state || null, phone || null, email || null, upi_id || null, req.params.id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE an outlet (Admin only)
app.delete('/api/outlets/:id', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  try {
    const sql = 'DELETE FROM outlets WHERE id = ?';
    logSqlStep('delete_outlet', sql, [req.params.id]);
    await pool.query(sql, [req.params.id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET all users (Admin only)
app.get('/api/admin/users', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  try {
    const [rows] = await pool.query(`
      SELECT u.id, u.name, u.email, u.role, u.outlet_id, o.name as outlet_name 
      FROM users u
      LEFT JOIN outlets o ON u.outlet_id = o.id
      ORDER BY u.id
    `);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST to register a new user (Admin only)
app.post('/api/admin/users', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  const { name, email, password, role, outlet_id } = req.body;
  if (!name || !email || !password) return res.status(400).json({ error: 'Name, email, and password are required' });
  try {
    const passwordHash = await bcrypt.hash(password, 10);
    const sql = 'INSERT INTO users (name, email, password_hash, role, outlet_id) VALUES (?, ?, ?, ?, ?)';
    logSqlStep('admin_create_user', sql, [name, email, role, outlet_id]);
    await pool.query(sql, [name, email, passwordHash, role || 'Store Staff', outlet_id || 1]);
    res.json({ success: true, message: 'User account created successfully!' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// PUT to edit user roles / outlets (Admin only)
app.put('/api/admin/users/:userId', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  const { role, outlet_id } = req.body;
  try {
    await pool.query("UPDATE users SET role = ?, outlet_id = ? WHERE id = ?", [role, outlet_id, req.params.userId]);
    res.json({ success: true, message: 'User details updated successfully!' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE a user account (Admin only)
app.delete('/api/admin/users/:userId', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') return res.status(403).json({ error: 'Admin role required' });
  try {
    await pool.query("DELETE FROM users WHERE id = ?", [req.params.userId]);
    res.json({ success: true, message: 'User account deleted successfully!' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/settings/database', authenticateToken, async (req, res) => {
  try {
    const configPath = path.join(__dirname, 'config.json');
    if (fs.existsSync(configPath)) {
      const raw = fs.readFileSync(configPath, 'utf-8');
      const config = JSON.parse(raw);
      return res.json({
        host: config.database?.host || 'localhost',
        port: config.database?.port || 3306,
        user: config.database?.user || 'root',
        password: config.database?.password || '',
        database: config.database?.database || 'ledgerpro'
      });
    }
    // Fallback default
    res.json({
      host: 'localhost',
      port: 3306,
      user: 'root',
      password: '',
      database: 'ledgerpro'
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/settings/database', authenticateToken, async (req, res) => {
  if (req.user.role !== 'Admin') {
    return res.status(403).json({ error: 'Admin role required' });
  }
  const { host, port, user, password, database } = req.body;
  try {
    const configPath = path.join(__dirname, 'config.json');
    let config = { database: { type: 'mysql' } };
    if (fs.existsSync(configPath)) {
      try {
        config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      } catch (e) {}
    }
    if (!config.database) {
      config.database = { type: 'mysql' };
    }
    config.database.host = host;
    config.database.port = parseInt(port) || 3306;
    config.database.user = user;
    config.database.password = password;
    config.database.database = database;

    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    res.json({ success: true, message: 'Database connection configuration saved. Please restart the backend server to apply changes.' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Server boot
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`LedgerPro REST API listening at http://localhost:${PORT}`);
});
