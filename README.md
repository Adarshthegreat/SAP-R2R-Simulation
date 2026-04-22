# R2R Financial Close — SAP Capstone Project
### Certification: SAP Certified Associate – Data Analyst (C_BCBDC)

---

## 📌 Project Overview
An end-to-end **Record-to-Report (R2R)** financial close simulation built with Python and SQLite.
Covers the full accounting cycle — from journal entry posting through trial balance, P&L, and balance sheet generation — replicating SAP FI/CO month-end close processes in a lightweight, portable stack.

---

## 🔄 R2R Process Flow

| Step | Process | Description |
|------|---------|-------------|
| 1 | **GL Accounting** | Maintain chart of accounts; classify transactions as Asset, Liability, Equity, Revenue, Expense |
| 2 | **Journal Entries** | Post double-entry (debit = credit) transactions to the general ledger |
| 3 | **AP & AR** | Record vendor invoices (Accounts Payable) and customer invoices (Accounts Receivable) with payment tracking |
| 4 | **Depreciation** | Apply straight-line depreciation monthly to fixed assets; post to Depreciation Expense + Accum. Depreciation |
| 5 | **Accruals** | Recognize incurred-but-unpaid expenses via accrual JEs (Debit Expense / Credit Accrued Liability) |
| 6 | **Trial Balance** | Aggregate all GL debits and credits; verify Σ Debits = Σ Credits |
| 7 | **P&L Statement** | Compute Revenue − Expenses = Net Profit per month |
| 8 | **Balance Sheet** | Verify Assets = Liabilities + Equity (accounting equation) |
| 9 | **Month-End Close** | Consolidate all processes; export reports; confirm period is balanced and closed |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.8+ | Core scripting and data processing |
| SQLite | Lightweight relational database (no server required) |
| pandas | Data manipulation, SQL-to-DataFrame, CSV export |
| numpy | Numeric calculations |
| matplotlib | Charts and visualizations |

---

## 📁 Project Structure

```
r2r-financial-close/
├── data/                        # Auto-generated outputs
│   ├── r2r.db                   # SQLite database
│   ├── journal_entries.csv
│   ├── trial_balance.csv
│   ├── profit_loss.csv
│   ├── invoices_ap.csv
│   ├── invoices_ar.csv
│   ├── depreciation.csv
│   ├── assets.csv
│   ├── payments.csv
│   └── financial_charts.png     # Revenue vs Expenses + Profit Trend
├── src/
│   └── main.py                  # Single-file application
├── requirements.txt
└── README.md
```

---

## ⚙️ How to Run

```bash
# 1. Clone / unzip the project
cd r2r-financial-close

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the project
python src/main.py
```

All outputs are generated automatically in the `/data` folder.

---

## 📤 Output Files

| File | Description |
|------|-------------|
| `r2r.db` | Full SQLite database with all tables |
| `journal_entries.csv` | All GL postings (3 months) |
| `trial_balance.csv` | Aggregated debit/credit per account |
| `profit_loss.csv` | Monthly Revenue, Expenses, Net Profit |
| `invoices_ap.csv` | Vendor invoices |
| `invoices_ar.csv` | Customer invoices |
| `depreciation.csv` | Monthly depreciation schedule |
| `payments.csv` | AP and AR payment records |
| `financial_charts.png` | Bar + line chart visualization |

---

## 📊 Sample Results (Q1 2024)

```
PROFIT & LOSS STATEMENT
Month        Revenue       Expenses     Net Profit
2024-01    $85,000.00    $74,700.00    $10,300.00
2024-02    $92,000.00    $78,700.00    $13,300.00
2024-03   $103,000.00    $86,700.00    $16,300.00
──────────────────────────────────────────────────
TOTAL     $280,000.00   $240,100.00    $39,900.00

TRIAL BALANCE:  ✓ BALANCED  (Debits = Credits)
BALANCE SHEET:  ✓ BALANCED  (Assets = Liabilities + Equity)
Month-End Close: ✅ COMPLETE
```

---

## 🏗️ Database Schema (10 Tables)

`company_master` · `gl_accounts` · `journal_entries` · `vendors` · `customers`
`invoices_ap` · `invoices_ar` · `payments` · `assets` · `depreciation`

---

## 📚 SAP Relevance

| SAP Module | Simulated Concept |
|-----------|------------------|
| FI-GL | General Ledger, Chart of Accounts, Journal Entries |
| FI-AP | Vendor Invoice Management, Payment Processing |
| FI-AR | Customer Invoicing, Collections |
| FI-AA | Asset Accounting, Depreciation Runs |
| CO | Period-End Close, P&L Reporting |
| SAP Analytics Cloud | Replicated via pandas + matplotlib |

---

*Capstone Project · SAP C_BCBDC · Record-to-Report · Financial Close*
