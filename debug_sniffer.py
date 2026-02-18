import csv
import io

header = "Item ID\tItem Name\tSKU\tHSN/SAC\tDescription\tRate\tAccount\tAccount Code\tTaxable\tExemption Reason\tTaxability Type\tProduct Type\tIntra State Tax Name\tIntra State Tax Rate\tIntra State Tax Type\tInter State Tax Name\tInter State Tax Rate\tInter State Tax Type\tSource\tReference ID\tLast Sync Time\tStatus\tUsage unit\tUnit Name\tPurchase Rate\tPurchase Account\tPurchase Account Code\tPurchase Description\tInventory Account\tInventory Account Code\tInventory Valuation Method\tReorder Point\tVendor\tOpening Stock\tOpening Stock Value\tStock On Hand\tItem Type\tSellable\tPurchasable\tTrack Inventory"

print(f"Header length: {len(header)}")
print(f"Contains tabs: {'\t' in header}")
print(f"Contains commas: {',' in header}")

try:
    dialect = csv.Sniffer().sniff(header)
    print(f"Detected delimiter: '{dialect.delimiter}' (repr: {repr(dialect.delimiter)})")
except csv.Error as e:
    print(f"Sniffer error: {e}")

# Simulate what happened in the code
f = io.StringIO(header)
try:
    dialect = csv.Sniffer().sniff(header)
except csv.Error:
    dialect = csv.excel

reader = csv.DictReader(f, dialect=dialect)
print(f"Fieldnames: {reader.fieldnames}")
