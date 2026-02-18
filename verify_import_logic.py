import csv
import sys

filename = r"d:\TSL-ACCOUNTING_ELEC\ItemsSKU-HS.csv"

try:
    with open(filename, 'r', encoding='utf-8-sig') as f:
        # Robust delimiter detection logic from master_data.py
        first_line = f.readline()
        f.seek(0)
        
        delimiters = [',', '\t', ';', '|']
        counts = {d: first_line.count(d) for d in delimiters}
        best_delimiter = max(counts, key=counts.get)
        
        dialect = None
        if counts[best_delimiter] > 0:
            class SimpleDialect(csv.Dialect):
                delimiter = best_delimiter
                quotechar = '"'
                doublequote = True
                skipinitialspace = True
                lineterminator = '\r\n'
                quoting = csv.QUOTE_MINIMAL
            dialect = SimpleDialect
            print(f"Detected delimiter via counts: '{best_delimiter}'")
        else:
            try:
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample)
                print(f"Detected delimiter via Sniffer: '{dialect.delimiter}'")
            except csv.Error:
                dialect = csv.excel
                print("Defaulted to excel dialect")

        reader = csv.DictReader(f, dialect=dialect)
        
        print(f"Fieldnames: {reader.fieldnames}")
        
        # Test header resolution logic
        found_headers = [h.strip() for h in reader.fieldnames]
        
        def find_header(candidates):
            for c in candidates:
                for h in found_headers:
                    if h.lower() == c.lower():
                        return h
            return None

        key_mapping = {
            'name': ['Item Name', 'Name', 'Product Name'],
            'sku': ['SKU', 'Item Code'],
            'selling_price': ['Rate', 'Selling Price', 'Price'],
        }

        print("\nResolved Headers:")
        for key, candidates in key_mapping.items():
            print(f"{key}: {find_header(candidates)}")
            
except Exception as e:
    print(f"Error: {e}")
