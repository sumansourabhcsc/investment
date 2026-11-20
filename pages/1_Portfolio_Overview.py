import streamlit as st

# =========================================================
# PAGE CONFIG — must be the first Streamlit call
# (if utils.sidebar_style.render_sidebar() also calls set_page_config,
#  delete one of the two)
# =========================================================
st.set_page_config(
    page_title="Taurus: Dashboard",
    layout="wide",
    page_icon="🐂",
)

import io
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value
from utils.load_funds import load_all_funds
from utils.xirr_overall import compute_overall_xirr
from utils.xirr_helper import compute_fund_xirr
from utils.sidebar_style import render_sidebar

render_sidebar("portfolio")

# =========================================================
# MUSIC (disabled)
# =========================================================
# from utils.music import play_background_music
# play_background_music(
#     "https://raw.githubusercontent.com/sumansourabhcsc/investment/main/music.mp3",
#     volume=0.02
# )

# =========================================================
# CONSTANTS
# =========================================================
SUCCESS = "#1D9E75"
DANGER  = "#E24B4A"
BG_MAIN = "#0A0F1E"
CARD_BG = "#0F1629"

HURDLE        = 12.0   # XIRR % treated as "par" for the treemap colour scale. Set your own benchmark.
MIN_HELD_YRS  = 1.0    # funds held for less than this are shown neutral (XIRR on short periods is noise)

PALETTE = [
    "#2E7D8C",  # deep teal blue
    "#E8573F",  # muted coral red
    "#D4A96A",  # warm sand/tan
    "#4A7C59",  # forest green
    "#5B6FA6",  # slate blue
    "#C4784A",  # burnt sienna
    "#7DB5B0",  # soft seafoam
    "#8B5E83",  # muted mauve
    "#B5C85A",  # olive lime
    "#3D5A80",  # navy blue
]

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
  <line x1="12" y1="7" x2="12" y2="4" stroke="#534AB7" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="24" y1="7" x2="24" y2="4" stroke="#534AB7" stroke-width="1.5" stroke-linecap="round"/>
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
  <line   x1="4" y1="30" x2="34" y2="30"
    stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
</svg>"""

ICON_TREEMAP = """
<svg width="36" height="36" viewBox="0 0 36 36">
  <rect x="4"  y="4"  width="13" height="13" rx="2" fill="none" stroke="#1D9E75" stroke-width="1.5"/>
  <rect x="19" y="4"  width="13" height="8"  rx="2" fill="none" stroke="rgba(29,158,117,0.5)" stroke-width="1.5"/>
  <rect x="19" y="14" width="13" height="3"  rx="1" fill="rgba(29,158,117,0.3)" stroke="rgba(29,158,117,0.3)" stroke-width="1"/>
  <rect x="4"  y="19" width="8"  height="13" rx="2" fill="none" stroke="rgba(29,158,117,0.5)" stroke-width="1.5"/>
  <rect x="14" y="19" width="18" height="13" rx="2" fill="none" stroke="rgba(29,158,117,0.4)" stroke-width="1.5"/>
</svg>"""


# =========================================================
# GLOBAL CSS
# (st.dataframe renders on a canvas, so DOM selectors can't style it —
#  theme it via .streamlit/config.toml [theme] instead)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
.stApp { background: #060910 !important; }
.block-container { padding-top: 2.5rem !important; padding-bottom: 3rem !important; max-width: 1800px !important; }
section[data-testid="stSidebar"] { background: #0A0E17 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.stSelectbox label, .stDateInput label {
    color: rgba(255,255,255,0.5) !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: 0.12em;
    font-weight: 500 !important; font-family: 'JetBrains Mono', monospace !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }
@keyframes livepulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }

/* selectbox/date input */
.stSelectbox > div > div, .stDateInput input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #F0F4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* bg grid animation */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridShift 25s linear infinite;
}
@keyframes gridShift { 0% { background-position: 0 0; } 100% { background-position: 60px 60px; } }

/* ── Tabs: pill-style bar instead of the default underline ── */
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
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def categorize(name: str) -> str:
    n = name.lower()
    if "fang" in n:       return "International"
    if "children" in n:   return "Hybrid / Children"
    if "bharat 22" in n:  return "Thematic FoF"
    if "small" in n:      return "Small cap"
    if "mid" in n:        return "Mid cap"
    if "large" in n:      return "Large cap"
    if "flexi" in n:      return "Flexi cap"
    return "Other"


def kpi_card(label, value, value_color, sub, sub_color="rgba(255,255,255,0.45)", hero=False):
    size   = "2.1rem" if hero else "1.5rem"
    border = "rgba(29,158,117,0.35)" if hero else "rgba(255,255,255,0.08)"
    return f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid {border};
        border-radius:14px; padding:18px 20px; height:100%; box-sizing:border-box;">
        <div style="font-size:11px; color:rgba(255,255,255,0.5); text-transform:uppercase;
            letter-spacing:0.1em; font-weight:500; margin-bottom:8px;">{label}</div>
        <div style="font-size:{size}; font-weight:700; line-height:1.1; color:{value_color};
            font-variant-numeric:tabular-nums;">{value}</div>
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
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:1.6rem;margin-top:0.4rem;">
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


def change_summary_box(total_change):
    sign  = "+" if total_change >= 0 else ""
    color = "#69F0AE" if total_change >= 0 else "#FF6B6B"
    icon  = "▲" if total_change >= 0 else "▼"
    st.markdown(f"""
    <div style="margin-top:14px; background:rgba(255,255,255,0.02); padding:16px 22px;
        border-radius:12px; border:1px solid rgba(255,255,255,0.06);
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:11px;
            color:rgba(255,255,255,0.5); letter-spacing:0.12em; text-transform:uppercase;">
            {icon} Total Daily Change Across All Funds
        </div>
        <div style="font-size:1.4rem; font-weight:700; font-family:'JetBrains Mono',monospace;
            color:{color};">{sign}₹{abs(total_change):,.2f}</div>
    </div>""", unsafe_allow_html=True)


# =========================================================
# CACHED DATA LOADERS
# (XIRR for every fund is expensive; refresh every 15 minutes.
#  Remove the decorators if you need every rerun to recompute.)
# =========================================================
@st.cache_data(ttl=900, show_spinner="Loading NAV data…")
def get_nav():
    return load_nav()


@st.cache_data(ttl=900, show_spinner="Computing fund returns…")
def build_summary():
    """Returns (rows, messages). Each row:
    [fund, code, units, invested, current, pnl, nav, nav_date, xirr_pct, held_years]"""
    nav_df   = get_nav()
    rows     = []
    messages = []
    today    = pd.Timestamp.today().normalize()

    for fund_name, meta in mutual_funds.items():
        try:
            code    = meta["code"]
            folder  = meta["folder"]
            fund_df = load_fund(folder)
            match   = nav_df[nav_df["SchemeCode"] == str(code)]
            if match.empty:
                messages.append(("warning", f"No NAV found for {fund_name} ({code})"))
                continue

            latest_row  = match.sort_values("Date", ascending=False).iloc[0]
            latest_nav  = float(latest_row["NAV"])
            latest_date = latest_row["Date"].date()
            invested    = calculate_invested_amount(fund_df)
            current     = calculate_current_value(fund_df, latest_nav)
            total_units = fund_df["Units"].sum()
            fund_xirr   = compute_fund_xirr(fund_df, latest_nav)

            first_date = pd.to_datetime(fund_df["Date"], errors="coerce").min() \
                if "Date" in fund_df.columns else pd.NaT
            held_years = (today - first_date).days / 365.25 if pd.notna(first_date) else float("nan")

            rows.append([
                fund_name, code, total_units, invested, current,
                current - invested, latest_nav, latest_date,
                fund_xirr * 100,          # numeric, not a formatted string
                held_years,
            ])
        except Exception as e:
            messages.append(("error", f"{fund_name} error: {e}"))
    return rows, messages


@st.cache_data(ttl=900, show_spinner="Computing overall XIRR…")
def get_overall_xirr_pct():
    return compute_overall_xirr(load_all_funds()) * 100


@st.cache_data(ttl=900, show_spinner=False)
def load_daily_files():
    """{fund_name: (code, DataFrame sorted by date)} for every fund that has a daily CSV."""
    out = {}
    for fund_name, meta in mutual_funds.items():
        path = f"mutualfund/{meta['folder']}/daily_{meta['code']}.csv"
        if not os.path.exists(path):
            continue
        d = pd.read_csv(path)
        d.columns = d.columns.str.strip()
        d["date"] = pd.to_datetime(d["date"], format="%d-%m-%Y", errors="coerce")
        out[fund_name] = (meta["code"], d.dropna(subset=["date"]).sort_values("date"))
    return out


def fund_pnl_series(daily_files):
    """Portfolio P&L per date = sum over funds of the day-on-day change in that fund's
    absolute_gain_loss (current value − invested). A new SIP raises value and invested by the
    same amount, so it cancels out and only market movement is left."""
    parts = []
    for _, (_code, d) in daily_files.items():
        if "absolute_gain_loss" not in d.columns:
            continue
        s = d[["date", "absolute_gain_loss"]].copy()
        s["absolute_gain_loss"] = pd.to_numeric(s["absolute_gain_loss"], errors="coerce")
        s = s.dropna().drop_duplicates("date", keep="last").sort_values("date")
        s["PnL"] = s["absolute_gain_loss"].diff()      # a fund's first row has no prior day → ignored
        parts.append(s[["date", "PnL"]].dropna())
    if not parts:
        return None
    return (pd.concat(parts).groupby("date", as_index=False)["PnL"].sum()
              .rename(columns={"date": "Date"}))


@st.cache_data(ttl=900, show_spinner=False)
def load_portfolio_daily():
    """Returns (DataFrame, basis).
    basis == "gain":  OneDayChange / OneDayChangePct are rebuilt from the per-fund gain/loss, so new
                      investments are excluded. The % is P&L divided by the previous day's total value.
                      "NewMoney" = the CSV's old value-based change minus the P&L (implied SIP amount).
    basis == "value": per-fund files missing → CSV columns used unchanged (they include new money)."""
    base = pd.read_csv("data/portfolio_daily.csv")
    base["Date"] = pd.to_datetime(base["Date"], format="%d-%m-%Y")
    base = base.sort_values("Date").reset_index(drop=True)

    pnl = fund_pnl_series(load_daily_files())
    if pnl is None or pnl.empty:
        return base, "value"

    df = base.merge(pnl, on="Date", how="outer").sort_values("Date").reset_index(drop=True)
    prev_value = df["TotalValue"].ffill().shift(1)
    if "OneDayChange" in df.columns:
        df["NewMoney"] = df["OneDayChange"] - df["PnL"]
    df["OneDayChange"]    = df["PnL"]
    df["OneDayChangePct"] = df["PnL"] / prev_value.where(prev_value > 0) * 100
    return df.drop(columns=["PnL"]), "gain"


# =========================================================
# PAGE HERO
# =========================================================
st.markdown("""
<div style="display:flex; align-items:flex-start; justify-content:space-between;
    margin-bottom:1.8rem; flex-wrap:wrap; gap:12px;">
    <div>
        <div style="font-size:2rem; font-weight:700; color:#F0F4FF;
            letter-spacing:-0.02em; font-family:'Space Grotesk',sans-serif;">
            Portfolio Dashboard
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
# PORTFOLIO REFRESH CONTROL
# =========================================================
refresh_col, info_col = st.columns([1, 5])

with refresh_col:
    if st.button("↻ Refresh Portfolio", key="refresh_portfolio", use_container_width=True):
        st.cache_data.clear()      # NAV, fund returns, XIRR, daily files, monthly investments — everything
        st.rerun()

with info_col:
    st.caption("Refresh after adding transactions, updating SIPs or downloading new NAV data.")



# =========================================================
# LOAD DATA + OVERALL METRICS
# =========================================================
summary, load_messages = build_summary()
for level, msg in load_messages:
    (st.warning if level == "warning" else st.error)(msg)

nav_df         = get_nav()
total_invested = sum(r[3] for r in summary)
total_current  = sum(r[4] for r in summary)

total_pnl           = total_current - total_invested
absolute_return_pct = ((total_pnl / total_invested) * 100) if total_invested > 0 else 0
overall_xirr_pct    = get_overall_xirr_pct()

pnl_color  = SUCCESS if total_pnl >= 0 else DANGER
ret_color  = SUCCESS if absolute_return_pct >= 0 else DANGER
xirr_color = SUCCESS if overall_xirr_pct >= 0 else DANGER
pnl_sign   = "+" if total_pnl >= 0 else ""
ret_sign   = "+" if absolute_return_pct >= 0 else ""
xirr_sign  = "+" if overall_xirr_pct >= 0 else ""

# # Today's change for the hero card (gain/loss based, excludes new investments)
# day_change, _basis = None, "gain"
# try:
#     _d, _basis = load_portfolio_daily()
#     day_change = float(_d["OneDayChange"].dropna().iloc[-1])
# except Exception:
#     day_change = None

# if day_change is None:
#     day_sub, day_col = "live NAV", "rgba(255,255,255,0.45)"
# else:
#     day_sub = (f"{'▲' if day_change >= 0 else '▼'} ₹{abs(day_change):,.0f} today"
#                + ("" if _basis == "gain" else " (incl. new money)"))
#     day_col = SUCCESS if day_change >= 0 else DANGER


# Today's change for the hero card
try:
    _d = pd.read_csv("data/portfolio_daily.csv")
    _d["Date"] = pd.to_datetime(_d["Date"], format="%d-%m-%Y")

    latest_record = _d.sort_values("Date").iloc[-1]

    day_change = float(latest_record["OneDayChange"])
    day_date = latest_record["Date"].strftime("%d %b %Y")

except Exception:
    day_change = None
    day_date = None

if day_change is None:
    day_sub = "Live NAV"
    day_col = "rgba(255,255,255,0.45)"
else:
    day_sub = (
        f"{'▲' if day_change >= 0 else '▼'} "
        f"₹{abs(day_change):,.0f} on {day_date}"
    )
    day_col = SUCCESS if day_change >= 0 else DANGER



# =========================================================
# KPI CARDS
# =========================================================
c1, c2, c3, c4, c5 = st.columns([1.4, 1, 1, 1, 1])

with c1:
    st.markdown(kpi_card("Current Value", f"₹{total_current:,.0f}", "#F1F5F9",
                         day_sub, day_col, hero=True), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("Total Invested", f"₹{total_invested:,.0f}", "#F1F5F9",
                         f"across {len(summary)} funds"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("Total P&L", f"{pnl_sign}₹{abs(total_pnl):,.0f}", pnl_color,
                         "unrealised gain/loss"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("Absolute Return", f"{ret_sign}{absolute_return_pct:.2f}%", ret_color,
                         "since first investment"), unsafe_allow_html=True)
with c5:
    st.markdown(kpi_card("Overall XIRR", f"{xirr_sign}{overall_xirr_pct:.2f}%", xirr_color,
                         "annualised return"), unsafe_allow_html=True)

st.divider()

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Fund Details",
    "📈  Daily Summary",
    "🗓️  Monthly Investment",
    "⚡  Daily Change",
])


# =========================================================
# TAB 1 — ALLOCATION + FUND DETAILS
# =========================================================
def render_fund_tab(summary_rows):
    df = pd.DataFrame(summary_rows, columns=[
        "Fund", "Code", "Units", "Invested", "Current",
        "P&L", "NAV", "NAV Date", "XIRR", "Held (yrs)"
    ])
    if df.empty:
        st.warning("No fund data available.")
        return

    df["Category"] = df["Fund"].map(categorize)
    df["Return %"] = df["P&L"] / df["Invested"] * 100
    df["Share"]    = df["Current"] / df["Current"].sum() * 100
    df = df.sort_values("Current", ascending=False).reset_index(drop=True)

    # Funds held under MIN_HELD_YRS get a neutral colour: short-period XIRR is mostly noise
    held_ok = df["Held (yrs)"].fillna(MIN_HELD_YRS) >= MIN_HELD_YRS
    df["XIRR (colour)"] = df["XIRR"].where(held_ok, HURDLE)

    # ── Where the money is ────────────────────────────────────────────
    sec_header(
        ICON_TREEMAP, "Where your money is",
        f"size = current value · colour = XIRR vs {HURDLE:.0f}% hurdle · grey = held < {MIN_HELD_YRS:.0f} yr",
    )
    col_map, col_side = st.columns([3, 2], gap="large")

    with col_map:
        fig_tree = px.treemap(
            df, path=["Fund"], values="Current", color="XIRR (colour)",
            custom_data=["Share", "XIRR", "Invested", "Held (yrs)"],
            color_continuous_scale=["#B91C1C", "#1F2937", "#15803D"],
            color_continuous_midpoint=HURDLE,
        )
        fig_tree.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}% · XIRR %{customdata[1]:.1f}%",
            textfont=dict(size=13, family="Space Grotesk"),
            marker=dict(line=dict(width=2, color="#060910")),
            hovertemplate=(
                "<b>%{label}</b><br>₹%{value:,.0f}<br>"
                "Invested ₹%{customdata[2]:,.0f}<br>"
                "XIRR %{customdata[1]:.2f}%<br>"
                "Held %{customdata[3]:.1f} yrs<extra></extra>"
            ),
        )
        fig_tree.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=0, l=0, r=0, b=0), height=470,
            font=dict(color="white", family="Space Grotesk"),
            coloraxis_colorbar=dict(title="XIRR %", thickness=10, len=0.6),
        )
        st.plotly_chart(fig_tree, use_container_width=True)

    with col_side:
        small_title("Category split")
        cat = (df.groupby("Category", as_index=False)["Current"].sum()
                 .sort_values("Current", ascending=False))
        cat["Share"] = cat["Current"] / cat["Current"].sum() * 100
        cat["Label"] = cat["Share"].map("{:.0f}%".format)
        cat["Row"]   = "Portfolio"

        fig_cat = px.bar(
            cat, x="Share", y="Row", color="Category", orientation="h",
            text="Label", color_discrete_sequence=PALETTE,
        )
        fig_cat.update_traces(textposition="inside", marker_line_width=0)
        fig_cat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=170,
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis=dict(visible=False, range=[0, 100]),
            yaxis=dict(visible=False),
            legend=dict(orientation="h", y=-0.15, title=None),
            font=dict(color="white", family="Space Grotesk"),
        )
        st.plotly_chart(fig_cat, use_container_width=True)

        # Rank only funds with a meaningful holding period (fallback: all)
        ranked = df[held_ok] if held_ok.sum() >= 3 else df

        def perf_rows(sub, color):
            return "".join(
                f'<div style="display:flex;justify-content:space-between;padding:6px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.06);font-size:13px;">'
                f'<span style="color:#E5E7EB;">{r.Fund}</span>'
                f'<span style="color:{color};font-weight:600;">{r.XIRR:.1f}%</span></div>'
                for r in sub.itertuples()
            )

        small_title(f"Best XIRR (held ≥ {MIN_HELD_YRS:.0f} yr)")
        st.markdown(perf_rows(ranked.nlargest(3, "XIRR"), SUCCESS), unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        small_title("Weakest XIRR")
        st.markdown(perf_rows(ranked.nsmallest(3, "XIRR"), DANGER), unsafe_allow_html=True)

    st.divider()

    # ── Fund table ────────────────────────────────────────────────────
    sec_header(ICON_FUND, "Fund Details", "live NAV · invested · P&L · XIRR")
    st.dataframe(
        df[["Fund", "Category", "Invested", "Current", "P&L", "Return %", "XIRR", "Held (yrs)"]],
        hide_index=True, use_container_width=True,
        height=min(40 * (len(df) + 1), 620),
        column_config={
            "Invested": st.column_config.NumberColumn(format="₹%d"),
            "Current":  st.column_config.NumberColumn(format="₹%d"),
            "P&L": st.column_config.ProgressColumn(
                format="₹%d",
                min_value=min(0.0, float(df["P&L"].min())),
                max_value=float(df["P&L"].max()),
            ),
            "Return %":   st.column_config.NumberColumn(format="%.1f"),
            "XIRR":       st.column_config.NumberColumn("XIRR %", format="%.2f"),
            "Held (yrs)": st.column_config.NumberColumn(format="%.1f"),
        },
    )

    with st.expander("More columns (code, units, NAV)"):
        st.dataframe(
            df[["Fund", "Code", "Units", "NAV", "NAV Date"]],
            hide_index=True, use_container_width=True,
        )

    # ── Downloads ─────────────────────────────────────────────────────
    export_df = df.drop(columns=["Share", "XIRR (colour)"]).copy()
    export_df["NAV Date"] = pd.to_datetime(export_df["NAV Date"]).dt.strftime("%d-%m-%Y")
    export_df = export_df.rename(columns={
        "Units": "Units",
        "Invested": "Invested (INR)",
        "Current": "Current Value (INR)",
        "P&L": "P&L (INR)",
        "XIRR": "XIRR (%)",
        "Return %": "Return (%)",
    })

    stamp = datetime.now().strftime("%Y%m%d")
    d1, d2, _ = st.columns([1, 1, 4])

    with d1:
        st.download_button(
            "⬇ CSV",
            data=export_df.to_csv(index=False).encode("utf-8-sig"),  # utf-8-sig so Excel opens it cleanly
            file_name=f"fund_details_{stamp}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with d2:
        try:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Fund Details")
            st.download_button(
                "⬇ Excel",
                data=buf.getvalue(),
                file_name=f"fund_details_{stamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except ModuleNotFoundError:
            st.caption("Add `openpyxl` to requirements.txt for Excel export.")


with tab1:
    render_fund_tab(summary)


# =========================================================
# SHARED HELPERS FOR TABS 2–4
# =========================================================
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_map   = {i + 1: n for i, n in enumerate(MONTH_NAMES)}
DIVERGING   = [[0, "#B91C1C"], [0.5, "#1F2937"], [1, "#15803D"]]


def keyed_container(key):
    """st.container(key=...) needs Streamlit >= 1.39; fall back to a plain container."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _inr(v, decimals=0):
    return f"{'+' if v >= 0 else '−'}₹{abs(v):,.{decimals}f}"


def _short(name, n=26):
    return name if len(name) <= n else name[:n - 1] + "…"


def _compact_inr(v):
    a = abs(v)
    if a >= 1e5:
        return f"{v / 1e5:+.1f}L"
    if a >= 1e3:
        return f"{v / 1e3:+.1f}k"
    return f"{v:+.0f}"


def _pfmt(x):
    return "n/a" if pd.isna(x) else f"{x:+.2f}%"


def _lakh(v):
    return f"₹{v / 1e5:.2f}L" if abs(v) >= 1e5 else f"₹{v:,.0f}"


def _tint_value(v):
    """Green for positive, red for negative; works on numbers and strings like '-1.2%'."""
    try:
        x = float(str(v).replace("%", "").replace(",", "").replace("₹", "").replace("+", ""))
    except ValueError:
        return ""
    if x > 0:
        return "color: #69F0AE; font-weight: 600"
    if x < 0:
        return "color: #FF6B6B; font-weight: 600"
    return "color: #9CA3AF"


def _fmt_dash(x):
    return "–" if (pd.isna(x) or x == 0) else f"{x:,.0f}"


def _styler_map(styler, func, subset):
    return (styler.map if hasattr(styler, "map") else styler.applymap)(func, subset=subset)


# =========================================================
# TAB 2 — DAILY PORTFOLIO SUMMARY
# =========================================================
def render_daily_tab():
    sec_header(ICON_DAILY_SUMMARY, "Daily Portfolio Summary",
               "performance · drawdown · monthly P&L")

    try:
        full, basis = load_portfolio_daily()
    except Exception as e:
        st.error(f"Could not load data/portfolio_daily.csv: {e}")
        return
    if full.empty:
        st.warning("data/portfolio_daily.csv has no rows.")
        return

    PERIODS  = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "All": None, "Custom": -1}
    min_date = full["Date"].min().date()
    max_date = full["Date"].max().date()

    # Optional "invested" column — opt-in, because the column name is a guess
    inv_col = next((c for c in full.columns
                    if "invest" in c.lower() and pd.api.types.is_numeric_dtype(full[c])), None)

    # ── Controls ─────────────────────────────────────────────────────
    col_btns, col_custom, col_inv = st.columns([3, 2.5, 2])
    with col_btns:
        with keyed_container("pillgroup_daily"):
            selected_period = st.radio(
                "Period", options=list(PERIODS.keys()),
                index=list(PERIODS.keys()).index("All"),      # default → All
                horizontal=True, label_visibility="collapsed",
            )
    with col_inv:
        show_inv = st.toggle(f"Show “{inv_col}” line", value=False) if inv_col else False

    if selected_period == "Custom":
        with col_custom:
            custom_range = st.date_input(
                "Date range", value=(min_date, max_date),
                min_value=min_date, max_value=max_date, label_visibility="collapsed",
            )
        # date_input returns a tuple only when both ends are picked
        if isinstance(custom_range, (list, tuple)) and len(custom_range) == 2:
            start_date, end_date = custom_range
        else:
            start_date, end_date = min_date, max_date
        chart_df = full[(full["Date"].dt.date >= start_date) &
                        (full["Date"].dt.date <= end_date)].copy()
    else:
        days = PERIODS[selected_period]
        if days is None:
            chart_df = full.copy()
        else:
            cutoff   = full["Date"].max() - pd.Timedelta(days=days)
            chart_df = full[full["Date"] >= cutoff].copy()

    chart_df = chart_df.dropna(subset=["OneDayChange"])
    if len(chart_df) < 2:
        st.info("Not enough data in this range — pick a wider period.")
        return

    # ── Period statistics ────────────────────────────────────────────
    chg = chart_df["OneDayChange"]
    pct = pd.to_numeric(
        chart_df["OneDayChangePct"].astype(str).str.replace("%", "", regex=False),
        errors="coerce",
    )
    cum         = (1 + pct.fillna(0) / 100).cumprod()           # return index, ignores new contributions
    drawdown    = (cum / cum.cummax() - 1) * 100
    period_pnl  = float(chg.sum())
    period_ret  = float((cum.iloc[-1] - 1) * 100)
    max_dd      = float(drawdown.min())
    n_up, n_down = int((chg > 0).sum()), int((chg < 0).sum())
    best_i, worst_i = chg.idxmax(), chg.idxmin()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5, k6 = st.columns([1.3, 1, 1, 1, 1, 1])
    with k1:
        st.markdown(kpi_card(
            "Period P&L", _inr(period_pnl), SUCCESS if period_pnl >= 0 else DANGER,
            f"{chart_df['Date'].min():%d %b} → {chart_df['Date'].max():%d %b %Y}", hero=True),
            unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card(
            "Return", f"{period_ret:+.2f}%", SUCCESS if period_ret >= 0 else DANGER,
            "compounded daily %"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card(
            "Up days", f"{n_up / len(chart_df) * 100:.0f}%", "#F1F5F9",
            f"{n_up} up · {n_down} down"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card(
            "Best day", _inr(chg[best_i]), SUCCESS,
            f"{chart_df.loc[best_i, 'Date']:%d %b %Y} · {_pfmt(pct[best_i])}"), unsafe_allow_html=True)
    with k5:
        st.markdown(kpi_card(
            "Worst day", _inr(chg[worst_i]), DANGER,
            f"{chart_df.loc[worst_i, 'Date']:%d %b %Y} · {_pfmt(pct[worst_i])}"), unsafe_allow_html=True)
    with k6:
        st.markdown(kpi_card(
            "Max drawdown", f"{max_dd:.2f}%", DANGER if max_dd < 0 else "#F1F5F9",
            "peak to trough"), unsafe_allow_html=True)

    if basis == "gain":
        st.caption("Daily change = day-on-day change in gain/loss (value − invested), summed across funds. "
                   "New SIP money is excluded; % is P&L ÷ previous day's total value.")
    else:
        st.warning("Per-fund daily files not found — daily change below is the change in total value "
                   "and includes new investments.")

    # ── Main chart: daily change bars + total value ──────────────────
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    small_title("Portfolio performance · daily change & total value")
    bar_colors = [SUCCESS if x >= 0 else DANGER for x in chg]

    fig_perf = make_subplots(specs=[[{"secondary_y": True}]])
    fig_perf.add_trace(go.Bar(
        x=chart_df["Date"], y=chg,
        name="Daily Change (₹)", marker_color=bar_colors, marker_line_width=0, opacity=0.75,
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Daily Change: ₹%{y:,.2f}<extra></extra>"
    ), secondary_y=False)
    fig_perf.add_trace(go.Scatter(
        x=chart_df["Date"], y=chart_df["TotalValue"],
        name="Total Value (₹)", mode="lines",
        line=dict(color="#4FC3F7", width=2.5),
        fill="tozeroy", fillcolor="rgba(79,139,249,0.06)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.0f}<extra></extra>"
    ), secondary_y=True)
    if show_inv and inv_col:
        fig_perf.add_trace(go.Scatter(
            x=chart_df["Date"], y=chart_df[inv_col],
            name=f"{inv_col} (₹)", mode="lines",
            line=dict(color="#EF9F27", width=2, dash="dot"),
            hovertemplate="<b>%{x|%d %b %Y}</b><br>" + inv_col + ": ₹%{y:,.0f}<extra></extra>"
        ), secondary_y=True)
    fig_perf.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
        font=dict(color="rgba(255,255,255,0.6)", family="Space Grotesk"),
        hovermode="x unified", height=460, margin=dict(t=20, b=40, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
            font=dict(size=12, color="rgba(255,255,255,0.6)"), bgcolor="rgba(0,0,0,0)"
        ),
        bargap=0.3,
        xaxis=dict(showgrid=False, zeroline=False),
    )
    fig_perf.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                          zeroline=False, tickprefix="₹", secondary_y=False)
    fig_perf.update_yaxes(showgrid=False, zeroline=False, tickprefix="₹", secondary_y=True)
    st.plotly_chart(fig_perf, use_container_width=True)

    # ── Drawdown + monthly P&L heatmap ───────────────────────────────
    col_dd, col_heat = st.columns(2, gap="large")

    with col_dd:
        small_title("Drawdown from peak (return-based, ignores new money)")
        fig_dd = go.Figure(go.Scatter(
            x=chart_df["Date"], y=drawdown, mode="lines",
            line=dict(color=DANGER, width=1.8),
            fill="tozeroy", fillcolor="rgba(226,75,74,0.18)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Drawdown: %{y:.2f}%<extra></extra>",
        ))
        fig_dd.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
            font=dict(color="rgba(255,255,255,0.6)", family="Space Grotesk"),
            height=300, margin=dict(t=10, b=30, l=10, r=10), showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                       zeroline=False, ticksuffix="%"),
        )
        st.plotly_chart(fig_dd, use_container_width=True)

    with col_heat:
        small_title("Monthly P&L (₹, all history)")
        monthly_pnl = (
            full.assign(Year=full["Date"].dt.year, Month=full["Date"].dt.month)
                .groupby(["Year", "Month"])["OneDayChange"].sum()
                .unstack("Month").reindex(columns=range(1, 13))
        )
        z    = monthly_pnl.to_numpy(dtype=float)
        text = [["" if pd.isna(v) else _compact_inr(v) for v in row] for row in z]
        fig_heat = go.Figure(go.Heatmap(
            z=z, x=MONTH_NAMES, y=[str(y) for y in monthly_pnl.index],
            text=text, texttemplate="%{text}", textfont=dict(size=11),
            colorscale=DIVERGING, zmid=0, showscale=False, xgap=3, ygap=3,
            hoverongaps=False,
            hovertemplate="<b>%{y} %{x}</b><br>P&L: ₹%{z:+,.0f}<extra></extra>",
        ))
        fig_heat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)", family="Space Grotesk"),
            height=max(200, len(monthly_pnl) * 48 + 70), margin=dict(t=10, b=10, l=10, r=10),
            yaxis=dict(type="category", autorange="reversed"),
            xaxis=dict(side="top"),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Data table + download ────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with st.expander(f"Daily data table · {len(chart_df)} days in view", expanded=False):
        disp = chart_df.sort_values("Date", ascending=False).copy()
        disp["Date"] = disp["Date"].dt.strftime("%d-%m-%Y")

        fmt = {}
        for c in disp.columns:
            if c != "Date" and pd.api.types.is_numeric_dtype(disp[c]):
                fmt[c] = ("{:+,.2f}" if c in ("OneDayChange", "NewMoney")
                          else "{:+.2f}%" if c == "OneDayChangePct" else "{:,.2f}")
        styler = disp.style.format(fmt)
        tint_cols = [c for c in ("OneDayChange", "OneDayChangePct") if c in disp.columns]
        if tint_cols:
            styler = _styler_map(styler, _tint_value, tint_cols)

        if "NewMoney" in disp.columns:
            st.caption("NewMoney = the CSV's old value-based change − the gain-based change. "
                       "It should be ≈ your SIP amount on SIP dates and ≈ 0 on other days.")
        st.dataframe(styler, hide_index=True, use_container_width=True, height=420)
        st.download_button(
            "⬇ CSV (this view)",
            data=disp.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"portfolio_daily_{datetime.now():%Y%m%d}.csv",
            mime="text/csv",
        )


with tab2:
    render_daily_tab()


# =========================================================
# TAB 3 — MONTHLY INVESTMENT SUMMARY
# =========================================================
@st.cache_data(ttl=900, show_spinner=False)
def load_monthly_investments():
    """Returns (DataFrame[Code, Fund, Year, Month, Amount], warning messages)."""
    rows, msgs = [], []
    for fund_name, meta in mutual_funds.items():
        try:
            d = load_fund(meta["folder"]).copy()
            d["Date"] = pd.to_datetime(d["Date"], errors="coerce")
            d = d.dropna(subset=["Date"])
            g = (d.groupby([d["Date"].dt.year.rename("Year"),
                            d["Date"].dt.month.rename("Month")])["Amount"]
                   .sum().reset_index())
            for _, r in g.iterrows():
                rows.append([meta["code"], fund_name, int(r["Year"]), int(r["Month"]), float(r["Amount"])])
        except Exception as e:
            msgs.append(f"{fund_name} skipped: {e}")
    return pd.DataFrame(rows, columns=["Code", "Fund", "Year", "Month", "Amount"]), msgs


def render_monthly_tab():
    sec_header(ICON_MONTHLY, "Monthly Investment Summary", "SIP breakdown by fund & month")

    monthly_df, msgs = load_monthly_investments()
    for m in msgs:
        st.warning(m)
    if monthly_df.empty:
        st.info("No investment data found.")
        return

    monthly_df = monthly_df.copy()
    monthly_df["Category"] = monthly_df["Fund"].map(categorize)
    years = sorted(monthly_df["Year"].unique())

    # ── Controls ─────────────────────────────────────────────────────
    c_year, c_group, c_cum, _ = st.columns([1.4, 2.4, 1.8, 3.4])
    with c_year:
        selected_year = int(st.selectbox("Select Year", years, index=len(years) - 1))
    with c_group:
        with keyed_container("pillgroup_monthly"):
            group_by = st.radio("Chart groups", ["Fund", "Category"], horizontal=True)
    with c_cum:
        show_cum = st.toggle("Cumulative line", value=True)

    year_df = monthly_df[monthly_df["Year"] == selected_year]
    now     = datetime.now()
    elapsed = 12 if selected_year < now.year else (now.month if selected_year == now.year else 12)

    by_month   = year_df.groupby("Month")["Amount"].sum().reindex(range(1, 13), fill_value=0.0)
    total_year = float(by_month.sum())
    prev_total = float(monthly_df.loc[monthly_df["Year"] == selected_year - 1, "Amount"].sum())
    avg_month  = total_year / elapsed if elapsed else 0.0
    peak_month = int(by_month.idxmax())
    invested_m = int((by_month.iloc[:elapsed] > 0).sum())
    active     = int(year_df.loc[year_df["Amount"] > 0, "Fund"].nunique())
    lifetime   = float(monthly_df["Amount"].sum())

    if prev_total > 0:
        yoy = (total_year / prev_total - 1) * 100
        yoy_text, yoy_color = f"{yoy:+.1f}% vs {selected_year - 1}", (SUCCESS if yoy >= 0 else DANGER)
    else:
        yoy_text, yoy_color = f"no {selected_year - 1} data to compare", "rgba(255,255,255,0.45)"

    # ── Summary strip ────────────────────────────────────────────────
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns([1.3, 1, 1, 1, 1])
    with k1:
        st.markdown(kpi_card(f"Invested in {selected_year}", f"₹{total_year:,.0f}", "#F1F5F9",
                             yoy_text, yoy_color, hero=True), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("Monthly average", f"₹{avg_month:,.0f}", "#F1F5F9",
                             f"over {elapsed} months"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Peak month", f"{month_map[peak_month]}", "#F1F5F9",
                             f"₹{by_month[peak_month]:,.0f}"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Consistency", f"{invested_m} / {elapsed}",
                             SUCCESS if invested_m == elapsed else "#F1F5F9",
                             "months with an investment"), unsafe_allow_html=True)
    with k5:
        st.markdown(kpi_card("Active funds", f"{active}", "#F1F5F9",
                             f"lifetime ₹{lifetime:,.0f}"), unsafe_allow_html=True)

    # ── Stacked bars + cumulative line ───────────────────────────────
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    small_title(f"Monthly investment by {group_by.lower()}")
    grp   = year_df.groupby([group_by, "Month"])["Amount"].sum().reset_index()
    order = grp.groupby(group_by)["Amount"].sum().sort_values(ascending=False).index

    fig_month = make_subplots(specs=[[{"secondary_y": True}]])
    for i, name in enumerate(order):
        s = (grp[grp[group_by] == name].set_index("Month")["Amount"]
                .reindex(range(1, 13), fill_value=0.0))
        fig_month.add_trace(go.Bar(
            x=MONTH_NAMES, y=s.values, name=str(name),
            marker_color=PALETTE[i % len(PALETTE)],
            hovertemplate="<b>" + str(name) + "</b><br>%{x}: ₹%{y:,.0f}<extra></extra>",
        ), secondary_y=False)
    if show_cum:
        cum = by_month.cumsum().iloc[:elapsed]
        fig_month.add_trace(go.Scatter(
            x=MONTH_NAMES[:elapsed], y=cum.values, name="Cumulative (₹)",
            mode="lines+markers", line=dict(color="#4FC3F7", width=2.5), marker=dict(size=6),
            hovertemplate="<b>Cumulative</b><br>%{x}: ₹%{y:,.0f}<extra></extra>",
        ), secondary_y=True)
    legend_rows   = -(-(len(order) + (1 if show_cum else 0)) // 4)   # ≈ 4 legend entries per row
    legend_bottom = 60 + 22 * legend_rows
    fig_month.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
        font=dict(color="rgba(255,255,255,0.6)", family="Space Grotesk"),
        height=380 + legend_bottom, margin=dict(t=20, b=legend_bottom, l=10, r=10),   # room for the legend
        legend=dict(font=dict(size=11, color="rgba(255,255,255,0.7)"),
                    bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="top", y=-0.12, xanchor="left", x=0),
        bargap=0.25, hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False, automargin=True,
                   categoryorder="array", categoryarray=MONTH_NAMES),
    )
    fig_month.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                           zeroline=False, tickprefix="₹", secondary_y=False)
    fig_month.update_yaxes(showgrid=False, zeroline=False, tickprefix="₹",
                           rangemode="tozero", secondary_y=True)
    st.plotly_chart(fig_month, use_container_width=True)

    # ── Fund × month table (heat-shaded, numeric, no inner scroll) ───
    small_title("Fund × month")
    pivot = (year_df.pivot_table(index=["Code", "Fund"], columns="Month",
                                 values="Amount", aggfunc="sum", fill_value=0)
                    .reindex(columns=range(1, 13), fill_value=0))
    pivot.columns = MONTH_NAMES
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False).reset_index()
    pivot["Code"] = pivot["Code"].astype(str)

    total_row = {"Code": "", "Fund": "TOTAL",
                 **{m: float(pivot[m].sum()) for m in MONTH_NAMES + ["Total"]}}
    final_df = pd.concat([pivot, pd.DataFrame([total_row])], ignore_index=True)

    vmax = float(pivot[MONTH_NAMES].to_numpy().max()) or 1.0

    def _shade(v):
        if not isinstance(v, (int, float)) or pd.isna(v) or v <= 0:
            return "color: rgba(255,255,255,0.25)"
        a = min(0.6, 0.12 + 0.48 * v / vmax)
        return f"background-color: rgba(29,158,117,{a:.2f}); color: #F0F4FF"

    def _bold_total(row):
        return ["font-weight: 700; border-top: 1px solid rgba(255,255,255,0.25)"
                if row["Fund"] == "TOTAL" else "" for _ in row]

    styler = final_df.style.format({c: _fmt_dash for c in MONTH_NAMES + ["Total"]})
    styler = _styler_map(styler, _shade, pd.IndexSlice[final_df.index[:-1], MONTH_NAMES])
    styler = styler.apply(_bold_total, axis=1)

    st.dataframe(
        styler, hide_index=True, use_container_width=True,
        height=min((len(final_df) + 1) * 35 + 3, 760),
        column_config={"Fund": st.column_config.TextColumn(width="large")},
    )
    st.download_button(
        f"⬇ CSV ({selected_year})",
        data=final_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"monthly_investment_{selected_year}.csv",
        mime="text/csv",
    )

    # ── Year-over-year + fund share ──────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    col_y, col_s = st.columns(2, gap="large")

    with col_y:
        small_title("Invested per year")
        by_year = monthly_df.groupby("Year")["Amount"].sum().reset_index()
        fig_y = go.Figure(go.Bar(
            x=by_year["Year"].astype(str), y=by_year["Amount"],
            marker_color=[SUCCESS if y == selected_year else "#3D5A80" for y in by_year["Year"]],
            text=[_lakh(v) for v in by_year["Amount"]], textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        ))
        fig_y.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.7)", family="Space Grotesk"),
            height=320, margin=dict(t=20, b=10, l=10, r=10),
            xaxis=dict(type="category", showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickprefix="₹"),
        )
        st.plotly_chart(fig_y, use_container_width=True)

    with col_s:
        small_title(f"Share of {selected_year} investment by fund")
        fund_tot = year_df.groupby("Fund")["Amount"].sum()
        fund_tot = fund_tot[fund_tot > 0].sort_values()
        if fund_tot.empty or total_year <= 0:
            st.info("No investments in this year.")
        else:
            fig_s = go.Figure(go.Bar(
                x=fund_tot.values, y=[_short(n, 30) for n in fund_tot.index], orientation="h",
                marker_color=SUCCESS,
                text=[f"{v / total_year * 100:.0f}%" for v in fund_tot.values],
                textposition="outside", cliponaxis=False,
                customdata=list(fund_tot.index),
                hovertemplate="<b>%{customdata}</b><br>₹%{x:,.0f}<extra></extra>",
            ))
            fig_s.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="rgba(255,255,255,0.7)", family="Space Grotesk"),
                height=max(320, len(fund_tot) * 28 + 60), margin=dict(t=10, b=10, l=10, r=40),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickprefix="₹"),
                yaxis=dict(automargin=True),
            )
            st.plotly_chart(fig_s, use_container_width=True)


with tab3:
    render_monthly_tab()


# =========================================================
# TAB 4 — DAILY CHANGE ACROSS FUNDS
# =========================================================
def compute_daily_changes(daily_files, target_date):
    """One row per fund that has a NAV on target_date and an earlier NAV to compare with."""
    target = pd.Timestamp(target_date)
    rows = []
    for fund_name, (code, d) in daily_files.items():
        today = d[d["date"] == target]
        prev  = d[d["date"] < target]
        if today.empty or prev.empty:
            continue
        rt, rp = today.iloc[-1], prev.iloc[-1]
        nav_t, nav_p = float(rt["nav"]), float(rp["nav"])
        rows.append({
            "Fund": fund_name,
            "Code": code,
            "Change (₹)": round(float(rt["absolute_gain_loss"]) - float(rp["absolute_gain_loss"]), 2),
            "NAV %": ((nav_t - nav_p) / nav_p * 100) if nav_p != 0 else 0.0,
        })
    return pd.DataFrame(rows, columns=["Fund", "Code", "Change (₹)", "NAV %"])


def _shift_daily_date(direction, dates):
    """Button callback: jump to the previous / next date that actually has data."""
    cur = st.session_state["daily_date"]
    if direction < 0:
        earlier = [d for d in dates if d < cur]
        if earlier:
            st.session_state["daily_date"] = earlier[-1]
    else:
        later = [d for d in dates if d > cur]
        if later:
            st.session_state["daily_date"] = later[0]


with tab4:
    sec_header(ICON_DAILY_CHANGE, "Daily Change Across Funds", "NAV movement · single date")

    daily_files = load_daily_files()
    avail_dates = sorted({x for _, d in daily_files.values() for x in d["date"].dt.date})

    if "daily_date" not in st.session_state:
        st.session_state["daily_date"] = nav_df["Date"].max().date()
    cur_date = st.session_state["daily_date"]

    # ── Date controls: previous / picker / next ──────────────────────
    b1, b2, b3, _ = st.columns([1.2, 2, 1.2, 6])
    with b1:
        st.button("◀ Prev day", key="daily_prev", use_container_width=True,
                  on_click=_shift_daily_date, args=(-1, avail_dates),
                  disabled=not any(d < cur_date for d in avail_dates))
    with b2:
        st.date_input("Select date", key="daily_date", label_visibility="collapsed")
    with b3:
        st.button("Next day ▶", key="daily_next", use_container_width=True,
                  on_click=_shift_daily_date, args=(1, avail_dates),
                  disabled=not any(d > cur_date for d in avail_dates))

    selected_date = st.session_state["daily_date"]
    df_day = compute_daily_changes(daily_files, selected_date)

    if df_day.empty:
        earlier = [d for d in avail_dates if d < selected_date]
        hint = (f" Most recent date with data before this one: **{earlier[-1].strftime('%d %b %Y')}**."
                if earlier else "")
        st.info(f"No fund data for {selected_date.strftime('%d %b %Y')} — probably a weekend or market holiday.{hint}")
    else:
        df_day = df_day.sort_values("Change (₹)", ascending=False).reset_index(drop=True)
        total_change = float(df_day["Change (₹)"].sum())
        n_up   = int((df_day["Change (₹)"] > 0).sum())
        n_down = int((df_day["Change (₹)"] < 0).sum())
        best, worst = df_day.iloc[0], df_day.iloc[-1]

        # ── Summary strip ────────────────────────────────────────────
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(kpi_card(
                "Total change", _inr(total_change),
                SUCCESS if total_change >= 0 else DANGER,
                selected_date.strftime("%A, %d %b %Y"), hero=True), unsafe_allow_html=True)
        with k2:
            st.markdown(kpi_card(
                "Up / Down", f"{n_up} / {n_down}", "#F1F5F9",
                f"of {len(df_day)} funds"), unsafe_allow_html=True)
        with k3:
            st.markdown(kpi_card(
                "Best fund", _short(best["Fund"]), "#F1F5F9",
                f"{_inr(best['Change (₹)'])} · {best['NAV %']:+.2f}%",
                SUCCESS if best["Change (₹)"] >= 0 else DANGER), unsafe_allow_html=True)
        with k4:
            st.markdown(kpi_card(
                "Worst fund", _short(worst["Fund"]), "#F1F5F9",
                f"{_inr(worst['Change (₹)'])} · {worst['NAV %']:+.2f}%",
                SUCCESS if worst["Change (₹)"] >= 0 else DANGER), unsafe_allow_html=True)

        shown   = set(df_day["Fund"])
        missing = [f for f in mutual_funds if f not in shown]
        if missing:
            st.caption(f"{len(shown)} of {len(mutual_funds)} funds have data for this date. "
                       f"No data: {', '.join(missing)}")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Chart (left) + full table (right, no scrolling) ──────────
        col_chart, col_tbl = st.columns([3, 2], gap="large")

        with col_chart:
            small_title("Change by fund")
            df_chart = df_day.sort_values("Change (₹)", ascending=True)
            vals = df_chart["Change (₹)"]
            lo, hi = min(float(vals.min()), 0.0), max(float(vals.max()), 0.0)
            span = (hi - lo) or 1.0

            fig = go.Figure(go.Bar(
                x=vals,
                y=[_short(n, 30) for n in df_chart["Fund"]],
                orientation="h",
                marker=dict(color=["#2ecc71" if v >= 0 else "#e74c3c" for v in vals]),
                text=[f"{_inr(v)} ({p:+.2f}%)" for v, p in zip(vals, df_chart["NAV %"])],
                textposition="outside",
                cliponaxis=False,
                textfont=dict(size=11),
                customdata=list(zip(df_chart["Fund"], df_chart["Code"], df_chart["NAV %"])),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Code: %{customdata[1]}<br>"
                    "Change: ₹%{x:+,.2f}<br>"
                    "NAV change: %{customdata[2]:+.2f}%<extra></extra>"
                ),
            ))
            fig.update_layout(
                height=max(320, len(df_chart) * 34 + 90),
                margin=dict(l=10, r=10, t=10, b=40),
                xaxis=dict(
                    title="Change in value (₹)",
                    range=[lo - span * (0.45 if lo < 0 else 0.02),
                           hi + span * (0.45 if hi > 0 else 0.02)],
                    zeroline=True, zerolinecolor="#555", zerolinewidth=1.5,
                    tickformat=",.0f", showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                ),
                yaxis=dict(automargin=True, tickfont=dict(size=12)),
                uniformtext=dict(mode="hide", minsize=9),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e0e0", family="Space Grotesk"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_tbl:
            small_title(f"All {len(df_day)} funds")

            table = df_day[["Fund", "Change (₹)", "NAV %"]].copy()

            table["Fund"] = table["Fund"].str.split().str[:3].str.join(" ")

            def _tint(v):
                c = "#69F0AE" if v > 0 else "#FF6B6B" if v < 0 else "#9CA3AF"
                return f"color: {c}; font-weight: 600"

            styler = table.style.format({"Change (₹)": "{:+,.2f}", "NAV %": "{:+.2f}%"})
            styler = (styler.map if hasattr(styler, "map") else styler.applymap)(
                _tint, subset=["Change (₹)", "NAV %"])

            st.dataframe(
                styler, hide_index=True, use_container_width=True,
                height=(len(table) + 1) * 35 + 3,      # every row visible, no inner scrollbar
                column_config={"Fund": st.column_config.TextColumn(width="large")},
            )


# =========================================================
# FOOTER
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
from utils.footer import show_footer
show_footer()
