# FinAI Controller 💼

An AI-powered financial control and analysis dashboard built with Python, Streamlit, Pandas, Plotly, and Gemini AI.

FinAI Controller helps analyze financial transactions through reconciliation, tax classification, cash-flow forecasting, and an AI-powered financial assistant.

## 🚀 Features

### Executive Dashboard
- Reconciliation rate and financial KPIs
- Settlement breakdown
- Cash-flow and liquidity visualization
- Quick financial insights

### Reconciliation Engine
- Compares internal ledger with bank statements
- Matches transactions using references, descriptions, amounts, and dates
- Identifies unmatched transactions
- Detects reconciliation exceptions
- Generates unclaimed bank transaction records

### Tax & Compliance Audit
- Analyzes tax categories
- Identifies transactions requiring review
- Provides tax-related transaction insights
- Supports rule-based tax analysis

### 14-Day Cash Forecasting
- Analyzes historical cash-flow data
- Tracks cash inflows and outflows
- Forecasts future closing balances
- Provides a 14-day cash-flow outlook

### Financial AI Agent 🤖
- Allows users to ask questions about financial data
- Provides insights across reconciliation, tax, and cash-flow modules
- Uses Gemini AI for natural-language financial analysis

### Audit Reports
- Generates an executive financial report
- Displays reconciliation KPIs
- Provides a summary of audited transactions

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Gemini AI API
- CSV

## 📁 Project Structure

```text
finai-controller/
│
├── app.py
├── main.py
├── qa_agent.py
├── reconciliation.py
├── forecasting.py
├── tax_matcher.py
├── report.py
├── generate_data.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── .streamlit/
│   └── config.toml
│
├── data/
│   ├── internal_ledger.csv
│   ├── bank_statement.csv
│   └── cashflow_history.csv
│
└── outputs/
    ├── reconciliation_results.csv
    ├── unclaimed_bank_records.csv
    ├── tax_matches.csv
    ├── cash_forecast.csv
    └── report.html