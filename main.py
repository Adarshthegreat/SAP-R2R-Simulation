"""
R2R Financial Close - SAP Capstone Project (C_BCBDC)
Record-to-Report: GL Accounting, JE, AP/AR, Depreciation, Accruals, Trial Balance, P&L, BS
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import date, timedelta
import random

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DB_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "r2r.db")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
random.seed(42)
np.random.seed(42)

MONTHS = [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1)]

# ─── 1. DATABASE SETUP ────────────────────────────────────────────────────────
DDL = """
CREATE TABLE IF NOT EXISTS company_master (
    id            INTEGER PRIMARY KEY,
    company_code  TEXT UNIQUE NOT NULL,
    company_name  TEXT NOT NULL,
    currency      TEXT DEFAULT 'USD',
    fiscal_year   INTEGER
);

CREATE TABLE IF NOT EXISTS gl_accounts (
    id            INTEGER PRIMARY KEY,
    account_code  TEXT UNIQUE NOT NULL,
    account_name  TEXT NOT NULL,
    account_type  TEXT NOT NULL,   -- ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    normal_balance TEXT NOT NULL   -- DEBIT, CREDIT
);

CREATE TABLE IF NOT EXISTS vendors (
    id            INTEGER PRIMARY KEY,
    vendor_code   TEXT UNIQUE NOT NULL,
    vendor_name   TEXT NOT NULL,
    payment_terms INTEGER DEFAULT 30
);

CREATE TABLE IF NOT EXISTS customers (
    id            INTEGER PRIMARY KEY,
    customer_code TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    credit_limit  REAL DEFAULT 50000
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id            INTEGER PRIMARY KEY,
    je_number     TEXT NOT NULL,
    posting_date  TEXT NOT NULL,
    gl_account    TEXT NOT NULL,
    description   TEXT,
    debit         REAL DEFAULT 0,
    credit        REAL DEFAULT 0,
    reference     TEXT,
    month         TEXT NOT NULL,
    FOREIGN KEY (gl_account) REFERENCES gl_accounts(account_code)
);

CREATE TABLE IF NOT EXISTS invoices_ap (
    id            INTEGER PRIMARY KEY,
    invoice_no    TEXT UNIQUE NOT NULL,
    vendor_code   TEXT NOT NULL,
    posting_date  TEXT NOT NULL,
    due_date      TEXT NOT NULL,
    amount        REAL NOT NULL,
    status        TEXT DEFAULT 'OPEN',
    FOREIGN KEY (vendor_code) REFERENCES vendors(vendor_code)
);

CREATE TABLE IF NOT EXISTS invoices_ar (
    id            INTEGER PRIMARY KEY,
    invoice_no    TEXT UNIQUE NOT NULL,
    customer_code TEXT NOT NULL,
    posting_date  TEXT NOT NULL,
    due_date      TEXT NOT NULL,
    amount        REAL NOT NULL,
    status        TEXT DEFAULT 'OPEN',
    FOREIGN KEY (customer_code) REFERENCES customers(customer_code)
);

CREATE TABLE IF NOT EXISTS payments (
    id            INTEGER PRIMARY KEY,
    payment_ref   TEXT NOT NULL,
    payment_date  TEXT NOT NULL,
    payment_type  TEXT NOT NULL,   -- AP or AR
    invoice_no    TEXT NOT NULL,
    amount        REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS assets (
    id            INTEGER PRIMARY KEY,
    asset_no      TEXT UNIQUE NOT NULL,
    asset_name    TEXT NOT NULL,
    purchase_date TEXT NOT NULL,
    cost          REAL NOT NULL,
    useful_life   INTEGER NOT NULL,  -- years
    salvage_value REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS depreciation (
    id            INTEGER PRIMARY KEY,
    asset_no      TEXT NOT NULL,
    period        TEXT NOT NULL,     -- YYYY-MM
    dep_amount    REAL NOT NULL,
    accum_dep     REAL NOT NULL,
    book_value    REAL NOT NULL,
    FOREIGN KEY (asset_no) REFERENCES assets(asset_no)
);
"""

def create_database():
    conn = sqlite3.connect(DB_PATH)
    for stmt in DDL.strip().split(";"):
        s = stmt.strip()
        if s:
            conn.execute(s)
    conn.commit()
    print("✓ Database & tables created.")
    return conn


# ─── 2. MASTER DATA ───────────────────────────────────────────────────────────
def insert_master_data(conn):
    conn.execute("INSERT OR IGNORE INTO company_master VALUES (1,'C001','Acme Corp','USD',2024)")

    accounts = [
        # Assets
        ("1000","Cash",              "ASSET",     "DEBIT"),
        ("1100","Accounts Receivable","ASSET",    "DEBIT"),
        ("1200","Inventory",         "ASSET",     "DEBIT"),
        ("1500","Fixed Assets",      "ASSET",     "DEBIT"),
        ("1510","Accum Depreciation","ASSET",     "CREDIT"),
        # Liabilities
        ("2000","Accounts Payable",  "LIABILITY", "CREDIT"),
        ("2100","Accrued Expenses",  "LIABILITY", "CREDIT"),
        ("2200","Short-Term Loan",   "LIABILITY", "CREDIT"),
        # Equity
        ("3000","Retained Earnings", "EQUITY",    "CREDIT"),
        ("3100","Share Capital",     "EQUITY",    "CREDIT"),
        # Revenue
        ("4000","Sales Revenue",     "REVENUE",   "CREDIT"),
        ("4100","Service Revenue",   "REVENUE",   "CREDIT"),
        # Expenses
        ("5000","Cost of Goods Sold","EXPENSE",   "DEBIT"),
        ("5100","Salaries Expense",  "EXPENSE",   "DEBIT"),
        ("5200","Rent Expense",      "EXPENSE",   "DEBIT"),
        ("5300","Utilities Expense", "EXPENSE",   "DEBIT"),
        ("5400","Depreciation Exp",  "EXPENSE",   "DEBIT"),
        ("5500","Accrued Expense",   "EXPENSE",   "DEBIT"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO gl_accounts(account_code,account_name,account_type,normal_balance) VALUES(?,?,?,?)",
        accounts
    )

    vendors = [
        ("V001","Tech Supplies Ltd",  30),
        ("V002","Office Needs Inc",   45),
        ("V003","Cloud Services Co",  15),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO vendors(vendor_code,vendor_name,payment_terms) VALUES(?,?,?)",
        vendors
    )

    customers = [
        ("C001","Global Traders",    100000),
        ("C002","Metro Retail Group", 75000),
        ("C003","Sunrise Exports",    50000),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO customers(customer_code,customer_name,credit_limit) VALUES(?,?,?)",
        customers
    )

    assets = [
        ("A001","Server Equipment", "2023-07-01", 120000, 5, 10000),
        ("A002","Office Furniture",  "2023-01-01",  30000, 7,  2000),
        ("A003","Company Vehicle",   "2023-10-01",  60000, 4,  5000),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO assets(asset_no,asset_name,purchase_date,cost,useful_life,salvage_value) VALUES(?,?,?,?,?,?)",
        assets
    )

    conn.commit()
    print("✓ Master data inserted.")


# ─── 3. SAMPLE TRANSACTIONS ───────────────────────────────────────────────────
def rand_date(base: date) -> str:
    """Random date within the given month."""
    end = (base.replace(month=base.month % 12 + 1, day=1) if base.month < 12
           else base.replace(year=base.year + 1, month=1, day=1)) - timedelta(days=1)
    return (base + timedelta(days=random.randint(0, (end - base).days))).isoformat()

def insert_journal_entries(conn):
    je_rows = []
    je_num  = 1000

    revenue_vals = [85000, 92000, 103000]
    cogs_vals    = [42000, 46000,  51000]
    salary_vals  = [18000, 18000,  19000]

    for i, m in enumerate(MONTHS):
        mstr = m.strftime("%Y-%m")
        d    = rand_date(m)

        # Revenue
        rev = revenue_vals[i]
        je_rows += [
            (f"JE{je_num:04d}", d, "1000", "Cash from sales",       rev,   0, f"REV{je_num}", mstr),
            (f"JE{je_num:04d}", d, "4000", "Sales revenue",           0,  rev, f"REV{je_num}", mstr),
        ]
        je_num += 1

        # COGS
        cogs = cogs_vals[i]
        je_rows += [
            (f"JE{je_num:04d}", d, "5000", "Cost of goods sold",    cogs,    0, f"COGS{je_num}", mstr),
            (f"JE{je_num:04d}", d, "1200", "Inventory consumed",       0,  cogs, f"COGS{je_num}", mstr),
        ]
        je_num += 1

        # Salaries
        sal = salary_vals[i]
        je_rows += [
            (f"JE{je_num:04d}", d, "5100", "Salary expense",         sal,   0, f"SAL{je_num}", mstr),
            (f"JE{je_num:04d}", d, "1000", "Cash paid – salaries",     0,  sal, f"SAL{je_num}", mstr),
        ]
        je_num += 1

        # Rent
        rent = 8000
        je_rows += [
            (f"JE{je_num:04d}", d, "5200", "Rent expense",           rent,    0, f"RENT{je_num}", mstr),
            (f"JE{je_num:04d}", d, "1000", "Cash paid – rent",          0,  rent, f"RENT{je_num}", mstr),
        ]
        je_num += 1

        # Utilities
        util = round(random.uniform(1200, 1800), 2)
        je_rows += [
            (f"JE{je_num:04d}", d, "5300", "Utilities expense",      util,    0, f"UTIL{je_num}", mstr),
            (f"JE{je_num:04d}", d, "1000", "Cash paid – utilities",     0,  util, f"UTIL{je_num}", mstr),
        ]
        je_num += 1

        # Accrued expense
        accr = 3500
        je_rows += [
            (f"JE{je_num:04d}", d, "5500", "Accrued expense",        accr,     0, f"ACCR{je_num}", mstr),
            (f"JE{je_num:04d}", d, "2100", "Accrued liability",         0,  accr, f"ACCR{je_num}", mstr),
        ]
        je_num += 1

    conn.executemany(
        "INSERT INTO journal_entries(je_number,posting_date,gl_account,description,debit,credit,reference,month) VALUES(?,?,?,?,?,?,?,?)",
        je_rows
    )
    conn.commit()
    print(f"✓ Journal entries inserted ({len(je_rows)} lines).")


def insert_ap_ar(conn):
    vendors   = ["V001","V002","V003"]
    customers = ["C001","C002","C003"]
    ap_rows, ar_rows, pay_rows = [], [], []

    for i, m in enumerate(MONTHS):
        for v in vendors:
            amt  = round(random.uniform(3000, 15000), 2)
            inv  = f"AP{m.strftime('%Y%m')}{v}"
            d    = rand_date(m)
            due  = (date.fromisoformat(d) + timedelta(days=30)).isoformat()
            ap_rows.append((inv, v, d, due, amt, "PAID"))
            pay_rows.append((f"PAY-AP-{inv}", due, "AP", inv, amt))

        for c in customers:
            amt  = round(random.uniform(5000, 25000), 2)
            inv  = f"AR{m.strftime('%Y%m')}{c}"
            d    = rand_date(m)
            due  = (date.fromisoformat(d) + timedelta(days=30)).isoformat()
            ar_rows.append((inv, c, d, due, amt, "COLLECTED"))
            pay_rows.append((f"PAY-AR-{inv}", due, "AR", inv, amt))

    conn.executemany(
        "INSERT OR IGNORE INTO invoices_ap(invoice_no,vendor_code,posting_date,due_date,amount,status) VALUES(?,?,?,?,?,?)",
        ap_rows
    )
    conn.executemany(
        "INSERT OR IGNORE INTO invoices_ar(invoice_no,customer_code,posting_date,due_date,amount,status) VALUES(?,?,?,?,?,?)",
        ar_rows
    )
    conn.executemany(
        "INSERT OR IGNORE INTO payments(payment_ref,payment_date,payment_type,invoice_no,amount) VALUES(?,?,?,?,?)",
        pay_rows
    )
    conn.commit()
    print("✓ AP / AR / Payments inserted.")


def insert_depreciation(conn):
    assets = conn.execute("SELECT asset_no, cost, useful_life, salvage_value FROM assets").fetchall()
    dep_rows = []
    for asset_no, cost, life, salvage in assets:
        annual  = (cost - salvage) / life
        monthly = round(annual / 12, 2)
        accum   = 0.0
        # Carry 6 prior months + 3 project months
        all_periods = [
            date(2023, m, 1).strftime("%Y-%m") for m in range(7, 13)
        ] + [m.strftime("%Y-%m") for m in MONTHS]
        for period in all_periods:
            accum += monthly
            bv     = round(cost - accum, 2)
            dep_rows.append((asset_no, period, monthly, round(accum, 2), bv))

    conn.executemany(
        "INSERT OR IGNORE INTO depreciation(asset_no,period,dep_amount,accum_dep,book_value) VALUES(?,?,?,?,?)",
        dep_rows
    )
    # Post depreciation JEs for the 3 project months
    je_rows = []
    je_num  = 9000
    for m in MONTHS:
        period = m.strftime("%Y-%m")
        rows = conn.execute(
            "SELECT SUM(dep_amount) FROM depreciation WHERE period=?", (period,)
        ).fetchone()
        dep_total = round(rows[0] or 0, 2)
        d = rand_date(m)
        je_rows += [
            (f"JE{je_num:04d}", d, "5400", "Depreciation expense",   dep_total,        0, f"DEP{je_num}", period),
            (f"JE{je_num:04d}", d, "1510", "Accum depreciation",             0, dep_total, f"DEP{je_num}", period),
        ]
        je_num += 1

    conn.executemany(
        "INSERT INTO journal_entries(je_number,posting_date,gl_account,description,debit,credit,reference,month) VALUES(?,?,?,?,?,?,?,?)",
        je_rows
    )
    conn.commit()
    print("✓ Depreciation calculated and posted.")


# ─── 4. ANALYTICS ─────────────────────────────────────────────────────────────
def trial_balance(conn) -> pd.DataFrame:
    """Sum debits and credits per GL account."""
    df = pd.read_sql("""
        SELECT j.gl_account AS account_code,
               g.account_name,
               g.account_type,
               ROUND(SUM(j.debit),  2) AS total_debit,
               ROUND(SUM(j.credit), 2) AS total_credit,
               ROUND(SUM(j.debit) - SUM(j.credit), 2) AS net_balance
        FROM journal_entries j
        JOIN gl_accounts g ON j.gl_account = g.account_code
        GROUP BY j.gl_account, g.account_name, g.account_type
        ORDER BY j.gl_account
    """, conn)
    return df

def profit_and_loss(conn) -> pd.DataFrame:
    """Monthly P&L from journal entries."""
    df = pd.read_sql("""
        SELECT j.month,
               g.account_type,
               ROUND(SUM(j.credit) - SUM(j.debit), 2) AS net_amount
        FROM journal_entries j
        JOIN gl_accounts g ON j.gl_account = g.account_code
        WHERE g.account_type IN ('REVENUE','EXPENSE')
        GROUP BY j.month, g.account_type
        ORDER BY j.month
    """, conn)

    pivot = df.pivot_table(index="month", columns="account_type", values="net_amount", aggfunc="sum").fillna(0)
    pivot.columns.name = None
    pivot = pivot.rename(columns={"REVENUE": "revenue", "EXPENSE": "expenses"})
    if "expenses" in pivot.columns:
        pivot["expenses"] = pivot["expenses"].abs()
    pivot["net_profit"] = pivot.get("revenue", 0) - pivot.get("expenses", 0)
    return pivot.reset_index()

def balance_sheet(conn) -> dict:
    """Simple balance sheet totals."""
    df = pd.read_sql("""
        SELECT g.account_type,
               g.normal_balance,
               ROUND(SUM(j.debit) - SUM(j.credit), 2) AS balance
        FROM journal_entries j
        JOIN gl_accounts g ON j.gl_account = g.account_code
        WHERE g.account_type IN ('ASSET','LIABILITY','EQUITY')
        GROUP BY g.account_type, g.normal_balance
    """, conn)

    totals = {"assets": 0, "liabilities": 0, "equity": 0}
    for _, row in df.iterrows():
        val = abs(row["balance"])
        if row["account_type"] == "ASSET":
            totals["assets"] += val
        elif row["account_type"] == "LIABILITY":
            totals["liabilities"] += val
        elif row["account_type"] == "EQUITY":
            totals["equity"] += val
    return {k: round(v, 2) for k, v in totals.items()}


# ─── 5. EXPORT CSV ────────────────────────────────────────────────────────────
def export_csvs(conn, pnl: pd.DataFrame, tb: pd.DataFrame):
    tables = ["company_master","gl_accounts","vendors","customers",
              "journal_entries","invoices_ap","invoices_ar","payments",
              "assets","depreciation"]
    for t in tables:
        pd.read_sql(f"SELECT * FROM {t}", conn).to_csv(
            os.path.join(DATA_DIR, f"{t}.csv"), index=False
        )
    pnl.to_csv(os.path.join(DATA_DIR, "profit_loss.csv"), index=False)
    tb.to_csv(os.path.join(DATA_DIR, "trial_balance.csv"), index=False)
    print(f"✓ CSVs exported to /data  ({len(tables)+2} files).")


# ─── 6. VISUALIZATION ─────────────────────────────────────────────────────────
def plot_charts(pnl: pd.DataFrame):
    months = pnl["month"].tolist()
    x      = range(len(months))
    rev    = pnl["revenue"].tolist()
    exp    = pnl["expenses"].tolist()
    profit = pnl["net_profit"].tolist()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Acme Corp — Q1 2024 Financial Close", fontsize=14, fontweight="bold")

    # Chart 1 – Revenue vs Expenses
    ax = axes[0]
    width = 0.35
    bars1 = ax.bar([i - width/2 for i in x], rev, width, label="Revenue",  color="#2ecc71", edgecolor="white")
    bars2 = ax.bar([i + width/2 for i in x], exp, width, label="Expenses", color="#e74c3c", edgecolor="white")
    ax.set_title("Monthly Revenue vs Expenses", fontweight="bold")
    ax.set_xticks(list(x)); ax.set_xticklabels(months)
    ax.set_ylabel("USD ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax.legend(); ax.grid(axis="y", linestyle="--", alpha=0.4)
    for bar in bars1: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+500,
                               f"${bar.get_height():,.0f}", ha="center", va="bottom", fontsize=8)
    for bar in bars2: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+500,
                               f"${bar.get_height():,.0f}", ha="center", va="bottom", fontsize=8)

    # Chart 2 – Net Profit Trend
    ax2 = axes[1]
    ax2.plot(months, profit, marker="o", linewidth=2.5, color="#3498db",
             markersize=8, markerfacecolor="white", markeredgewidth=2.5)
    ax2.fill_between(months, profit, alpha=0.15, color="#3498db")
    ax2.set_title("Net Profit Trend", fontweight="bold")
    ax2.set_ylabel("USD ($)")
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
    ax2.grid(linestyle="--", alpha=0.4)
    for i, (m, p) in enumerate(zip(months, profit)):
        ax2.annotate(f"${p:,.0f}", (m, p), textcoords="offset points",
                     xytext=(0, 10), ha="center", fontsize=9, fontweight="bold", color="#2c3e50")

    plt.tight_layout()
    out = os.path.join(DATA_DIR, "financial_charts.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ Charts saved → {out}")


# ─── 7. MONTH-END CLOSE SUMMARY ───────────────────────────────────────────────
def print_close_summary(pnl: pd.DataFrame, bs: dict, tb: pd.DataFrame):
    print("\n" + "═"*55)
    print("  ACME CORP — R2R MONTH-END CLOSE REPORT  (Q1 2024)")
    print("═"*55)

    print("\n📊  PROFIT & LOSS STATEMENT")
    print(f"  {'Month':<10} {'Revenue':>12} {'Expenses':>12} {'Net Profit':>12}")
    print("  " + "-"*48)
    for _, r in pnl.iterrows():
        print(f"  {r['month']:<10} ${r['revenue']:>11,.2f} ${r['expenses']:>11,.2f} ${r['net_profit']:>11,.2f}")
    print(f"\n  {'TOTAL':<10} ${pnl['revenue'].sum():>11,.2f} "
          f"${pnl['expenses'].sum():>11,.2f} ${pnl['net_profit'].sum():>11,.2f}")

    print("\n📋  BALANCE SHEET (Cumulative)")
    print(f"  Assets      : ${bs['assets']:>12,.2f}")
    print(f"  Liabilities : ${bs['liabilities']:>12,.2f}")
    print(f"  Equity      : ${bs['equity']:>12,.2f}")
    chk = bs['assets'] - bs['liabilities'] - bs['equity']
    print(f"  Check (A=L+E): {'✓ BALANCED' if abs(chk) < 1 else f'⚠ Diff={chk:.2f}'}")

    print("\n📒  TRIAL BALANCE CHECK")
    total_dr = tb["total_debit"].sum()
    total_cr = tb["total_credit"].sum()
    print(f"  Total Debits  : ${total_dr:>12,.2f}")
    print(f"  Total Credits : ${total_cr:>12,.2f}")
    diff = round(total_dr - total_cr, 2)
    print(f"  Difference    : {'✓ 0.00 — BALANCED' if diff == 0 else f'⚠ {diff}'}")

    print("\n" + "═"*55)
    print("  Month-End Close: ✅  COMPLETE")
    print("═"*55 + "\n")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n🚀 R2R Financial Close — SAP Capstone Project\n")

    conn = create_database()
    insert_master_data(conn)
    insert_journal_entries(conn)
    insert_ap_ar(conn)
    insert_depreciation(conn)

    tb  = trial_balance(conn)
    pnl = profit_and_loss(conn)
    bs  = balance_sheet(conn)

    export_csvs(conn, pnl, tb)
    plot_charts(pnl)
    print_close_summary(pnl, bs, tb)

    conn.close()

if __name__ == "__main__":
    main()
