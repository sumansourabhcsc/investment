# Working Tools — Enhanced Version
# Improvements:
#   1. SIP vs Lumpsum comparison overlay (Tab 1 & 2)
#   2. Inflation-adjusted real corpus (Tab 1 & 2)
#   3. Nifty 50 benchmark comparison on Fund Return tab (Tab 3)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import requests
from utils.fund_prediction import show_fund_prediction
from utils.fund_comparison import show_fund_comparison

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus – Tools",
    page_icon="🐂",
    layout="wide"
)

# ─────────────────────────────────────────────
# Background + Styling (matches app.py)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Base: deep midnight navy ── */
    .stApp {
        background-color: #020d1a;
        background-image: none;
        position: relative;
        min-height: 100vh;
    }

    /* ── Layer 1: radial teal glow orbs (pure CSS, no image) ── */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background:
            radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(0, 245, 212, 0.07) 0%, transparent 65%),
            radial-gradient(ellipse 60% 80% at 85% 75%,  rgba(0, 180, 245, 0.06) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 50% 100%, rgba(0, 245, 212, 0.04) 0%, transparent 55%),
            radial-gradient(ellipse 100% 100% at 50% 0%,  rgba(2, 20, 40, 0.8)  0%, #020d1a 70%);
        z-index: 0;
        pointer-events: none;
    }

    /* ── Layer 2: fine dot-grid pattern ── */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(circle, rgba(0,245,212,0.18) 1px, transparent 1px);
        background-size: 38px 38px;
        z-index: 0;
        pointer-events: none;
        opacity: 0.55;
    }

    .stApp > * { position: relative; z-index: 1; }

    /* ── Sidebar: dark glass panel ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
        border-right: 1px solid rgba(0,245,212,0.1) !important;
        box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    }

    /* ── Subtle animated pulse on the accent orb ── */
    @keyframes taurus-pulse {
        0%   { opacity: 1; }
        50%  { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .stApp::before { animation: taurus-pulse 8s ease-in-out infinite; }

    /* ── Streamlit main block: slight glass backdrop ── */
    [data-testid="stAppViewContainer"] > section.main > div.block-container {
        background: rgba(2, 16, 32, 0.45);
        border-left: 1px solid rgba(0,245,212,0.07);
        border-right: 1px solid rgba(0,245,212,0.07);
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
        border-radius: 0;
    }

    /* ── Tabs: styled to match the dark theme ── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: rgba(0,245,212,0.04) !important;
        border-bottom: 1px solid rgba(0,245,212,0.15) !important;
        border-radius: 8px 8px 0 0 !important;
        gap: 2px;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        color: rgba(255,255,255,0.5) !important;
        border-radius: 6px 6px 0 0 !important;
        font-size: 13px !important;
        padding: 10px 18px !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        color: #00f5d4 !important;
        background: rgba(0,245,212,0.08) !important;
        border-bottom: 2px solid #00f5d4 !important;
    }

    /* ── Inputs, selects: dark glass style ── */
    .stTextInput input, .stNumberInput input, .stSelectbox select,
    div[data-baseweb="input"] input {
        background: rgba(0,245,212,0.04) !important;
        border: 1px solid rgba(0,245,212,0.2) !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: rgba(0,245,212,0.6) !important;
        box-shadow: 0 0 0 2px rgba(0,245,212,0.12) !important;
    }

    /* ── Primary button: teal glow ── */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #00c9a7 0%, #00f5d4 100%) !important;
        color: #020d1a !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 20px rgba(0,245,212,0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 6px 28px rgba(0,245,212,0.40) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Sliders: teal track ── */
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background: #00f5d4 !important;
        box-shadow: 0 0 8px rgba(0,245,212,0.5) !important;
    }
    html, body, [class*="css"] { color: white; }

    .result-card {
        background: rgba(0, 245, 212, 0.08);
        border: 1px solid rgba(0, 245, 212, 0.35);
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 8px;
    }
    .result-card h3 {
        color: #00f5d4; margin-bottom: 4px; font-size: 14px;
        letter-spacing: 0.12em; text-transform: uppercase;
    }
    .result-card p { font-size: 28px; font-weight: 700; color: white; margin: 0; }
    .result-card .sub { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; }

    /* ── Inflation card: amber tint ── */
    .result-card-inflation {
        background: rgba(255, 193, 7, 0.07);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 8px;
    }
    .result-card-inflation h3 {
        color: #ffc107; margin-bottom: 4px; font-size: 14px;
        letter-spacing: 0.12em; text-transform: uppercase;
    }
    .result-card-inflation p { font-size: 28px; font-weight: 700; color: white; margin: 0; }
    .result-card-inflation .sub { font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px; }

    .gain-positive { color: #00f5d4; font-weight: 600; }
    .gain-negative { color: #ff6b6b; font-weight: 600; }

    .year-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .year-table th {
        color: #00f5d4; text-align: left; padding: 8px 12px;
        border-bottom: 1px solid rgba(0,245,212,0.2);
        font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
    }
    .year-table td {
        padding: 8px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.85);
    }
    .year-table tr:hover td { background: rgba(0,245,212,0.05); }

    .section-label {
        font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
        color: #00f5d4; margin-bottom: 12px; margin-top: 4px;
    }
    .xirr-badge {
        display: inline-block;
        background: rgba(0, 245, 212, 0.15);
        border: 1px solid rgba(0, 245, 212, 0.4);
        border-radius: 20px; padding: 6px 18px;
        font-size: 22px; font-weight: 700; color: #00f5d4; margin-top: 6px;
    }
    .xirr-badge-neg {
        background: rgba(255, 107, 107, 0.15);
        border-color: rgba(255, 107, 107, 0.4); color: #ff6b6b;
    }

    /* ── dual-result section banners ── */
    .calc-section-banner {
        border-radius: 10px;
        padding: 10px 16px;
        margin: 18px 0 10px 0;
        font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
        font-weight: 600;
    }
    .banner-at-end {
        background: rgba(255, 193, 7, 0.10);
        border: 1px solid rgba(255, 193, 7, 0.35);
        color: #ffc107;
    }
    .banner-today {
        background: rgba(0, 245, 212, 0.10);
        border: 1px solid rgba(0, 245, 212, 0.35);
        color: #00f5d4;
    }
    .banner-compare {
        background: rgba(138, 43, 226, 0.10);
        border: 1px solid rgba(138, 43, 226, 0.35);
        color: #bf80ff;
    }
    .banner-inflation {
        background: rgba(255, 193, 7, 0.08);
        border: 1px solid rgba(255, 193, 7, 0.25);
        color: #ffc107;
    }
    .growth-pill {
        display: inline-block;
        background: rgba(0, 245, 212, 0.12);
        border: 1px solid rgba(0, 245, 212, 0.3);
        border-radius: 14px;
        padding: 3px 12px;
        font-size: 12px;
        color: #00f5d4;
        margin-left: 8px;
        vertical-align: middle;
    }
    .growth-pill-warn {
        background: rgba(255, 193, 7, 0.12);
        border-color: rgba(255, 193, 7, 0.3);
        color: #ffc107;
    }

    /* ── Benchmark badge ── */
    .benchmark-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,165,0,0.12);
        border: 1px solid rgba(255,165,0,0.35);
        border-radius: 8px; padding: 8px 14px;
        font-size: 13px; color: #ffb347;
    }
    .benchmark-badge strong { font-size: 18px; }

    .info-box {
        background: rgba(0,245,212,0.05);
        border: 1px solid rgba(0,245,212,0.15);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 12px;
        color: rgba(255,255,255,0.6);
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def fmt_inr(amount: float) -> str:
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def inflation_adjusted(amount: float, years: int, inflation_rate: float = 6.0) -> float:
    """Return today's purchasing-power equivalent of a future amount."""
    return amount / ((1 + inflation_rate / 100) ** years)


def calc_sip(monthly_sip, annual_rate, years, stepup_pct=0.0, lumpsum=0.0):
    monthly_rate = annual_rate / 100 / 12
    breakdown = []
    invested = lumpsum
    corpus = lumpsum
    current_sip = monthly_sip
    for yr in range(1, years + 1):
        for _ in range(12):
            corpus = corpus * (1 + monthly_rate) + current_sip
            invested += current_sip
        breakdown.append({
            "Year": yr, "Monthly SIP": current_sip,
            "Total Invested": invested, "Corpus Value": corpus,
            "Gains": corpus - invested,
        })
        if stepup_pct > 0:
            current_sip = current_sip * (1 + stepup_pct / 100)
    return {
        "total_invested": invested, "final_corpus": corpus,
        "total_gains": corpus - invested,
        "abs_return": ((corpus - invested) / invested * 100) if invested > 0 else 0,
        "breakdown": breakdown,
    }


def calc_lumpsum(principal, annual_rate, years):
    breakdown = []
    for yr in range(1, years + 1):
        corpus = principal * ((1 + annual_rate / 100) ** yr)
        breakdown.append({"Year": yr, "Corpus Value": corpus, "Gains": corpus - principal})
    final = breakdown[-1]["Corpus Value"]
    gains = final - principal
    return {
        "principal": principal, "final_corpus": final, "total_gains": gains,
        "abs_return": (gains / principal * 100) if principal > 0 else 0,
        "breakdown": breakdown,
    }


def render_result_cards(cols_data):
    cols = st.columns(len(cols_data))
    for col, (label, value, sub) in zip(cols, cols_data):
        with col:
            st.markdown(
                f'<div class="result-card"><h3>{label}</h3>'
                f'<p>{value}</p><div class="sub">{sub}</div></div>',
                unsafe_allow_html=True,
            )


def render_inflation_card(real_corpus: float, nominal_corpus: float, years: int, inflation_rate: float):
    """Render an amber inflation-adjusted result card."""
    loss_pct = (1 - real_corpus / nominal_corpus) * 100
    st.markdown(
        f'<div class="result-card-inflation">'
        f'<h3>🌡️ Inflation-Adjusted Value</h3>'
        f'<p>{fmt_inr(real_corpus)}</p>'
        f'<div class="sub">In today\'s purchasing power &nbsp;·&nbsp; '
        f'at {inflation_rate:.0f}% inflation over {years}y &nbsp;·&nbsp; '
        f'<span style="color:#ffc107;">{loss_pct:.1f}% eaten by inflation</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _chart_layout():
    """Shared Plotly layout for all charts."""
    return dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(bgcolor="rgba(0,0,0,0.4)"),
    )


# ─────────────────────────────────────────────
# Nifty 50 Benchmark helpers
# ─────────────────────────────────────────────

def _parse_mfapi_date(d_str: str) -> date:
    """
    Parse dates from mfapi.in which returns DD-MM-YYYY (e.g. '16-05-2026').
    Also handles YYYY-MM-DD just in case.
    """
    parts = d_str.strip().replace("/", "-").split("-")
    if len(parts) != 3:
        raise ValueError(f"Unexpected date format: {d_str}")
    if len(parts[0]) == 4:
        # YYYY-MM-DD
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        # DD-MM-YYYY  ← mfapi standard format
        return date(int(parts[2]), int(parts[1]), int(parts[0]))


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nifty50_nav_history() -> dict:
    """
    Fetch Nifty 50 index fund NAV history from mfapi.in.
    Tries multiple Nifty 50 index fund codes in order:
      120716 — UTI Nifty 50 Index Fund – Direct Growth
      119598 — SBI Nifty Index Fund – Direct Growth
      118989 — HDFC Index Fund Nifty 50 Plan – Direct
    Returns {"code", "name", "navs": {date: float}} or {} on failure.
    """
    # Fund codes for popular Nifty 50 direct index funds on mfapi.in
    candidates = [
        ("120716", "UTI Nifty 50 Index Fund – Direct Growth"),
        ("119598", "SBI Nifty Index Fund – Direct Growth"),
        ("118989", "HDFC Index Fund Nifty 50 Plan – Direct"),
    ]
    last_error = ""
    for code, fallback_name in candidates:
        try:
            r = requests.get(
                f"https://api.mfapi.in/mf/{code}",
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 (Taurus/1.0)"},
            )
            if r.status_code != 200:
                last_error = f"HTTP {r.status_code} for fund {code}"
                continue

            data = r.json()
            nav_dict = {}
            parse_errors = 0
            for entry in data.get("data", []):
                try:
                    d = _parse_mfapi_date(entry["date"])
                    nav_dict[d] = float(entry["nav"])
                except Exception:
                    parse_errors += 1

            if nav_dict:
                scheme_name = data.get("meta", {}).get("scheme_name", fallback_name)
                return {
                    "code": code,
                    "name": scheme_name,
                    "navs": nav_dict,
                    "parse_errors": parse_errors,
                }
            else:
                last_error = f"Fund {code} returned 0 valid NAV entries ({parse_errors} parse errors)"

        except requests.exceptions.Timeout:
            last_error = f"Timeout fetching fund {code}"
        except Exception as e:
            last_error = str(e)

    # All candidates failed — return error info so the UI can show it
    return {"error": last_error}


def calc_benchmark_sip_returns(nav_history: dict, monthly_amount: float,
                                 sip_start: date, sip_end: date) -> dict | None:
    """
    Compute SIP returns for a benchmark fund (Nifty 50 proxy)
    over the same period as the user's fund.
    Returns dict with total_invested, current_value, abs_return_pct, xirr_pct.
    """
    if not nav_history:
        return None
    navs = nav_history["navs"]
    sorted_dates = sorted(navs.keys())

    def nearest_nav(target: date):
        # Find the closest available NAV date on or before target
        candidates = [d for d in sorted_dates if d <= target]
        if not candidates:
            candidates = sorted_dates[:1]
        return candidates[-1], navs[candidates[-1]]

    total_units = 0.0
    total_invested = 0.0

    cur = date(sip_start.year, sip_start.month, 1)
    while cur <= sip_end:
        nav_date, nav = nearest_nav(cur)
        units = monthly_amount / nav
        total_units += units
        total_invested += monthly_amount
        # Next month
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)

    today_date, today_nav = nearest_nav(date.today())
    current_value = total_units * today_nav
    gains = current_value - total_invested
    abs_ret = (gains / total_invested * 100) if total_invested > 0 else 0

    return {
        "name": nav_history["name"],
        "total_invested": total_invested,
        "current_value": current_value,
        "total_gains": gains,
        "abs_return_pct": abs_ret,
        "today_nav": today_nav,
        "today_date": today_date,
    }


def _render_fund_table(table_rows):
    """Render the SIP transaction log table for Fund Return tab."""
    if not table_rows:
        return
    col_labels = {
        "SIP Date":               "SIP Date",
        "NAV Date":               "NAV Date",
        "NAV at Investment (₹)":  "NAV (₹)",
        "Amount Invested (₹)":    "Amount",
        "Units Purchased":        "Units",
        "Cumulative Units":       "Cum. Units",
        "Total Invested (₹)":     "Invested",
        "Current Value (₹)":      "Curr. Value",
        "Gain / Loss (₹)":        "Gain/Loss",
    }
    headers_fr = list(table_rows[0].keys())
    header_html = "".join(
        f'<th style="white-space:nowrap;">{col_labels.get(h, h)}</th>'
        for h in headers_fr
    )
    rows_html = ""
    for row in table_rows:
        r_html = ""
        for k, v in row.items():
            style = 'style="white-space:nowrap;"'
            if k in ("Amount Invested (₹)", "Total Invested (₹)", "Current Value (₹)"):
                r_html += f"<td {style}>{fmt_inr(v)}</td>"
            elif k == "Gain / Loss (₹)":
                color = "#00f5d4" if v >= 0 else "#ff6b6b"
                r_html += f'<td style="white-space:nowrap;color:{color};">{fmt_inr(v)}</td>'
            elif k == "NAV at Investment (₹)":
                r_html += f"<td {style}>₹{v:.4f}</td>"
            elif k in ("Units Purchased", "Cumulative Units"):
                r_html += f"<td {style}>{v:.4f}</td>"
            elif isinstance(v, date):
                r_html += f'<td {style}>{v.strftime("%d %b %y")}</td>'
            else:
                r_html += f"<td {style}>{v}</td>"
        rows_html += f"<tr>{r_html}</tr>"
    st.markdown(
        f'<div style="overflow-x:auto;max-height:400px;overflow-y:auto;'
        f'margin-top:8px;border:1px solid rgba(0,245,212,0.15);border-radius:8px;">'
        f'<table class="year-table" style="min-width:700px;table-layout:auto;">'
        f'<thead><tr>{header_html}</tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def render_breakdown_table(breakdown, currency_keys):
    if not breakdown:
        return
    headers = list(breakdown[0].keys())
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for row in breakdown:
        row_html = ""
        for k, v in row.items():
            if k in currency_keys:
                cell = fmt_inr(v)
            elif k == "Year":
                cell = str(int(v))
            elif isinstance(v, float):
                cell = fmt_inr(v)
            else:
                cell = str(v)
            row_html += f"<td>{cell}</td>"
        rows_html += f"<tr>{row_html}</tr>"
    st.markdown(
        f'<div style="overflow-x:auto;max-height:380px;overflow-y:auto;margin-top:16px;'
        f'border:1px solid rgba(0,245,212,0.15);border-radius:8px;">'
        f'<table class="year-table"><thead><tr>{header_html}</tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Page Header
# ─────────────────────────────────────────────
st.markdown("## 🛠️ Tools")
st.markdown(
    "<div style='color:rgba(255,255,255,0.5);font-size:13px;margin-bottom:24px;'>"
    "Financial calculators to plan and analyse your investments</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab_sip, tab_lumpsum, tab_fund, tab_pred, tab_compare  = st.tabs([
    "📈  SIP Calculator",
    "💰  Lumpsum Calculator",
    "🔍  Fund Return",
    "📈 Fund Prediction",
    "📉  Fund Comparison",      
    "🔧  More (Coming Soon)",
])


# ══════════════════════════════════════════════
# TAB 1 – SIP CALCULATOR
# ══════════════════════════════════════════════
with tab_sip:
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="section-label">Basic Details</div>', unsafe_allow_html=True)
        monthly_sip = st.number_input(
            "Monthly SIP Amount (₹)", min_value=100, max_value=10_000_000,
            value=5000, step=500, key="sip_amount",
        )
        annual_rate = st.slider("Expected Annual Return (%)", 1.0, 30.0, 12.0, 0.5, key="sip_rate")
        years = st.slider("Investment Duration (Years)", 1, 40, 10, 1, key="sip_years")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Optional: Lumpsum Top-up</div>', unsafe_allow_html=True)
        lumpsum = st.number_input(
            "Initial Lumpsum (₹)", min_value=0, max_value=100_000_000,
            value=0, step=1000, key="sip_lumpsum",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Optional: Step-Up SIP</div>', unsafe_allow_html=True)
        enable_stepup = st.toggle("Enable Annual Step-Up", value=False, key="sip_stepup_toggle")
        stepup_pct = 0.0
        if enable_stepup:
            stepup_pct = st.slider("Annual Step-Up (%)", 1.0, 50.0, 10.0, 1.0, key="sip_stepup_pct")
            st.caption(
                f"Your SIP grows: ₹{monthly_sip:,} → "
                f"₹{monthly_sip * ((1 + stepup_pct/100) ** years):,.0f} by Year {years}"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        # ── NEW: Enhancement toggles ──
        st.markdown('<div class="section-label">Analysis Options</div>', unsafe_allow_html=True)

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            show_compare_sip = st.toggle(
                "📊 Compare vs Lumpsum",
                value=False,
                key="sip_compare_toggle",
                help="Overlay Lumpsum chart — same total amount invested as SIP, same rate & duration"
            )
        with col_t2:
            show_inflation_sip = st.toggle(
                "🌡️ Inflation Adjusted",
                value=False,
                key="sip_inflation_toggle",
                help="Show corpus in today's purchasing power after accounting for inflation"
            )

        if show_inflation_sip:
            inflation_rate_sip = st.slider(
                "Assumed Inflation Rate (%)", 3.0, 10.0, 6.0, 0.5, key="sip_inflation_rate"
            )
        else:
            inflation_rate_sip = 6.0

        st.markdown("<br>", unsafe_allow_html=True)
        calc_sip_btn = st.button(
            "📊 Calculate", type="primary", key="calc_sip", width="stretch",
        )

    with right:
        if calc_sip_btn:
            result = calc_sip(monthly_sip, annual_rate, years, stepup_pct, lumpsum)
            gain_cls = "gain-positive" if result["total_gains"] >= 0 else "gain-negative"
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
            render_result_cards([
                ("Total Invested", fmt_inr(result["total_invested"]), "Principal contributed"),
                ("Final Corpus", fmt_inr(result["final_corpus"]),
                 f'<span class="{gain_cls}">{result["abs_return"]:+.1f}% absolute return</span>'),
                ("Total Gains", fmt_inr(result["total_gains"]), f"At {annual_rate}% p.a."),
            ])

            # ── Inflation-Adjusted Card ──
            if show_inflation_sip:
                real_corpus = inflation_adjusted(result["final_corpus"], years, inflation_rate_sip)
                st.markdown("<br>", unsafe_allow_html=True)
                render_inflation_card(real_corpus, result["final_corpus"], years, inflation_rate_sip)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Chart ──
            chart_df = pd.DataFrame({
                "Year": [r["Year"] for r in result["breakdown"]],
                "Invested": [r["Total Invested"] for r in result["breakdown"]],
                "Corpus (SIP)": [r["Corpus Value"] for r in result["breakdown"]],
            }).set_index("Year")

            fig_sip = go.Figure()
            fig_sip.add_trace(go.Scatter(
                x=chart_df.index, y=chart_df["Invested"],
                name="Invested (SIP)", line=dict(color="#4a9eff", width=2),
            ))
            fig_sip.add_trace(go.Scatter(
                x=chart_df.index, y=chart_df["Corpus (SIP)"],
                name="Corpus (SIP)", line=dict(color="#00f5d4", width=2),
            ))

            # ── NEW: Compare vs Lumpsum overlay ──
            if show_compare_sip:
                # Use same total investment amount as lumpsum principal
                equivalent_lumpsum = result["total_invested"]
                result_ls_compare = calc_lumpsum(equivalent_lumpsum, annual_rate, years)
                ls_corpus_by_year = [r["Corpus Value"] for r in result_ls_compare["breakdown"]]
                ls_years = [r["Year"] for r in result_ls_compare["breakdown"]]

                fig_sip.add_trace(go.Scatter(
                    x=ls_years, y=ls_corpus_by_year,
                    name="Corpus (Lumpsum equiv.)",
                    line=dict(color="#bf80ff", width=2, dash="dash"),
                ))

            # ── Inflation line on chart ──
            if show_inflation_sip:
                real_by_year = [
                    inflation_adjusted(r["Corpus Value"], r["Year"], inflation_rate_sip)
                    for r in result["breakdown"]
                ]
                fig_sip.add_trace(go.Scatter(
                    x=chart_df.index, y=real_by_year,
                    name=f"Real Value ({inflation_rate_sip:.0f}% inflation)",
                    line=dict(color="#ffc107", width=2, dash="dot"),
                ))

            fig_sip.update_layout(**_chart_layout())
            st.plotly_chart(fig_sip, width="stretch")

            # ── SIP vs Lumpsum comparison insight banner ──
            if show_compare_sip:
                sip_c = result["final_corpus"]
                ls_c = result_ls_compare["final_corpus"]
                diff = sip_c - ls_c
                winner = "SIP" if diff >= 0 else "Lumpsum"
                diff_pct = abs(diff / ls_c * 100)
                color = "#00f5d4" if diff >= 0 else "#bf80ff"
                st.markdown(
                    f'<div class="calc-section-banner banner-compare">'
                    f'📊 Compare: <strong style="color:{color};">{winner}</strong> wins by '
                    f'<strong style="color:{color};">{fmt_inr(abs(diff))}</strong> '
                    f'({diff_pct:.1f}%) over {years}y &nbsp;·&nbsp; '
                    f'Same ₹{fmt_inr(equivalent_lumpsum)} invested, same {annual_rate}% rate'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="info-box">💡 Lumpsum deploys capital immediately so it compounds '
                    'longer. SIP wins when the market grows during the investment period, '
                    'as periodic buying averages out entry costs (rupee cost averaging).</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div class="section-label" style="margin-top:16px;">Year-by-Year Breakdown</div>',
                unsafe_allow_html=True,
            )
            render_breakdown_table(
                result["breakdown"],
                ["Monthly SIP", "Total Invested", "Corpus Value", "Gains"],
            )
        else:
            st.markdown(
                '<br><br><div style="text-align:center;opacity:0.4;padding:60px 20px;">'
                '<div style="font-size:48px;">📈</div>'
                '<div style="margin-top:12px;font-size:14px;">Fill in the details and hit Calculate</div>'
                '</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════
# TAB 2 – LUMPSUM CALCULATOR
# ══════════════════════════════════════════════
with tab_lumpsum:
    st.markdown("<br>", unsafe_allow_html=True)
    left2, right2 = st.columns([1, 1], gap="large")

    with left2:
        st.markdown('<div class="section-label">Investment Details</div>', unsafe_allow_html=True)
        principal = st.number_input(
            "Investment Amount (₹)", min_value=1000, max_value=100_000_000,
            value=1_00_000, step=1000, key="ls_principal",
        )
        ls_rate = st.slider("Expected Annual Return (%)", 1.0, 30.0, 12.0, 0.5, key="ls_rate")
        ls_years = st.slider("Investment Duration (Years)", 1, 40, 10, 1, key="ls_years")

        st.markdown("<br>", unsafe_allow_html=True)
        # ── NEW: Enhancement toggles ──
        st.markdown('<div class="section-label">Analysis Options</div>', unsafe_allow_html=True)

        col_lt1, col_lt2 = st.columns(2)
        with col_lt1:
            show_compare_ls = st.toggle(
                "📊 Compare vs SIP",
                value=False,
                key="ls_compare_toggle",
                help="Overlay SIP chart — same total invested spread monthly, same rate & duration"
            )
        with col_lt2:
            show_inflation_ls = st.toggle(
                "🌡️ Inflation Adjusted",
                value=False,
                key="ls_inflation_toggle",
                help="Show corpus in today's purchasing power after accounting for inflation"
            )

        if show_inflation_ls:
            inflation_rate_ls = st.slider(
                "Assumed Inflation Rate (%)", 3.0, 10.0, 6.0, 0.5, key="ls_inflation_rate"
            )
        else:
            inflation_rate_ls = 6.0

        st.markdown("<br>", unsafe_allow_html=True)
        calc_ls_btn = st.button(
            "📊 Calculate", type="primary", key="calc_ls", width="stretch",
        )

    with right2:
        if calc_ls_btn:
            result_ls = calc_lumpsum(principal, ls_rate, ls_years)
            gain_cls_ls = "gain-positive" if result_ls["total_gains"] >= 0 else "gain-negative"
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
            render_result_cards([
                ("Principal", fmt_inr(result_ls["principal"]), "One-time investment"),
                ("Final Corpus", fmt_inr(result_ls["final_corpus"]),
                 f'<span class="{gain_cls_ls}">{result_ls["abs_return"]:+.1f}% absolute return</span>'),
                ("Total Gains", fmt_inr(result_ls["total_gains"]), f"At {ls_rate}% p.a."),
            ])

            # ── Inflation-Adjusted Card ──
            if show_inflation_ls:
                real_corpus_ls = inflation_adjusted(result_ls["final_corpus"], ls_years, inflation_rate_ls)
                st.markdown("<br>", unsafe_allow_html=True)
                render_inflation_card(real_corpus_ls, result_ls["final_corpus"], ls_years, inflation_rate_ls)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Chart ──
            chart_df_ls = pd.DataFrame({
                "Year": [r["Year"] for r in result_ls["breakdown"]],
                "Principal": [result_ls["principal"]] * ls_years,
                "Corpus (Lumpsum)": [r["Corpus Value"] for r in result_ls["breakdown"]],
            }).set_index("Year")

            fig_ls = go.Figure()
            fig_ls.add_trace(go.Scatter(
                x=chart_df_ls.index, y=chart_df_ls["Principal"],
                name="Principal", line=dict(color="#4a9eff", width=2),
            ))
            fig_ls.add_trace(go.Scatter(
                x=chart_df_ls.index, y=chart_df_ls["Corpus (Lumpsum)"],
                name="Corpus (Lumpsum)", line=dict(color="#00f5d4", width=2),
            ))

            # ── NEW: Compare vs SIP overlay ──
            if show_compare_ls:
                # Equivalent monthly SIP = principal / (years * 12)
                equivalent_monthly = principal / (ls_years * 12)
                result_sip_compare = calc_sip(equivalent_monthly, ls_rate, ls_years)
                sip_corpus_by_year = [r["Corpus Value"] for r in result_sip_compare["breakdown"]]
                sip_years = [r["Year"] for r in result_sip_compare["breakdown"]]

                fig_ls.add_trace(go.Scatter(
                    x=sip_years, y=sip_corpus_by_year,
                    name=f"Corpus (SIP ₹{equivalent_monthly:,.0f}/mo)",
                    line=dict(color="#bf80ff", width=2, dash="dash"),
                ))

            # ── Inflation line on chart ──
            if show_inflation_ls:
                real_by_year_ls = [
                    inflation_adjusted(r["Corpus Value"], r["Year"], inflation_rate_ls)
                    for r in result_ls["breakdown"]
                ]
                fig_ls.add_trace(go.Scatter(
                    x=chart_df_ls.index, y=real_by_year_ls,
                    name=f"Real Value ({inflation_rate_ls:.0f}% inflation)",
                    line=dict(color="#ffc107", width=2, dash="dot"),
                ))

            fig_ls.update_layout(**_chart_layout())
            st.plotly_chart(fig_ls, width="stretch")

            # ── Lumpsum vs SIP comparison insight banner ──
            if show_compare_ls:
                ls_c = result_ls["final_corpus"]
                sip_c = result_sip_compare["final_corpus"]
                diff = ls_c - sip_c
                winner = "Lumpsum" if diff >= 0 else "SIP"
                diff_pct = abs(diff / sip_c * 100)
                color = "#00f5d4" if diff >= 0 else "#bf80ff"
                st.markdown(
                    f'<div class="calc-section-banner banner-compare">'
                    f'📊 Compare: <strong style="color:{color};">{winner}</strong> wins by '
                    f'<strong style="color:{color};">{fmt_inr(abs(diff))}</strong> '
                    f'({diff_pct:.1f}%) over {ls_years}y &nbsp;·&nbsp; '
                    f'Equiv. SIP = ₹{equivalent_monthly:,.0f}/mo'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="info-box">💡 Lumpsum wins when markets rise steadily — '
                    'your full capital compounds from day one. SIP wins in volatile or '
                    'declining markets via rupee cost averaging.</div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div class="section-label" style="margin-top:16px;">Year-by-Year Breakdown</div>',
                unsafe_allow_html=True,
            )
            render_breakdown_table(result_ls["breakdown"], ["Corpus Value", "Gains"])
        else:
            st.markdown(
                '<br><br><div style="text-align:center;opacity:0.4;padding:60px 20px;">'
                '<div style="font-size:48px;">💰</div>'
                '<div style="margin-top:12px;font-size:14px;">Fill in the details and hit Calculate</div>'
                '</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════
# TAB 3 – FUND RETURN CALCULATOR
# ══════════════════════════════════════════════
with tab_fund:
    from utils.fund_return_calculator import calculate_sip_returns
    from config import mutual_funds

    st.markdown("<br>", unsafe_allow_html=True)
    left3, right3 = st.columns([1, 1], gap="large")

    with left3:
        # ── Fund Selection ──
        st.markdown('<div class="section-label">Select Fund</div>', unsafe_allow_html=True)

        fund_source = st.radio(
            "Fund source",
            ["My Portfolio", "Enter Fund Code"],
            horizontal=True,
            key="fund_source",
            label_visibility="collapsed",
        )

        fund_code = None

        if fund_source == "My Portfolio":
            fund_names = list(mutual_funds.keys())
            selected_fund_name = st.selectbox("Choose from your portfolio", fund_names, key="fund_select")
            fund_code = mutual_funds[selected_fund_name]["code"]
            st.caption(f"Fund code: `{fund_code}`")
        else:
            custom_code = st.text_input(
                "Enter Fund Code (from mfapi.in)",
                placeholder="e.g. 125497",
                key="fund_custom_code",
            )
            fund_code = custom_code.strip() if custom_code else None

        # ── SIP Details ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">SIP Details</div>', unsafe_allow_html=True)

        sip_amount = st.number_input(
            "Monthly SIP Amount (₹)",
            min_value=100, max_value=10_000_000, value=5000, step=500,
            key="fr_sip_amount",
        )

        sip_start = st.date_input(
            "SIP Start Date", value=date(2022, 1, 1), key="fr_sip_start",
            help="SIP will be invested on the 1st of each month from this date",
        )

        # ── Calculation Mode ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Calculation Mode</div>', unsafe_allow_html=True)

        calc_mode = st.radio(
            "calc_mode_radio",
            options=["SIP Ongoing (no end date)", "SIP Stopped (with end date)"],
            key="fr_calc_mode",
            label_visibility="collapsed",
            help=(
                "Ongoing: SIP is still running — shows total value as of today.\n\n"
                "Stopped: SIP ended on a specific date — shows corpus at that date "
                "AND what it's worth today (investments kept compounding)."
            ),
        )

        sip_end = None

        if calc_mode == "SIP Ongoing (no end date)":
            sip_end = date.today()
            st.caption(f"SIP treated as active through today ({sip_end.strftime('%d %b %Y')})")
        else:
            sip_end = st.date_input(
                "SIP End Date",
                value=date(2023, 12, 31),
                key="fr_sip_end_stopped",
                help="The last month in which SIP was invested",
            )
            st.caption(
                "📌 Two results will be shown:\n"
                "① Corpus value **at SIP end date**\n"
                "② Current value **as of today** (corpus kept growing after SIP stopped)"
            )

        # ── NEW: Benchmark toggle ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Analysis Options</div>', unsafe_allow_html=True)
        show_benchmark = st.toggle(
            "📊 Compare vs Nifty 50",
            value=False,
            key="fr_benchmark_toggle",
            help="Fetch Nifty 50 index fund NAV and compare your fund's SIP returns vs the benchmark",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        calc_fund_btn = st.button(
            "🔍 Analyse Fund Returns", type="primary", key="calc_fund",
            width="stretch", disabled=(not fund_code),
        )

    # ── Results ──
    with right3:
        if calc_fund_btn:
            if not fund_code:
                st.error("Please enter or select a fund code.")
            elif sip_end and sip_start >= sip_end:
                st.error("SIP Start Date must be before End Date.")
            else:
                # ── Optionally pre-fetch Nifty 50 benchmark ──
                benchmark_result = None
                if show_benchmark:
                    with st.spinner("Fetching Nifty 50 index data..."):
                        nifty_nav_history = fetch_nifty50_nav_history()
                        if nifty_nav_history.get("navs"):
                            benchmark_result = calc_benchmark_sip_returns(
                                nifty_nav_history, sip_amount, sip_start,
                                sip_end if calc_mode == "SIP Stopped (with end date)" else date.today()
                            )
                        else:
                            err_detail = nifty_nav_history.get("error", "Unknown error")
                            st.warning(
                                f"⚠️ Could not fetch Nifty 50 data — benchmark unavailable.\n\n"
                                f"**Reason:** `{err_detail}`\n\n"
                                f"Check that `api.mfapi.in` is reachable from your Streamlit server."
                            )

                # ────────────────────────────────────────────────
                # MODE A: SIP Ongoing
                # ────────────────────────────────────────────────
                if calc_mode == "SIP Ongoing (no end date)":
                    with st.spinner("Fetching NAV history and calculating returns..."):
                        try:
                            result_fr = calculate_sip_returns(
                                fund_code=fund_code,
                                monthly_amount=sip_amount,
                                sip_start_date=sip_start,
                                sip_end_date=date.today(),
                                valuation_date=date.today(),
                            )
                        except ValueError as e:
                            st.error(f"❌ {e}")
                            result_fr = None

                    if result_fr:
                        st.markdown("<br>", unsafe_allow_html=True)

                        # Fund name banner
                        st.markdown(
                            f'<div style="background:rgba(0,245,212,0.06);border:1px solid rgba(0,245,212,0.2);'
                            f'border-radius:8px;padding:12px 16px;margin-bottom:16px;">'
                            f'<div style="font-size:11px;letter-spacing:0.1em;text-transform:uppercase;'
                            f'color:#00f5d4;">Fund</div>'
                            f'<div style="font-size:15px;font-weight:600;margin-top:2px;">'
                            f'{result_fr["fund_name"]}</div>'
                            f'<div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px;">'
                            f'Code: {result_fr["fund_code"]} &nbsp;|&nbsp; '
                            f'Valuation date: {result_fr["valuation_date"]}</div></div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            '<div class="calc-section-banner banner-today">'
                            '📈 SIP Ongoing — Current Value as of Today'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        gain_cls = "gain-positive" if result_fr["total_gains"] >= 0 else "gain-negative"
                        render_result_cards([
                            ("Total Invested",
                             fmt_inr(result_fr["total_invested"]),
                             f"{len(result_fr['sip_rows'])} SIP instalments"),
                            ("Current Value",
                             fmt_inr(result_fr["current_value"]),
                             f'<span class="{gain_cls}">{result_fr["abs_return_pct"]:+.1f}% absolute</span>'),
                            ("Total Gains",
                             fmt_inr(result_fr["total_gains"]),
                             f'Units held: {result_fr["total_units"]:,.4f}'),
                            ("Latest NAV",
                             f'₹{result_fr["latest_nav"]:.4f}',
                             f'as on {result_fr["latest_nav_date"].strftime("%d %b %Y")}'),
                        ])

                        # XIRR
                        st.markdown("<br>", unsafe_allow_html=True)
                        if result_fr["xirr_pct"] is not None:
                            xv = result_fr["xirr_pct"]
                            badge_cls = "xirr-badge" if xv >= 0 else "xirr-badge xirr-badge-neg"
                            sign = "+" if xv >= 0 else ""
                            st.markdown(
                                f'<div style="text-align:center;padding:12px 0;">'
                                f'<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;'
                                f'color:#00f5d4;margin-bottom:8px;">XIRR (Annualised Return)</div>'
                                f'<span class="{badge_cls}">{sign}{xv:.2f}% p.a.</span></div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.warning(f"XIRR could not be calculated: {result_fr['xirr_error']}")

                        # ── NEW: Nifty 50 Benchmark Comparison ──
                        if show_benchmark and benchmark_result:
                            fund_val = result_fr["current_value"]
                            bench_val = benchmark_result["current_value"]
                            alpha = fund_val - bench_val
                            alpha_pct = result_fr["abs_return_pct"] - benchmark_result["abs_return_pct"]
                            beat = alpha >= 0
                            alpha_color = "#00f5d4" if beat else "#ff6b6b"
                            alpha_label = "outperformed" if beat else "underperformed"

                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown(
                                '<div class="calc-section-banner banner-compare">'
                                '📊 Nifty 50 Benchmark Comparison'
                                '</div>',
                                unsafe_allow_html=True,
                            )

                            bcol1, bcol2, bcol3 = st.columns(3)
                            with bcol1:
                                st.markdown(
                                    f'<div class="result-card">'
                                    f'<h3>Your Fund</h3>'
                                    f'<p>{fmt_inr(fund_val)}</p>'
                                    f'<div class="sub">{result_fr["abs_return_pct"]:+.1f}% absolute</div>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
                            with bcol2:
                                st.markdown(
                                    f'<div class="result-card" style="border-color:rgba(255,165,0,0.35);'
                                    f'background:rgba(255,165,0,0.07);">'
                                    f'<h3 style="color:#ffb347;">Nifty 50 Index</h3>'
                                    f'<p>{fmt_inr(bench_val)}</p>'
                                    f'<div class="sub">{benchmark_result["abs_return_pct"]:+.1f}% absolute</div>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
                            with bcol3:
                                st.markdown(
                                    f'<div class="result-card" style="border-color:rgba({("0,245,212" if beat else "255,107,107")},0.4);'
                                    f'background:rgba({("0,245,212" if beat else "255,107,107")},0.07);">'
                                    f'<h3 style="color:{alpha_color};">Alpha</h3>'
                                    f'<p style="color:{alpha_color};">{fmt_inr(abs(alpha))}</p>'
                                    f'<div class="sub">'
                                    f'Fund {alpha_label} by {abs(alpha_pct):.1f}%'
                                    f'</div></div>',
                                    unsafe_allow_html=True,
                                )

                            verdict = (
                                f'✅ Your fund <strong style="color:#00f5d4;">beat the Nifty 50</strong> '
                                f'by {fmt_inr(abs(alpha))} ({abs(alpha_pct):.1f}%) — '
                                f'active management added value.'
                                if beat else
                                f'⚠️ Your fund <strong style="color:#ff6b6b;">lagged the Nifty 50</strong> '
                                f'by {fmt_inr(abs(alpha))} ({abs(alpha_pct):.1f}%) — '
                                f'a Nifty 50 index fund would have done better.'
                            )
                            st.markdown(
                                f'<div class="info-box" style="margin-top:12px;">'
                                f'{verdict}<br>'
                                f'<span style="font-size:11px;opacity:0.6;">'
                                f'Benchmark: {benchmark_result["name"]} (Nifty 50 proxy via mfapi.in)'
                                f'</span></div>',
                                unsafe_allow_html=True,
                            )

                        # ── Chart ──
                        rows = result_fr["sip_rows"]
                        if rows:
                            chart_data = pd.DataFrame({
                                "Date": [r["NAV Date"] for r in rows],
                                "Invested (₹)": [r["Total Invested (₹)"] for r in rows],
                                "Current Value (₹)": [r["Current Value (₹)"] for r in rows],
                            }).set_index("Date")
                            st.caption("📊 Invested vs Current Value over time")

                            fig_fr = go.Figure()
                            fig_fr.add_trace(go.Scatter(
                                x=chart_data.index, y=chart_data["Invested (₹)"],
                                name="Invested", line=dict(color="#4a9eff", width=2),
                            ))
                            fig_fr.add_trace(go.Scatter(
                                x=chart_data.index, y=chart_data["Current Value (₹)"],
                                name="Current Value", line=dict(color="#00f5d4", width=2),
                            ))
                            fig_fr.update_layout(**_chart_layout())
                            st.plotly_chart(fig_fr, width="stretch")

                        st.markdown(
                            '<div class="section-label" style="margin-top:16px;">SIP Transaction Log</div>',
                            unsafe_allow_html=True,
                        )
                        _render_fund_table(result_fr["sip_rows"])

                # ────────────────────────────────────────────────
                # MODE B: SIP Stopped — two calculations
                # ────────────────────────────────────────────────
                else:
                    result_at_end = None
                    result_today = None

                    with st.spinner("Calculating corpus at SIP end date..."):
                        try:
                            result_at_end = calculate_sip_returns(
                                fund_code=fund_code,
                                monthly_amount=sip_amount,
                                sip_start_date=sip_start,
                                sip_end_date=sip_end,
                                valuation_date=sip_end,
                            )
                        except ValueError as e:
                            st.error(f"❌ (At SIP End) {e}")

                    with st.spinner("Calculating current value as of today..."):
                        try:
                            result_today = calculate_sip_returns(
                                fund_code=fund_code,
                                monthly_amount=sip_amount,
                                sip_start_date=sip_start,
                                sip_end_date=sip_end,
                                valuation_date=date.today(),
                            )
                        except ValueError as e:
                            st.error(f"❌ (Today) {e}")

                    if result_at_end or result_today:
                        st.markdown("<br>", unsafe_allow_html=True)

                        _banner_result = result_at_end or result_today
                        st.markdown(
                            f'<div style="background:rgba(0,245,212,0.06);border:1px solid rgba(0,245,212,0.2);'
                            f'border-radius:8px;padding:12px 16px;margin-bottom:8px;">'
                            f'<div style="font-size:11px;letter-spacing:0.1em;text-transform:uppercase;'
                            f'color:#00f5d4;">Fund</div>'
                            f'<div style="font-size:15px;font-weight:600;margin-top:2px;">'
                            f'{_banner_result["fund_name"]}</div>'
                            f'<div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px;">'
                            f'Code: {_banner_result["fund_code"]}'
                            f' &nbsp;|&nbsp; SIP: {sip_start.strftime("%d %b %Y")}'
                            f' → {sip_end.strftime("%d %b %Y")}'
                            f'</div></div>',
                            unsafe_allow_html=True,
                        )

                    # ── SECTION 1: At SIP End Date ──
                    if result_at_end:
                        st.markdown(
                            f'<div class="calc-section-banner banner-at-end">'
                            f'① Corpus at SIP End &nbsp;—&nbsp; {sip_end.strftime("%d %b %Y")}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        gc1 = "gain-positive" if result_at_end["total_gains"] >= 0 else "gain-negative"
                        render_result_cards([
                            ("Total Invested",
                             fmt_inr(result_at_end["total_invested"]),
                             f"{len(result_at_end['sip_rows'])} SIP instalments"),
                            ("Corpus at End",
                             fmt_inr(result_at_end["current_value"]),
                             f'<span class="{gc1}">{result_at_end["abs_return_pct"]:+.1f}% absolute</span>'),
                            ("Gains at End",
                             fmt_inr(result_at_end["total_gains"]),
                             f'Units held: {result_at_end["total_units"]:,.4f}'),
                            ("NAV at End",
                             f'₹{result_at_end["current_nav"]:.4f}',
                             f'as on {result_at_end["valuation_date"].strftime("%d %b %Y")}'),
                        ])

                        if result_at_end["xirr_pct"] is not None:
                            xv1 = result_at_end["xirr_pct"]
                            bc1 = "xirr-badge" if xv1 >= 0 else "xirr-badge xirr-badge-neg"
                            sign1 = "+" if xv1 >= 0 else ""
                            st.markdown(
                                f'<div style="text-align:center;padding:8px 0 4px;">'
                                f'<div style="font-size:10px;letter-spacing:0.18em;text-transform:uppercase;'
                                f'color:#ffc107;margin-bottom:6px;">XIRR at SIP End</div>'
                                f'<span class="{bc1}" style="background:rgba(255,193,7,0.12);'
                                f'border-color:rgba(255,193,7,0.4);color:#ffc107;">'
                                f'{sign1}{xv1:.2f}% p.a.</span></div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.caption(f"XIRR (at end) unavailable: {result_at_end['xirr_error']}")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # ── SECTION 2: Current Value Today ──
                    if result_today:
                        days_since = (date.today() - sip_end).days
                        years_since = days_since / 365.25
                        time_label = (
                            f"{int(years_since)}y {int((years_since % 1) * 12)}m since SIP stopped"
                            if years_since >= 1
                            else f"{int(days_since / 30)}m since SIP stopped"
                        )

                        extra_growth = 0.0
                        if result_at_end:
                            extra_growth = result_today["current_value"] - result_at_end["current_value"]

                        st.markdown(
                            f'<div class="calc-section-banner banner-today">'
                            f'② Value Today &nbsp;—&nbsp; {date.today().strftime("%d %b %Y")}'
                            f'<span class="growth-pill">{time_label}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                        gc2 = "gain-positive" if result_today["total_gains"] >= 0 else "gain-negative"
                        extra_card_sub = (
                            f'corpus grew {fmt_inr(extra_growth)} after stop'
                            if result_at_end else "growth since SIP stopped"
                        )
                        render_result_cards([
                            ("Total Invested",
                             fmt_inr(result_today["total_invested"]),
                             "same as at end — no new instalments"),
                            ("Current Value",
                             fmt_inr(result_today["current_value"]),
                             f'<span class="{gc2}">{result_today["abs_return_pct"]:+.1f}% absolute</span>'),
                            ("Extra Growth",
                             fmt_inr(extra_growth),
                             extra_card_sub),
                            ("Latest NAV",
                             f'₹{result_today["latest_nav"]:.4f}',
                             f'as on {result_today["latest_nav_date"].strftime("%d %b %Y")}'),
                        ])

                        if result_today["xirr_pct"] is not None:
                            xv2 = result_today["xirr_pct"]
                            bc2 = "xirr-badge" if xv2 >= 0 else "xirr-badge xirr-badge-neg"
                            sign2 = "+" if xv2 >= 0 else ""
                            st.markdown(
                                f'<div style="text-align:center;padding:8px 0 4px;">'
                                f'<div style="font-size:10px;letter-spacing:0.18em;text-transform:uppercase;'
                                f'color:#00f5d4;margin-bottom:6px;">XIRR (as of Today)</div>'
                                f'<span class="{bc2}">{sign2}{xv2:.2f}% p.a.</span></div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.caption(f"XIRR (today) unavailable: {result_today['xirr_error']}")

                    # ── NEW: Nifty 50 Benchmark Comparison (Stopped mode) ──
                    if show_benchmark and benchmark_result and result_today:
                        fund_val = result_today["current_value"]
                        bench_val = benchmark_result["current_value"]
                        alpha = fund_val - bench_val
                        alpha_pct = result_today["abs_return_pct"] - benchmark_result["abs_return_pct"]
                        beat = alpha >= 0
                        alpha_color = "#00f5d4" if beat else "#ff6b6b"
                        alpha_label = "outperformed" if beat else "underperformed"

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(
                            '<div class="calc-section-banner banner-compare">'
                            '📊 Nifty 50 Benchmark Comparison (as of today)'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        bcol1, bcol2, bcol3 = st.columns(3)
                        with bcol1:
                            st.markdown(
                                f'<div class="result-card"><h3>Your Fund</h3>'
                                f'<p>{fmt_inr(fund_val)}</p>'
                                f'<div class="sub">{result_today["abs_return_pct"]:+.1f}% absolute</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        with bcol2:
                            st.markdown(
                                f'<div class="result-card" style="border-color:rgba(255,165,0,0.35);'
                                f'background:rgba(255,165,0,0.07);">'
                                f'<h3 style="color:#ffb347;">Nifty 50 Index</h3>'
                                f'<p>{fmt_inr(bench_val)}</p>'
                                f'<div class="sub">{benchmark_result["abs_return_pct"]:+.1f}% absolute</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        with bcol3:
                            st.markdown(
                                f'<div class="result-card" style="border-color:rgba({("0,245,212" if beat else "255,107,107")},0.4);'
                                f'background:rgba({("0,245,212" if beat else "255,107,107")},0.07);">'
                                f'<h3 style="color:{alpha_color};">Alpha</h3>'
                                f'<p style="color:{alpha_color};">{fmt_inr(abs(alpha))}</p>'
                                f'<div class="sub">Fund {alpha_label} by {abs(alpha_pct):.1f}%</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                        verdict = (
                            f'✅ Your fund <strong style="color:#00f5d4;">beat the Nifty 50</strong> '
                            f'by {fmt_inr(abs(alpha))} ({abs(alpha_pct):.1f}%).'
                            if beat else
                            f'⚠️ Your fund <strong style="color:#ff6b6b;">lagged the Nifty 50</strong> '
                            f'by {fmt_inr(abs(alpha))} ({abs(alpha_pct):.1f}%) — '
                            f'a passive Nifty index fund would have done better over this period.'
                        )
                        st.markdown(
                            f'<div class="info-box" style="margin-top:12px;">'
                            f'{verdict}<br>'
                            f'<span style="font-size:11px;opacity:0.6;">'
                            f'Benchmark: {benchmark_result["name"]} (Nifty 50 proxy via mfapi.in)'
                            f'</span></div>',
                            unsafe_allow_html=True,
                        )

                    # ── Chart ──
                    if result_today and result_today["sip_rows"]:
                        st.markdown("<br>", unsafe_allow_html=True)
                        rows_today = result_today["sip_rows"]

                        chart_data_stopped = pd.DataFrame({
                            "Date": [r["NAV Date"] for r in rows_today],
                            "Invested (₹)": [r["Total Invested (₹)"] for r in rows_today],
                            "Value (today's NAV) (₹)": [r["Current Value (₹)"] for r in rows_today],
                        }).set_index("Date")
                        st.caption(
                            "📊 Invested vs Portfolio Value — all units valued at today's NAV. "
                            "Invested line is flat after SIP stopped."
                        )

                        fig_stopped = go.Figure()
                        fig_stopped.add_trace(go.Scatter(
                            x=chart_data_stopped.index,
                            y=chart_data_stopped["Invested (₹)"],
                            name="Invested", line=dict(color="#4a9eff", width=2),
                        ))
                        fig_stopped.add_trace(go.Scatter(
                            x=chart_data_stopped.index,
                            y=chart_data_stopped["Value (today's NAV) (₹)"],
                            name="Current Value", line=dict(color="#00f5d4", width=2),
                        ))
                        fig_stopped.update_layout(**_chart_layout())
                        st.plotly_chart(fig_stopped, width="stretch")

                    # ── Transaction log ──
                    if result_today and result_today["sip_rows"]:
                        st.markdown(
                            '<div class="section-label" style="margin-top:16px;">'
                            'SIP Transaction Log (valued at today\'s NAV)'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        _render_fund_table(result_today["sip_rows"])

        else:
            st.markdown(
                '<br><br><div style="text-align:center;opacity:0.4;padding:60px 20px;">'
                '<div style="font-size:48px;">🔍</div>'
                '<div style="margin-top:12px;font-size:14px;">Select a fund and fill in the details</div>'
                '</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════
# TAB 4 – Prediction
# ══════════════════════════════════════════════
with tab_pred:
    show_fund_prediction()


# ══════════════════════════════════════════════
# TAB 5 – FUND COMPARISON
# ══════════════════════════════════════════════
with tab_compare:
    show_fund_comparison()



# ══════════════════════════════════════════════
# TAB 5 – COMING SOON
# ══════════════════════════════════════════════
with tab_more:
    st.markdown(
        '<br><div style="text-align:center;padding:80px 20px;opacity:0.5;">'
        '<div style="font-size:56px;">🔧</div>'
        '<div style="font-size:18px;margin-top:16px;font-weight:600;">More Calculators Coming Soon</div>'
        '<div style="font-size:13px;margin-top:8px;color:rgba(255,255,255,0.5);">'
        'Goal Planner · Tax Estimator · Portfolio Overlap</div></div>',
        unsafe_allow_html=True,
    )
