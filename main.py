from pathlib import Path
import generate_data
import reconciliation
import forecasting
import tax_matcher
import report


def main():
    print("Starting AI Finance Controller Pipeline...")

    data_dir = Path(__file__).parent / "data"

    required_data = [
        data_dir / "internal_ledger.csv",
        data_dir / "bank_statement.csv",
        data_dir / "cashflow_history.csv",
    ]

    if not all(p.exists() for p in required_data):
        print("Generating synthetic source datasets...")
        generate_data.generate_synthetic_finance_data()

    print("Running Reconciliation Engine...")
    reconciliation.run_reconciliation()

    print("Running 14-Day Cash Forecasting...")
    forecasting.run_forecasting()

    print("Running Tax Line Matcher...")
    tax_matcher.run_tax_matching()

    print("Generating Executive HTML Report...")
    report.generate_report()

    print("Pipeline Finished Successfully! All outputs refreshed.")


if __name__ == "__main__":
    main()