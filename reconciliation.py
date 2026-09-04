from pathlib import Path
import pandas as pd


def run_reconciliation():
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = data_dir / "internal_ledger.csv"
    bank_path = data_dir / "bank_statement.csv"

    if not ledger_path.exists() or not bank_path.exists():
        raise FileNotFoundError(
            "Input ledger or bank statement not found in /data"
        )

    # ------------------------------------------------------------
    # LOAD FILES
    # ------------------------------------------------------------
    df_ledger = pd.read_csv(ledger_path)
    df_bank = pd.read_csv(bank_path)

    # Clean column names
    df_ledger.columns = df_ledger.columns.str.strip()
    df_bank.columns = df_bank.columns.str.strip()

    # ------------------------------------------------------------
    # VALIDATE LEDGER
    # ------------------------------------------------------------
    required_ledger = [
        "entry_id",
        "date",
        "description",
        "reference",
        "category",
        "amount",
        "tax_category"
    ]

    missing_ledger = [
        col for col in required_ledger
        if col not in df_ledger.columns
    ]

    if missing_ledger:
        raise ValueError(
            f"Missing columns in internal_ledger.csv: {missing_ledger}"
        )

    # ------------------------------------------------------------
    # VALIDATE BANK STATEMENT
    # ------------------------------------------------------------
    required_bank = [
        "transaction_id",
        "date",
        "description",
        "reference",
        "type",
        "amount",
        "remarks"
    ]

    missing_bank = [
        col for col in required_bank
        if col not in df_bank.columns
    ]

    if missing_bank:
        raise ValueError(
            f"Missing columns in bank_statement.csv: {missing_bank}"
        )

    # ------------------------------------------------------------
    # RECONCILIATION
    # ------------------------------------------------------------
    reconciliation_results = []
    matched_bank_ids = set()

    for _, l_row in df_ledger.iterrows():

        ledger_id = l_row["entry_id"]
        ledger_date = str(l_row["date"])
        ledger_description = str(l_row["description"]).strip()
        ledger_reference = str(l_row["reference"]).strip()
        ledger_amount = float(l_row["amount"])

        matched_bank_id = "—"
        status = "EXCEPTION"
        reason = "No matching record"

        for _, b_row in df_bank.iterrows():

            bank_id = b_row["transaction_id"]

            # Prevent one bank transaction from being matched twice
            if bank_id in matched_bank_ids:
                continue

            bank_date = str(b_row["date"])
            bank_description = str(b_row["description"]).strip()
            bank_reference = str(b_row["reference"]).strip()
            bank_amount = float(b_row["amount"])

            # Normalize text for comparison
            ledger_desc_lower = ledger_description.lower()
            bank_desc_lower = bank_description.lower()

            # ----------------------------------------------------
            # 1. EXACT REFERENCE + AMOUNT
            # ----------------------------------------------------
            if (
                ledger_reference.lower() == bank_reference.lower()
                and abs(ledger_amount - bank_amount) < 0.001
            ):
                matched_bank_id = bank_id
                status = "MATCHED"
                reason = "Exact reference and amount match"

                matched_bank_ids.add(bank_id)
                break

            # ----------------------------------------------------
            # 2. EXACT DESCRIPTION + AMOUNT + DATE
            # ----------------------------------------------------
            elif (
                ledger_desc_lower == bank_desc_lower
                and abs(ledger_amount - bank_amount) < 0.001
                and ledger_date == bank_date
            ):
                matched_bank_id = bank_id
                status = "MATCHED"
                reason = "Exact description, amount and date match"

                matched_bank_ids.add(bank_id)
                break

            # ----------------------------------------------------
            # 3. DESCRIPTION + AMOUNT
            # ----------------------------------------------------
            elif (
                ledger_desc_lower in bank_desc_lower
                and abs(ledger_amount - bank_amount) < 0.001
            ):
                matched_bank_id = bank_id
                status = "MATCHED"
                reason = "Description and amount match"

                matched_bank_ids.add(bank_id)
                break

            # ----------------------------------------------------
            # 4. AMOUNT TOLERANCE
            # ----------------------------------------------------
            elif (
                ledger_desc_lower in bank_desc_lower
                and abs(ledger_amount - bank_amount) <= 1.00
            ):
                matched_bank_id = bank_id
                status = "MATCHED"
                reason = "Amount tolerance match"

                matched_bank_ids.add(bank_id)
                break

        # --------------------------------------------------------
        # SAVE RECONCILIATION RESULT
        # --------------------------------------------------------
        reconciliation_results.append({
            "Ledger ID": ledger_id,
            "Vendor": ledger_description,
            "Amount": ledger_amount,
            "Date": ledger_date,
            "Matched Bank ID": matched_bank_id,
            "Status": status,
            "Reason": reason
        })

    # ------------------------------------------------------------
    # FIND UNCLAIMED BANK RECORDS
    # ------------------------------------------------------------
    unclaimed = []

    for _, b_row in df_bank.iterrows():

        bank_id = b_row["transaction_id"]

        if bank_id not in matched_bank_ids:
            unclaimed.append({
                "Bank ID": bank_id,
                "Description": b_row["description"],
                "Amount": b_row["amount"],
                "Date": b_row["date"]
            })

    # ------------------------------------------------------------
    # WRITE OUTPUT FILES
    # ------------------------------------------------------------
    pd.DataFrame(reconciliation_results).to_csv(
        outputs_dir / "reconciliation_results.csv",
        index=False
    )

    pd.DataFrame(unclaimed).to_csv(
        outputs_dir / "unclaimed_bank_records.csv",
        index=False
    )

    print("Reconciliation and Unclaimed files written to /outputs.")


if __name__ == "__main__":
    run_reconciliation()