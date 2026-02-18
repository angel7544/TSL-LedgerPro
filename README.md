# LedgerPro Desktop Accounting Software

Professional accounting software built with Python and PySide6.

## Features
- **Dashboard**: Sales, Purchase, GST overview with charts.
- **Invoices**: Create GST compliant invoices with auto-numbering.
- **Stock Management**: FIFO based stock valuation.
- **Reports**: Sales, Purchase, GST, Outstanding reports.
- **PDF Generation**: Professional invoice PDFs.
- **Authentication**: Secure login/signup system.

## Setup
1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run
To start the application:
```bash
python main.py
```

## Structure
- `main.py`: Entry point.
- `database/`: Database schema and connection logic.
- `modules/`: Business logic (GST, Stock, Invoices).
- `ui/`: PySide6 UI components.
- `auth/`: Authentication logic and UI.
- `pdf/`: PDF generation logic.
