# 📦 Ledger Pro - Stock Import Guide (CSV / Excel)

This guide helps you import stock/items into Ledger Pro using CSV or Excel.

---

## 🚀 Supported File Format

You can upload:

* `.csv` ✅ (Recommended)
* `.xlsx` ✅

---

## 📊 Required Columns (Simple Format)

Use this format for uploading stock:

```csv
name,sku,gst_rate,selling_price,purchase_price,stock_on_hand,unit
```

### 📌 Example:

```csv
Laptop Dell,SKU001,18,50000,40000,10,pcs
Mouse Logitech,SKU002,18,500,300,50,pcs
Office Chair,SKU003,12,3000,2000,25,pcs
```

---

## 🧠 Column Explanation (English + Hindi)

| Column         | Meaning (English)   | मतलब (Hindi)         |
| -------------- | ------------------- | -------------------- |
| name           | Item/Product name   | प्रोडक्ट का नाम      |
| sku            | Unique product code | यूनिक कोड            |
| gst_rate       | GST %               | GST प्रतिशत          |
| selling_price  | Selling price       | बेचने की कीमत        |
| purchase_price | Purchase price      | खरीदने की कीमत       |
| stock_on_hand  | Available stock     | उपलब्ध स्टॉक         |
| unit           | pcs/kg/ltr etc      | यूनिट (जैसे pcs, kg) |

---

## ⚠️ Important Things to Check

### 1️⃣ Vendor ID (Advanced Use)

* Must match existing vendor in database
* Example: `vendor_id = 1`

👉 Hindi:
Vendor ID database में पहले से होना चाहिए

---

### 2️⃣ Taxable Field

```text
1 = Yes (Taxable)
0 = No (Non-taxable)
```

👉 Hindi:

* 1 = टैक्स लगेगा
* 0 = टैक्स नहीं लगेगा

---

### 3️⃣ Item Type

```text
Goods / Service
```

👉 Hindi:

* Goods = सामान
* Service = सेवा

---

## 🎯 Recommended Approach (Best Practice)

👉 Use only simple format:

```csv
name,sku,gst_rate,selling_price,purchase_price,stock_on_hand,unit
```

✔ Easy for users
✔ Less errors
✔ Faster import

👉 Hindi:

* कम कॉलम = कम गलती
* यूजर के लिए आसान

---

## 🔄 Backend Mapping (For Developers)

Internally, system maps extra fields like:

* account_code
* inventory_account_code
* taxable
* item_type

👉 Users don’t need to fill these manually.

👉 Hindi:
ये सभी fields backend में automatically handle होते हैं

---

## ⚡ Import Query (Optional - Advanced)

```sql
LOAD DATA INFILE 'C:/stocks.csv'
INTO TABLE items
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

👉 Hindi:
यह query direct CSV को database में डालने के लिए है

---

## ❗ Common Mistakes

❌ Duplicate SKU
❌ Missing required fields
❌ Wrong GST format
❌ Empty file

👉 Hindi:

* SKU duplicate नहीं होना चाहिए
* जरूरी कॉलम खाली नहीं होना चाहिए

---

## 💡 Tips

✔ Keep file clean
✔ Use correct format
✔ Validate before upload

👉 Hindi:

* फाइल साफ रखें
* सही format use करें

---

## 🚀 Final Note

This system is designed to:

* Simplify stock import
* Reduce manual entry
* Improve accuracy

👉 Hindi:
यह system stock management को आसान और fast बनाता है

---

🔥 Happy Accounting with Ledger Pro
