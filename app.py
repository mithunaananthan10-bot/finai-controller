import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FinAI Controller",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"

FILE_RECON = OUTPUTS_DIR / "reconciliation_results.csv"
FILE_UNCLAIMED = OUTPUTS_DIR / "unclaimed_bank_records.csv"
FILE_TAX = OUTPUTS_DIR / "tax_matches.csv"
FILE_FORECAST = OUTPUTS_DIR / "cash_forecast.csv"
FILE_CASHFLOW_HIST = DATA_DIR / "cashflow_history.csv"
FILE_REPORT_HTML = OUTPUTS_DIR / "report.html"

FILE_BANK = DATA_DIR / "bank_statement.csv"
FILE_LEDGER = DATA_DIR / "internal_ledger.csv"


# ============================================================
# OPTIONAL AI AGENT
# ============================================================

try:
    import qa_agent
except Exception:
    qa_agent = None


# ============================================================
# SESSION STATE
# ============================================================

if "pipeline_last_run" not in st.session_state:
    st.session_state.pipeline_last_run = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your Financial AI Agent. "
                "I can help explain reconciliation exceptions, "
                "tax issues, cash-flow risks and audit findings."
            )
        },
        {
            "role": "user",
            "content": "Why did transaction L-1004 fail to reconcile?"
        },
        {
            "role": "assistant",
            "content": (
                "🔎 Audit Trace — L-1004\n\n"
                "The transaction appears as an exception because "
                "the ledger and bank records did not satisfy the "
                "configured matching conditions.\n\n"
                "• Merchant: Starbucks\n"
                "• Amount: $25.60\n"
                "• Transaction date: May 21, 2026\n"
                "• Status: Exception\n"
                "• Suggested action: Review petty-cash / supporting records."
            )
        }
    ]


# ============================================================
# MODERN FINTECH DESIGN SYSTEM
# ============================================================

st.markdown(
    """<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system,
    BlinkMacSystemFont, sans-serif !important;
}

/* ============================================================
   STREAMLIT HEADER / SIDEBAR TOGGLE
   ============================================================ */

#MainMenu,
footer {
    visibility: hidden;
}

[data-testid="stHeader"] {
    visibility: visible !important;
}

[data-testid="stHeader"] button {
    font-family: inherit !important;
}

/* Show a clean arrow instead of "Double arrow" text */

button[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarExpandButton"],
button[aria-label*="Collapse sidebar"],
button[aria-label*="Expand sidebar"] {
    font-size: 0 !important;
    width: 38px !important;
    min-width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

button[data-testid="stSidebarCollapseButton"]::after,
button[aria-label*="Collapse sidebar"]::after {
    content: "‹" !important;
    font-size: 27px !important;
    line-height: 1 !important;
    font-weight: 700 !important;
    color: #cbd5e1 !important;
}

button[data-testid="stSidebarExpandButton"]::after,
button[aria-label*="Expand sidebar"]::after {
    content: "›" !important;
    font-size: 27px !important;
    line-height: 1 !important;
    font-weight: 700 !important;
    color: #cbd5e1 !important;
}

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp p,
.stApp label,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    font-family: 'Plus Jakarta Sans', -apple-system,
    BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background-color: #07090e !important;
    background:
        radial-gradient(
            circle at 10% 8%,
            rgba(37, 99, 235, 0.16) 0%,
            transparent 42%
        ),
        radial-gradient(
            circle at 90% 18%,
            rgba(56, 189, 248, 0.10) 0%,
            transparent 38%
        ),
        radial-gradient(
            circle at 50% 95%,
            rgba(30, 58, 138, 0.14) 0%,
            transparent 48%
        ),
        linear-gradient(
            180deg,
            #070a12 0%,
            #06080d 50%,
            #040508 100%
        ) !important;
    background-attachment: fixed !important;
}

.block-container {
    max-width: 1440px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0b0f19 0%,
        #090c14 45%,
        #05070c 100%
    ) !important;
    border-right: 1px solid rgba(59, 130, 246, 0.15) !important;
}

section[data-testid="stSidebar"] > div {
    padding: 1.25rem 1rem !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] span {
    color: #cbd5e1;
}


/* ============================================================
   SIDEBAR BRAND
   ============================================================ */

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 6px 18px 6px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 18px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg,#2563eb,#1d4ed8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 16px rgba(37,99,235,0.45);
}

.brand-text-title {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: -0.3px;
    line-height: 1.2;
}

.brand-text-sub {
    font-size: 11px !important;
    color: #94a3b8 !important;
    margin-top: 2px;
}


/* ============================================================
   STATUS
   ============================================================ */

.status-badge-card {
    background: linear-gradient(145deg,#0e172a 0%,#090f1d 100%);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 20px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
}

.status-badge-sub {
    font-size: 9px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #64748b !important;
    font-weight: 600;
}

.status-badge-val {
    font-size: 12px !important;
    color: #f1f5f9 !important;
    font-weight: 600;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 7px;
}

.dot-pulse {
    height: 8px;
    width: 8px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px #10b981;
}


/* ============================================================
   SIDEBAR NAVIGATION
   ============================================================ */

section[data-testid="stSidebar"] .stRadio label p {
    color: #f0f2f5 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 10px;
    padding: 10px 12px !important;
    transition: all 0.2s ease;
    margin-bottom: 2px;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(30,41,59,0.5) !important;
}

section[data-testid="stSidebar"]
[role="radiogroup"]
label[data-checked="true"] {
    background: linear-gradient(
        90deg,
        #1d4ed8 0%,
        #2563eb 100%
    ) !important;
    box-shadow: 0 4px 16px rgba(37,99,235,0.35);
}

section[data-testid="stSidebar"]
[role="radiogroup"]
label[data-checked="true"] p {
    color: #ffffff !important;
}


/* ============================================================
   HEADER
   ============================================================ */

.fintech-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(
        135deg,
        rgba(16,26,46,0.85) 0%,
        rgba(10,15,27,0.95) 100%
    );
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px;
    padding: 22px 28px;
    margin-bottom: 24px;
    backdrop-filter: blur(10px);
    box-shadow:
        0 10px 30px -10px rgba(0,0,0,0.6),
        0 0 24px -6px rgba(37,99,235,0.18);
}

.fintech-title {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: -0.5px;
}

.fintech-sub {
    font-size: 12px !important;
    color: #94a3b8 !important;
    margin-top: 4px;
}

.fintech-pill {
    background: linear-gradient(
        135deg,
        rgba(37,99,235,0.22),
        rgba(56,189,248,0.12)
    );
    border: 1px solid rgba(59,130,246,0.45);
    color: #60a5fa !important;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    box-shadow: 0 0 12px rgba(59,130,246,0.25);
}


/* ============================================================
   HEADINGS
   ============================================================ */

.view-title {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    margin-top: 6px;
}

.view-sub {
    font-size: 12px !important;
    color: #94a3b8 !important;
    margin-bottom: 18px;
}


/* ============================================================
   METRIC CARDS
   ============================================================ */

div[data-testid="stMetric"] {
    position: relative !important;
    background: linear-gradient(
        150deg,
        #101c33 0%,
        #0b1324 55%,
        #070c17 100%
    ) !important;
    border: 1px solid rgba(59,130,246,0.28) !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    box-shadow:
        0 8px 24px -6px rgba(0,0,0,0.6),
        0 0 20px -4px rgba(37,99,235,0.22),
        inset 0 1px 1px rgba(255,255,255,0.08) !important;
    transition: all 0.25s ease-in-out !important;
}

div[data-testid="stMetric"]:hover {
    border-color: rgba(96,165,250,0.55) !important;
    box-shadow:
        0 12px 30px -4px rgba(0,0,0,0.7),
        0 0 28px rgba(56,189,248,0.35),
        inset 0 1px 2px rgba(255,255,255,0.15) !important;
    transform: translateY(-2px);
}

div[data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

div[data-testid="stMetricValue"] div {
    color: #ffffff !important;
    font-size: 26px !important;
    font-weight: 800 !important;
}

div[data-testid="stMetricDelta"] div,
div[data-testid="stMetricDelta"] span {
    color: #38bdf8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
}


/* ============================================================
   CARDS
   ============================================================ */

.fintech-card {
    position: relative;
    background: linear-gradient(
        160deg,
        #0e172a 0%,
        #0a1120 60%,
        #070a13 100%
    ) !important;
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 18px !important;
    padding: 20px 22px;
    margin-bottom: 18px;
    box-shadow:
        0 10px 30px -8px rgba(0,0,0,0.55),
        0 0 24px -6px rgba(37,99,235,0.15),
        inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

.fintech-card-title {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

.fintech-card-sub {
    font-size: 11px !important;
    color: #94a3b8 !important;
    margin-top: 3px;
    margin-bottom: 12px;
}


/* ============================================================
   UPLOAD CARDS
   ============================================================ */

.upload-card {
    background: linear-gradient(145deg,#0e172a 0%,#080e1b 100%);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 10px;
    min-height: 92px;
    box-shadow:
        0 8px 24px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

.upload-title {
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
}

.upload-sub {
    font-size: 10px;
    color: #64748b;
    margin-top: 4px;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

section[data-testid="stFileUploader"] {
    background: rgba(8,14,27,0.7) !important;
    border: 1px dashed rgba(59,130,246,0.35) !important;
    border-radius: 12px !important;
    padding: 6px !important;
}

section[data-testid="stFileUploader"]:hover {
    border-color: #38bdf8 !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

button[kind="primary"] {
    background: linear-gradient(
        135deg,
        #2563eb 0%,
        #1d4ed8 100%
    ) !important;
    border: 1px solid #60a5fa !important;
    box-shadow:
        0 4px 18px rgba(37,99,235,0.45),
        0 0 20px -2px rgba(96,165,250,0.38),
        inset 0 1px 1px rgba(255,255,255,0.3) !important;
    color: #ffffff !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(
        135deg,
        #3b82f6 0%,
        #2563eb 100%
    ) !important;
    border-color: #93c5fd !important;
    box-shadow:
        0 6px 24px 2px rgba(37,99,235,0.6),
        0 0 28px 2px rgba(56,189,248,0.55),
        inset 0 1px 2px rgba(255,255,255,0.5) !important;
    transform: translateY(-1px);
}


/* ============================================================
   SELECT
   ============================================================ */

div[data-baseweb="select"] > div {
    background: linear-gradient(
        145deg,
        #0e172a 0%,
        #090f1d 100%
    ) !important;
    border: 1px solid rgba(59,130,246,0.32) !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] > div:hover,
div[data-baseweb="select"] > div:focus-within {
    border-color: #38bdf8 !important;
}


/* ============================================================
   DATAFRAME
   ============================================================ */

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(59,130,246,0.22) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    background: linear-gradient(
        180deg,
        #0a0f1c 0%,
        #060912 100%
    ) !important;
}


/* ============================================================
   INFO BOXES
   ============================================================ */

.info-card-box {
    background: linear-gradient(145deg,#0e1a31,#080f1d);
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 14px;
    padding: 18px;
    color: #cbd5e1;
    line-height: 1.6;
}

.warning-card-box {
    background: linear-gradient(145deg,#211b0c,#130f08);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 14px;
    padding: 16px;
    color: #f8fafc;
}


/* ============================================================
   CHAT
   ============================================================ */

.chat-bubble-user {
    background: linear-gradient(135deg,#1d4ed8,#2563eb);
    border-radius: 16px 16px 4px 16px;
    padding: 14px 17px;
    margin: 8px 0 8px 20%;
    color: white;
}

.chat-bubble-ai {
    background: linear-gradient(145deg,#0e172a,#080e19);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 16px 16px 16px 4px;
    padding: 14px 17px;
    margin: 8px 20% 8px 0;
    color: #cbd5e1;
}

.chat-meta {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #94a3b8;
    margin-bottom: 7px;
}


/* ============================================================
   FOOTER
   ============================================================ */

.app-footer {
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid rgba(255,255,255,0.05);
    text-align: center;
    color: #475569;
    font-size: 11px;
}

</style>""",
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

@st.cache_data(show_spinner=False)
def load_csv(path):
    try:
        if path.exists() and path.stat().st_size > 0:
            return pd.read_csv(path)
    except Exception:
        pass
    return pd.DataFrame()


def save_uploaded_dataset(uploaded_file, target_path):
    if uploaded_file is not None:
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        load_csv.clear()
        return True

    return False


def find_column(df, possible_names):
    if df.empty:
        return None

    lower_map = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for name in possible_names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]

    for col in df.columns:
        col_lower = str(col).lower()

        for name in possible_names:
            if name.lower() in col_lower:
                return col

    return None


def style_chart(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color="#8a99ad",
            size=11
        ),
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#8a99ad", size=11)
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#2563eb",
            font_color="#ffffff",
            font_size=11,
            font_family="Plus Jakarta Sans, sans-serif"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#1a273e",
        tickfont=dict(color="#64748b")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#131c2e",
        zeroline=False,
        linecolor="#1a273e",
        tickfont=dict(color="#64748b")
    )

    return fig


def run_main_pipeline():
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        result = subprocess.run(
            [
                sys.executable,
                str(BASE_DIR / "main.py")
            ],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            env=env
        )

        if result.returncode == 0:
            st.session_state.pipeline_last_run = datetime.now()
            load_csv.clear()
            return True, result.stdout

        return False, result.stderr

    except Exception as e:
        return False, str(e)


def get_reconciliation_data():
    return (
        load_csv(FILE_RECON),
        load_csv(FILE_UNCLAIMED)
    )


def get_tax_data():
    return load_csv(FILE_TAX)


def get_forecast_data():
    return load_csv(FILE_FORECAST)


# ============================================================
# REQUIRED FILE CHECK
# ============================================================

required_files = [
    FILE_RECON,
    FILE_UNCLAIMED,
    FILE_TAX,
    FILE_FORECAST
]

missing_files = [
    file
    for file in required_files
    if not file.exists() or file.stat().st_size == 0
]

if missing_files:
    with st.spinner("Preparing finance pipeline..."):
        success, output = run_main_pipeline()

    if not success:
        st.warning(
            "Some pipeline output files are unavailable. "
            "Check your input data and run the finance pipeline."
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """<div class="brand-wrapper">
    <div class="brand-icon">💼</div>
    <div>
        <div class="brand-text-title">FinAI Controller</div>
        <div class="brand-text-sub">Ledger & Audit Intelligence</div>
    </div>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div class="status-badge-card">
    <div class="status-badge-sub">System Status</div>
    <div class="status-badge-val">
        <span class="dot-pulse"></span>
        Operational Engine
    </div>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='font-size:11px;
        font-weight:700;
        color:#64748b;
        text-transform:uppercase;
        letter-spacing:0.8px;
        margin-bottom:8px;'>
        Navigation
        </p>
        """,
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "📊 Executive Dashboard",
            "🔍 Reconciliation Engine",
            "⚖️ Tax & Compliance Audit",
            "📈 14-Day Cash Forecasting",
            "🤖 Financial AI Agent",
            "📑 Audit Reports"
        ],
        label_visibility="collapsed"
    )

    st.markdown(
        """
        <div style='margin-top:20px;
        margin-bottom:20px;
        border-top:1px solid #162032;'>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 Run Finance Pipeline",
        use_container_width=True,
        type="primary"
    ):

        with st.spinner("Running finance pipeline..."):
            success, output = run_main_pipeline()

        if success:
            st.success("Pipeline completed successfully.")
            st.rerun()

        else:
            st.error("Pipeline execution failed.")

            if output:
                st.code(output[-3000:])

    if st.session_state.pipeline_last_run:
        run_time = st.session_state.pipeline_last_run.strftime(
            "%d %b %Y • %I:%M %p"
        )
    else:
        run_time = "Not run in this session"

    st.markdown(
        f"""
        <div style="font-size:10px;
        color:#64748b;
        margin-top:16px;
        line-height:1.6;
        padding:0 4px;">
        Last pipeline run<br>
        <b style="color:#94a3b8;">
        {run_time}
        </b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP HEADER
# ============================================================

st.markdown(
    """<div class="fintech-header">
    <div>
        <div class="fintech-title">Financial Control Center</div>
        <div class="fintech-sub">
            Reconciliation • Tax Compliance • Cash Forecasting • AI Financial Analysis
        </div>
    </div>
    <div class="fintech-pill">● LIVE AUDIT ACTIVE</div>
</div>""",
    unsafe_allow_html=True
)


# ============================================================
# 1. EXECUTIVE DASHBOARD
# ============================================================

if page == "📊 Executive Dashboard":

    # --------------------------------------------------------
    # LOAD DATA FIRST
    # --------------------------------------------------------

    recon_df, unclaimed_df = get_reconciliation_data()
    tax_df = get_tax_data()
    forecast_df = get_forecast_data()

    # --------------------------------------------------------
    # CALCULATE METRICS
    # --------------------------------------------------------

    matched_count = 0
    exception_count = 0
    total_count = 0

    if not recon_df.empty:

        status_col = find_column(
            recon_df,
            [
                "status",
                "match_status",
                "reconciliation_status"
            ]
        )

        if status_col:

            status_series = (
                recon_df[status_col]
                .astype(str)
                .str.lower()
            )

            matched_count = status_series.str.contains(
                r"\b(match|matched|reconciled|success)\b",
                regex=True,
                na=False
            ).sum()

            total_count = len(recon_df)

            exception_count = max(
                total_count - matched_count,
                0
            )

        else:
            total_count = len(recon_df)

    match_rate = (
        matched_count / total_count * 100
        if total_count
        else 0
    )

    unclaimed_amount = 0

    if not unclaimed_df.empty:

        amount_col = find_column(
            unclaimed_df,
            [
                "amount",
                "transaction_amount",
                "value"
            ]
        )

        if amount_col:

            unclaimed_amount = (
                pd.to_numeric(
                    unclaimed_df[amount_col],
                    errors="coerce"
                )
                .fillna(0)
                .sum()
            )

    # ========================================================
    # FRONT SECTION — CHARTS FIRST
    # ========================================================

    st.markdown(
        """<div class="view-title">
        Executive Financial Overview
</div>
<div class="view-sub">
Real-time view of settlement health and projected liquidity.
</div>""",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # CHART 1 — SETTLEMENT
    # CHART 2 — LIQUIDITY
    # --------------------------------------------------------

    left, right = st.columns([1, 1.65])

    with left:

        st.markdown(
            """<div class="fintech-card">
    <div class="fintech-card-title">
        🧾 Settlement Breakdown
    </div>
    <div class="fintech-card-sub">
        Reconciled versus outstanding records
    </div>
</div>""",
            unsafe_allow_html=True
        )

        settlement_df = pd.DataFrame({
            "Status": [
                "Matched",
                "Exceptions"
            ],
            "Count": [
                matched_count,
                exception_count
            ]
        })

        fig = px.pie(
            settlement_df,
            names="Status",
            values="Count",
            hole=0.68,
            color="Status",
            color_discrete_map={
                "Matched": "#2563eb",
                "Exceptions": "#38bdf8"
            }
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent",
            marker=dict(
                line=dict(
                    color="#07090e",
                    width=4
                )
            ),
            hovertemplate=(
                "<b>%{label}</b>"
                "<br>Records: %{value}"
                "<br>Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig = style_chart(fig, 330)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with right:

        st.markdown(
            """<div class="fintech-card">
    <div class="fintech-card-title">
        💧 Liquidity & Cash Trajectory
    </div>
    <div class="fintech-card-sub">
        Forecasted cash movement and projected balance
    </div>
</div>""",
            unsafe_allow_html=True
        )

        chart_df = pd.DataFrame()

        if not forecast_df.empty:

            date_col = find_column(
                forecast_df,
                [
                    "date",
                    "forecast_date",
                    "transaction_date"
                ]
            )

            balance_col = find_column(
                forecast_df,
                [
                    "predicted_balance",
                    "forecast_balance",
                    "balance",
                    "closing_balance"
                ]
            )

            if date_col and balance_col:

                chart_df = forecast_df[
                    [date_col, balance_col]
                ].copy()

                chart_df.columns = [
                    "Date",
                    "Balance"
                ]

                chart_df["Date"] = pd.to_datetime(
                    chart_df["Date"],
                    errors="coerce"
                )

                chart_df["Balance"] = pd.to_numeric(
                    chart_df["Balance"],
                    errors="coerce"
                )

                chart_df = chart_df.dropna()

        if not chart_df.empty:

            fig_cash = go.Figure()

            fig_cash.add_trace(
                go.Scatter(
                    x=chart_df["Date"],
                    y=chart_df["Balance"],
                    mode="lines+markers",
                    line=dict(
                        color="#3b82f6",
                        width=3,
                        shape="spline"
                    ),
                    marker=dict(
                        size=6,
                        color="#60a5fa",
                        line=dict(
                            color="#1d4ed8",
                            width=2
                        )
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(37,99,235,0.12)",
                    hovertemplate=(
                        "<b>%{x|%d %b}</b>"
                        "<br>Balance: $%{y:,.2f}"
                        "<extra></extra>"
                    )
                )
            )

            fig_cash = style_chart(
                fig_cash,
                330
            )

            st.plotly_chart(
                fig_cash,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:

            st.info(
                "Cash forecast data is not currently available."
            )

    # ========================================================
    # METRICS AFTER CHARTS
    # ========================================================

    st.markdown(
        "<div style='height:12px;'></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div class="view-title">
        Financial Health Metrics
</div>
<div class="view-sub">
Key indicators from the current finance pipeline.
</div>""",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Reconciliation Rate",
            f"{match_rate:.1f}%",
            "Ledger health"
        )

    with col2:
        st.metric(
            "Matched Records",
            f"{matched_count:,}",
            "Reconciled"
        )

    with col3:
        st.metric(
            "Exceptions",
            f"{exception_count:,}",
            "Requires action"
        )

    with col4:
        st.metric(
            "Unclaimed Bank Funds",
            f"${unclaimed_amount:,.2f}",
            "Outstanding"
        )

    # ========================================================
    # QUICK AI CHECK
    # ========================================================

    st.markdown(
        "<div style='height:20px;'></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div class="view-title">
        🤖 Quick AI Finance Check
</div>
<div class="view-sub">
Ask the financial AI agent about your current reconciliation
and compliance status.
</div>""",
        unsafe_allow_html=True
    )

    query = st.text_input(
        "Ask your finance question",
        placeholder=(
            "Example: Which reconciliation exceptions "
            "need immediate attention?"
        ),
        label_visibility="collapsed"
    )

    if query:

        if qa_agent is not None:

            try:
                answer = qa_agent.ask_agent(query)

            except Exception as e:
                answer = f"Unable to query AI agent: {e}"

        else:

            answer = (
                "The Financial AI Agent module is not currently "
                "available. Please ensure qa_agent.py is present."
            )

        st.markdown(
            f"""<div class="info-card-box">
    <b style="color:#60a5fa;">🤖 AI Analysis</b>
    <br><br>
    {answer}
</div>""",
            unsafe_allow_html=True
        )

    # ========================================================
    # FILE UPLOAD — MOVED TO BOTTOM
    # ========================================================

    st.markdown(
        "<div style='height:35px;'></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div class="view-title">
        📂 Dataset Update Center
</div>
<div class="view-sub">
Upload new financial datasets only when you want to replace
the current data used by the finance pipeline.
</div>""",
        unsafe_allow_html=True
    )

    upload_col1, upload_col2, upload_col3 = st.columns(3)

    with upload_col1:

        st.markdown(
            """<div class="upload-card">
    <div class="upload-title">🏦 Bank Statement</div>
    <div class="upload-sub">
        Bank-side transaction records used for reconciliation.
    </div>
</div>""",
            unsafe_allow_html=True
        )

        bank_file = st.file_uploader(
            "Upload Bank Statement CSV",
            type=["csv"],
            key="bank_statement_upload",
            help="Upload your bank transaction CSV."
        )

    with upload_col2:

        st.markdown(
            """<div class="upload-card">
    <div class="upload-title">📒 Internal Ledger</div>
    <div class="upload-sub">
        Internal accounting records used for reconciliation.
    </div>
</div>""",
            unsafe_allow_html=True
        )

        ledger_file = st.file_uploader(
            "Upload Internal Ledger CSV",
            type=["csv"],
            key="internal_ledger_upload",
            help="Upload your internal ledger CSV."
        )

    with upload_col3:

        st.markdown(
            """<div class="upload-card">
    <div class="upload-title">💰 Cash Flow History</div>
    <div class="upload-sub">
        Historical cash movement used for 14-day forecasting.
    </div>
</div>""",
            unsafe_allow_html=True
        )

        cashflow_file = st.file_uploader(
            "Upload Cash Flow History CSV",
            type=["csv"],
            key="cashflow_history_upload",
            help="Upload historical cash flow CSV."
        )

    status_cols = st.columns(3)

    with status_cols[0]:

        if bank_file is not None:
            st.success(
                f"Bank Statement ready: {bank_file.name}"
            )
        else:
            st.caption(
                "Using current bank_statement.csv"
            )

    with status_cols[1]:

        if ledger_file is not None:
            st.success(
                f"Internal Ledger ready: {ledger_file.name}"
            )
        else:
            st.caption(
                "Using current internal_ledger.csv"
            )

    with status_cols[2]:

        if cashflow_file is not None:
            st.success(
                f"Cash Flow ready: {cashflow_file.name}"
            )
        else:
            st.caption(
                "Using current cashflow_history.csv"
            )

    st.markdown(
        "<div style='height:10px;'></div>",
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 Update Datasets & Run Pipeline",
        use_container_width=True,
        type="primary",
        key="update_and_run_pipeline"
    ):

        uploaded_any = False

        if bank_file is not None:
            save_uploaded_dataset(
                bank_file,
                FILE_BANK
            )
            uploaded_any = True

        if ledger_file is not None:
            save_uploaded_dataset(
                ledger_file,
                FILE_LEDGER
            )
            uploaded_any = True

        if cashflow_file is not None:
            save_uploaded_dataset(
                cashflow_file,
                FILE_CASHFLOW_HIST
            )
            uploaded_any = True

        if uploaded_any:

            with st.spinner(
                "Processing datasets and refreshing financial analysis..."
            ):

                success, output = run_main_pipeline()

            if success:

                st.success(
                    "Datasets updated successfully. "
                    "Reconciliation, tax analysis, cash forecasting "
                    "and reports have been refreshed."
                )

                st.rerun()

            else:

                st.error(
                    "Pipeline execution failed."
                )

                if output:
                    st.code(output[-3000:])

        else:

            st.warning(
                "Please upload at least one CSV dataset "
                "before running the pipeline."
            )


# ============================================================
# 2. RECONCILIATION ENGINE
# ============================================================

elif page == "🔍 Reconciliation Engine":

    recon_df, unclaimed_df = get_reconciliation_data()

    st.markdown(
        """<div class="view-title">
        🔍 Reconciliation Engine
</div>
<div class="view-sub">
Compare internal ledger activity with bank-side transactions
and isolate exceptions.
</div>""",
        unsafe_allow_html=True
    )

    matched_count = 0
    exception_count = 0

    if not recon_df.empty:

        status_col = find_column(
            recon_df,
            [
                "status",
                "match_status",
                "reconciliation_status"
            ]
        )

        if status_col:

            statuses = (
                recon_df[status_col]
                .astype(str)
                .str.lower()
            )

            matched_count = statuses.str.contains(
                r"\b(match|matched|reconciled|success)\b",
                regex=True,
                na=False
            ).sum()

            exception_count = (
                len(recon_df) - matched_count
            )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Total Records",
            f"{len(recon_df):,}"
        )

    with c2:
        st.metric(
            "Matched",
            f"{matched_count:,}"
        )

    with c3:
        st.metric(
            "Exceptions",
            f"{exception_count:,}"
        )

    tab1, tab2 = st.tabs(
        [
            "📚 Ledger vs Bank",
            "💰 Unclaimed Bank Deposits"
        ]
    )

    with tab1:

        if recon_df.empty:

            st.warning(
                "No reconciliation results available."
            )

        else:

            status_col = find_column(
                recon_df,
                [
                    "status",
                    "match_status",
                    "reconciliation_status"
                ]
            )

            if status_col:

                statuses = (
                    ["All"] +
                    sorted(
                        recon_df[status_col]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                )

                selected_status = st.selectbox(
                    "Filter by status",
                    statuses
                )

                display_df = recon_df.copy()

                if selected_status != "All":

                    display_df = display_df[
                        display_df[status_col]
                        .astype(str)
                        == selected_status
                    ]

            else:

                display_df = recon_df.copy()

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

    with tab2:

        if unclaimed_df.empty:

            st.info(
                "No unclaimed bank records were detected."
            )

        else:

            amount_col = find_column(
                unclaimed_df,
                [
                    "amount",
                    "transaction_amount",
                    "value"
                ]
            )

            if amount_col:

                total_unclaimed = (
                    pd.to_numeric(
                        unclaimed_df[amount_col],
                        errors="coerce"
                    )
                    .fillna(0)
                    .sum()
                )

                st.markdown(
                    f"""<div class="warning-card-box">
    💰 <b>Unclaimed Exposure:</b>
    ${total_unclaimed:,.2f}
</div>""",
                    unsafe_allow_html=True
                )

            st.dataframe(
                unclaimed_df,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# 3. TAX & COMPLIANCE
# ============================================================

elif page == "⚖️ Tax & Compliance Audit":

    tax_df = get_tax_data()

    st.markdown(
        """<div class="view-title">
        ⚖️ Tax & Compliance Audit
</div>
<div class="view-sub">
Analyze invoice classification, tax categories,
and items flagged for human review.
</div>""",
        unsafe_allow_html=True
    )

    total_invoices = len(tax_df)
    distinct_tax_codes = 0
    pending_reviews = 0

    if not tax_df.empty:

        tax_code_col = find_column(
            tax_df,
            [
                "tax_code",
                "tax_category",
                "tax_type",
                "category"
            ]
        )

        if tax_code_col:

            distinct_tax_codes = (
                tax_df[tax_code_col]
                .dropna()
                .astype(str)
                .nunique()
            )

        status_col = find_column(
            tax_df,
            [
                "status",
                "review_status",
                "classification_status"
            ]
        )

        if status_col:

            statuses = (
                tax_df[status_col]
                .astype(str)
                .str.lower()
            )

            pending_reviews = statuses.str.contains(
                "pending|review|flag"
            ).sum()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Audited Invoices",
            f"{total_invoices:,}"
        )

    with c2:
        st.metric(
            "Tax Categories",
            f"{distinct_tax_codes:,}"
        )

    with c3:
        st.metric(
            "Pending Review",
            f"{pending_reviews:,}"
        )

    if not tax_df.empty:

        category_col = find_column(
            tax_df,
            [
                "tax_category",
                "category",
                "tax_code",
                "tax_type",
                "classification"
            ]
        )

        if category_col:

            tax_counts = (
                tax_df[category_col]
                .fillna("Unclassified")
                .astype(str)
                .value_counts()
                .reset_index()
            )

            tax_counts.columns = [
                "Category",
                "Count"
            ]

            left, right = st.columns([1.3, 1])

            with left:

                st.markdown(
                    """<div class="fintech-card">
    <div class="fintech-card-title">
        🧾 Tax Classification Distribution
    </div>
    <div class="fintech-card-sub">
        Categorized invoice shares
    </div>
</div>""",
                    unsafe_allow_html=True
                )

                fig_tax = px.pie(
                    tax_counts,
                    names="Category",
                    values="Count",
                    hole=0.62,
                    color_discrete_sequence=[
                        "#2563eb",
                        "#38bdf8",
                        "#0ea5e9",
                        "#6366f1",
                        "#475569"
                    ]
                )

                fig_tax.update_traces(
                    textposition="outside",
                    textinfo="label+percent",
                    marker=dict(
                        line=dict(
                            color="#07090e",
                            width=3
                        )
                    ),
                    hovertemplate=(
                        "<b>%{label}</b>"
                        "<br>Count: %{value}"
                        "<br>Share: %{percent}"
                        "<extra></extra>"
                    )
                )

                fig_tax = style_chart(
                    fig_tax,
                    360
                )

                st.plotly_chart(
                    fig_tax,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            with right:

                st.markdown(
                    """<div class="fintech-card">
    <div class="fintech-card-title">
        📊 Category Summary
    </div>
    <div class="fintech-card-sub">
        Invoice volume breakdown
    </div>
</div>""",
                    unsafe_allow_html=True
                )

                summary_df = tax_counts.copy()

                summary_df["Share"] = (
                    summary_df["Count"]
                    / summary_df["Count"].sum()
                    * 100
                ).round(1).astype(str) + "%"

                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "Tax category information is not available."
            )

    else:

        st.warning(
            "Tax matching results are not available."
        )

    st.markdown(
        "<div style='height:20px;'></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div class="view-title">
        🚩 Review Flagged Line Items
</div>
<div class="view-sub">
Transactions requiring additional audit approval
or manual classification.
</div>""",
        unsafe_allow_html=True
    )

    if not tax_df.empty:

        status_col = find_column(
            tax_df,
            [
                "status",
                "review_status",
                "classification_status"
            ]
        )

        flagged_df = tax_df.copy()

        if status_col:

            flagged_mask = (
                flagged_df[status_col]
                .astype(str)
                .str.lower()
                .str.contains(
                    "pending|review|flag|exception"
                )
            )

            flagged_df = flagged_df[flagged_mask]

        if flagged_df.empty:

            st.success(
                "No flagged tax line items were identified."
            )

        else:

            st.dataframe(
                flagged_df,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# 4. CASH FORECASTING
# ============================================================

elif page == "📈 14-Day Cash Forecasting":

    forecast_df = get_forecast_data()

    st.markdown(
        """<div class="view-title">
        📈 14-Day Cash Forecasting
</div>
<div class="view-sub">
Monitor liquidity trajectory, baseline burn rate,
and runway projections.
</div>""",
        unsafe_allow_html=True
    )

    timeframe = st.radio(
        "Forecast timeframe",
        [
            "1 Week",
            "2 Weeks",
            "Custom"
        ],
        horizontal=True
    )

    if timeframe == "1 Week":
        days = 7
    elif timeframe == "2 Weeks":
        days = 14
    else:
        days = st.slider(
            "Forecast days",
            1,
            30,
            14
        )

    prepared_forecast = pd.DataFrame()

    if not forecast_df.empty:

        date_col = find_column(
            forecast_df,
            [
                "date",
                "forecast_date",
                "transaction_date"
            ]
        )

        balance_col = find_column(
            forecast_df,
            [
                "predicted_balance",
                "forecast_balance",
                "balance",
                "closing_balance"
            ]
        )

        if date_col and balance_col:

            prepared_forecast = forecast_df[
                [date_col, balance_col]
            ].copy()

            prepared_forecast.columns = [
                "Date",
                "Balance"
            ]

            prepared_forecast["Date"] = pd.to_datetime(
                prepared_forecast["Date"],
                errors="coerce"
            )

            prepared_forecast["Balance"] = pd.to_numeric(
                prepared_forecast["Balance"],
                errors="coerce"
            )

            prepared_forecast = (
                prepared_forecast
                .dropna()
                .sort_values("Date")
                .head(days)
            )

    current_balance = (
        prepared_forecast["Balance"].iloc[0]
        if not prepared_forecast.empty
        else 0
    )

    predicted_balance = (
        prepared_forecast["Balance"].iloc[-1]
        if not prepared_forecast.empty
        else 0
    )

    lowest_balance = (
        prepared_forecast["Balance"].min()
        if not prepared_forecast.empty
        else 0
    )

    peak_balance = (
        prepared_forecast["Balance"].max()
        if not prepared_forecast.empty
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Current Balance",
            f"${current_balance:,.2f}"
        )

    with c2:
        st.metric(
            "Predicted Balance",
            f"${predicted_balance:,.2f}",
            f"{predicted_balance-current_balance:+,.2f}"
        )

    with c3:
        st.metric(
            "Lowest Dip",
            f"${lowest_balance:,.2f}"
        )

    with c4:
        st.metric(
            "Projected Peak",
            f"${peak_balance:,.2f}"
        )

    st.markdown(
        """<div class="fintech-card">
    <div class="fintech-card-title">
        💧 Cash Balance Projection Curve
    </div>
    <div class="fintech-card-sub">
        Simulated cash trajectory over chosen window
    </div>
</div>""",
        unsafe_allow_html=True
    )

    if not prepared_forecast.empty:

        fig_forecast = go.Figure()

        fig_forecast.add_trace(
            go.Scatter(
                x=prepared_forecast["Date"],
                y=prepared_forecast["Balance"],
                mode="lines+markers",
                name="Liquidity",
                line=dict(
                    color="#3b82f6",
                    width=3.5,
                    shape="spline"
                ),
                marker=dict(
                    size=7,
                    color="#60a5fa",
                    line=dict(
                        color="#1e3a8a",
                        width=2
                    )
                ),
                fill="tozeroy",
                fillcolor="rgba(37,99,235,0.12)",
                hovertemplate=(
                    "<b>%{x|%d %b %Y}</b>"
                    "<br>Projected Balance: $%{y:,.2f}"
                    "<extra></extra>"
                )
            )
        )

        fig_forecast = style_chart(
            fig_forecast,
            380
        )

        st.plotly_chart(
            fig_forecast,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    else:

        st.info(
            "Cash forecast data is not available."
        )

    with st.expander(
        "📅 View Projected Ledger Schedule",
        expanded=False
    ):

        if not prepared_forecast.empty:

            st.dataframe(
                prepared_forecast,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No projected ledger schedule available."
            )


# ============================================================
# 5. FINANCIAL AI AGENT
# ============================================================

elif page == "🤖 Financial AI Agent":

    st.markdown(
        """<div class="view-title">
        🤖 Financial AI Agent
</div>
<div class="view-sub">
Ask questions regarding exceptions, audit records,
and liquidity status.
</div>""",
        unsafe_allow_html=True
    )

    if qa_agent is not None:

        st.markdown(
            """<div class="info-card-box">
    🟢 <b>AI Copilot Online</b>
    — Financial analysis engine is ready to assist.
</div>""",
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """<div class="warning-card-box">
    🟡 <b>AI Module Offline</b>
    — <code>qa_agent.py</code> was not found.
</div>""",
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <p style='font-size:12px;
        font-weight:700;
        color:#94a3b8;'>
        💡 Suggested Quick Questions
        </p>
        """,
        unsafe_allow_html=True
    )

    prompt_cols = st.columns(3)

    suggested_prompts = [
        "Which transactions failed reconciliation?",
        "What are the main tax compliance risks?",
        "Will cash balance fall below a safe level?"
    ]

    for i, prompt in enumerate(suggested_prompts):

        with prompt_cols[i]:

            if st.button(
                prompt,
                use_container_width=True,
                key=f"prompt_{i}"
            ):

                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": prompt
                    }
                )

                if qa_agent is not None:

                    try:
                        response = qa_agent.ask_agent(prompt)

                    except Exception as e:
                        response = f"AI Agent error: {e}"

                else:

                    response = (
                        "AI Agent is unavailable. "
                        "Please check qa_agent.py."
                    )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": response
                    }
                )

                st.rerun()

    if st.button("🗑️ Clear History"):

        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "Chat history cleared. "
                    "How can I assist with your financial records?"
                )
            }
        ]

        st.rerun()

    for message in st.session_state.chat_history:

        content = (
            str(message["content"])
            .replace("\n", "<br>")
        )

        if message["role"] == "user":

            st.markdown(
                f"""<div class="chat-bubble-user">
    <div class="chat-meta">YOU</div>
    {content}
</div>""",
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""<div class="chat-bubble-ai">
    <div class="chat-meta">
        🤖 FINAI AUDITOR
    </div>
    {content}
</div>""",
                unsafe_allow_html=True
            )

    user_query = st.chat_input(
        "Ask the Financial AI Agent..."
    )

    if user_query:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_query
            }
        )

        if qa_agent is not None:

            try:
                answer = qa_agent.ask_agent(user_query)

            except Exception as e:

                answer = (
                    "I encountered an issue while "
                    f"processing your question: {e}"
                )

        else:

            answer = (
                "The Financial AI Agent is "
                "not currently available."
            )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.rerun()


# ============================================================
# 6. AUDIT REPORTS
# ============================================================

elif page == "📑 Audit Reports":

    st.markdown(
        """<div class="view-title">
        📑 Audit Reports
</div>
<div class="view-sub">
Generate and review the consolidated financial audit package.
</div>""",
        unsafe_allow_html=True
    )

    st.markdown(
        """<div class="fintech-card">
    <div class="fintech-card-title">
        📋 Consolidated Finance Report
    </div>
    <div class="fintech-card-sub">
        Reconciliation, tax matching and cash forecasting
        packaged into an audit-ready artifact.
    </div>
</div>""",
        unsafe_allow_html=True
    )

    if st.button(
        "📊 Generate Latest Audit Report",
        type="primary"
    ):

        report_file = BASE_DIR / "report.py"

        if report_file.exists():

            with st.spinner(
                "Generating audit report..."
            ):

                try:

                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    env["PYTHONUTF8"] = "1"

                    result = subprocess.run(
                        [
                            sys.executable,
                            str(report_file)
                        ],
                        cwd=str(BASE_DIR),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=180,
                        env=env
                    )

                    if result.returncode == 0:

                        st.success(
                            "Audit report generated successfully."
                        )

                    else:

                        st.error(
                            "Report generation failed."
                        )

                        if result.stderr:
                            st.code(
                                result.stderr[-2000:]
                            )

                except Exception as e:

                    st.error(
                        f"Unable to generate report: {e}"
                    )

        else:

            st.warning(
                "report.py was not found in the project directory."
            )

    if FILE_REPORT_HTML.exists():

        with open(
            FILE_REPORT_HTML,
            "rb"
        ) as rf:

            st.download_button(
                label="⬇️ Download Audit Report (HTML)",
                data=rf,
                file_name="finai_audit_report.html",
                mime="text/html",
                use_container_width=False
            )

    else:

        st.info(
            "Generate the report first to enable download."
        )

    st.markdown(
        '<div class="view-title">📊 Audit Summary Snapshot</div>',
        unsafe_allow_html=True
    )

    recon_df = load_csv(FILE_RECON)
    tax_df = load_csv(FILE_TAX)

    left, right = st.columns(2)

    with left:

        st.markdown(
            """<div class="fintech-card">
    <div class="fintech-card-title">
        🔍 Reconciliation Status Summary
    </div>
</div>""",
            unsafe_allow_html=True
        )

        if recon_df.empty:

            st.info(
                "No reconciliation data available."
            )

        else:

            status_col = find_column(
                recon_df,
                [
                    "status",
                    "match_status",
                    "reconciliation_status"
                ]
            )

            if status_col:

                summary = (
                    recon_df[status_col]
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )

                summary.columns = [
                    "Status",
                    "Count"
                ]

                st.dataframe(
                    summary,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.dataframe(
                    recon_df.head(20),
                    use_container_width=True,
                    hide_index=True
                )

    with right:

        st.markdown(
            """<div class="fintech-card">
    <div class="fintech-card-title">
        ⚖️ Tax Status Summary
    </div>
</div>""",
            unsafe_allow_html=True
        )

        if tax_df.empty:

            st.info(
                "No tax matching data available."
            )

        else:

            category_col = find_column(
                tax_df,
                [
                    "tax_category",
                    "category",
                    "tax_code",
                    "tax_type"
                ]
            )

            if category_col:

                summary = (
                    tax_df[category_col]
                    .fillna("Unclassified")
                    .astype(str)
                    .value_counts()
                    .reset_index()
                )

                summary.columns = [
                    "Category",
                    "Invoices"
                ]

                st.dataframe(
                    summary,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.dataframe(
                    tax_df.head(20),
                    use_container_width=True,
                    hide_index=True
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """<div class="app-footer">
    FinAI Controller
    &nbsp;•&nbsp;
    Enterprise Finance Intelligence
    &nbsp;•&nbsp;
    Ledger
    &nbsp;•&nbsp;
    Tax
    &nbsp;•&nbsp;
    Cash Flow
    &nbsp;•&nbsp;
    AI Audit
</div>""",
    unsafe_allow_html=True
)