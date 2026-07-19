# 🚀 LedgerPro - Database Setup & Execution Guide (`sql_steps`)

This document provides a step-by-step instructions for initializing, configuring, and seeding the database for **LedgerPro Desktop Application** using both **SQLite** and **MySQL** database engines.

---

## 📋 Overview of `sql_steps` Directory

The `sql_steps` directory contains modular, executable SQL scripts organized into sequential steps:

| Step Directory | Description | Primary SQL Files |
|---|---|---|
| **`step_1_schema/`** | Core DDL table definitions, Views & B-Tree Indexes (Migration v8) | `01_sqlite_schema.sql`, `02_mysql_schema.sql`, `03_sqlite_views.sql`, `04_mysql_views.sql` |
| **`step_2_api_queries/`** | Categorized CRUD & single-query FIFO aggregated queries | `01_auth...`, `02_master_data...`, `03_inventory...`, `04_sales...`, `05_purchases...`, `06_payments...`, `07_reports...`, `08_settings...` |
| **`step_3_org_roles_schema/`** | Role-Based Access Control (RBAC) & Multi-Org schema | `01_org_and_roles_schema.sql` |
| **`step_4_recreate_db/`** | Full drop & recreate scripts for fresh resets | `01_recreate_sqlite_db.sql`, `02_recreate_mysql_db.sql` |
| **`step_5_seed_admin/`** | Seed script for primary Admin account | `01_seed_admin_user.sql` |
| **`step_6_seed_admin_with_org/`** | Full organization seed dataset with sample transactions | `01_seed_admin_with_org_data.sql` |

---

## 🛠️ Step-by-Step Setup Instructions

### Option A: Automatic Setup (Recommended for Python App)

The LedgerPro application handles database initialization and schema migration automatically on startup.

1. Ensure python dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the main application:
   ```bash
   python main.py
   ```
   *The application will automatically detect missing tables, create SQLite schemas, apply migrations (v1 to v8 including B-tree performance indexes), and initialize the default database.*

---

### Option B: Manual Setup via SQLite CLI

If you want to manually create or reset the local SQLite database (`database/ledgerpro.db`):

```bash
# Navigate to workspace root
cd d:\TSL_LEDGER_PRO

# 1. Apply SQLite Base Schemas (Step 1)
sqlite3 database/ledgerpro.db < sql_steps/step_1_schema/01_sqlite_schema.sql

# 2. Apply SQLite Database Views (Step 1)
sqlite3 database/ledgerpro.db < sql_steps/step_1_schema/03_sqlite_views.sql

# 3. Seed Admin User & Company Settings (Step 5)
sqlite3 database/ledgerpro.db < sql_steps/step_5_seed_admin/01_seed_admin_user.sql

# 4. (Optional) Seed Sample Organization Dataset (Step 6)
sqlite3 database/ledgerpro.db < sql_steps/step_6_seed_admin_with_org/01_seed_admin_with_org_data.sql
```

---

### Option C: Manual Setup via MySQL Server

To run LedgerPro on a remote or network MySQL server:

#### 1. Interactive Python Helper (Easiest)
Run the interactive MySQL configuration script:
```bash
python mysql_setup.py
```
Follow the prompts to enter Host, Port, MySQL User, Password, and Database Name (`ledgerpro`).

#### 2. Manual MySQL CLI Execution
```bash
# Create Database & Schemas
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS ledgerpro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Execute MySQL Schema & Views
mysql -u root -p ledgerpro < sql_steps/step_1_schema/02_mysql_schema.sql
mysql -u root -p ledgerpro < sql_steps/step_1_schema/04_mysql_views.sql

# Seed Admin User & Organization Data
mysql -u root -p ledgerpro < sql_steps/step_6_seed_admin_with_org/01_seed_admin_with_org_data.sql
```

#### 3. Update `config.json` for MySQL
Ensure `config.json` in the root directory contains the MySQL backend credentials:
```json
{
  "database": {
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "ledgerpro"
  }
}
```

---

## 🔑 Default Credentials

After running Step 5 or Step 6 seed scripts, log in with the following credentials:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Owner / Admin** | `admin@br31tech.live` | `admin123` | Full Access (Settings, Users, Audit Logs, Reports) |
| **Owner (Org Seed)** | `owner@br31tech.live` | `admin123` | Full Administrative Rights |
| **Store Manager** | `manager@br31tech.live` | `admin123` | Inventory, Bills, Invoices, Master Data |
| **Billing Staff** | `staff@br31tech.live` | `admin123` | Counter POS Billing & Receipt Printing |

---

## 🔄 Recreating / Resetting Database (Fresh Start)

To completely reset the database to a clean state:

- **For SQLite**:
  ```bash
  sqlite3 database/ledgerpro.db < sql_steps/step_4_recreate_db/01_recreate_sqlite_db.sql
  python create_admin.py
  ```
- **For MySQL**:
  ```bash
  mysql -u root -p < sql_steps/step_4_recreate_db/02_recreate_mysql_db.sql
  python create_admin.py
  ```

---

## ✅ Pre-flight Checklist Before Launching Application

Before launching `python main.py`:
- [x] Verified `sql_steps/` files exist.
- [x] Configured database engine (`sqlite` or `mysql`) in `config.json`.
- [x] Applied Table Schemas & Database Views (`step_1_schema`).
- [x] Seeded Administrator account (`create_admin.py` or `step_5_seed_admin`).
- [x] Verified PySide6 and PyMySQL Python dependencies (`requirements.txt`).

Happy LedgerPro Building! 🚀
