# LedgerPro Desktop - Codebase Analysis, System Improvements & Feature Roadmap

This document presents a comprehensive evaluation of **LedgerPro Desktop**, covering code health analysis, identified potential issues, architectural recommendations, proposed feature enhancements for **Staff**, **Managers**, and **Administrators**, and a detailed implementation specification for **Thermal Receipt Printer Support (80mm / 58mm POS Receipts)**.

---

## 1. Codebase Architecture & Code Health Analysis

### Current Architecture Strengths
- **Modular GUI Architecture**: Clean separation between PySide6 UI views (`ui/`), database engine abstraction (`database/`), business logic modules (`modules/`), and ReportLab PDF document generators (`pdf/`).
- **Cross-Database Abstraction Layer**: Unified query runner `execute_read_query()` and `execute_write_query()` supporting both local **SQLite (WAL mode)** and remote/network **MySQL** database engines.
- **FIFO Inventory Valuation Engine**: `modules/stock_fifo.py` accurately tracks inventory batches, COGS (Cost of Goods Sold), and batch deduction across invoices and purchase bills.
- **Role-Based Access Control (RBAC)**: Role checks (`Owner`, `Manager`, `Staff`) integrated into `auth/session.py` and `ui/main_window.py` for UI item filtering and feature restriction.

---

## 2. Identified Technical Issues & Code Health Improvements

### 1. Database Connection Pooling (MySQL)
- **Observation**: `get_connection()` in `database/db.py` creates a brand-new `pymysql.connect(...)` socket connection on every single query execution and closes it in a `finally:` block.
- **Impact**: On high-frequency operations or multi-user networks, repeated TCP handshake overhead slows down UI response time.
- **Recommendation**: Implement PyMySQL connection pooling using `dbutils.pooled_db` or a light persistent connection wrapper with auto-reconnect logic.

### 2. Main Thread UI Blocking on Heavy Queries / PDF Exports
- **Observation**: PDF generation (`pdf/generator.py`) and large report queries run synchronously on the main Qt GUI thread.
- **Impact**: UI can momentarily freeze during generation of multi-page PDFs or heavy annual GST reports.
- **Recommendation**: Wrap heavy ReportLab PDF rendering and Excel export functions in `QThread` or `QRunnable` worker threads with progress indicators.

### 3. Database Backup Functionality for MySQL
- **Observation**: `backup_db()` in `ui/settings.py` copies `database/ledgerpro.db` via `shutil.copy()`.
- **Impact**: While this works for SQLite, it does not backup remote MySQL database tables.
- **Recommendation**: Update `backup_db()` to check `is_mysql()` and trigger `mysqldump` or generate a serialized JSON/SQL dump of all tables when connected to MySQL.

### 4. Audit Trail & Activity Logging
- **Observation**: Changes to invoices, payments, vendor bills, and stock adjustments are modified directly without logging which user performed the action.
- **Impact**: Owners cannot trace who deleted an invoice, modified stock quantities, or recorded a payment.
- **Recommendation**: Add an `audit_logs` table tracking timestamp, user ID, user name, action type (`CREATE`, `UPDATE`, `DELETE`), module, and record ID.

---

## 3. Feature Suggestions for Users & Staff

### 1. Dedicated POS / Counter Billing Screen
- **Overview**: A streamlined, high-speed point-of-sale billing interface optimized for retail counters.
- **Key Features**:
  - Barcode scanner input field for instant item addition.
  - Keyboard shortcuts (`F2` to search items, `F4` to apply discount, `F12` to complete sale).
  - Quick Payment modal: Cash tendered vs Change due calculator.
  - One-click **Thermal POS Receipt Print**.

### 2. Dynamic UPI Payment QR Code Generation
- **Overview**: Generate a dynamic UPI payment QR code directly on invoices and receipts.
- **Details**: Using `qrcode` and `reportlab`, generate a QR code containing `upi://pay?pa=YOUR_UPI_ID&pn=COMPANY_NAME&am=TOTAL_AMOUNT&tn=INV_NUMBER`. Customers can scan with GPay, PhonePe, Paytm, or BHIM to pay instantly.

### 3. Quotations / Estimates & Proforma Invoices
- **Overview**: Create and send Quotations and Proforma Invoices to prospective clients.
- **Details**: Include a "Convert to Invoice" button that automatically creates a GST-compliant sales invoice and deducts stock without needing manual re-entry.

### 4. Bulk Stock Import & Item Barcode Label Printing
- **Overview**: Import items via CSV/Excel and print barcode labels.
- **Details**: Generate printable barcode label sheets (A4 grid or 50x25mm sticky labels) for item SKUs.

---

## 4. Feature Suggestions for Managers & Administrators

### 1. Audit Trail & Staff Activity Monitor (Admin Only)
- **Overview**: Detailed log of all user activities in the system.
- **Key Features**:
  - Filter logs by User, Action Type (`INSERT`, `UPDATE`, `DELETE`), Module, or Date range.
  - Shows before/after values for critical edits (e.g. price overrides, bill deletions).

### 2. Stock Reorder & Expiry Alert System
- **Overview**: Automated alert notifications when items fall below `reorder_point`.
- **Key Features**:
  - Visual notification badge on sidebar for items requiring stock replenishment.
  - One-click draft Purchase Order generation for low-stock vendors.

### 3. Customer & Vendor Credit Limit Control
- **Overview**: Set credit limits per customer account.
- **Key Features**:
  - Warns staff or blocks invoice creation if a customer's total outstanding balance exceeds their authorized credit limit.

### 4. GSTR-1 & GSTR-3B GST Filing Export Engine
- **Overview**: Export sales, purchases, HSN summary, and B2B/B2C GST tables in official Excel/JSON format for portal filing.

---

## 5. Thermal Receipt Printer Support (80mm / 58mm ESC/POS)

### 1. Specification & Architecture
Retail counters need fast receipt printing on standard thermal paper rolls:
- **80mm (3-inch / 48 columns)**: Standard POS width.
- **58mm (2-inch / 32 columns)**: Compact portable/Bluetooth thermal printer width.

### 2. Integration Approaches

#### Approach A: Direct ESC/POS Byte Stream (Fastest & Native)
Using `python-escpos` or native Windows raw printer API (`win32print`), send binary ESC/POS formatting commands directly to USB, Serial, Network (TCP/IP), or Bluetooth thermal printers.
- **Benefits**: Instant printing (less than 1 second), no print dialog popups, automatic paper cutter trigger (`ESC i` / `GS V`).

#### Approach B: ReportLab Thermal Page Sizing (PDF-Based)
Use ReportLab with custom page width (`80 * mm` or `58 * mm`) and dynamic height to render thermal receipts as PDF files, then send to system default printer via PySide `QPrinter` / `win32api`.

### 3. Thermal Receipt Layout Structure
```
========================================
             THE SPACE LABS             
      123 Business St, City, State      
         GSTIN: 27AAAAA0000A1Z5         
             Ph: +91 9876543210         
========================================
Receipt #: INV-2026-0042
Date: 2026-07-19 17:05    Cashier: Staff 1
Customer: Walk-in Customer
----------------------------------------
Item                 Qty   Rate   Amount
----------------------------------------
Wireless Mouse        2    450.00 900.00
Mechanical Keyboard   1   2500.00 2500.00
----------------------------------------
Subtotal:                       3400.00
GST (18%):                       612.00
Discount:                         12.00
----------------------------------------
GRAND TOTAL:                   ₹4000.00
----------------------------------------
Payment Method: CASH
Cash Received: ₹4000.00   Change: ₹0.00
----------------------------------------
       Scan to Pay via UPI (GPay/UPI)
             [ QR CODE IMAGE ]          
----------------------------------------
      Thank You for Shopping With Us!   
--------- Powered by LedgerPro POS -----
========================================
```

---

## 6. Suggested Implementation Action Plan

| Phase | Category | Task | Priority |
|---|---|---|---|
| **Phase 1** | **Core Fixes** | Implement MySQL Connection Pooling & Database Backup script for MySQL | High |
| **Phase 2** | **Hardware** | Add ESC/POS 80mm/58mm Thermal Printer Engine & Print Settings in Settings Page | High |
| **Phase 3** | **Audit & Security** | Add `audit_logs` table & Admin Activity Monitoring Screen | High |
| **Phase 4** | **Counter Billing** | Build Quick POS Counter Billing Screen with Barcode & UPI QR Code | Medium |
| **Phase 5** | **GST & Analytics**| GSTR-1 Excel/JSON Filing Export Engine & Reorder Point Alerts | Medium |
