# 📊 Ledger Pro - Views & Ledger System Documentation

This document explains all database **Views** and **Ledger System** used in Ledger Pro.

👉 It helps in:

* Reporting 📈
* Analytics 📊
* Accounting (Debit/Credit) 💰

---

# 🧠 What are Views?

### English:

Views are **virtual tables** created from SQL queries. They do not store data but show processed results.

### Hindi:

Views एक तरह की **virtual table** होती हैं जो query से data दिखाती हैं, खुद data store नहीं करती।

---

# 📊 1. Invoice Summary View

```sql
invoice_summary
```

### Purpose:

Shows invoice + customer details in one place.

### Use Case:

* Invoice list page
* Dashboard

👉 Hindi:
Invoice और customer data एक साथ दिखाने के लिए

---

# 💰 2. Customer Balance View

```sql
customer_balance
```

### Purpose:

Shows how much each customer owes.

### Formula:

```
Total Invoice - Total Payment
```

👉 Hindi:
कस्टमर ने कितना पैसा देना है (Outstanding Balance)

---

# 🧾 3. Invoice Details View

```sql
invoice_details
```

### Purpose:

Shows invoice items with product details.

### Use Case:

* Invoice detail page

👉 Hindi:
Invoice के अंदर कौन-कौन से items हैं

---

# 🏪 4. Vendor Summary View

```sql
vendor_summary
```

### Purpose:

Total purchases from each vendor.

👉 Hindi:
किस vendor से कितना खरीद हुआ

---

# 📦 5. Inventory Status View

```sql
inventory_status
```

### Purpose:

Shows stock + value of inventory.

### Formula:

```
stock_on_hand × purchase_price
```

👉 Hindi:
Stock की value calculate करने के लिए

---

# 💳 6. Payment History View

```sql
payment_history
```

### Purpose:

Shows all payments (customer + vendor)

👉 Hindi:
किसने कब payment किया

---

# 📊 7. Monthly Revenue View

```sql
monthly_revenue
```

### Purpose:

Shows month-wise sales revenue

👉 Hindi:
हर महीने की income दिखाता है

---

# 📈 8. Monthly Profit View

```sql
monthly_profit
```

### Purpose:

Shows profit calculation

### Formula:

```
Sales - Cost = Profit
```

👉 Hindi:
Profit निकालने के लिए

---

# 📒 Ledger System (Core Accounting)

## 🧠 What is Ledger?

### English:

Ledger records all financial transactions using **debit and credit system**

### Hindi:

Ledger हर transaction को debit/credit में track करता है

---

# 🧱 Ledger Table

```sql
ledger
```

### Columns:

| Column       | Meaning          |
| ------------ | ---------------- |
| date         | Transaction date |
| account_type | customer/vendor  |
| account_id   | ID reference     |
| debit        | Money coming     |
| credit       | Money going      |

👉 Hindi:

* Debit = पैसा आ रहा है
* Credit = पैसा जा रहा है

---

# 🔄 How Ledger Works

| Action           | Debit    | Credit   |
| ---------------- | -------- | -------- |
| Invoice          | Customer | Revenue  |
| Payment Received | Cash     | Customer |
| Purchase         | Expense  | Vendor   |

---

# ⚡ Triggers (Auto Ledger)

### English:

Triggers automatically insert data into ledger when:

* Invoice created
* Payment received
* Bill created

👉 No UI changes needed

---

### Hindi:

Trigger automatically ledger में entry डालते हैं जब:

* Invoice बनता है
* Payment होता है

👉 UI बदलने की जरूरत नहीं

---

# 👁️ Ledger Views

---

## 📘 Customer Ledger

```sql
customer_ledger
```

### Purpose:

Shows customer-wise transactions

👉 Hindi:
हर customer का हिसाब

---

## 🏪 Vendor Ledger

```sql
vendor_ledger
```

### Purpose:

Shows vendor transactions

👉 Hindi:
Vendor का पूरा हिसाब

---

## 📊 General Ledger View

```sql
ledger_view
```

### Purpose:

All transactions in one place

👉 Hindi:
सारे transactions एक जगह

---

# ⚠️ Important Notes

### English:

* Views do not store data
* Ledger works in background
* Triggers automate entries

### Hindi:

* Views data store नहीं करते
* Ledger background में चलता है
* Trigger auto काम करता है

---

# 🚀 Best Practices

✔ Keep schema clean
✔ Use views for reports
✔ Use ledger for accounting

👉 Hindi:

* Database clean रखें
* Views से report बनाएं

---

# 🔥 Final Result

After this system:

✅ Automated accounting
✅ Monthly reports
✅ Customer/vendor tracking
✅ Inventory insights

---

# 🙌 Conclusion

Ledger Pro now supports:

* Professional reporting 📊
* Accounting system 💰
* Scalable database 🚀

👉 Hindi:
अब आपका app professional accounting system बन चुका है

---

🔥 Happy Building - Ledger Pro
