from pathlib import Path
import pandas as pd
import streamlit as st
from google import genai


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

# For Streamlit Cloud, the API key will be stored in
# Streamlit Secrets.
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# LOAD FINANCIAL DATA
# ============================================================

def load_financial_data():
    """
    Loads the financial output CSV files generated
    by the AI Finance Controller pipeline.
    """

    base_dir = Path(__file__).parent
    outputs_dir = base_dir / "outputs"

    recon_path = outputs_dir / "reconciliation_results.csv"
    unclaimed_path = outputs_dir / "unclaimed_bank_records.csv"
    tax_path = outputs_dir / "tax_matches.csv"
    forecast_path = outputs_dir / "cash_forecast.csv"

    context_parts = []

    # --------------------------------------------------------
    # Reconciliation data
    # --------------------------------------------------------

    if recon_path.exists():
        df_recon = pd.read_csv(recon_path)

        context_parts.append(
            "=== RECONCILIATION DATA ===\n"
            + df_recon.to_string(index=False)
        )

    # --------------------------------------------------------
    # Unclaimed bank transactions
    # --------------------------------------------------------

    if unclaimed_path.exists():
        df_unc = pd.read_csv(unclaimed_path)

        context_parts.append(
            "=== UNCLAIMED BANK TRANSACTIONS ===\n"
            + df_unc.to_string(index=False)
        )

    # --------------------------------------------------------
    # Tax matching data
    # --------------------------------------------------------

    if tax_path.exists():
        df_tax = pd.read_csv(tax_path)

        context_parts.append(
            "=== TAX MATCHING DATA ===\n"
            + df_tax.to_string(index=False)
        )

    # --------------------------------------------------------
    # Cash forecast data
    # --------------------------------------------------------

    if forecast_path.exists():
        df_fc = pd.read_csv(forecast_path)

        context_parts.append(
            "=== CASH FORECAST DATA ===\n"
            + df_fc.to_string(index=False)
        )

    return "\n\n".join(context_parts)


# ============================================================
# GEMINI Q&A AGENT
# ============================================================

def ask_agent(query_str: str) -> str:
    """
    Sends the user's finance question and available
    financial data to Gemini and returns the answer.
    """

    # Load current financial data
    financial_context = load_financial_data()

    # --------------------------------------------------------
    # Check whether financial files are available
    # --------------------------------------------------------

    if not financial_context:
        return (
            "⚠️ Financial output files were not found.\n\n"
            "Please run the finance pipeline first."
        )

    # --------------------------------------------------------
    # Prompt for Gemini
    # --------------------------------------------------------

    prompt = f"""
You are an AI Finance Controller.

Your job is to answer finance-related questions using
ONLY the financial data provided below.

You have access to:

- Bank reconciliation results
- Unclaimed bank transactions
- Tax matching results
- Cash-flow forecasts

================ FINANCIAL DATA ================

{financial_context}

================ USER QUESTION ================

{query_str}

================ INSTRUCTIONS ================

1. Answer the user's question directly.

2. Use ONLY the financial data provided above.

3. Do NOT invent transactions, vendors, dates,
   amounts, balances or financial information.

4. If the question refers to a transaction ID,
   provide the relevant transaction details.

5. If the user asks about reconciliation,
   explain whether the transaction is MATCHED or
   an EXCEPTION and provide the reason when available.

6. If the user asks about unclaimed transactions,
   provide the number and total amount when available.

7. If the user asks about tax review,
   explain the relevant review status and transaction
   information from the data.

8. If the user asks about cash forecasting,
   use the actual forecast data provided.

9. If calculations are required, calculate them
   using the provided data.

10. If the requested information does not exist
    in the provided data, clearly say that it is
    unavailable.

11. Do not claim that you performed an action that
    you did not perform.

12. Give a professional but easy-to-understand answer.

13. Use bullet points when presenting multiple
    financial details.

14. Use ₹ or $ according to the currency shown
    in the provided financial data.

================ END DATA ================
"""

    # --------------------------------------------------------
    # Call Gemini API
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text

        return "⚠️ Gemini returned an empty response."

    except Exception as e:

        return (
            "⚠️ Unable to contact Gemini.\n\n"
            f"Error: {str(e)}"
        )


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        ask_agent(
            "Why did L-1004 fail to reconcile?"
        )
    )

    print("\n" + "=" * 70 + "\n")

    print(
        ask_agent(
            "What is the predicted balance after one week?"
        )
    )

    print("\n" + "=" * 70 + "\n")

    print(
        ask_agent(
            "List the matched vendors."
        )
    )