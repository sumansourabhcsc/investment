##new
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

from plotly.subplots import make_subplots

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value
from utils.load_funds import load_all_funds
from utils.xirr_overall import compute_overall_xirr
from utils.xirr_helper import compute_fund_xirr

st.divider()

from utils.sidebar_style import render_sidebar
render_sidebar("dashboard_update")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Taurus: Dashboard Update",
    layout="wide",
    page_icon="🌿"
)

# =========================================================
# "LIVELIHOOD" PALETTE — vivid, alive, growth-coded
# =========================================================
SUCCESS = "#00E68A"   # vivid living emerald — growth / gain
DANGER  = "#FF5D5D"   # warm coral red — loss
GOLD    = "#FFB020"   # harvest gold — prosperity
VIOLET  = "#8B6BFF"   # spark violet — highlight
TEAL    = "#2DD4BF"   # aqua teal — accent
SUN     = "#FFD54F"   # sunflower — accent

PALETTE = [
    "#00E68A",  # vivid emerald
    "#FFB020",  # golden amber
    "#FF6F61",  # coral
    "#2DD4BF",  # turquoise
    "#8B6BFF",  # violet spark
    "#FFD54F",  # sunflower yellow
    "#FF8A65",  # warm orange
    "#4CD9A8",  # jade
    "#26C6DA",  # aqua
    "#B388FF",  # lavender
]

ICON_FUND = """
<svg width="34" height="34" viewBox="0 0 36 36">
  <rect x="4" y="6" width="28" height="24" rx="3" fill="none" stroke="#00E68A" stroke-width="1.5"/>
  <line x1="4" y1="13" x2="32" y2="13" stroke="#00E68A" stroke-width="1.5"/>
  <rect x="9"  y="18" width="6"  height="2" rx="1" fill="#00E68A"/>
  <rect x="9"  y="23" width="10" height="2" rx="1" fill="rgba(0,230,138,0.4)"/>
  <rect x="21" y="18" width="6"  height="2" rx="1" fill="rgba(0,230,138,0.4)"/>
  <rect x="21" y="23" width="4"  height="2" rx="1" fill="rgba(0,230,138,0.4)"/>
</svg>"""

ICON_DAILY_SUMMARY = """
<svg width="34" height="34" viewBox="0 0 36 36">
  <rect x="5"  y="8"  width="5" height="20" rx="2" fill="rgba(0,230,138,0.35)"/>
  <rect x="13" y="13" width="5" height="15" rx="2" fill="rgba(0,230,138,0.55)"/>
  <rect x="21" y="10" width="5" height="18" rx="2" fill="rgba(0,230,138,0.75)"/>
  <rect x="29" y="16" width="5" height="12" rx="2" fill="#00E68A"/>
  <line x1="3" y1="29" x2="36" y2="29" stroke="rgba(0,230,138,0.3)" stroke-width="1"/>
</svg>"""

ICON_MONTHLY = """
<svg width="34" height="34" viewBox="0 0 36 36">
  <rect x="4"  y="6"  width="28" height="26" rx="3" fill="none" stroke="#FFB020" stroke-width="1.5"/>
  <line x1="4"  y1="13" x2="32" y2="13" stroke="#FFB020" stroke-width="1.5"/>
  <circle cx="12" cy="9.5" r="2" fill="#FFB020"/>
  <circle cx="24" cy="9.5" r="2" fill="#FFB020"/>
  <line x1="12" y1="7" x2="12" y2="4" stroke="#FFB020" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="24" y1="7" x2="24" y2="4" stroke="#FFB020" stroke-width="1.5" stroke-linecap="round"/>
  <rect x="9"  y="17" width="4" height="4" rx="1" fill="rgba(255,176,32,0.5)"/>
  <rect x="16" y="17" width="4" height="4" rx="1" fill="#FFB020"/>
  <rect x="23" y="17" width="4" height="4" rx="1" fill="rgba(255,176,32,0.3)"/>
  <rect x="9"  y="24" width="4" height="4" rx="1" fill="rgba(255,176,32,0.3)"/>
  <rect x="16" y="24" width="4" height="4" rx="1" fill="rgba(255,176,32,0.5)"/>
  <rect x="23" y="24" width="4" height="4" rx="1" fill="#FFB020"/>
</svg>"""

ICON_DAILY_CHANGE = """
<svg width="34" height="34" viewBox="0 0 36 36">
  <polyline points="4,26 10,18 16,22 22,12 28,16 34,8"
    fill="none" stroke="#FF6F61" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="34" cy="8"  r="3"   fill="#FFD54F"/>
  <circle cx="22" cy="12" r="2"   fill="rgba(255,111,97,0.6)"/>
  <line   x1="4" y1="30" x2="34" y2="30"
    stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
</svg>"""

ICON_TREEMAP = """
<svg width="34" height="34" viewBox="0 0 36 36">
  <rect x="4"  y="4"  width="13" height="13" rx="2" fill="none" stroke="#2DD4BF" stroke-width="1.5"/>
  <rect x="19" y="4"  width="13" height="8"  rx="2" fill="none" stroke="rgba(45,212,191,0.5)" stroke-width="1.5"/>
  <rect x="19" y="14" width="13" height="3"  rx="1" fill="rgba(45,212,191,0.3)" stroke="rgba(45,212,191,0.3)" stroke-width="1"/>
  <rect x="4"  y="19" width="8"  height="13" rx="2" fill="none" stroke="rgba(45,212,191,0.5)" stroke-width="1.5"/>
  <rect x="14" y="19" width="18" height="13" rx="2" fill="none" stroke="rgba(45,212,191,0.4)" stroke-width="1.5"/>
</svg>"""


# =========================================================
# FONTS + THEME — "living" glass, aurora backdrop
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif !important; }

.stApp {
    background: #060b08 !important;
    position: relative;
}

/* living aurora glow — emerald / gold / coral breathing light */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 65% 50% at 12% 8%,  rgba(0,230,138,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 55% 60% at 92% 18%,  rgba(255,176,32,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 50% 100%, rgba(255,111,97,0.06) 0%, transparent 55%);
    animation: auroraBreathe 10s ease-in-out infinite;
}
@keyframes auroraBreathe { 0%,100% { opacity:1; } 50% { opacity:0.55; } }

.stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: radial-gradient(circle, rgba(0,230,138,0.10) 1px, transparent 1px);
    background-size: 42px 42px;
    opacity: 0.5;
}

.stApp > * { position: relative; z-index: 1; }

.block-container { padding-top: 2.2rem !important; padding-bottom: 3rem !important; max-width: 1800px !important; }
section[data-testid="stSidebar"] { background: #070f0b !important; border-right: 1px solid rgba(0,230,138,0.08) !important; }

[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden !important; border: 1px solid rgba(0,230,138,0.1) !important; }
.stSelectbox label, .stDateInput label {
    color: rgba(230,255,240,0.35) !important; font-size: 9px !important;
    text-transform: uppercase; letter-spacing: 0.15em;
    font-weight: 600 !important; font-family: 'JetBrains Mono', monospace !important;
}
hr { border-color: rgba(0,230,138,0.1) !important; margin: 2rem 0 !important; }
@keyframes livepulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }

[data-testid="stDataFrame"] thead tr th {
    background: rgba(0,230,138,0.04) !important;
    color: rgba(230,255,240,0.4) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important; letter-spacing: 0.12em !important; text-transform: uppercase !important;
}
[data-testid="stDataFrame"] tbody tr td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: rgba(225,245,235,0.8) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td { background: rgba(0,230,138,0.03) !important; }

.stSelectbox > div > div, .stDateInput input {
    background: rgba(0,230,138,0.05) !important;
    border: 1px solid rgba(0,230,138,0.15) !important;
    border-radius: 10px !important; color: #EFFFF6 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* pill-style tabs */
div[data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(255,255,255,0.025);
    padding: 7px;
    border-radius: 16px;
    border: 1px solid rgba(0,230,138,0.12);
    margin-bottom: 0.6rem;
}
button[data-baseweb="tab"] {
    height: 46px;
    border-radius: 11px !important;
    color: rgba(230,255,240,0.5) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.06em;
    background: transparent !important;
    border: none !important;
    transition: all 0.22s ease;
}
button[data-baseweb="tab"]:hover {
    background: rgba(0,230,138,0.07) !important;
    color: #00E68A !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,230,138,0.22), rgba(255,176,32,0.14)) !important;
    color: #ffffff !important;
    box-shadow: 0 0 24px rgba(0,230,138,0.18), inset 0 0 0 1px rgba(0,230,138,0.3);
}
div[data-baseweb="tab-highlight"] { background-color: transparent !important; }
div[data-baseweb="tab-border"]    { display: none !important; }

/* glass card hover lift, reused via .life-card class */
.life-card { transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease; }
.life-card:hover {
    transform: translateY(-3px);
    border-color: rgba(0,230,138,0.4) !important;
    box-shadow: 0 12px 32px rgba(0,230,138,0.12);
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,230,138,0.25); border-radius: 6px; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def kpi_card(icon, label, value, value_color, sub, bar_gradient):
    return f"""
    <div class="life-card" style="background:rgba(255,255,255,0.035); border:1px solid rgba(0,230,138,0.14);
        border-radius:16px; padding:20px 20px 16px; position:relative;
        overflow:hidden; box-sizing:border-box; height:100%;">
        <div style="position:absolute; top:0; left:0; right:0; height:3px;
            background:{bar_gradient};"></div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:10px;">
            <div style="width:30px; height:30px; border-radius:9px; display:flex; align-items:center;
                justify-content:center; font-size:15px; background:rgba(255,255,255,0.05);
                border:1px solid rgba(255,255,255,0.08);">{icon}</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:9px;
                color:rgba(230,255,240,0.38); text-transform:uppercase;
                letter-spacing:0.15em; font-weight:600;">{label}</div>
        </div>
        <div style="font-size:1.45rem; font-weight:800; font-family:'JetBrains Mono',monospace;
            line-height:1.1; color:{value_color};">{value}</div>
        <div style="font-size:9.5px; color:rgba(230,255,240,0.3); margin-top:6px;
            font-family:'JetBrains Mono',monospace; letter-spacing:0.02em;">{sub}</div>
    </div>"""


def sec_header(icon_svg, title, subtitle=""):
    icon_part = f'<div style="display:flex;align-items:center;justify-content:center;width:34px;height:34px;flex-shrink:0;">{icon_svg}</div>' if icon_svg else ""
    sub_part  = f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(230,255,240,0.35);letter-spacing:0.15em;text-transform:uppercase;margin-top:3px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:1.6rem;margin-top:0.4rem;">
        {icon_part}
        <div>
            <div style="font-size:17px;font-weight:700;color:#EFFFF6;font-family:'Manrope',sans-serif;line-height:1.1;">{title}</div>
            {sub_part}
        </div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg, rgba(0,230,138,0.25), transparent);margin-left:6px;"></div>
    </div>""", unsafe_allow_html=True)


def change_summary_box(total_change):
    sign  = "+" if total_change >= 0 else ""
    color = SUCCESS if total_change >= 0 else DANGER
    icon  = "▲" if total_change >= 0 else "▼"
    st.markdown(f"""
    <div style="margin-top:14px; background:rgba(255,255,255,0.025); padding:18px 24px;
        border-radius:14px; border:1px solid rgba(0,230,138,0.14);
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:10px;
            color:rgba(230,255,240,0.42); letter-spacing:0.12em; text-transform:uppercase;">
            {icon} Total Daily Change Across All Funds
        </div>
        <div style="font-size:1.4rem; font-weight:800; font-family:'JetBrains Mono',monospace;
            color:{color};">{sign}₹{abs(total_change):,.2f}</div>
    </div>""", unsafe_allow_html=True)


# =========================================================
# HERO — "living pulse" header
# =========================================================
components.html("""
<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@800&family=JetBrains+Mono:wght@400;500&display=swap');
  *,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
  body { background:transparent; font-family:'Manrope',sans-serif; overflow:hidden; }
  .row { display:flex; align-items:flex-start; justify-content:space-between; gap:14px; padding-top:6px; }
  h1 {
    font-weight:800; letter-spacing:-0.02em; line-height:1.05;
    font-size:clamp(1.7rem, 5vw, 2.6rem);
    background:linear-gradient(120deg, #00E68A 0%, #FFD54F 45%, #FF8A65 80%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  }
  .tag { font-family:'JetBrains Mono',monospace; font-size:10px; letter-spacing:0.22em;
    color:rgba(230,255,240,0.35); text-transform:uppercase; margin-top:6px; }
  .pill { display:inline-flex; align-items:center; gap:7px; margin-top:12px;
    background:rgba(0,230,138,0.1); border:1px solid rgba(0,230,138,0.28);
    border-radius:22px; padding:6px 14px; font-size:11px; font-weight:600;
    color:#00E68A; font-family:'JetBrains Mono',monospace; }
  .dot { width:7px; height:7px; border-radius:50%; background:#00E68A;
    animation:beat 1.3s ease-in-out infinite; }
  @keyframes beat { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.35; transform:scale(0.6); } }
  .heart-wrap { flex-shrink:0; width:64px; height:64px; position:relative;
    display:flex; align-items:center; justify-content:center; margin-top:4px; }
  .ring { position:absolute; width:26px; height:26px; border-radius:50%;
    border:1px solid #00E68A; opacity:0; animation:ripple 1.6s ease-out infinite; }
  .ring:nth-child(2){animation-delay:.4s;border-color:#FFB020;}
  .ring:nth-child(3){animation-delay:.8s;border-color:#FF6F61;}
  @keyframes ripple { 0% { transform:scale(1); opacity:.6; } 100% { transform:scale(3.2); opacity:0; } }
  .core { width:16px; height:16px; border-radius:50%; z-index:5;
    background:radial-gradient(circle at 35% 35%, #00E68Add, #FFB02066);
    animation:throb .9s ease-in-out infinite alternate; }
  @keyframes throb { from{box-shadow:0 0 6px #00E68A99;} to{box-shadow:0 0 16px #FFB02099;} }
  .divider { width:100%; height:1px; margin-top:16px;
    background:linear-gradient(90deg, rgba(0,230,138,0.45), rgba(255,176,32,0.2), transparent); }
</style></head>
<body>
<div class="row">
  <div style="flex:1;min-width:0;">
    <h1>Dashboard Update</h1>
    <div class="tag">◈ Taurus · Reimagined Portfolio View · Live NAV</div>
    <div class="pill"><span class="dot"></span> Live &amp; Breathing</div>
  </div>
  <div class="heart-wrap">
    <div class="ring"></div><div class="ring"></div><div class="ring"></div>
    <div class="core"></div>
  </div>
</div>
<div class="divider"></div>
</body></html>
""", height=145, scrolling=False)


# =========================================================
# LOAD NAV + PROCESS FUNDS
# =========================================================
nav_df         = load_nav()
summary        = []
total_invested = 0
total_current  = 0

for fund_name, meta in mutual_funds.items():
    try:
        code      = meta["code"]
        folder    = meta["folder"]
        fund_df   = load_fund(folder)
        match     = nav_df[nav_df["SchemeCode"] == str(code)]
        if match.empty:
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue
        latest_row  = match.sort_values("Date", ascending=False).iloc[0]
        latest_nav  = float(latest_row["NAV"])
        latest_date = latest_row["Date"].date()
        invested    = calculate_invested_amount(fund_df)
        current     = calculate_current_value(fund_df, latest_nav)
        total_units = fund_df["Units"].sum()
        fund_xirr   = compute_fund_xirr(fund_df, latest_nav)
        total_invested += invested
        total_current  += current
        summary.append([
            fund_name, code, total_units, invested, current,
            current - invested, latest_nav, latest_date,
            f"{fund_xirr * 100:.2f}%"
        ])
    except Exception as e:
        st.error(f"{fund_name} error: {e}")


# =========================================================
# COMPUTE OVERALL METRICS
# =========================================================
total_pnl           = total_current - total_invested
absolute_return_pct = ((total_pnl / total_invested) * 100) if total_invested > 0 else 0
all_funds_df        = load_all_funds()
overall_xirr        = compute_overall_xirr(all_funds_df)
overall_xirr_pct    = overall_xirr * 100

pnl_color  = SUCCESS if total_pnl >= 0 else DANGER
ret_color  = SUCCESS if absolute_return_pct >= 0 else DANGER
xirr_color = SUCCESS if overall_xirr_pct >= 0 else DANGER
pnl_sign   = "+" if total_pnl >= 0 else ""
ret_sign   = "+" if absolute_return_pct >= 0 else ""
xirr_sign  = "+" if overall_xirr_pct >= 0 else ""


# =========================================================
# KPI CARDS
# =========================================================
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(kpi_card(
        "🌱", "Total Invested",
        f"₹{total_invested:,.0f}",
        "#EFFFF6",
        f"across {len(summary)} funds",
        f"linear-gradient(90deg, {GOLD}, {SUN})"
    ), unsafe_allow_html=True)

with c2:
    st.markdown(kpi_card(
        "🌿", "Current Value",
        f"₹{total_current:,.0f}",
        SUCCESS, "live NAV",
        f"linear-gradient(90deg, {SUCCESS}, {TEAL})"
    ), unsafe_allow_html=True)

with c3:
    st.markdown(kpi_card(
        "⚡", "Total P&L",
        f"{pnl_sign}₹{abs(total_pnl):,.0f}",
        pnl_color, "unrealised gain/loss",
        f"linear-gradient(90deg, {TEAL}, {VIOLET})"
    ), unsafe_allow_html=True)

with c4:
    st.markdown(kpi_card(
        "📈", "Absolute Return",
        f"{ret_sign}{absolute_return_pct:.2f}%",
        ret_color, "since first investment",
        f"linear-gradient(90deg, {GOLD}, {DANGER})"
    ), unsafe_allow_html=True)

with c5:
    st.markdown(kpi_card(
        "🎯", "Overall XIRR",
        f"{xirr_sign}{overall_xirr_pct:.2f}%",
        xirr_color, "annualised return",
        f"linear-gradient(90deg, {VIOLET}, {SUCCESS})"
    ), unsafe_allow_html=True)

st.divider()

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "≡  Fund Details",
    "▐  Daily Summary",
    "⊞  Monthly Investment",
    "∧  Daily Change",
])


# =========================================================
# TAB 1 — FUND DETAILS + PORTFOLIO ALLOCATION
# =========================================================
with tab1:
    sec_header(ICON_FUND,         "Fund Details",          "live NAV · invested · P&L · XIRR")

    df = pd.DataFrame(summary, columns=[
        "Fund", "SchemeCode", "TotalUnits", "Invested", "Current",
        "P&L", "Latest NAV", "NAV Date", "XIRR"
    ])

    col_tbl, col_donut = st.columns([7, 3])

    with col_tbl:
        display_df = df.copy()

        rows_html = ""
        for i, (_, row) in enumerate(display_df.iterrows(), start=1):
            pnl_val   = row["P&L"]
            pnl_color = SUCCESS if pnl_val >= 0 else DANGER
            pnl_sign  = "+" if pnl_val >= 0 else ""
            xirr_val  = float(str(row["XIRR"]).replace("%", ""))
            xirr_col  = SUCCESS if xirr_val >= 0 else DANGER

            rows_html += f"""
            <tr>
                <td style="padding:11px 14px; color:rgba(230,255,240,0.25); font-size:10px; text-align:center; width:36px;">{i}</td>
                <td style="padding:11px 14px; color:#EFFFF6; font-weight:600; max-width:200px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{row['Fund']}">{row['Fund']}</td>
                <td style="padding:11px 14px; color:rgba(230,255,240,0.4); font-size:10px;">{row['SchemeCode']}</td>
                <td style="padding:11px 14px; color:rgba(230,255,240,0.6);">{row['TotalUnits']:.3f}</td>
                <td style="padding:11px 14px; color:rgba(255,213,79,0.85);">&#8377;{row['Invested']:,.0f}</td>
                <td style="padding:11px 14px; color:#2DD4BF;">&#8377;{row['Current']:,.0f}</td>
                <td style="padding:11px 14px; color:{pnl_color}; font-weight:700;">{pnl_sign}&#8377;{abs(pnl_val):,.0f}</td>
                <td style="padding:11px 14px; color:rgba(230,255,240,0.7);">{row['Latest NAV']:.2f}</td>
                <td style="padding:11px 14px; color:rgba(230,255,240,0.5); font-size:10px;">{row['NAV Date']}</td>
                <td style="padding:11px 14px; color:{xirr_col}; font-weight:700;">{row['XIRR']}</td>
            </tr>"""

        headers = ["#", "Fund", "Code", "Units", "Invested", "Current", "P&amp;L", "NAV", "NAV Date", "XIRR"]
        header_html = "".join(
            f'<th style="padding:11px 14px; text-align:left; font-family:JetBrains Mono,monospace; font-size:9px; color:rgba(230,255,240,0.35); text-transform:uppercase; letter-spacing:0.15em; font-weight:600; white-space:nowrap;">{h}</th>'
            for h in headers
        )

        table_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            html, body {{ background: transparent; height: 100%; }}
            .wrap {{
                overflow-x: auto;
                overflow-y: auto;
                height: 100%;
                border-radius: 14px;
                border: 1px solid rgba(0,230,138,0.14);
                background: rgba(255,255,255,0.02);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
            }}
            thead tr {{ background: rgba(0,230,138,0.05); }}
            thead th {{
                position: sticky; top: 0; z-index: 10;
                background: #0a140f;
                border-bottom: 1px solid rgba(0,230,138,0.14);
                box-shadow: 0 1px 0 rgba(0,230,138,0.08);
            }}
            tbody tr {{ border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }}
            tbody tr:last-child {{ border-bottom: none; }}
            tbody tr:hover td {{ background: rgba(0,230,138,0.035); }}
        </style>
        </head>
        <body>
        <div class="wrap">
            <table>
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        </body>
        </html>
        """

        components.html(table_html, height=min((len(display_df) + 1) * 52, 560), scrolling=True)

    with col_donut:
        fig_donut = go.Figure(go.Pie(
            labels=df["Fund"], values=df["Current"], hole=0.65,
            marker=dict(colors=PALETTE[:len(df)], line=dict(color="#060b08", width=3)),
            textinfo="percent",
            textfont=dict(size=12, family="JetBrains Mono"),
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
        ))
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#EFFFF6", family="Manrope"), showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=320,
            annotations=[dict(
                text=f"<b>₹{total_current/1e5:.1f}L</b>",
                x=0.5, y=0.5,
                font=dict(size=18, color="#00E68A", family="JetBrains Mono"),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.divider()
    sec_header(ICON_TREEMAP, "Portfolio Allocation", "treemap by current value")

    fig_tree = px.treemap(
        df, path=["Fund"], values="Current",
        color="Fund",
        color_discrete_sequence=PALETTE[:len(df)],
        hover_data={"Invested": True, "XIRR": True}
    )
    fig_tree.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#EFFFF6", family="Manrope"),
        margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False
    )
    fig_tree.update_traces(
        textinfo="label+percent entry",
        textfont=dict(size=13, family="Manrope"),
        marker=dict(line=dict(width=2, color="#060b08"))
    )
    st.plotly_chart(fig_tree, use_container_width=True)


# =========================================================
# TAB 2 — DAILY PORTFOLIO SUMMARY + PERFORMANCE CHART
# =========================================================
with tab2:
    sec_header(ICON_DAILY_SUMMARY, "Daily Portfolio Summary", "sorted by date · all funds")

    daily_path = "data/portfolio_daily.csv"
    daily_df   = pd.read_csv(daily_path)
    daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
    daily_df = daily_df.sort_values("Date", ascending=False)

    display_daily = daily_df.copy()
    display_daily["Date"] = display_daily["Date"].dt.strftime("%d-%m-%Y")
    st.dataframe(display_daily, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec_header(ICON_DAILY_SUMMARY, "Portfolio Performance", "daily change · total value")

    chart_df_full = daily_df.sort_values("Date")

    PERIODS = {"1M": 30, "3M": 90, "6M": 180, "All": None, "Custom": -1}

    col_btns, col_custom = st.columns([3, 2])

    with col_btns:
        selected_period = st.radio(
            "Period",
            options=list(PERIODS.keys()),
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )

    min_date = chart_df_full["Date"].min().date()
    max_date = chart_df_full["Date"].max().date()

    if selected_period == "Custom":
        with col_custom:
            custom_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed",
            )
        if isinstance(custom_range, (list, tuple)) and len(custom_range) == 2:
            start_date, end_date = custom_range
        else:
            start_date, end_date = min_date, max_date

        chart_df = chart_df_full[
            (chart_df_full["Date"].dt.date >= start_date) &
            (chart_df_full["Date"].dt.date <= end_date)
        ]
    else:
        days = PERIODS[selected_period]
        if days is None:
            chart_df = chart_df_full.copy()
        else:
            cutoff = chart_df_full["Date"].max() - pd.Timedelta(days=days)
            chart_df = chart_df_full[chart_df_full["Date"] >= cutoff]

    chart_df["OneDayChangePct_val"] = (
        chart_df["OneDayChangePct"].str.replace("%", "", regex=False).astype(float)
    )
    bar_colors = [SUCCESS if x >= 0 else DANGER for x in chart_df["OneDayChange"]]

    fig_perf = make_subplots(specs=[[{"secondary_y": True}]])
    fig_perf.add_trace(go.Bar(
        x=chart_df["Date"], y=chart_df["OneDayChange"],
        name="Daily Change (₹)", marker_color=bar_colors, marker_line_width=0, opacity=0.8,
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Daily Change: ₹%{y:,.2f}<extra></extra>"
    ), secondary_y=False)
    fig_perf.add_trace(go.Scatter(
        x=chart_df["Date"], y=chart_df["TotalValue"],
        name="Total Value (₹)", mode="lines",
        line=dict(color=TEAL, width=2.5),
        fill="tozeroy", fillcolor="rgba(45,212,191,0.08)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.0f}<extra></extra>"
    ), secondary_y=True)
    fig_perf.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,20,15,0.6)",
        font=dict(color="rgba(230,255,240,0.6)", family="Manrope"),
        hovermode="x unified", height=460, margin=dict(t=20, b=40, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
            font=dict(size=12, color="rgba(230,255,240,0.6)"), bgcolor="rgba(0,0,0,0)"
        ),
        bargap=0.3,
        xaxis=dict(showgrid=False, zeroline=False),
    )

    fig_perf.update_yaxes(
        showgrid=True, gridcolor="rgba(0,230,138,0.06)",
        zeroline=False, tickprefix="₹", secondary_y=False
    )
    fig_perf.update_yaxes(
        showgrid=False, zeroline=False, tickprefix="₹", secondary_y=True
    )
    st.plotly_chart(fig_perf, use_container_width=True)

# =========================================================
# TAB 3 — MONTHLY INVESTMENT SUMMARY + BAR CHART
# =========================================================
with tab3:
    sec_header(ICON_MONTHLY,      "Monthly Investment Summary", "SIP breakdown by fund & month")

    monthly_data = []
    month_map    = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                    7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

    for fund_name, meta in mutual_funds.items():
        try:
            folder   = meta["folder"]
            code     = meta["code"]
            df_month = load_fund(folder)
            df_month["Date"]  = pd.to_datetime(df_month["Date"], errors="coerce")
            df_month          = df_month.dropna(subset=["Date"])
            df_month["Year"]  = df_month["Date"].dt.year
            df_month["Month"] = df_month["Date"].dt.month
            grouped = df_month.groupby(["Year", "Month"])["Amount"].sum().reset_index()
            for _, row in grouped.iterrows():
                monthly_data.append([code, fund_name, row["Year"], row["Month"], row["Amount"]])
        except Exception as e:
            st.warning(f"{fund_name} skipped: {e}")

    if monthly_data:
        monthly_df    = pd.DataFrame(monthly_data, columns=["Code", "Fund", "Year", "Month", "Amount"])
        years         = sorted(monthly_df["Year"].dropna().astype(int).unique())
        selected_year = st.selectbox("Select Year", years, index=len(years) - 1)

        year_df  = monthly_df[monthly_df["Year"] == selected_year]
        pivot_df = year_df.pivot_table(
            index=["Code", "Fund"], columns="Month",
            values="Amount", aggfunc="sum", fill_value=0
        ).reset_index()
        pivot_df = pivot_df.rename(columns=month_map)
        for m in month_map.values():
            if m not in pivot_df.columns:
                pivot_df[m] = 0

        month_cols        = list(month_map.values())
        pivot_df          = pivot_df[["Code", "Fund"] + month_cols]
        pivot_df["Total"] = pivot_df[month_cols].sum(axis=1)
        total_row = ["", "TOTAL"] + [pivot_df[m].sum() for m in month_cols] + [pivot_df["Total"].sum()]
        final_df  = pd.concat(
            [pivot_df, pd.DataFrame([total_row], columns=pivot_df.columns)],
            ignore_index=True
        )
        for col in final_df.select_dtypes(include="number").columns:
            final_df[col] = final_df[col].map(lambda x: f"{x:,.0f}")
        st.dataframe(final_df, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        bar_data = year_df.copy()
        bar_data["Month_Name"] = bar_data["Month"].map(month_map)
        fig_month = px.bar(
            bar_data, x="Month_Name", y="Amount", color="Fund",
            barmode="stack", color_discrete_sequence=PALETTE,
            labels={"Month_Name": "Month", "Amount": "Amount (₹)"}
        )
        fig_month.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,20,15,0.6)",
            font=dict(color="rgba(230,255,240,0.6)", family="Manrope"),
            height=340, margin=dict(t=20, b=10, l=10, r=10),
            legend=dict(
                font=dict(size=11, color="rgba(230,255,240,0.55)"),
                bgcolor="rgba(0,0,0,0)", orientation="h",
                yanchor="top", y=-0.2, xanchor="left", x=0
            ),
            bargap=0.25,
            xaxis=dict(
                showgrid=False, zeroline=False,
                categoryorder="array", categoryarray=list(month_map.values())
            ),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(0,230,138,0.06)",
                zeroline=False, tickprefix="₹"
            ),
        )
        st.plotly_chart(fig_month, use_container_width=True)


# =========================================================
# TAB 4 — DAILY CHANGE ACROSS FUNDS
# =========================================================
with tab4:
    sec_header(ICON_DAILY_CHANGE, "Daily Change Across Funds",  "NAV movement · single date")

    latest_nav_date  = nav_df["Date"].max().date()
    selected_date    = st.date_input("Select Date", value=latest_nav_date)
    selected_date_dt = pd.to_datetime(selected_date)

    daily_rows = []

    for fund_name, meta in mutual_funds.items():
        folder    = meta["folder"]
        code      = meta["code"]
        file_path = f"mutualfund/{folder}/daily_{code}.csv"
        if not os.path.exists(file_path):
            continue
        df_daily         = pd.read_csv(file_path)
        df_daily.columns = df_daily.columns.str.strip()
        df_daily["date"] = pd.to_datetime(df_daily["date"], format="%d-%m-%Y", errors="coerce")
        df_daily         = df_daily.dropna(subset=["date"]).sort_values("date")

        today_rows = df_daily[df_daily["date"] == selected_date_dt]
        if today_rows.empty:
            continue
        row_today = today_rows.iloc[-1]
        prev_rows = df_daily[df_daily["date"] < selected_date_dt]
        if prev_rows.empty:
            continue
        row_prev       = prev_rows.iloc[-1]
        change_in_val  = float(row_today["absolute_gain_loss"]) - float(row_prev["absolute_gain_loss"])
        nav_today      = float(row_today["nav"])
        nav_prev       = float(row_prev["nav"])
        pct_change_nav = ((nav_today - nav_prev) / nav_prev * 100) if nav_prev != 0 else 0
        indicator      = "🟢 ↑" if nav_today > nav_prev else "🔴 ↓"

        daily_rows.append([
            row_today["date"].strftime("%d-%m-%Y"),
            fund_name, code,
            round(change_in_val, 2),
            f"{pct_change_nav:.2f}%",
            indicator
        ])

    df_daily_change = pd.DataFrame(daily_rows, columns=[
        "Date", "Fund Name", "Fund Code",
        "Change in Value", "% Change in NAV", "Indicator"
    ])
    st.dataframe(df_daily_change, use_container_width=True)

    total_change = df_daily_change["Change in Value"].sum() if not df_daily_change.empty else 0
    change_summary_box(total_change)

    # ── Horizontal Bar Chart ──────────────────────────────────────────
    if not df_daily_change.empty:
        df_chart = df_daily_change.copy().sort_values("Change in Value", ascending=True)

        colors = [
            SUCCESS if v >= 0 else DANGER
            for v in df_chart["Change in Value"]
        ]

        max_label_len = 32
        short_names = [
            name if len(name) <= max_label_len else name[:max_label_len - 1] + "…"
            for name in df_chart["Fund Name"]
        ]

        fig = go.Figure(go.Bar(
            x=df_chart["Change in Value"],
            y=short_names,
            orientation="h",
            marker=dict(color=colors),
            text=[
                f"₹{v:+,.2f}  ({pct})"
                for v, pct in zip(df_chart["Change in Value"], df_chart["% Change in NAV"])
            ],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(size=11, color="#EFFFF6"),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Code: %{customdata[1]}<br>"
                "Change: ₹%{x:+,.2f}<br>"
                "NAV Change: %{customdata[2]}<extra></extra>"
            ),
            customdata=list(zip(
                df_chart["Fund Name"],
                df_chart["Fund Code"],
                df_chart["% Change in NAV"],
            )),
        ))

        chart_height = max(300, len(df_chart) * 52 + 120)
        max_abs = df_chart["Change in Value"].abs().max()
        x_pad = max_abs * 0.45

        fig.update_layout(
            title=dict(
                text=f"Daily Change in Value — {selected_date.strftime('%d %b %Y')}",
                font=dict(size=15, color="#EFFFF6"),
                x=0,
            ),
            xaxis=dict(
                title="Change in Value (₹)",
                range=[-(max_abs + x_pad), max_abs + x_pad],
                zeroline=True,
                zerolinecolor="rgba(230,255,240,0.25)",
                zerolinewidth=1.5,
                tickformat=",.0f",
                gridcolor="rgba(0,230,138,0.06)",
            ),
            yaxis=dict(
                automargin=True,
                tickfont=dict(size=12, color="rgba(230,255,240,0.7)"),
            ),
            height=chart_height,
            margin=dict(l=20, r=180, t=50, b=120),
            uniformtext=dict(mode="hide", minsize=9),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(230,255,240,0.7)"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=12),
            ),
            annotations=[
                dict(
                    x=0.0, y=-0.13,
                    xref="paper", yref="paper",
                    text="🟢  Gain (positive change)",
                    showarrow=False,
                    font=dict(size=12, color=SUCCESS),
                    xanchor="left",
                ),
                dict(
                    x=0.5, y=-0.13,
                    xref="paper", yref="paper",
                    text="🔴  Loss (negative change)",
                    showarrow=False,
                    font=dict(size=12, color=DANGER),
                    xanchor="left",
                ),
            ],
        )

        st.plotly_chart(fig, use_container_width=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
from utils.footer import show_footer
show_footer()
