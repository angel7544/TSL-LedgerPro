# LedgerPro Desktop - Codebase Architecture, System Improvements & Technical Roadmap (MySQL Edition)

This document presents an engineering evaluation, architectural roadmap, and technical improvement specification for **LedgerPro Desktop Application** built with **Python (PySide6)** and backed by an enterprise **MySQL Database Engine**.

---

## 🏗️ System Architecture & Data Pipeline (MySQL Engine)

LedgerPro is structured into a clean multi-layer desktop architecture. The PySide6 Qt GUI communicates with pure-Python business logic services, which query the central **MySQL Database** via PyMySQL.

```mermaid
graph TD
    subgraph View Layer ["PySide6 Qt GUI Thread"]
        V_Dash["Dashboard Screen"]
        V_POS["Counter POS Screen"]
        V_Inv["Sales Invoicing"]
        V_Stock["FIFO Inventory"]
        V_Audit["Admin Audit Monitor"]
    end

    subgraph Service Layer ["Python Business Logic Services"]
        S_FIFO["stock_fifo.py (FIFO Cost Engine)"]
        S_Inv["invoice.py (GST Tax Calculation)"]
        S_Auth["auth_logic.py (RBAC & Audit Logging)"]
        S_PDF["pdf/generator.py & thermal_generator.py"]
    end

    subgraph Database Layer ["MySQL Database Infrastructure"]
        DB_Conn["database/db.py (PyMySQL Connection Manager & Query Translator)"]
        DB_Pool["PyMySQL Connection Pool"]
        DB_MySQL[("MySQL Server (Tables & Database Views)")]
    end

    V_Dash --> S_FIFO
    V_POS --> S_Inv
    V_Inv --> S_Inv
    V_Stock --> S_FIFO
    V_Audit --> S_Auth

    S_FIFO --> DB_Conn
    S_Inv --> DB_Conn
    S_Auth --> DB_Conn
    S_PDF --> DB_Conn

    DB_Conn --> DB_Pool
    DB_Pool -->|"TCP/IP Socket"| DB_MySQL
```

---

## 1. Technical Audit & Code Health Improvements (MySQL Focus)

### 1. Database Connection Pooling for MySQL
- **Current Observation**: `get_connection()` in `database/db.py` creates a new `pymysql.connect(...)` socket connection on every query call and closes it in a `finally:` block.
- **Performance Impact**: Repeated TCP socket initialization on high-frequency transactions introduces latency, particularly over network connections.
- **Architectural Solution**: Implement connection pooling using `dbutils.pooled_db` or a thread-safe connection wrapper to reuse active MySQL connections.

```mermaid
graph LR
    subgraph NonPooled ["Current Behavior (Socket Overhead)"]
        A1["Query Request"] --> A2["Open MySQL Socket"]
        A2 --> A3["Execute Query"]
        A3 --> A4["Close Socket"]
    end

    subgraph Pooled ["Recommended Connection Pool"]
        B1["Query Request"] --> B2["Borrow Connection from Pool"]
        B2 --> B3["Execute Query"]
        B3 --> B4["Return Connection to Pool"]
    end
```

---

### 2. Main Thread UI Responsive Execution
- **Current Observation**: Heavy queries (such as annual GST summaries or ReportLab multi-page PDF rendering) run on the main Qt GUI thread.
- **Solution**: Execute PDF generation and heavy report queries inside `QThread` / `QRunnable` worker pools to keep the PySide6 UI smooth and responsive.

---

### 3. Automated MySQL Database Backup Engine
- **Current Observation**: Legacy backup function performed local file copy of SQLite databases.
- **Solution**: Update `ui/settings.py` backup routine to execute `mysqldump` commands or export serialized JSON database snapshots when connected to MySQL.

---

### 4. Audit Trail & Staff Activity Tracking (`audit_logs`)
- **Current Structure**: System actions (creating invoices, editing stock levels, deleting records, logging in) are executed without user attribution.
- **Solution**: Enforce automated logging via `log_audit_action()` into the `audit_logs` MySQL table:
  - Fields: `id`, `user_id`, `user_name`, `action`, `module`, `record_id`, `details`, `timestamp`.

---

## 2. Feature Improvements for Staff & POS Billing

### 1. Dedicated POS / Counter Billing Screen
- Barcode scanner input field for fast item lookups (`F2` shortcut).
- Instant cash tendered vs change due calculator.
- One-click **Thermal POS Receipt Printing**.

### 2. ESC/POS Thermal Receipt Printer Pipeline (80mm / 58mm)

```mermaid
graph LR
    POS_UI["POS Billing View (F12 Complete Sale)"] --> Data_Prep["Prepare Transaction Data & Item List"]
    Data_Prep --> ESC_Build["Format ESC/POS Commands (Center Header, Column Alignment, Cut Command)"]
    ESC_Build --> Driver_Choice{"Printer Connection Type"}
    Driver_Choice -->|"Direct USB / COM"| ESC_Raw["Send Binary Bytes via python-escpos / win32print"]
    Driver_Choice -->|"PDF Thermal"| ESC_PDF["Render 80mm/58mm PDF via ReportLab"]
    ESC_Raw --> Thermal_Print["Thermal Paper Output & Auto Paper Cut"]
    ESC_PDF --> Thermal_Print
```

---

### 3. Dynamic UPI Payment QR Code Generation
- Embed dynamic UPI QR code (`upi://pay?pa=YOUR_UPI_ID&pn=COMPANY_NAME&am=AMOUNT`) on invoices and POS receipts using `qrcode` and `ReportLab`. Customers scan via Google Pay, PhonePe, Paytm, or BHIM.

---

## 3. Feature Improvements for Managers & Administrators

### 1. Audit Trail & Activity Monitor (Admin View)
- Filterable activity table showing user actions (`INSERT`, `UPDATE`, `DELETE`), module, date ranges, and record IDs.

### 2. Customer Credit Limit Control
- Set authorized credit limits per customer profile. Warn or block invoice creation if customer balance exceeds authorized credit limits.

### 3. GSTR-1 & GSTR-3B Filing Export Engine
- Export B2B, B2C, HSN summary, and input tax tables in Excel/JSON format for portal GST filing.

---

## 4. Implementation Action Plan Roadmap

```mermaid
graph TD
    Phase1["Phase 1: Core MySQL Fixes\nMySQL Connection Pooling & Mysqldump Backup Engine"] --> Phase2["Phase 2: Hardware & POS\nESC/POS 80mm/58mm Thermal Receipt Generator"]
    Phase2 --> Phase3["Phase 3: Security & Audit\nAudit Logs Table & Admin User Activity Monitor"]
    Phase3 --> Phase4["Phase 4: Counter Billing\nQuick POS Counter Screen & Dynamic UPI QR Code"]
    Phase4 --> Phase5["Phase 5: Compliance & Analytics\nGSTR-1 Filing Export Engine & Reorder Point Alerts"]
```

| Phase | Milestone | Deliverable | Priority |
|---|---|---|---|
| **Phase 1** | Core Infrastructure | MySQL Connection Pooling & `mysqldump` Backup Integration | **High** |
| **Phase 2** | POS Hardware | ESC/POS 80mm / 58mm Thermal Printer Engine & Setup UI | **High** |
| **Phase 3** | Security & Audit | `audit_logs` MySQL Table & Admin Monitoring Screen | **High** |
| **Phase 4** | Counter POS | High-Speed POS Screen & Dynamic UPI QR Code Generation | **Medium** |
| **Phase 5** | GST Compliance | GSTR-1 Excel/JSON Export Engine & Stock Reorder Alerts | **Medium** |
