import streamlit as st

# =========================================================
# PAGE CONFIG — must be the first Streamlit call
# (if utils.sidebar_style.render_sidebar() also calls set_page_config,
#  delete one of the two)
# =========================================================
st.set_page_config(page_title="Taurus: Funds", layout="wide", page_icon="🐂")

import base64
import json
import os
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.graph_objects as go

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.xirr_helper import compute_fund_xirr
from utils.sidebar_style import render_sidebar

render_sidebar("fund_details")

# =========================================================
# CONSTANTS
# =========================================================
SUCCESS = "#1D9E75"
DANGER  = "#E24B4A"
AMBER   = "#EF9F27"
BLUE    = "#4F8BF9"

LTCG_EXEMPTION = 125000.0     # per financial year, across ALL equity investments
LTCG_RATE      = 0.125
STCG_RATE      = 0.20

ICON_FUND = """
<svg width="36" height="36" viewBox="0 0 36 36">
  <rect x="4" y="6" width="28" height="24" rx="3" fill="none" stroke="#1D9E75" stroke-width="1.5"/>
  <line x1="4" y1="13" x2="32" y2="13" stroke="#1D9E75" stroke-width="1.5"/>
  <rect x="9"  y="18" width="6"  height="2" rx="1" fill="#69F0AE"/>
  <rect x="9"  y="23" width="10" height="2" rx="1" fill="rgba(105,240,174,0.4)"/>
  <rect x="21" y="18" width="6"  height="2" rx="1" fill="rgba(105,240,174,0.4)"/>
  <rect x="21" y="23" width="4"  height="2" rx="1" fill="rgba(105,240,174,0.4)"/>
</svg>"""

ICON_DAILY_SUMMARY = """
<svg width="36" height="36" viewBox="0 0 36 36">
  <rect x="5"  y="8"  width="5" height="20" rx="2" fill="rgba(29,158,117,0.35)"/>
  <rect x="13" y="13" width="5" height="15" rx="2" fill="rgba(29,158,117,0.55)"/>
  <rect x="21" y="10" width="5" height="18" rx="2" fill="rgba(29,158,117,0.75)"/>
  <rect x="29" y="16" width="5" height="12" rx="2" fill="#1D9E75"/>
  <line x1="3" y1="29" x2="36" y2="29" stroke="rgba(105,240,174,0.3)" stroke-width="1"/>
</svg>"""

ICON_MONTHLY = """
<svg width="36" height="36" viewBox="0 0 36 36">
  <rect x="4"  y="6"  width="28" height="26" rx="3" fill="none" stroke="#534AB7" stroke-width="1.5"/>
  <line x1="4"  y1="13" x2="32" y2="13" stroke="#534AB7" stroke-width="1.5"/>
  <circle cx="12" cy="9.5" r="2" fill="#534AB7"/>
  <circle cx="24" cy="9.5" r="2" fill="#534AB7"/>
  <rect x="9"  y="17" width="4" height="4" rx="1" fill="rgba(83,74,183,0.5)"/>
  <rect x="16" y="17" width="4" height="4" rx="1" fill="#534AB7"/>
  <rect x="23" y="17" width="4" height="4" rx="1" fill="rgba(83,74,183,0.3)"/>
  <rect x="9"  y="24" width="4" height="4" rx="1" fill="rgba(83,74,183,0.3)"/>
  <rect x="16" y="24" width="4" height="4" rx="1" fill="rgba(83,74,183,0.5)"/>
  <rect x="23" y="24" width="4" height="4" rx="1" fill="#534AB7"/>
</svg>"""

ICON_DAILY_CHANGE = """
<svg width="36" height="36" viewBox="0 0 36 36">
  <polyline points="4,26 10,18 16,22 22,12 28,16 34,8"
    fill="none" stroke="#1D9E75" stroke-width="2"
    stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="34" cy="8"  r="3"   fill="#69F0AE"/>
  <circle cx="22" cy="12" r="2"   fill="rgba(105,240,174,0.6)"/>
  <line   x1="4" y1="30" x2="34" y2="30" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
</svg>"""


# =========================================================
# GLOBAL CSS (same look as the Portfolio Overview page)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
.stApp { background: #060910 !important; }
.block-container { padding-top: 2.5rem !important; padding-bottom: 3rem !important; max-width: 1800px !important; }
section[data-testid="stSidebar"] { background: #0A0E17 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.stSelectbox label, .stDateInput label, .stNumberInput label {
    color: rgba(255,255,255,0.5) !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 500 !important; font-family: 'JetBrains Mono', monospace !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }
@keyframes livepulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }

.stSelectbox > div > div, .stDateInput input, .stNumberInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #F0F4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stApp::before {
    content: ''; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px; animation: gridShift 25s linear infinite;
}
@keyframes gridShift { 0% { background-position: 0 0; } 100% { background-position: 60px 60px; } }

/* ── Tabs: pill-style bar ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px; padding: 6px; overflow-x: auto;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07); border-radius: 14px;
}
.stTabs [data-baseweb="tab"] {
    height: 44px; padding: 0 20px; border-radius: 10px; white-space: nowrap;
    background: transparent; color: rgba(255,255,255,0.55);
    font-size: 15px; font-weight: 600; transition: all 0.2s;
}
.stTabs [data-baseweb="tab"]:hover { color: #FFFFFF; background: rgba(255,255,255,0.05); }
.stTabs [aria-selected="true"] {
    color: #F0F4FF !important;
    background: linear-gradient(135deg, rgba(29,158,117,0.24), rgba(6,182,212,0.14)) !important;
    box-shadow: inset 0 0 0 1px rgba(29,158,117,0.5), 0 0 18px rgba(29,158,117,0.12);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.6rem; }

/* ── Radio groups inside keyed containers → pills ── */
div[class*="st-key-pillgroup_"] div[role="radiogroup"] { gap: 6px; flex-wrap: wrap; }
div[class*="st-key-pillgroup_"] div[role="radiogroup"] > label {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 999px; padding: 4px 14px; margin: 0; transition: all 0.2s;
}
div[class*="st-key-pillgroup_"] div[role="radiogroup"] > label:hover { border-color: rgba(29,158,117,0.5); }
div[class*="st-key-pillgroup_"] div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(29,158,117,0.2); border-color: rgba(29,158,117,0.65);
}

/* ── Fund header ── */
.fund-header { display: flex; align-items: center; gap: 16px; }
.fund-logo-wrap {
    width: 56px; height: 56px; border-radius: 12px; flex-shrink: 0; overflow: hidden;
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.1);
    display: flex; align-items: center; justify-content: center;
}
.fund-logo-wrap img { width: 100%; height: 100%; object-fit: contain; padding: 5px; }
.fund-logo-fallback { font-size: 28px; line-height: 1; }
.fund-title { font-size: 1.7rem; font-weight: 700; color: #F0F4FF; letter-spacing: -0.02em; line-height: 1.15; }
.fund-sub {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.1em;
    color: rgba(255,255,255,0.45); margin-top: 6px; text-transform: uppercase;
}
.nav-badge {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(29,158,117,0.3);
    border-radius: 14px; padding: 12px 20px; display: inline-block; text-align: right; float: right;
}
.nav-badge .nav-val { font-size: 1.7rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #F0F4FF; line-height: 1.1; }
.nav-badge .nav-date { font-size: 11px; color: rgba(255,255,255,0.5); margin-top: 4px; font-family: 'JetBrains Mono', monospace; }

.chip-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.4rem; }
.chip {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 8px 14px;
}
.chip .k { font-family:'JetBrains Mono',monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: rgba(255,255,255,0.45); }
.chip .v { font-family:'JetBrains Mono',monospace; font-size: 14px; color: #F0F4FF; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def inr(val, decimals=2):
    return f"₹{val:,.{decimals}f}"


def signed_inr(val, decimals=0):
    return f"{'+' if val >= 0 else '−'}₹{abs(val):,.{decimals}f}"


def pct(val, decimals=2):
    if pd.isna(val):
        return "n/a"
    return f"{'+' if val >= 0 else ''}{val:.{decimals}f}%"


def keyed_container(key):
    """st.container(key=...) needs Streamlit >= 1.39; fall back to a plain container."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def kpi_card(label, value, value_color, sub, sub_color="rgba(255,255,255,0.45)", hero=False):
    size   = "2.1rem" if hero else "1.5rem"
    border = "rgba(29,158,117,0.35)" if hero else "rgba(255,255,255,0.08)"
    return f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid {border};
        border-radius:14px; padding:18px 20px; height:100%; box-sizing:border-box;">
        <div style="font-size:11px; color:rgba(255,255,255,0.5); text-transform:uppercase;
            letter-spacing:0.1em; font-weight:500; margin-bottom:8px;">{label}</div>
        <div style="font-size:{size}; font-weight:700; line-height:1.1; color:{value_color};
            font-variant-numeric:tabular-nums; white-space:nowrap;">{value}</div>
        <div style="font-size:12px; color:{sub_color}; margin-top:6px;">{sub}</div>
    </div>"""


def sec_header(icon_svg, title, subtitle=""):
    icon_part = (
        f'<div style="display:flex;align-items:center;justify-content:center;'
        f'width:36px;height:36px;flex-shrink:0;">{icon_svg}</div>'
    ) if icon_svg else ""
    sub_part = (
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        f'color:rgba(255,255,255,0.45);letter-spacing:0.12em;text-transform:uppercase;'
        f'margin-top:3px;">{subtitle}</div>'
    ) if subtitle else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:1.4rem;margin-top:0.4rem;">
        {icon_part}
        <div>
            <div style="font-size:18px;font-weight:700;color:#F0F4FF;font-family:'Space Grotesk',sans-serif;line-height:1.1;">{title}</div>
            {sub_part}
        </div>
        <div style="flex:1;height:1px;background:rgba(255,255,255,0.06);margin-left:6px;"></div>
    </div>""", unsafe_allow_html=True)


def small_title(text):
    st.markdown(
        f'<div style="font-size:12px;font-weight:600;color:rgba(255,255,255,0.6);'
        f'text-transform:uppercase;letter-spacing:0.1em;margin:4px 0 8px;">{text}</div>',
        unsafe_allow_html=True,
    )


def chips(items):
    html = "".join(f'<div class="chip"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in items)
    st.markdown(f'<div class="chip-row">{html}</div>', unsafe_allow_html=True)


def tint_value(v):
    """Green for positive, red for negative; works on numbers and strings like '-1.2%'."""
    try:
        x = float(str(v).replace("%", "").replace(",", "").replace("₹", "").replace("+", "").replace("−", "-"))
    except ValueError:
        return ""
    if x > 0:
        return "color: #69F0AE; font-weight: 600"
    if x < 0:
        return "color: #FF6B6B; font-weight: 600"
    return "color: #9CA3AF"


def style_gain_type(val):
    return f"color: {SUCCESS if val == 'LTCG' else AMBER}; font-weight: 600;"


def styler_map(styler, func, subset):
    return (styler.map if hasattr(styler, "map") else styler.applymap)(func, subset=subset)


def plotly_base(height, **kw):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
        font=dict(family="Space Grotesk", color="rgba(255,255,255,0.6)"),
        margin=dict(l=10, r=10, t=20, b=10), height=height, hovermode="x unified", **kw,
    )


LOGO_MAP = {
    "mirae": "mirae.png", "axis": "axis.png", "bandhan": "bandhan.png",
    "edelweiss": "edelweiss.png", "hsbc": "HSBC.png", "icici": "icici.png",
    "kotak": "kotak.png", "motilal": "motilal.png", "nippon": "nippon.png",
    "parag parikh": "paragparikh.png", "ppfas": "paragparikh.png",
    "quant": "quant.png", "sbi": "sbi.png",
}


@st.cache_data(show_spinner=False)
def get_logo_base64(fund_name: str):
    name_lower = fund_name.lower()
    for keyword, filename in LOGO_MAP.items():
        if keyword in name_lower:
            path = os.path.join("utils", "logo", filename)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
    return None


def fund_logo_html(fund_name: str) -> str:
    b64 = get_logo_base64(fund_name)
    if b64:
        return f'<img src="data:image/png;base64,{b64}" alt="{fund_name} logo">'
    return '<span class="fund-logo-fallback">📁</span>'


# =========================================================
# CACHED LOADERS
# =========================================================
@st.cache_data(ttl=900, show_spinner=False)
def get_nav():
    return load_nav()


@st.cache_data(ttl=900, show_spinner=False)
def load_daily(folder, code):
    """Per-fund daily snapshot, newest first. Empty DataFrame if the file doesn't exist."""
    try:
        d = pd.read_csv(f"mutualfund/{folder}/daily_{code}.csv")
    except FileNotFoundError:
        return pd.DataFrame()
    d.columns = d.columns.str.strip()
    d["Date"] = pd.to_datetime(d["date"], format="%d-%m-%Y", errors="coerce")
    d = d.dropna(subset=["Date"]).drop(columns=["date"])
    return d.sort_values("Date", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=900, show_spinner=False)
def load_nav_history(fund_code):
    """Returns (DataFrame[Date, NAV], message). message is "" when everything is fine."""
    nav_file = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "NAVHistory", f"{fund_code}.json")
    )
    if not os.path.exists(nav_file):
        return pd.DataFrame(), f"NAV history file not found: NAVHistory/{fund_code}.json"
    try:
        with open(nav_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "data" in data and data["data"]:
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
            df = df.dropna(subset=["nav"]).sort_values("date").reset_index(drop=True)
            return df.rename(columns={"date": "Date", "nav": "NAV"}), ""
        return pd.DataFrame(), ""
    except Exception as e:
        return pd.DataFrame(), f"Failed to load NAV history: {e}"


@st.cache_data(ttl=900, show_spinner=False)
def get_fund_xirr_pct(folder, nav):
    try:
        return float(compute_fund_xirr(load_fund(folder), nav)) * 100
    except Exception:
        return float("nan")


# =========================================================
# PAGE HERO
# =========================================================
st.markdown("""
<div style="display:flex; align-items:flex-start; justify-content:space-between;
    margin-bottom:1.8rem; flex-wrap:wrap; gap:12px;">
    <div>
        <div style="font-size:2rem; font-weight:700; color:#F0F4FF;
            letter-spacing:-0.02em; font-family:'Space Grotesk',sans-serif;">
            Individual Funds
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
            color:rgba(255,255,255,0.45); margin-top:5px; letter-spacing:0.18em; text-transform:uppercase;">
            ◈ Taurus · Mutual Fund Tracker · Live NAV
        </div>
        <div style="display:inline-flex; align-items:center; gap:6px; margin-top:10px;
            background:rgba(29,158,117,0.1); border:1px solid rgba(29,158,117,0.25);
            border-radius:20px; padding:5px 12px; font-size:12px; font-weight:500;
            color:#1D9E75; font-family:'JetBrains Mono',monospace;">
            <div style="width:6px; height:6px; border-radius:50%; background:#1D9E75;
                animation:livepulse 2s ease-in-out infinite;"></div>
            Live NAV
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# FUND SELECTOR + DATA
# =========================================================
nav_df = get_nav()

sel_col, _ = st.columns([2, 5])
with sel_col:
    selected_fund = st.selectbox("Select Fund", list(mutual_funds.keys()), key="fund_select")

meta        = mutual_funds[selected_fund]
scheme_code = meta["code"]
folio_no    = meta.get("folio", "—")
folder      = meta["folder"]

fund_df = load_fund(folder).copy()
fund_df["Date"] = pd.to_datetime(fund_df["Date"])
daily_df = load_daily(folder, scheme_code)

match = nav_df[nav_df["SchemeCode"] == str(scheme_code)]
if match.empty:
    st.error("No NAV data found for this fund.")
    st.stop()

latest_row  = match.sort_values("Date", ascending=False).iloc[0]
latest_nav  = float(latest_row["NAV"])
latest_date = latest_row["Date"].date()

# ── Computed metrics ─────────────────────────────────────
total_units     = fund_df["Units"].sum()
invested        = fund_df["Amount"].sum()
current_value   = total_units * latest_nav
profit          = current_value - invested
avg_buy_nav     = invested / total_units if total_units > 0 else 0
absolute_return = ((current_value - invested) / invested * 100) if invested > 0 else 0
xirr_pct        = get_fund_xirr_pct(folder, latest_nav)

# Change in gain/loss between the last two daily rows (excludes new SIP money)
day_chg, day_date = None, None
if not daily_df.empty and "absolute_gain_loss" in daily_df.columns and len(daily_df) >= 2:
    g = pd.to_numeric(daily_df["absolute_gain_loss"], errors="coerce")
    if pd.notna(g.iloc[0]) and pd.notna(g.iloc[1]):
        day_chg  = float(g.iloc[0] - g.iloc[1])
        day_date = daily_df["Date"].iloc[0]      # date of the latest daily row (daily_df is newest first)


# =========================================================
# FUND HEADER
# =========================================================
col_title, col_nav = st.columns([3, 1])

with col_title:
    st.markdown(f"""
    <div class="fund-header">
        <div class="fund-logo-wrap">{fund_logo_html(selected_fund)}</div>
        <div>
            <div class="fund-title">{selected_fund}</div>
            <div class="fund-sub">Scheme {scheme_code} &nbsp;·&nbsp; Direct Growth &nbsp;·&nbsp; Folio {folio_no}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    st.markdown(f"""
    <div class="nav-badge">
        <div class="nav-val">{inr(latest_nav)}</div>
        <div class="nav-date">NAV · {latest_date.strftime('%d %b %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


# =========================================================
# KPI CARDS
# =========================================================
pnl_color  = SUCCESS if profit >= 0 else DANGER
ret_color  = SUCCESS if absolute_return >= 0 else DANGER
xirr_color = "#F1F5F9" if pd.isna(xirr_pct) else (SUCCESS if xirr_pct >= 0 else DANGER)

if day_chg is None:
    day_sub, day_col = f"NAV {latest_date.strftime('%d %b %Y')}", "rgba(255,255,255,0.45)"
else:
    day_sub = f"{'▲' if day_chg >= 0 else '▼'} {inr(abs(day_chg), 0)} on {day_date.strftime('%d %b %Y')}"
    day_col = SUCCESS if day_chg >= 0 else DANGER

c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 1, 1, 1, 1, 1, 1])
with c1:
    st.markdown(kpi_card("Current Value", inr(current_value, 0), "#F1F5F9", day_sub, day_col, hero=True),
                unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Invested", inr(invested, 0), "#F1F5F9", f"{len(fund_df)} installments"),
                unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("P&L", signed_inr(profit), pnl_color, "unrealised"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Abs. Return", pct(absolute_return), ret_color, "since first investment"),
                unsafe_allow_html=True)
with c5:
    st.markdown(kpi_card("XIRR", pct(xirr_pct, 1), xirr_color, "annualised"), unsafe_allow_html=True)
with c6:
    st.markdown(kpi_card("Avg Buy NAV", inr(avg_buy_nav), "#F1F5F9",
                         f"NAV now {pct((latest_nav / avg_buy_nav - 1) * 100, 1) if avg_buy_nav else 'n/a'}"),
                unsafe_allow_html=True)
with c7:
    st.markdown(kpi_card("Total Units", f"{total_units:,.2f}", "#F1F5F9", "held"), unsafe_allow_html=True)

st.divider()


# =========================================================
# TABS
# =========================================================
tab_overview, tab_nav_history, tab_harvest = st.tabs([
    "📋  Overview",
    "📈  NAV History",
    "🌾  Tax Harvesting",
])


# ─────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────
with tab_overview:

    first_date  = fund_df["Date"].min()
    held_years  = (pd.Timestamp.today().normalize() - first_date).days / 365.25
    
    held_months = round(held_years * 12)
    held_y, held_m = divmod(held_months, 12)

    
    
    
    n_inst      = len(fund_df)
    chips([
        ("First investment", first_date.strftime("%d %b %Y")),
        ("Installments",     f"{n_inst}"),
        ("Avg installment",  inr(invested / n_inst if n_inst else 0, 0)),
        ("Held for", f"{held_y}Y {held_m}M"),
    ])

    col_sip, col_daily = st.columns(2, gap="large")

    # ── SIP history ──────────────────────────────────────
    with col_sip:
        sec_header(ICON_MONTHLY, "SIP History", "every installment · buy NAV · gain since")
        sip = fund_df.sort_values("Date", ascending=False).reset_index(drop=True).copy()
        if {"Amount", "Units"}.issubset(sip.columns):
            sip["Buy NAV"] = sip["Amount"] / sip["Units"].where(sip["Units"] > 0)
            sip["Gain %"]  = (latest_nav / sip["Buy NAV"] - 1) * 100
        sip["Date"] = sip["Date"].dt.date

        fmt = {c: f for c, f in {"Amount": "₹{:,.2f}", "Units": "{:,.4f}",
                                 "Buy NAV": "₹{:,.4f}", "Gain %": "{:+.2f}%"}.items() if c in sip.columns}
        sip_styler = sip.style.format(fmt)
        if "Gain %" in sip.columns:
            sip_styler = styler_map(sip_styler, tint_value, ["Gain %"])
        st.dataframe(sip_styler, hide_index=True, use_container_width=True, height=320)

    # ── Daily NAV movement ───────────────────────────────
    with col_daily:
        sec_header(ICON_DAILY_CHANGE, "Daily NAV Movement", "latest first")
        if daily_df.empty:
            st.info("No daily snapshot data available for this fund.")
        else:
            dd = daily_df.copy()
            if "nav" in dd.columns:
                dd["Daily Change %"] = (pd.to_numeric(dd["nav"], errors="coerce").pct_change(-1) * 100).round(2)
            dd["Date"] = dd["Date"].dt.date
            dd = dd[["Date"] + [c for c in dd.columns if c != "Date"]]

            fmt = {}
            for c in dd.columns:
                if c != "Date" and pd.api.types.is_numeric_dtype(dd[c]):
                    fmt[c] = ("{:+.2f}%" if c == "Daily Change %" else "{:,.4f}" if c == "nav" else "{:,.2f}")
            dd_styler = dd.style.format(fmt, na_rep="–")
            if "Daily Change %" in dd.columns:
                dd_styler = styler_map(dd_styler, tint_value, ["Daily Change %"])
            st.dataframe(dd_styler, hide_index=True, use_container_width=True, height=320)

    st.divider()

    # ── Portfolio value trend ────────────────────────────
    sec_header(ICON_DAILY_SUMMARY, "Portfolio Value Trend", "value vs invested · or gain / loss")

    if daily_df.empty:
        st.info("No daily snapshot data available to plot.")
    else:
        chart_df = daily_df.sort_values("Date").copy()
        cols = set(chart_df.columns)
        inv_s  = pd.to_numeric(chart_df["invested"], errors="coerce") if "invested" in cols else None
        gain_s = pd.to_numeric(chart_df["absolute_gain_loss"], errors="coerce") if "absolute_gain_loss" in cols else None
        if "current_value" in cols:
            val_s = pd.to_numeric(chart_df["current_value"], errors="coerce")
        elif inv_s is not None and gain_s is not None:
            val_s = inv_s + gain_s
        else:
            val_s = None
        if gain_s is None and val_s is not None and inv_s is not None:
            gain_s = val_s - inv_s

        if val_s is None:
            st.info("The daily file has no current_value (or invested + absolute_gain_loss) columns to plot.")
        else:
            with keyed_container("pillgroup_trend"):
                trend_view = st.radio("Chart view", ["Value vs invested", "Gain / loss"],
                                      horizontal=True, label_visibility="collapsed")

            fig2 = go.Figure()
            if trend_view == "Gain / loss" and gain_s is not None:
                line_col = SUCCESS if float(gain_s.dropna().iloc[-1]) >= 0 else DANGER
                fig2.add_trace(go.Scatter(
                    x=chart_df["Date"], y=gain_s, mode="lines", name="Gain / loss",
                    line=dict(color=line_col, width=2.5),
                    fill="tozeroy", fillcolor="rgba(29,158,117,0.10)" if line_col == SUCCESS else "rgba(226,75,74,0.10)",
                    hovertemplate="<b>%{x|%d %b %Y}</b><br>Gain / loss: ₹%{y:,.2f}<extra></extra>",
                ))
                fig2.add_hline(y=0, line_color="rgba(255,255,255,0.25)", line_width=1)
            else:
                fig2.add_trace(go.Scatter(
                    x=chart_df["Date"], y=val_s, mode="lines+markers", name="Portfolio Value",
                    line=dict(color=SUCCESS, width=2.5), marker=dict(size=4, color=SUCCESS),
                    fill="tozeroy", fillcolor="rgba(29,158,117,0.07)",
                    hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.2f}<extra></extra>",
                ))
                if inv_s is not None:
                    fig2.add_trace(go.Scatter(
                        x=chart_df["Date"], y=inv_s, mode="lines", name="Invested",
                        line=dict(color=BLUE, width=1.8, dash="dot"),
                        hovertemplate="<b>%{x|%d %b %Y}</b><br>Invested: ₹%{y:,.2f}<extra></extra>",
                    ))
            fig2.update_layout(
                **plotly_base(400),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, tickprefix="₹"),
            )
            st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────────────────
# TAB 2 — NAV HISTORY
# ─────────────────────────────────────────────────────────
with tab_nav_history:

    sec_header(ICON_DAILY_CHANGE, "NAV History", "range · highs & lows · your purchases")

    RANGE_MAP = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "All": 9999}

    with keyed_container("pillgroup_navrange"):
        range_choice = st.radio(
            "Quick Range", options=["Custom", "1M", "3M", "6M", "1Y", "3Y", "All"],
            index=4, horizontal=True, label_visibility="collapsed", key="nav_range_choice",
        )

    col_d1, col_d2, _sp = st.columns([1, 1, 3])
    if range_choice == "Custom":
        with col_d1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365),
                                       max_value=date.today(), key="start_date")
        with col_d2:
            end_date = st.date_input("End Date", value=date.today(), min_value=start_date,
                                     max_value=date.today(), key="end_date")
    else:
        start_date = date.today() - timedelta(days=RANGE_MAP[range_choice])
        end_date   = date.today()
        for col, lab, d in ((col_d1, "FROM", start_date), (col_d2, "TO", end_date)):
            with col:
                st.markdown(f"""
                <div style="display:inline-flex;align-items:center;gap:8px;margin-top:6px;
                    background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);
                    border-radius:8px;padding:6px 14px;font-family:'JetBrains Mono',monospace;font-size:13px;">
                    <span style="color:rgba(255,255,255,0.4);font-size:11px;">{lab}</span>
                    <span style="color:rgba(255,255,255,0.9);">{d.strftime("%d %b %Y")}</span>
                </div>""", unsafe_allow_html=True)

    nav_df_full, nav_msg = load_nav_history(scheme_code)
    if nav_msg:
        st.warning(nav_msg)

    if not nav_df_full.empty:
        nav_df_full = nav_df_full.copy()
        nav_df_full["MA50"] = nav_df_full["NAV"].rolling(50, min_periods=10).mean()   # computed on full history
        nav_filtered = nav_df_full[
            (nav_df_full["Date"] >= pd.Timestamp(start_date)) &
            (nav_df_full["Date"] <= pd.Timestamp(end_date))
        ].reset_index(drop=True)
    else:
        nav_filtered = pd.DataFrame()

    if nav_filtered.empty:
        st.warning("No NAV data for the selected date range.")
    else:
        max_row   = nav_filtered.loc[nav_filtered["NAV"].idxmax()]
        min_row   = nav_filtered.loc[nav_filtered["NAV"].idxmin()]
        nav_start = nav_filtered["NAV"].iloc[0]
        nav_end   = nav_filtered["NAV"].iloc[-1]
        range_chg = (nav_end - nav_start) / nav_start * 100

        last_year = nav_df_full[nav_df_full["Date"] >= nav_df_full["Date"].max() - timedelta(days=365)]
        hi52      = float(last_year["NAV"].max())
        from_high = (latest_nav / hi52 - 1) * 100

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(kpi_card("Highest NAV", inr(max_row["NAV"], 4), "#F1F5F9",
                                 max_row["Date"].strftime("%d %b %Y")), unsafe_allow_html=True)
        with k2:
            st.markdown(kpi_card("Lowest NAV", inr(min_row["NAV"], 4), "#F1F5F9",
                                 min_row["Date"].strftime("%d %b %Y")), unsafe_allow_html=True)
        with k3:
            st.markdown(kpi_card("Range change", pct(range_chg), SUCCESS if range_chg >= 0 else DANGER,
                                 f"{start_date.strftime('%d %b')} → {end_date.strftime('%d %b %Y')}"),
                        unsafe_allow_html=True)
        with k4:
            st.markdown(kpi_card("From 52-week high", pct(from_high), SUCCESS if from_high >= 0 else DANGER,
                                 f"high {inr(hi52, 2)}"), unsafe_allow_html=True)
        with k5:
            vs_avg = (latest_nav / avg_buy_nav - 1) * 100 if avg_buy_nav else float("nan")
            st.markdown(kpi_card("Your avg buy NAV", inr(avg_buy_nav, 4), "#F1F5F9",
                                 f"NAV now {pct(vs_avg, 1)} vs your cost",
                                 SUCCESS if (not pd.isna(vs_avg) and vs_avg >= 0) else DANGER),
                        unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        t1, t2, t3, _t = st.columns([1.2, 1.4, 1.4, 4])
        with t1:
            show_ma = st.toggle("50-day average", value=False)
        with t2:
            show_buys = st.toggle("My purchases", value=True)
        with t3:
            show_avg = st.toggle("Avg buy NAV line", value=True)

        col_tbl, col_cht = st.columns([1, 2], gap="large")

        with col_tbl:
            display_df = nav_filtered[["Date", "NAV"]].sort_values("Date", ascending=False).reset_index(drop=True)
            display_df["Daily %"] = (display_df["NAV"].pct_change(-1) * 100)
            display_df["Date"]    = display_df["Date"].dt.date
            nav_styler = display_df.style.format({"NAV": "₹{:,.4f}", "Daily %": "{:+.2f}%"}, na_rep="–")
            nav_styler = styler_map(nav_styler, tint_value, ["Daily %"])
            st.dataframe(nav_styler, hide_index=True, use_container_width=True, height=420)
            st.download_button(
                "⬇ CSV (this range)",
                data=display_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"nav_{scheme_code}_{start_date:%Y%m%d}_{end_date:%Y%m%d}.csv",
                mime="text/csv",
            )

        with col_cht:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=nav_filtered["Date"], y=nav_filtered["NAV"], mode="lines", name="NAV",
                line=dict(color=BLUE, width=2),
                fill="tozeroy", fillcolor="rgba(79,139,249,0.08)",
                hovertemplate="<b>%{x|%d %b %Y}</b><br>NAV: ₹%{y:.4f}<extra></extra>",
            ))
            if show_ma:
                fig.add_trace(go.Scatter(
                    x=nav_filtered["Date"], y=nav_filtered["MA50"], mode="lines", name="50-day avg",
                    line=dict(color=AMBER, width=1.6, dash="dash"),
                    hovertemplate="50-day avg: ₹%{y:.4f}<extra></extra>",
                ))
            if show_buys:
                buys = fund_df[(fund_df["Date"] >= pd.Timestamp(start_date)) &
                               (fund_df["Date"] <= pd.Timestamp(end_date))]
                if not buys.empty:
                    fig.add_trace(go.Scatter(
                        x=buys["Date"], y=buys["Amount"] / buys["Units"].where(buys["Units"] > 0),
                        mode="markers", name="Your purchases",
                        marker=dict(symbol="triangle-up", size=11, color="#69F0AE",
                                    line=dict(color="#060910", width=1)),
                        customdata=buys["Amount"],
                        hovertemplate="<b>%{x|%d %b %Y}</b><br>Bought at ₹%{y:.4f}<br>Amount ₹%{customdata:,.0f}<extra></extra>",
                    ))
            if show_avg and avg_buy_nav > 0:
                fig.add_hline(y=avg_buy_nav, line_color="rgba(105,240,174,0.6)", line_dash="dot", line_width=1.4,
                              annotation_text=f"your avg ₹{avg_buy_nav:,.2f}", annotation_position="top left",
                              annotation_font=dict(size=11, color="rgba(105,240,174,0.9)"))
            fig.update_layout(
                **plotly_base(470),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, tickprefix="₹"),
            )
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────
# TAB 3 — TAX HARVESTING
# ─────────────────────────────────────────────────────────
def holding_period_days(buy_date):
    return (date.today() - buy_date.date()).days


def classify_lot(buy_date):
    return "LTCG" if holding_period_days(buy_date) > 365 else "STCG"


def tax_rate(gain_type):
    return LTCG_RATE if gain_type == "LTCG" else STCG_RATE


def build_fifo_plan(lots_sorted, sell_nav, target):
    """Redeem oldest units first until the NET realised gain reaches `target`.
    Lots that are at a loss at sell_nav are NOT skipped: a FIFO redemption has to go through
    them, and their loss reduces the net gain. Returns (plan rows, net gain realised)."""
    plan, net = [], 0.0
    for _, lot in lots_sorted.iterrows():
        if net >= target - 1e-9:
            break
        units = float(lot["Units"])
        if units <= 0:
            continue
        lot_buy_nav   = float(lot["Amount"]) / units
        gain_per_unit = sell_nav - lot_buy_nav

        if gain_per_unit > 0:
            units_to_sell = min((target - net) / gain_per_unit, units)
        else:
            units_to_sell = units                     # loss lot: FIFO redeems it in full

        gain = units_to_sell * gain_per_unit
        plan.append({
            "SIP Date":        lot["Date"].date(),
            "Gain Type":       lot["Gain Type"],
            "Holding Days":    int(lot["Holding Days"]),
            "Buy NAV":         round(lot_buy_nav, 4),
            "Units Available": round(units, 4),
            "Units to Sell":   round(units_to_sell, 4),
            "Cost Basis":      round(units_to_sell * lot_buy_nav, 2),
            "Sell Value":      round(units_to_sell * sell_nav, 2),
            "Gain Realised":   round(gain, 2),
        })
        net += gain
    return plan, net


with tab_harvest:

    sec_header(ICON_FUND, "Tax Harvesting Calculator", "FIFO · LTCG 12.5% · STCG 20%")

    # ── Lot-wise breakdown ───────────────────────────────
    lots = fund_df.sort_values("Date").reset_index(drop=True).copy()
    lots["Gain Type"]     = lots["Date"].apply(classify_lot)
    lots["Current Value"] = lots["Units"] * latest_nav
    lots["Gain"]          = lots["Current Value"] - lots["Amount"]
    lots["Gain %"]        = (lots["Gain"] / lots["Amount"] * 100).round(2)
    lots["Tax Rate"]      = lots["Gain Type"].apply(tax_rate)
    lots["Approx Tax"]    = (lots["Gain"].clip(lower=0) * lots["Tax Rate"]).round(2)
    lots["Holding Days"]  = lots["Date"].apply(holding_period_days)

    st.markdown("""
    <div style="background:rgba(79,139,249,0.07);border:1px solid rgba(79,139,249,0.2);
        border-radius:12px;padding:14px 18px;margin-bottom:20px;font-size:13px;
        color:rgba(255,255,255,0.65);line-height:1.7;">
        <b style="color:rgba(255,255,255,0.9);">How this works:</b>
        Equity MF gains held &gt;1 year are <b style="color:#1D9E75;">LTCG (12.5%)</b> with a ₹1.25L exemption per
        financial year. Gains held ≤1 year are <b style="color:#EF9F27;">STCG (20%)</b>. Tax harvesting means realising
        gains up to the exemption each year to reset your cost basis. Units are redeemed
        <b style="color:#fff;">oldest first (FIFO)</b>, so older lots that are at a loss are redeemed first and reduce
        the net profit. The ₹1.25L exemption is shared across <b style="color:#fff;">all</b> your equity holdings —
        enter what you've already used below. Estimates exclude 4% cess and surcharge.
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ───────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)
    with col_b:
        sell_nav = st.number_input(
            "Expected Sell NAV (₹)", min_value=0.01, value=float(latest_nav),
            step=0.01, format="%.4f",
            help="Defaults to today's NAV. Adjust if you expect to sell at a different price.")
    with col_c:
        exemption_used = st.number_input(
            "LTCG exemption already used this FY (₹)", min_value=0.0, max_value=LTCG_EXEMPTION,
            value=0.0, step=1000.0, format="%.2f",
            help="Long-term gains you have already booked this financial year in other equity funds/stocks.")
    exemption_left = LTCG_EXEMPTION - exemption_used
    with col_a:
        target_profit = st.number_input(
            "Target Profit to Harvest (₹)", min_value=0.0,
            value=float(min(exemption_left, max(profit, 0.0))), step=1000.0, format="%.2f",
            help="Net profit you want to realise. Default: the LTCG exemption still available.")

    st.divider()

    # ── FIFO plan + tax ──────────────────────────────────
    sell_plan, net_gain = build_fifo_plan(lots, sell_nav, target_profit)
    plan_df = pd.DataFrame(sell_plan)

    total_units_sell = float(plan_df["Units to Sell"].sum()) if sell_plan else 0.0
    total_sell_value = float(plan_df["Sell Value"].sum())    if sell_plan else 0.0
    ltcg_gain_realised = float(plan_df.loc[plan_df["Gain Type"] == "LTCG", "Gain Realised"].sum()) if sell_plan else 0.0
    stcg_gain_realised = float(plan_df.loc[plan_df["Gain Type"] == "STCG", "Gain Realised"].sum()) if sell_plan else 0.0

    # Set-off: a short-term loss can offset long-term gains; a long-term loss only offsets long-term gains
    ltcg_net, stcg_net = ltcg_gain_realised, stcg_gain_realised
    if stcg_net < 0:
        ltcg_net += stcg_net
        stcg_net = 0.0
    ltcg_net     = max(ltcg_net, 0.0)
    taxable_ltcg = max(0.0, ltcg_net - exemption_left)
    ltcg_tax     = taxable_ltcg * LTCG_RATE
    stcg_tax     = stcg_net * STCG_RATE
    total_tax    = ltcg_tax + stcg_tax

    if target_profit > 0 and net_gain < target_profit - 1:
        st.warning(f"At NAV ₹{sell_nav:,.4f} even redeeming every unit only realises {inr(net_gain)} "
                   f"(target {inr(target_profit)}). The plan below sells all lots.")
    n_loss_lots = int((plan_df["Gain Realised"] < 0).sum()) if sell_plan else 0
    if n_loss_lots:
        st.info(f"{n_loss_lots} older lot(s) are at a loss at this NAV. FIFO redeems them first, so they are in "
                f"the plan and reduce the net profit.")

    # ── Summary cards ────────────────────────────────────
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(kpi_card("Units to Redeem", f"{total_units_sell:,.4f}", "#F1F5F9",
                             f"of {total_units:,.4f} total units", hero=True), unsafe_allow_html=True)
    with r2:
        st.markdown(kpi_card("Redemption Amount", inr(total_sell_value), "#F1F5F9",
                             f"at NAV ₹{sell_nav:,.4f}"), unsafe_allow_html=True)
    with r3:
        st.markdown(kpi_card("Net Profit Realised", inr(net_gain), SUCCESS if net_gain >= 0 else DANGER,
                             f"LTCG {inr(ltcg_gain_realised)} · STCG {inr(stcg_gain_realised)}"),
                    unsafe_allow_html=True)
    with r4:
        st.markdown(kpi_card("Estimated Tax", inr(total_tax), AMBER if total_tax > 0 else SUCCESS,
                             f"LTCG {inr(ltcg_tax)} · STCG {inr(stcg_tax)}"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Lot-wise sell plan ───────────────────────────────
    sec_header(ICON_MONTHLY, "Lot-wise Sell Plan", "oldest lots first")
    if sell_plan:
        plan_styler = plan_df.style.format({
            "Buy NAV": "₹{:.4f}", "Units Available": "{:.4f}", "Units to Sell": "{:.4f}",
            "Cost Basis": "₹{:,.2f}", "Sell Value": "₹{:,.2f}", "Gain Realised": "₹{:,.2f}",
        })
        plan_styler = styler_map(plan_styler, style_gain_type, ["Gain Type"])
        plan_styler = styler_map(plan_styler, tint_value, ["Gain Realised"])
        st.dataframe(plan_styler, hide_index=True, use_container_width=True,
                     height=min((len(plan_df) + 1) * 35 + 3, 420))
        st.download_button(
            "⬇ CSV (sell plan)",
            data=plan_df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"sell_plan_{scheme_code}_{date.today():%Y%m%d}.csv",
            mime="text/csv",
        )
    else:
        st.info("Set a target profit above ₹0 to see a sell plan.")

    st.divider()

    # ── All lots overview ────────────────────────────────
    sec_header(ICON_FUND, "All Lots Overview", "tax shown is if the whole lot were sold today, before any exemption")

    lots_display = lots[["Date", "Units", "Amount", "Gain Type", "Holding Days",
                         "Current Value", "Gain", "Gain %", "Approx Tax"]].copy()
    lots_display["Date"] = lots_display["Date"].dt.date
    lots_styler = lots_display.style.format({
        "Amount": "₹{:,.2f}", "Current Value": "₹{:,.2f}", "Gain": "₹{:,.2f}",
        "Gain %": "{:+.2f}%", "Approx Tax": "₹{:,.2f}", "Units": "{:.4f}",
    })
    lots_styler = styler_map(lots_styler, tint_value, ["Gain", "Gain %"])
    lots_styler = styler_map(lots_styler, style_gain_type, ["Gain Type"])
    st.dataframe(lots_styler, hide_index=True, use_container_width=True,
                 height=min((len(lots_display) + 1) * 35 + 3, 420))
    st.download_button(
        "⬇ CSV (all lots)",
        data=lots_display.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"lots_{scheme_code}_{date.today():%Y%m%d}.csv",
        mime="text/csv",
    )

    st.divider()

    # ── LTCG exemption utilisation ───────────────────────
    sec_header(ICON_DAILY_SUMMARY, "LTCG Exemption Utilisation", "this financial year")

    used_total = exemption_used + ltcg_net
    used_pct   = used_total / LTCG_EXEMPTION * 100
    bar_color  = SUCCESS if used_pct <= 100 else AMBER

    st.markdown(f"""
    <div style="margin-bottom:8px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;
        font-size:12px;color:rgba(255,255,255,0.55);font-family:'JetBrains Mono',monospace;">
        <span>₹0</span>
        <span style="color:rgba(255,255,255,0.85);">
            ₹{used_total:,.0f} of ₹{LTCG_EXEMPTION:,.0f} used
            (₹{exemption_used:,.0f} already + ₹{ltcg_net:,.0f} this plan)
        </span>
        <span>₹1,25,000</span>
    </div>
    <div style="background:rgba(255,255,255,0.07);border-radius:6px;height:10px;overflow:hidden;">
        <div style="width:{min(used_pct, 100):.1f}%;background:{bar_color};height:100%;border-radius:6px;"></div>
    </div>
    <div style="margin-top:6px;font-size:11px;color:rgba(255,255,255,0.4);font-family:'JetBrains Mono',monospace;">
        {used_pct:.1f}% of the annual LTCG exemption {'consumed' if used_pct <= 100 else 'exceeded — the excess is taxed at 12.5%'}
    </div>
    """, unsafe_allow_html=True)

    remaining_exempt = max(0.0, LTCG_EXEMPTION - used_total)
    if remaining_exempt > 0:
        st.markdown(f"""
        <div style="margin-top:12px;background:rgba(29,158,117,0.07);border:1px solid rgba(29,158,117,0.2);
            border-radius:10px;padding:12px 16px;font-size:13px;color:rgba(255,255,255,0.65);">
            💡 <b style="color:#1D9E75;">₹{remaining_exempt:,.2f}</b> of your LTCG exemption is still unused this year.
            Consider harvesting more across other equity funds to use the full ₹1.25L.
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
from utils.footer import show_footer
show_footer()
