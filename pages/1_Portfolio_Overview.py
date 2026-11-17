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
    if st.button(
        "↻ Refresh Portfolio",
        key="refresh_portfolio",
        use_container_width=True
    ):
        # Clear cached NAV
        get_nav.clear()

        # Clear cached fund calculations
        build_summary.clear()

        # Clear cached overall XIRR
        get_overall_xirr_pct.clear()

        # Recalculate everything
        st.rerun()

with info_col:
    st.caption(
        "Refresh after adding transactions, updating SIPs "
        "or downloading new NAV data."
    )

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

# Today's change for the hero card
try:
    _d = pd.read_csv("data/portfolio_daily.csv")
    _d["Date"] = pd.to_datetime(_d["Date"], format="%d-%m-%Y")
    day_change = float(_d.sort_values("Date").iloc[-1]["OneDayChange"])
except Exception:
    day_change = None

if day_change is None:
    day_sub, day_col = "live NAV", "rgba(255,255,255,0.45)"
else:
    day_sub = f"{'▲' if day_change >= 0 else '▼'} ₹{abs(day_change):,.0f} today"
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
    "≡  Fund Details",
    "▐  Daily Summary",
    "⊞  Monthly Investment",
    "∧  Daily Change",
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

    # ── Time-period filter ──────────────────────────────────────────────────
    chart_df_full = daily_df.sort_values("Date")

    PERIODS = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "All": None, "Custom": -1}

    col_btns, col_custom = st.columns([3, 2])

    with col_btns:
        selected_period = st.radio(
            "Period",
            options=list(PERIODS.keys()),
            index=list(PERIODS.keys()).index("All"),   # default → All
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
        # date_input returns a tuple only when both ends are picked
        if isinstance(custom_range, (list, tuple)) and len(custom_range) == 2:
            start_date, end_date = custom_range
        else:
            start_date, end_date = min_date, max_date

        chart_df = chart_df_full[
            (chart_df_full["Date"].dt.date >= start_date) &
            (chart_df_full["Date"].dt.date <= end_date)
        ].copy()
    else:
        days = PERIODS[selected_period]
        if days is None:
            chart_df = chart_df_full.copy()
        else:
            cutoff = chart_df_full["Date"].max() - pd.Timedelta(days=days)
            chart_df = chart_df_full[chart_df_full["Date"] >= cutoff].copy()
    # ────────────────────────────────────────────────────────────────────────

    chart_df["OneDayChangePct_val"] = (
        chart_df["OneDayChangePct"].astype(str).str.replace("%", "", regex=False).astype(float)
    )
    bar_colors = [SUCCESS if x >= 0 else DANGER for x in chart_df["OneDayChange"]]

    fig_perf = make_subplots(specs=[[{"secondary_y": True}]])
    fig_perf.add_trace(go.Bar(
        x=chart_df["Date"], y=chart_df["OneDayChange"],
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
    fig_perf.update_yaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.05)",
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
    sec_header(ICON_MONTHLY, "Monthly Investment Summary", "SIP breakdown by fund & month")

    monthly_data = []
    month_map    = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

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
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
            font=dict(color="rgba(255,255,255,0.6)", family="Space Grotesk"),
            height=340, margin=dict(t=20, b=10, l=10, r=10),
            legend=dict(
                font=dict(size=11, color="rgba(255,255,255,0.55)"),
                bgcolor="rgba(0,0,0,0)", orientation="h",
                yanchor="top", y=-0.2, xanchor="left", x=0
            ),
            bargap=0.25,
            xaxis=dict(
                showgrid=False, zeroline=False,
                categoryorder="array", categoryarray=list(month_map.values())
            ),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                zeroline=False, tickprefix="₹"
            ),
        )
        st.plotly_chart(fig_month, use_container_width=True)


# =========================================================
# TAB 4 — DAILY CHANGE ACROSS FUNDS
# =========================================================
with tab4:
    sec_header(ICON_DAILY_CHANGE, "Daily Change Across Funds", "NAV movement · single date")

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
            "#2ecc71" if v >= 0 else "#e74c3c"
            for v in df_chart["Change in Value"]
        ]

        # Truncate long names for display but keep full name in hover
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
            cliponaxis=False,          # stops Plotly clipping outside-labels
            textfont=dict(size=11),
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

        chart_height = max(300, len(df_chart) * 52 + 120)   # 52px per fund, min 300
        max_abs = df_chart["Change in Value"].abs().max()
        x_pad   = max_abs * 0.45                            # breathing room for labels

        fig.update_layout(
            title=dict(
                text=f"Daily Change in Value — {selected_date.strftime('%d %b %Y')}",
                font=dict(size=15),
                x=0,
            ),
            xaxis=dict(
                title="Change in Value (₹)",
                range=[-(max_abs + x_pad), max_abs + x_pad],
                zeroline=True,
                zerolinecolor="#555",
                zerolinewidth=1.5,
                tickformat=",.0f",
            ),
            yaxis=dict(
                automargin=True,
                tickfont=dict(size=12),
            ),
            height=chart_height,
            margin=dict(l=20, r=180, t=50, b=120),
            uniformtext=dict(mode="hide", minsize=9),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=12),
            ),
            # Manual legend
            annotations=[
                dict(
                    x=0.0, y=-0.13,
                    xref="paper", yref="paper",
                    text="🟢  Gain (positive change)",
                    showarrow=False,
                    font=dict(size=12, color="#2ecc71"),
                    xanchor="left",
                ),
                dict(
                    x=0.5, y=-0.13,
                    xref="paper", yref="paper",
                    text="🔴  Loss (negative change)",
                    showarrow=False,
                    font=dict(size=12, color="#e74c3c"),
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
