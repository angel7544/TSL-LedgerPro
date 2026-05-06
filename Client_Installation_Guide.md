# LedgerPro Desktop - Client Installation & Configuration Guide

Welcome to **LedgerPro Desktop**! This guide will walk you through the process of installing, configuring, and running the application on your Windows machine.

---

## 1. System Requirements

- **Operating System:** Windows 10 or Windows 11 (64-bit recommended)
- **Disk Space:** At least 200 MB of free space
- **Memory (RAM):** Minimum 4 GB (8 GB recommended for large data sets)
- **Database:** Local SQLite (built-in) OR MySQL Server (optional, for multi-user networking)

---

## 2. Installation Steps

LedgerPro Desktop does not require a complex installation process. It is provided as a standalone executable.

1. **Download/Receive the Application:**
   Extract the provided `LedgerProDesktop` `.zip` folder to your desired location (e.g., `C:\LedgerProDesktop` or your Desktop).

2. **Run the Application:**
   Inside the extracted folder, locate the `LedgerProDesktop.exe` file.
   - *Tip:* You can right-click `LedgerProDesktop.exe` and select **Send to > Desktop (create shortcut)** for easy access.

3. **First Run Initialization:**
   Double-click the executable to start the application. On its first run, LedgerPro Desktop will automatically initialize the local SQLite database and required data files. You will see a splash screen showing the loading progress.

---

## 3. Database Configuration

LedgerPro Desktop supports two database modes: **SQLite** (default, offline) and **MySQL** (remote/networked).

### Option A: Local SQLite (Default)
By default, the application is pre-configured to use SQLite. No further configuration is needed. The database file (`ledgerpro.db`) will be securely stored within the application's internal data directory automatically.

### Option B: MySQL (Networked / Multi-User / Cloud)
If you wish to use a centralized MySQL server to sync data across multiple computers (either on a local network or via a cloud server over the internet):
1. Locate the `config.json` file in the same directory as your executable.
2. Open `config.json` with a text editor (like Notepad).
3. Update the database credentials to match your MySQL server:
   ```json
   {
       "database": {
           "type": "mysql",
           "host": "your.cloud.database.ip_or_domain", // Cloud IP, domain, or "localhost"
           "port": 3306,
           "user": "root",            // Your MySQL username
           "password": "yourpassword",// Your MySQL password
           "database": "ledgerpro"
       }
   }
   ```
4. **Note:** The application fully supports remote MySQL connections over the internet (e.g., AWS, Hostinger, DigitalOcean, etc.). Ensure that your MySQL server is running, allows remote remote connections from your IP, and the database `ledgerpro` has been created. The schema will be automatically initialized when you run the application or setup script.

---

## 4. Initial Login & Account Setup

1. **Sign Up / Admin Creation:**
   When the Login Screen appears for the first time, click on the **Sign Up** button to create your initial administrator account.
   
2. **Alternatively (Pre-configured Admin):**
   If an administrator account has already been provided to you by your IT provider, use those credentials to log in (e.g., `admin@br31tech.live` / `admin123`).

3. **Login:**
   Enter your email and password, then click **Login** to access the main dashboard.

---

## 5. Post-Installation & Next Steps

Once you are logged into LedgerPro Desktop, you can begin configuring your accounting and inventory data.

### Reference Documentation
For advanced setup, please refer to the additional documentation provided in the `Documentation_DB` folder:

- **[Stock Import Guide]**: Learn how to easily bulk-import your existing inventory via CSV/Excel using `ReadMe (Stock Import Guide (CSV_Excel)).md`.
- **[Database Schema]**: For advanced IT users who wish to integrate or backup the database, refer to `ReadMe (Database Schema Documentation).md`.
- **[Ledger & Views]**: To understand how the accounting, outstanding balances, and views work, read `ReadMe (Views & Ledger System Documentation).md`.

### Adding Your First Items
1. Navigate to the **Items** section.
2. Click **Import CSV** to upload your bulk items (refer to the Stock Import Guide for the correct format).
3. Set your custom pricing tiers (SP1, SP2, SP3) and GST rates.

**Need Help?**
If you encounter any issues during installation or setup, please contact technical support at **support@br31tech.live**.
