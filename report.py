from pathlib import Path
import pandas as pd

def generate_report():
    base_dir = Path(__file__).parent
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    recon_path = outputs_dir / "reconciliation_results.csv"
    tax_path = outputs_dir / "tax_matches.csv"
    forecast_path = outputs_dir / "cash_forecast.csv"

    df_recon = pd.read_csv(recon_path) if recon_path.exists() else pd.DataFrame()

    total_recs = len(df_recon)
    matched = len(df_recon[df_recon["Status"].str.upper() == "MATCHED"]) if not df_recon.empty else 0
    exceptions = len(df_recon[df_recon["Status"].str.upper() == "EXCEPTION"]) if not df_recon.empty else 0
    match_rate = (matched / total_recs * 100) if total_recs > 0 else 0

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AI Finance Controller Executive Report</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #F8F7F2; color: #1E2A24; padding: 30px; }}
        .header {{ border-bottom: 2px solid #154332; padding-bottom: 10px; margin-bottom: 20px; }}
        .kpi-container {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .kpi-card {{ background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px 25px; flex: 1; }}
        .kpi-val {{ font-size: 24px; font-weight: bold; color: #154332; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 15px; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 10px 14px; border-bottom: 1px solid #E5E7EB; text-align: left; font-size: 13px; }}
        th {{ background: #0C2E22; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI FINANCE CONTROLLER — EXECUTIVE REPORT</h1>
        <p>Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    <div class="kpi-container">
        <div class="kpi-card"><div>MATCH RATE</div><div class="kpi-val">{match_rate:.1f}%</div></div>
        <div class="kpi-card"><div>MATCHED RECORDS</div><div class="kpi-val">{matched}</div></div>
        <div class="kpi-card"><div>EXCEPTIONS</div><div class="kpi-val" style="color:#B91C1C;">{exceptions}</div></div>
        <div class="kpi-card"><div>TOTAL AUDITED</div><div class="kpi-val">{total_recs}</div></div>
    </div>
    <h2>Reconciliation Summary</h2>
    {df_recon.head(10).to_html(classes="table", index=False) if not df_recon.empty else "<p>No data</p>"}
</body>
</html>
"""
    with open(outputs_dir / "report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Executive report generated at /outputs/report.html.")

if __name__ == "__main__":
    generate_report()
