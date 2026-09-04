from datetime import datetime, timedelta
import os
from pathlib import Path
import random
import numpy as np
import pandas as pd

def generate_synthetic_finance_data():
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    random.seed(42)
    np.random.seed(42)

    vendors = [
        ("Amazon Services", 1250.00, "GST - Purchases"),
        ("Microsoft Azure", 2300.00, "GST - Purchases"),
        ("Office Depot", 150.75, "GST - Purchases"),
        ("Starbucks", 25.60, "AI_REVIEW"),
        ("Uber", 38.90, "GST - Purchases"),
        ("Google Cloud", 1850.00, "GST - Purchases"),
        ("Slack Technologies", 450.00, "GST - Purchases"),
        ("WeWork Office", 3200.00, "TDS - Section 194C"),
        ("Consulting Partner X", 5500.00, "TDS - Section 194J"),
        ("Legal Counsel LLP", 4200.00, "TDS - Section 194J"),
        ("Acme Supplies", 890.00, "GST - Purchases"),
        ("Client Alpha Invoice", 8500.00, "GST - Sales"),
        ("Client Beta Invoice", 12400.00, "GST - Sales"),
        ("Client Gamma Invoice", 6700.00, "GST - Sales"),
        ("Enterprise Contract Delta", 19500.00, "GST - Sales"),
    ]

    start_date = datetime(2026, 5, 1)
    ledger_records = []
    bank_records = []
    bank_id_counter = 8840

    for i in range(1, 61):
        ledger_id = f"L-{1000 + i}"
        vendor_choice, base_amt, tax_cat = random.choice(vendors)
        
        variation = random.choice([0.0, 0.0, 0.0, random.uniform(-5.0, 5.0)])
        amount = round(base_amt + variation, 2)
        txn_date = start_date + timedelta(days=random.randint(0, 25))
        date_str = txn_date.strftime("%b %d, %Y")

        ledger_records.append({
            "Ledger ID": ledger_id,
            "Vendor": vendor_choice,
            "Amount": amount,
            "Date": date_str,
            "Tax Category": tax_cat
        })

        if i not in [4, 18, 31, 47]:
            bank_id_counter += 1
            b_id = f"B-{bank_id_counter}"
            bank_amt = amount
            if i in [3, 15]:
                bank_amt = round(amount + 0.50, 2)
            
            b_date = txn_date + timedelta(days=random.choice([0, 0, 1]))
            bank_records.append({
                "Bank ID": b_id,
                "Description": f"Payment to {vendor_choice}" if "Invoice" not in vendor_choice else f"Receipt from {vendor_choice}",
                "Amount": bank_amt,
                "Date": b_date.strftime("%b %d, %Y")
            })

    unclaimed = [
        {"Bank ID": "B-U001", "Description": "Incoming Wire Transfer", "Amount": 4500.00, "Date": "May 19, 2026"},
        {"Bank ID": "B-U002", "Description": "ACH Credit - Unknown", "Amount": 1250.00, "Date": "May 21, 2026"},
        {"Bank ID": "B-U003", "Description": "Check Deposit - Unidentified", "Amount": 3200.00, "Date": "May 22, 2026"}
    ]
    bank_records.extend(unclaimed)

    cashflow_records = []
    cur_bal = 108000.00
    hist_start = datetime(2026, 5, 18)
    for d in range(21):
        day_date = hist_start + timedelta(days=d)
        change = random.uniform(-4000, 3500)
        if d == 4:
            change = 12000
        cur_bal = max(20000, round(cur_bal + change, 2))
        cashflow_records.append({
            "Date": day_date.strftime("%Y-%m-%d"),
            "Balance": cur_bal
        })
    cashflow_records[-1]["Balance"] = 87520.00

    pd.DataFrame(ledger_records).to_csv(data_dir / "internal_ledger.csv", index=False)
    pd.DataFrame(bank_records).to_csv(data_dir / "bank_statement.csv", index=False)
    pd.DataFrame(cashflow_records).to_csv(data_dir / "cashflow_history.csv", index=False)
    print("Synthetic dataset created successfully in /data folder.")

if __name__ == "__main__":
    generate_synthetic_finance_data()
