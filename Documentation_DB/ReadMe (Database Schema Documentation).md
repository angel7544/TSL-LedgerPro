# 🧱 Ledger Pro - Database Schema Documentation

This document explains the complete database structure of **Ledger Pro Desktop Application**.

---

# 🚀 Overview

### English:

Ledger Pro is a **complete accounting and inventory management system** that handles:

* Customers & Vendors 👥
* Sales & Purchases 🧾
* Inventory Management 📦
* Payments 💳
* Ledger & Accounting 💰

---

### Hindi:

Ledger Pro एक **complete accounting और inventory system** है जो handle करता है:

* Customers और Vendors
* Sales (Invoices) और Purchases (Bills)
* Stock / Inventory
* Payments
* Ledger system

---

# 🧩 Core Modules

---

## 👥 1. Users

```sql
users
```

### Purpose:

Stores application users (login system)

👉 Hindi:
App users (login करने वाले लोग)

---

## 🧍 2. Customers

```sql
customers
```

### Purpose:

Stores customer details

* Name, GSTIN, State
* Contact info

👉 Hindi:
Customer की पूरी जानकारी

---

## 🏪 3. Vendors

```sql
vendors
```

### Purpose:

Stores supplier/vendor data

👉 Hindi:
Supplier / vendor details

---

## 📦 4. Items (Inventory)

```sql
items
```

### Purpose:

Central inventory table

Includes:

* SKU
* Prices (Selling/Purchase)
* GST
* Stock

👉 Hindi:
सारे products / items यहीं store होते हैं

---

## 📊 5. Stock Batches (FIFO System)

```sql
stock_batches
```

### Purpose:

Tracks stock purchase batches

👉 Used for:

* FIFO (First In First Out)

👉 Hindi:
Stock को batch-wise track करता है

---

## 🧾 6. Invoices (Sales)

```sql
invoices
```

### Purpose:

Stores sales transactions

👉 Includes:

* Customer
* Total amount
* Tax, discount

👉 Hindi:
Sales bill (invoice)

---

## 🧾 7. Invoice Items

```sql
invoice_items
```

### Purpose:

Stores items inside each invoice

👉 Hindi:
Invoice के अंदर items

---

## 🏪 8. Bills (Purchases)

```sql
bills
```

### Purpose:

Stores purchase transactions

👉 Hindi:
Purchase bill

---

## 🧾 9. Bill Items

```sql
bill_items
```

### Purpose:

Stores items inside purchase bills

👉 Hindi:
Purchase items

---

## 💳 10. Payments

```sql
payments
```

### Purpose:

Tracks all incoming & outgoing payments

👉 Linked to:

* Invoices
* Bills
* Customers
* Vendors

👉 Hindi:
Payments (incoming + outgoing)

---

## ⚙️ 11. Settings

```sql
settings
```

### Purpose:

Stores system configuration

👉 Hindi:
App settings

---

# 📒 12. Ledger System (Advanced Accounting)

```sql
ledger
```

### Purpose:

Tracks all transactions in debit/credit format

---

### English:

* Debit = Money received
* Credit = Money paid

---

### Hindi:

* Debit = पैसा आया
* Credit = पैसा गया

---

# 🔄 Data Flow (How System Works)

---

## 🧾 Sales Flow

```text
Customer → Invoice → Invoice Items → Payment → Ledger
```

👉 Hindi:
Customer → Invoice → Payment → Ledger entry

---

## 🏪 Purchase Flow

```text
Vendor → Bill → Bill Items → Payment → Ledger
```

👉 Hindi:
Vendor → Purchase → Payment → Ledger

---

## 📦 Inventory Flow

```text
Items → Stock Batches → Invoice/Bill → Stock Update
```

👉 Hindi:
Item → Stock → Sale/Purchase → Stock update

---

# 🔗 Relationships (Important)

* customers → invoices
* vendors → bills
* invoices → invoice_items
* bills → bill_items
* items → all transactions
* payments → invoices/bills

👉 Hindi:
सभी tables आपस में linked हैं

---

# ⚡ Key Features of Schema

### English:

* Fully normalized database
* Supports GST system
* Inventory tracking (FIFO)
* Scalable for large data
* Supports accounting (ledger)

---

### Hindi:

* Clean database design
* GST ready
* Stock tracking system
* Accounting support

---

# 📊 What This Schema Enables

### ✔ Business Features:

* Create invoices & bills
* Track stock in real-time
* Manage customers/vendors
* Record payments
* Generate reports

---

### ✔ Accounting Features:

* Customer balance
* Vendor balance
* Profit calculation
* Ledger tracking

---

# 🔥 Summary (Simple Explanation)

### English:

This schema represents a **mini accounting software (like Tally/Zoho Books)** with inventory + billing + payment + ledger system.

---

### Hindi:

यह schema एक **complete accounting software** जैसा है जिसमें:

* Billing
* Stock
* Payment
* Ledger

सब कुछ integrated है

---

# 🚀 Final Result

After implementation:

✅ Full accounting system
✅ Inventory management
✅ Financial tracking
✅ Business analytics

---

# 🙌 Conclusion

Ledger Pro database is designed to be:

* Scalable 🚀
* Maintainable 🧩
* Production-ready 🔥

---

🔥 Built for real-world business use
