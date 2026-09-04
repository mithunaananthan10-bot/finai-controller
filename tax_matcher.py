from pathlib import Path
import pandas as pd


def run_tax_matching():
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = data_dir / "internal_ledger.csv"

    if not ledger_path.exists():
        raise FileNotFoundError(
            "data/internal_ledger.csv not found."
        )

    df_ledger = pd.read_csv(ledger_path)

    # Clean column names
    df_ledger.columns = df_ledger.columns.str.strip()

    # ------------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # ------------------------------------------------------------
    required_columns = [
        "entry_id",
        "description",
        "amount",
        "date",
        "tax_category"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df_ledger.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in internal_ledger.csv: {missing_columns}"
        )

    # ------------------------------------------------------------
    # TAX MATCHING
    # ------------------------------------------------------------
    tax_records = []

    for _, row in df_ledger.iterrows():

        ledger_id = row["entry_id"]
        vendor = str(row["description"])
        amount = float(row["amount"])
        date = str(row["date"])
        cat = str(row["tax_category"]).strip()

        # AI review rule
        is_review = (
            cat.upper() == "AI_REVIEW"
            or "Starbucks" in vendor
        )

        status = "AI_REVIEW" if is_review else "VERIFIED"

        tax_category = (
            "AI Review Required"
            if is_review
            else cat
        )

        tax_records.append({
            "Ledger ID": ledger_id,
            "Vendor": vendor,
            "Amount": amount,
            "Date": date,
            "Tax Category": tax_category,
            "Review Status": status
        })

    # ------------------------------------------------------------
    # SAVE OUTPUT
    # ------------------------------------------------------------
    pd.DataFrame(tax_records).to_csv(
        outputs_dir / "tax_matches.csv",
        index=False
    )

    print("Tax matches written to /outputs/tax_matches.csv.")


if __name__ == "__main__":
    run_tax_matching()