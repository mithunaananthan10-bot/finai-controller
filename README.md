# FinAI Controller 💼

An AI-powered financial control and analysis dashboard built with **Python, Streamlit, Pandas, Plotly, and Gemini AI**.

FinAI Controller helps businesses analyze financial transactions through reconciliation, tax classification, cash-flow forecasting, and an AI-powered financial assistant.

---

## 🚀 Features

### 1. Executive Dashboard
- Overall financial health overview
- Reconciliation rate
- Matched and unmatched transaction summary
- Settlement breakdown
- Cash-flow and liquidity visualization
- Quick AI-generated financial insights

### 2. Reconciliation Engine
- Compares internal ledger transactions with bank statements
- Matches transactions using references, descriptions, amounts, and dates
- Identifies unmatched transactions
- Detects amount mismatches
- Generates reconciliation results and unclaimed bank records

### 3. Tax & Compliance Audit
- Analyzes tax categories from the internal ledger
- Groups transactions by tax category
- Identifies transactions requiring additional review
- Provides tax-related transaction insights
- Uses rule-based analysis for tax review

### 4. 14-Day Cash Forecasting
- Analyzes historical cash-flow data
- Calculates cash inflow and outflow trends
- Forecasts future closing cash balances
- Provides a 14-day cash-flow outlook
- Helps identify potential liquidity risks

### 5. Financial AI Agent 🤖
- Allows users to ask questions about financial data
- Provides insights across reconciliation, tax, and cash-flow modules
- Uses Gemini AI for natural-language financial analysis
- Supports interactive question-and-answer functionality

### 6. Audit Reports
- Generates an executive financial report
- Displays reconciliation KPIs
- Provides a summary of audited transactions
- Stores generated reports in the `outputs` directory

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit** — Web dashboard
- **Pandas** — Data processing and analysis
- **Plotly** — Interactive visualizations
- **Gemini API** — AI-powered financial assistant
- **CSV** — Financial data storage

---

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