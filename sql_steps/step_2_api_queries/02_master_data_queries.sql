-- ============================================================================
-- LedgerPro - Step 2 API Queries: Master Data (Customers, Vendors, Items)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CUSTOMERS
-- ----------------------------------------------------------------------------

-- Fetch all customers
SELECT id, name, email, phone, address, gstin, state, customer_type, created_at 
FROM customers 
ORDER BY name ASC;

-- Fetch customer by ID
SELECT id, name, email, phone, address, gstin, state, customer_type 
FROM customers 
WHERE id = ?;

-- Search customers by keyword
SELECT id, name, email, phone, gstin 
FROM customers 
WHERE name LIKE ? OR phone LIKE ? OR gstin LIKE ?;

-- Create customer
INSERT INTO customers (name, email, phone, address, gstin, state, customer_type) 
VALUES (?, ?, ?, ?, ?, ?, ?);

-- Update customer
UPDATE customers 
SET name = ?, email = ?, phone = ?, address = ?, gstin = ?, state = ?, customer_type = ? 
WHERE id = ?;

-- Delete customer
DELETE FROM customers 
WHERE id = ?;

-- ----------------------------------------------------------------------------
-- VENDORS
-- ----------------------------------------------------------------------------

-- Fetch all vendors
SELECT id, name, email, phone, address, gstin, state, created_at 
FROM vendors 
ORDER BY name ASC;

-- Fetch vendor by ID
SELECT id, name, email, phone, address, gstin, state 
FROM vendors 
WHERE id = ?;

-- Search vendors
SELECT id, name, email, phone, gstin 
FROM vendors 
WHERE name LIKE ? OR phone LIKE ? OR gstin LIKE ?;

-- Create vendor
INSERT INTO vendors (name, email, phone, address, gstin, state) 
VALUES (?, ?, ?, ?, ?, ?);

-- Update vendor
UPDATE vendors 
SET name = ?, email = ?, phone = ?, address = ?, gstin = ?, state = ? 
WHERE id = ?;

-- Delete vendor
DELETE FROM vendors 
WHERE id = ?;

-- ----------------------------------------------------------------------------
-- ITEMS MASTER
-- ----------------------------------------------------------------------------

-- Fetch all catalog items
SELECT id, name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, 
       purchase_price, reorder_point, stock_on_hand, opening_stock, opening_stock_value, 
       item_type, is_sellable, is_purchasable, track_inventory, vendor_id 
FROM items 
ORDER BY name ASC;

-- Fetch item by ID
SELECT * FROM items WHERE id = ?;

-- Search item by SKU or barcode
SELECT * FROM items WHERE sku = ?;

-- Create catalog item
INSERT INTO items (
    name, sku, hsn_sac, gst_rate, description, unit, selling_price, sp1, sp2, sp3, 
    purchase_price, reorder_point, stock_on_hand, opening_stock, opening_stock_value, 
    account_code, purchase_account_code, inventory_account_code, taxable, exemption_reason, 
    taxability_type, product_type, intra_state_tax_rate, inter_state_tax_rate, purchase_description, 
    inventory_valuation_method, item_type, is_sellable, is_purchasable, track_inventory, vendor_id
) VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, 
    ?, ?, ?, ?, ?, ?
);

-- Update catalog item
UPDATE items SET 
    name = ?, sku = ?, hsn_sac = ?, gst_rate = ?, description = ?, unit = ?, 
    selling_price = ?, sp1 = ?, sp2 = ?, sp3 = ?, purchase_price = ?, reorder_point = ?, 
    stock_on_hand = ?, item_type = ?, is_sellable = ?, is_purchasable = ?, track_inventory = ?, vendor_id = ? 
WHERE id = ?;

-- Delete catalog item
DELETE FROM items WHERE id = ?;
