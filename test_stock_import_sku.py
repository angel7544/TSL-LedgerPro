
import csv
import io
from datetime import datetime

# Mock functions
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# Mock DB
items_db = {
    1: {'id': 1, 'name': 'Item A', 'sku': 'SKU-A', 'stock_on_hand': 10, 'purchase_price': 100.0},
    2: {'id': 2, 'name': 'Item B', 'sku': 'SKU-B', 'stock_on_hand': 5, 'purchase_price': 50.0},
    3: {'id': 3, 'name': 'Item C', 'sku': 'SKU-C', 'stock_on_hand': 0, 'purchase_price': 20.0},
}

stock_batches = []

def execute_read_query(query, params):
    val = params[0]
    result = []
    if "sku = ?" in query:
        for item in items_db.values():
            if item.get('sku') == val:
                result.append(item)
    elif "name = ?" in query:
        for item in items_db.values():
            if item['name'] == val:
                result.append(item)
    return result

def add_stock(item_id, quantity, rate, date):
    print(f"Adding stock: Item {item_id}, Qty {quantity}, Rate {rate}, Date {date}")
    items_db[item_id]['stock_on_hand'] += quantity

def reduce_stock_fifo(item_id, quantity):
    print(f"Reducing stock: Item {item_id}, Qty {quantity}")
    items_db[item_id]['stock_on_hand'] -= quantity

# Mock CSV Content
csv_content = """Item Name,SKU,Stock On Hand
,SKU-A,15
Item B,,2
Item X,SKU-C, 
Item D,SKU-D,10
"""

def test_import():
    f = io.StringIO(csv_content)
    
    # Delimiter detection
    first_line = f.readline()
    f.seek(0)
    delimiters = [',', '\t', ';', '|']
    counts = {d: first_line.count(d) for d in delimiters}
    best_delimiter = max(counts, key=counts.get)
    print(f"Detected delimiter: '{best_delimiter}'")
    
    reader = csv.DictReader(f, delimiter=best_delimiter)
    
    found_headers = [h.strip() for h in reader.fieldnames]
    print(f"Headers: {found_headers}")
    
    def find_header(candidates):
        for c in candidates:
            for h in found_headers:
                if h.lower() == c.lower():
                    return h
        return None

    name_col = find_header(['Item Name', 'Name', 'Product Name'])
    sku_col = find_header(['SKU', 'Item SKU', 'Product Code'])
    stock_col = find_header(['Stock On Hand', 'Qty', 'Quantity', 'Stock'])
    
    print(f"Name Col: {name_col}, SKU Col: {sku_col}, Stock Col: {stock_col}")

    for row_idx, row in enumerate(reader, start=1):
        clean_row = {k.strip(): v for k, v in row.items() if k}
        
        item_name = clean_row.get(name_col, '').strip() if name_col else ''
        item_sku = clean_row.get(sku_col, '').strip() if sku_col else ''
        
        if not item_name and not item_sku:
            continue
            
        identifier = item_sku if item_sku else item_name
        print(f"Processing row {row_idx}: {identifier}")

        try:
            qty_str = clean_row.get(stock_col, '')
            if not qty_str or not str(qty_str).strip():
                print("  Skipping empty stock")
                continue 
            
            new_qty = float(str(qty_str).replace(',', '').strip())
            print(f"  New Qty: {new_qty}")
            
            # Find Item
            items = []
            if item_sku:
                print(f"  Looking up by SKU: {item_sku}")
                items = execute_read_query("SELECT id, stock_on_hand, purchase_price FROM items WHERE sku = ?", (item_sku,))
            
            if not items and item_name:
                print(f"  Looking up by Name: {item_name}")
                items = execute_read_query("SELECT id, stock_on_hand, purchase_price FROM items WHERE name = ?", (item_name,))
                
            if not items:
                print(f"  Error: Item not found: {identifier}")
                continue
                
            item = items[0]
            item_id = item['id']
            current_qty = item['stock_on_hand']
            purchase_price = item['purchase_price']
            
            print(f"  Found Item: {item['name']} (ID: {item_id}), Current Qty: {current_qty}")
            
            if new_qty > current_qty:
                diff = new_qty - current_qty
                add_stock(item_id, diff, purchase_price, get_current_date())
            elif new_qty < current_qty:
                diff = current_qty - new_qty
                reduce_stock_fifo(item_id, diff)
            else:
                print("  No change")
                
        except Exception as e:
            print(f"  Error: {e}")

test_import()
