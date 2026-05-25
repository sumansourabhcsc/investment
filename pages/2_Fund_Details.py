import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import date, timedelta
import base64
import os
import math
import json

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.xirr_helper import compute_fund_xirr

# pages/2_Fund_Details.py
from utils.sidebar_style import render_sidebar
render_sidebar("fund_details")
# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Taurus: Funds", layout="wide", page_icon="🐂")


# =========================
# GLOBAL STYLES
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

.page-title {
    font-size: 26px; font-weight: 600; color: #ffffff;
    letter-spacing: -0.4px; margin-bottom: 2px;
}
.page-subtitle {
    font-size: 13px; color: rgba(255,255,255,0.45);
    font-family: 'DM Mono', monospace; margin-bottom: 1.5rem;
}
.fund-header {
    display: flex; align-items: center; gap: 14px; margin-bottom: 2px;
}
.fund-logo-wrap {
    width: 48px; height: 48px; border-radius: 10px;
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.1);
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; flex-shrink: 0;
}
.fund-logo-wrap img { width: 100%; height: 100%; object-fit: contain; padding: 4px; }
.fund-logo-fallback { font-size: 26px; line-height: 1; }

.nav-badge {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 14px 22px;
    display: inline-block; text-align: right;
}
.nav-badge .nav-val {
    font-size: 28px; font-weight: 600;
    font-family: 'DM Mono', monospace; color: #ffffff; line-height: 1.1;
}
.nav-badge .nav-date {
    font-size: 11px; color: rgba(255,255,255,0.4);
    margin-top: 3px; font-family: 'DM Mono', monospace;
}

.metric-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.5rem; }
.metric-card {
    flex: 1; min-width: 120px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 14px 16px;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 3px; height: 100%; border-radius: 3px 0 0 3px;
}
.metric-card.c-blue::before   { background: #4F8BF9; }
.metric-card.c-green::before  { background: #1D9E75; }
.metric-card.c-red::before    { background: #E24B4A; }
.metric-card.c-amber::before  { background: #EF9F27; }
.metric-card.c-purple::before { background: #7F77DD; }
.metric-card.c-pink::before   { background: #D4537E; }
.metric-card.c-teal::before   { background: #00f5d4; }

.metric-label {
    font-size: 10px; color: rgba(255,255,255,0.45);
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 6px; font-weight: 500;
}
.metric-value {
    font-size: 20px; font-weight: 600; color: #ffffff;
    font-family: 'DM Mono', monospace; line-height: 1.2;
}
.metric-value.pos { color: #1D9E75; }
.metric-value.neg { color: #E24B4A; }

.section-header {
    font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.5);
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.75rem; display: flex; align-items: center; gap: 8px;
}
.section-header span {
    flex: 1; height: 1px; background: rgba(255,255,255,0.08); display: inline-block;
}

/* ── Category pill buttons ── */
div[data-testid="stButton"].cat-pill > button,
div[data-testid="stButton"].cat-pill-active > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 5px 14px !important;
    border-radius: 20px !important;
    min-height: 0 !important;
    height: auto !important;
    line-height: 1.5 !important;
    white-space: nowrap !important;
}
div[data-testid="stButton"].cat-pill > button {
    border: 1px solid rgba(255,255,255,0.18) !important;
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.5) !important;
}
div[data-testid="stButton"].cat-pill > button:hover {
    border-color: rgba(0,245,212,0.4) !important;
    color: rgba(0,245,212,0.85) !important;
    background: rgba(0,245,212,0.06) !important;
}
div[data-testid="stButton"].cat-pill-active > button {
    border: 1px solid rgba(0,245,212,0.6) !important;
    background: rgba(0,245,212,0.13) !important;
    color: #00f5d4 !important;
}

/* ── Fund card buttons ── */
div[data-testid="stButton"].fund-card > button,
div[data-testid="stButton"].fund-card-active > button {
    text-align: left !important;
    width: 100% !important;
    min-height: 82px !important;
    height: auto !important;
    padding: 12px 14px !important;
    border-radius: 10px !important;
    line-height: 1.4 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    font-family: 'DM Mono', monospace !important;
}
div[data-testid="stButton"].fund-card > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    color: rgba(255,255,255,0.75) !important;
}
div[data-testid="stButton"].fund-card > button:hover {
    background: rgba(0,245,212,0.06) !important;
    border-color: rgba(0,245,212,0.35) !important;
}
div[data-testid="stButton"].fund-card-active > button {
    background: rgba(0,245,212,0.10) !important;
    border: 2px solid rgba(0,245,212,0.6) !important;
    color: #ffffff !important;
}

/* Tax Harvesting specific */
.harvest-result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 10px;
}
.harvest-result-card.highlight {
    background: rgba(29,158,117,0.08);
    border-color: rgba(29,158,117,0.3);
}
.harvest-result-card.warn {
    background: rgba(239,159,39,0.08);
    border-color: rgba(239,159,39,0.3);
}
.harvest-label {
    font-size: 11px; color: rgba(255,255,255,0.4);
    text-transform: uppercase; letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.harvest-value {
    font-size: 22px; font-weight: 600;
    font-family: 'DM Mono', monospace; color: #ffffff;
}
.harvest-sub {
    font-size: 11px; color: rgba(255,255,255,0.3);
    margin-top: 4px; font-family: 'DM Mono', monospace;
}
.lot-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 13px;
}
.lot-row:last-child { border-bottom: none; }
.lot-tag {
    font-size: 10px; padding: 2px 8px; border-radius: 20px;
    font-family: 'DM Mono', monospace; font-weight: 500;
}
.lot-tag.ltcg { background: rgba(29,158,117,0.15); color: #1D9E75; border: 1px solid rgba(29,158,117,0.3); }
.lot-tag.stcg { background: rgba(239,159,39,0.15); color: #EF9F27; border: 1px solid rgba(239,159,39,0.3); }
.lot-tag.sell { background: rgba(79,139,249,0.15); color: #4F8BF9; border: 1px solid rgba(79,139,249,0.3); }

[data-testid="stDataFrame"] {
    border-radius: 10px; overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
hr { border-color: rgba(255,255,255,0.07) !important; }
[data-testid="stSelectbox"] label {
    font-size: 12px !important; color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase; letter-spacing: 0.07em;
}
</style>
""", unsafe_allow_html=True)


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
        <div style="font-family:'JetBrains Mono',monospace; font-size:10px;
            color:rgba(255,255,255,0.3); margin-top:5px; letter-spacing:0.2em; text-transform:uppercase;">
            ◈ Taurus · Mutual Fund Tracker
        </div>
        <div style="display:inline-flex; align-items:center; gap:6px; margin-top:10px;
            background:rgba(29,158,117,0.1); border:1px solid rgba(29,158,117,0.25);
            border-radius:20px; padding:5px 12px; font-size:11px; font-weight:500;
            color:#1D9E75; font-family:'JetBrains Mono',monospace;">
            <div style="width:6px; height:6px; border-radius:50%; background:#1D9E75;
                animation:livepulse 2s ease-in-out infinite;"></div>
            Live NAV
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# =========================
# HELPERS
# =========================
def inr(val):
    return f"₹{val:,.2f}"

def pct(val, decimals=2):
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.{decimals}f}%"

def section_header(title):
    st.markdown(f'<div class="section-header">{title} <span></span></div>', unsafe_allow_html=True)

LOGO_MAP = {
    "mirae":        "mirae.png",
    "axis":         "axis.png",
    "bandhan":      "bandhan.png",
    "edelweiss":    "edelweiss.png",
    "hsbc":         "HSBC.png",
    "icici":        "icici.png",
    "kotak":        "kotak.png",
    "motilal":      "motilal.png",
    "nippon":       "nippon.png",
    "parag parikh": "paragparikh.png",
    "ppfas":        "paragparikh.png",
    "quant":        "quant.png",
    "sbi":          "sbi.png",
}

def get_logo_base64(fund_name: str) -> str | None:
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


# =========================
# DATA LOADING
# =========================
nav_df = load_nav()

fund_options = list(mutual_funds.keys())

# ── Derive all unique categories in config order ──
all_categories = ["All"] + sorted(
    list(dict.fromkeys(v["category"] for v in mutual_funds.values()))
)

# ── Session state: active category + selected fund ──
if "selected_fund" not in st.session_state:
    st.session_state.selected_fund = fund_options[0]
if "active_category" not in st.session_state:
    st.session_state.active_category = "All"


# =========================
# FUND SELECTOR — Option A
# =========================
section_header("🗂️ Select Fund")

# ── Category pill buttons ──
# Inject per-button class via a wrapping div keyed to each button
pill_cols = st.columns(len(all_categories))
for i, cat in enumerate(all_categories):
    is_active = st.session_state.active_category == cat
    css_class = "cat-pill-active" if is_active else "cat-pill"
    with pill_cols[i]:
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(cat, key=f"cat_{cat}", use_container_width=True):
            st.session_state.active_category = cat
            filtered = [
                n for n, v in mutual_funds.items()
                if cat == "All" or v["category"] == cat
            ]
            if st.session_state.selected_fund not in filtered:
                st.session_state.selected_fund = filtered[0]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

# ── Fund card buttons ──
filtered_funds = [
    (name, info) for name, info in mutual_funds.items()
    if st.session_state.active_category == "All"
    or info["category"] == st.session_state.active_category
]

cards_per_row = 4
rows = [filtered_funds[i:i+cards_per_row] for i in range(0, len(filtered_funds), cards_per_row)]

for row in rows:
    cols = st.columns(cards_per_row)
    for col, (name, info) in zip(cols, row):
        is_selected = st.session_state.selected_fund == name
        css_class = "fund-card-active" if is_selected else "fund-card"
        # Multi-line label: category / name / code — rendered as plain text inside the button
        label = f"{info['category'].upper()}\n{name}\n{info['code']}"
        with col:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"fund_{info['code']}", use_container_width=True):
                st.session_state.selected_fund = name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

st.divider()

# ── Resolve selected fund ──
selected_fund = st.session_state.selected_fund
scheme_code   = mutual_funds[selected_fund]["code"]
folio_no      = mutual_funds[selected_fund]["folio"]
folder        = mutual_funds[selected_fund]["folder"]
fund_df       = load_fund(folder)

daily_path = f"mutualfund/{folder}/daily_{scheme_code}.csv"
try:
    daily_df = pd.read_csv(daily_path)
    daily_df["Date"] = pd.to_datetime(daily_df["date"], format="%d-%m-%Y")
    daily_df = daily_df.sort_values("Date", ascending=False).reset_index(drop=True)
except FileNotFoundError:
    daily_df = pd.DataFrame()

match = nav_df[nav_df["SchemeCode"] == str(scheme_code)]
if match.empty:
    st.error("No NAV data found for this fund.")
    st.stop()

latest_row  = match.sort_values("Date", ascending=False).iloc[0]
latest_nav  = float(latest_row["NAV"])
latest_date = latest_row["Date"].date()


# =========================
# COMPUTED METRICS
# =========================
total_units     = fund_df["Units"].sum()
invested        = fund_df["Amount"].sum()
current_value   = total_units * latest_nav
profit          = current_value - invested
avg_buy_nav     = invested / total_units if total_units > 0 else 0
absolute_return = ((current_value - invested) / invested * 100) if invested > 0 else 0
fund_xirr       = compute_fund_xirr(fund_df, latest_nav)
xirr_pct        = fund_xirr * 100


# =========================
# HEADER
# =========================
col_title, col_nav = st.columns([3, 1])

with col_title:
    logo_inner = fund_logo_html(selected_fund)
    st.markdown(f"""
    <div class="fund-header">
        <div class="fund-logo-wrap">{logo_inner}</div>
        <div>
            <div class="page-title">{selected_fund}</div>
            <div class="page-subtitle">Scheme Code: {scheme_code} &nbsp;·&nbsp; Direct Growth &nbsp;·&nbsp; Folio No: {folio_no}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_nav:
    st.markdown(f"""
    <div class="nav-badge">
        <div class="nav-val">{inr(latest_nav)}</div>
        <div class="nav-date">NAV {latest_date}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# METRIC CARDS
# =========================
pnl_accent = "c-green" if profit >= 0 else "c-red"
pnl_color  = "pos"     if profit >= 0 else "neg"
ret_color  = "pos"     if absolute_return >= 0 else "neg"
xirr_color = "pos"     if xirr_pct >= 0 else "neg"

cards = [
    ("💰 Invested",      inr(invested),                                    "c-blue",   ""),
    ("📈 Current Value", inr(current_value),                               "c-green",  "pos"),
    ("📊 P&L",           ("+" if profit >= 0 else "") + inr(profit),       pnl_accent, pnl_color),
    ("📉 Abs. Return",   pct(absolute_return),                             "c-amber",  ret_color),
    ("🧮 Avg Buy NAV",   inr(avg_buy_nav),                                 "c-purple", ""),
    ("📦 Total Units",   f"{total_units:,.2f}",                            "c-pink",   ""),
    ("📌 XIRR",          pct(xirr_pct, 1),                                 "c-teal",   xirr_color),
]

st.markdown('<div class="metric-row">', unsafe_allow_html=True)
cols = st.columns(7)
for col, (label, value, accent, extra) in zip(cols, cards):
    with col:
        st.markdown(f"""
        <div class="metric-card {accent}">
            <div class="metric-label">{label}</div>
            <div class="metric-value {extra}">{value}</div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.divider()


# =========================
# TABS
# =========================
tab_overview, tab_nav_history, tab_harvest = st.tabs([
    "📋 Overview",
    "📈 NAV History",
    "🌾 Tax Harvesting"
])


# ─────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────
with tab_overview:

    col_sip, col_daily = st.columns(2)

    with col_sip:
        section_header("📋 SIP History")
        fund_df_sorted = fund_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
        fund_df_sorted["Date"] = fund_df_sorted["Date"].dt.date
        st.dataframe(fund_df_sorted, use_container_width=True, height=280)

    with col_daily:
        section_header("📅 Daily NAV Movement")
        if daily_df.empty:
            st.info("No daily snapshot data available for this fund.")
        else:
            df_display = daily_df.copy()
            df_display["Date"] = df_display["Date"].dt.date
            if "NAV" in df_display.columns:
                df_display["Daily Change %"] = (
                    df_display["NAV"].pct_change(-1) * 100
                ).round(2)
            st.dataframe(df_display, use_container_width=True, height=280)

    st.divider()
    section_header("📊 Portfolio Value Trend")

    if daily_df.empty:
        st.info("No daily snapshot data available to plot.")
    else:
        chart_df = daily_df.copy()
        chart_df["date"] = pd.to_datetime(chart_df["date"], format="%d-%m-%Y")
        chart_df = chart_df.sort_values("date")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=chart_df["date"], y=chart_df["current_value"],
            mode="lines+markers", name="Portfolio Value",
            line=dict(color="#1D9E75", width=2.5),
            marker=dict(size=5, color="#1D9E75"),
            fill="tozeroy", fillcolor="rgba(29,158,117,0.07)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.2f}<extra></extra>"
        ))
        if "invested" in chart_df.columns:
            fig2.add_trace(go.Scatter(
                x=chart_df["date"], y=chart_df["invested"],
                mode="lines", name="Invested",
                line=dict(color="#4F8BF9", width=1.5, dash="dot"),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Invested: ₹%{y:,.2f}<extra></extra>"
            ))
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif", color="rgba(255,255,255,0.6)"),
            margin=dict(l=10, r=10, t=20, b=10), height=380, hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=12)),
            xaxis=dict(showgrid=False, zeroline=False, title="Date"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, title="Value (₹)", tickprefix="₹"),
        )
        st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────
# TAB 2 — NAV HISTORY
# ─────────────────────────
with tab_nav_history:

    section_header("📈 NAV History")

    range_choice = st.radio(
        "Quick Range", options=["Custom", "1M", "3M", "6M", "1Y", "3Y", "All"],
        index=4, horizontal=True, label_visibility="collapsed", key="nav_range_choice"
    )

    range_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "All": 9999}

    if range_choice != "Custom":
        days          = range_map[range_choice]
        default_start = date.today() - timedelta(days=days)
        default_end   = date.today()
    else:
        default_start = date.today() - timedelta(days=365)
        default_end   = date.today()

    col_d1, col_d2, col_spacer = st.columns([1, 1, 3])

    if range_choice == "Custom":
        with col_d1:
            start_date = st.date_input("Start Date", value=default_start, max_value=date.today(), key="start_date")
        with col_d2:
            end_date = st.date_input("End Date", value=default_end, min_value=start_date, max_value=date.today(), key="end_date")
    else:
        start_date = default_start
        end_date   = default_end
        with col_d1:
            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:8px;
                background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.07);
                border-radius:6px;padding:5px 12px;font-family:'DM Mono',monospace;
                font-size:13px;color:rgba(255,255,255,0.5);">
                <span style="color:rgba(255,255,255,0.3);font-size:11px;">FROM</span>
                <span style="color:rgba(255,255,255,0.85);">{start_date.strftime("%d %b %Y")}</span>
            </div>""", unsafe_allow_html=True)
        with col_d2:
            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:8px;
                background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.07);
                border-radius:6px;padding:5px 12px;font-family:'DM Mono',monospace;
                font-size:13px;color:rgba(255,255,255,0.5);">
                <span style="color:rgba(255,255,255,0.3);font-size:11px;">TO</span>
                <span style="color:rgba(255,255,255,0.85);">{end_date.strftime("%d %b %Y")}</span>
            </div>""", unsafe_allow_html=True)

    def fetch_nav_history(fund_code):
        nav_file = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "NAVHistory", f"{fund_code}.json")
        )
        try:
            if not os.path.exists(nav_file):
                st.warning(f"NAV history file not found: NAVHistory/{fund_code}.json")
                return pd.DataFrame()
            with open(nav_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "data" in data and data["data"]:
                df = pd.DataFrame(data["data"])
                df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
                df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
                df = df.sort_values("date").reset_index(drop=True)
                df.rename(columns={"date": "Date", "nav": "NAV"}, inplace=True)
                return df
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to load NAV history: {e}")
            return pd.DataFrame()

    nav_df_full = fetch_nav_history(scheme_code)

    if not nav_df_full.empty:
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
        chg_color = "#1D9E75" if range_chg >= 0 else "#E24B4A"
        chg_sign  = "+" if range_chg >= 0 else ""

        st.markdown(f"""
        <div style="display:flex;gap:10px;margin:14px 0 18px 0;flex-wrap:wrap;">
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:10px 16px;min-width:130px;">
                <div style="font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">Highest NAV</div>
                <div style="font-size:15px;color:#fff;font-family:'DM Mono';">₹{max_row['NAV']:.4f}</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.25);margin-top:2px;">{max_row['Date'].strftime("%d %b %Y")}</div>
            </div>
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:10px 16px;min-width:130px;">
                <div style="font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">Lowest NAV</div>
                <div style="font-size:15px;color:#fff;font-family:'DM Mono';">₹{min_row['NAV']:.4f}</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.25);margin-top:2px;">{min_row['Date'].strftime("%d %b %Y")}</div>
            </div>
            <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:10px 16px;min-width:130px;">
                <div style="font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">Range Change</div>
                <div style="font-size:15px;color:{chg_color};font-family:'DM Mono';">{chg_sign}{range_chg:.2f}%</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.25);margin-top:2px;">{start_date.strftime("%d %b")} → {end_date.strftime("%d %b %Y")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_tbl, col_cht = st.columns([1, 2])
        with col_tbl:
            display_df = nav_filtered.copy()
            display_df = display_df.sort_values("Date", ascending=False).reset_index(drop=True)
            display_df["Date"] = display_df["Date"].dt.date
            display_df["NAV"]  = display_df["NAV"].round(4)
            st.dataframe(display_df, use_container_width=True, height=360)
        with col_cht:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=nav_filtered["Date"], y=nav_filtered["NAV"],
                mode="lines", name="NAV",
                line=dict(color="#4F8BF9", width=2),
                fill="tozeroy", fillcolor="rgba(79,139,249,0.08)",
                hovertemplate="<b>%{x|%d %b %Y}</b><br>NAV: ₹%{y:.4f}<extra></extra>"
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Outfit, sans-serif", color="rgba(255,255,255,0.6)"),
                margin=dict(l=10, r=10, t=20, b=10), height=360, hovermode="x unified", showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, tickprefix="₹"),
            )
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────
# TAB 3 — TAX HARVESTING
# ─────────────────────────
with tab_harvest:

    section_header("🌾 Tax Harvesting Calculator")

    # ── Helpers ──
    def holding_period_days(buy_date):
        return (date.today() - buy_date.date()).days

    def classify_lot(buy_date):
        return "LTCG" if holding_period_days(buy_date) > 365 else "STCG"

    def tax_rate(gain_type):
        return 0.125 if gain_type == "LTCG" else 0.20

    def style_gain_type(val):
        if val == "LTCG":
            return "color: #1D9E75; font-weight: 600;"
        return "color: #EF9F27; font-weight: 600;"

    def color_gain(val):
        if isinstance(val, (int, float)):
            return "color: #1D9E75;" if val >= 0 else "color: #E24B4A;"
        return ""

    # ── Build lot-wise breakdown ──
    lots = fund_df.copy().sort_values("Date").reset_index(drop=True)
    lots["Gain Type"]     = lots["Date"].apply(classify_lot)
    lots["Current Value"] = lots["Units"] * latest_nav
    lots["Gain"]          = lots["Current Value"] - lots["Amount"]
    lots["Gain %"]        = (lots["Gain"] / lots["Amount"] * 100).round(2)
    lots["Tax Rate"]      = lots["Gain Type"].apply(tax_rate)
    lots["Approx Tax"]    = (lots["Gain"].clip(lower=0) * lots["Tax Rate"]).round(2)
    lots["Holding Days"]  = lots["Date"].apply(holding_period_days)

    total_ltcg = lots.loc[lots["Gain Type"] == "LTCG", "Gain"].clip(lower=0).sum()
    total_stcg = lots.loc[lots["Gain Type"] == "STCG", "Gain"].clip(lower=0).sum()

    LTCG_EXEMPTION = 125000.0

    st.markdown("""
    <div style="background:rgba(79,139,249,0.07);border:1px solid rgba(79,139,249,0.2);
        border-radius:10px;padding:12px 16px;margin-bottom:20px;font-size:12.5px;
        color:rgba(255,255,255,0.6);line-height:1.7;">
        <b style="color:rgba(255,255,255,0.85);">How this works:</b>
        Equity MF gains held &gt;1 year are <b style="color:#1D9E75;">LTCG (12.5%)</b> with ₹1.25L annual exemption.
        Gains held ≤1 year are <b style="color:#EF9F27;">STCG (20%)</b>. Tax harvesting means realising gains
        up to the LTCG exemption limit each year to reset your cost basis — reducing future tax.
        Units are sold <b style="color:#fff;">oldest first (FIFO)</b>. Enter a target profit below to see
        exactly how many units to redeem.
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ──
    col_inp1, col_inp2 = st.columns([1, 1])

    with col_inp1:
        target_profit = st.number_input(
            "Target Profit to Harvest (₹)",
            min_value=0.0,
            max_value=float(max(profit, 0)),
            value=float(min(LTCG_EXEMPTION, max(profit, 0))),
            step=1000.0,
            format="%.2f",
            help="How much profit you want to realise. Default is the LTCG exemption limit ₹1,25,000."
        )

    with col_inp2:
        sell_nav = st.number_input(
            "Expected Sell NAV (₹)",
            min_value=0.01,
            value=float(latest_nav),
            step=0.01,
            format="%.4f",
            help="Defaults to today's NAV. Adjust if you expect to sell at a different price."
        )

    st.divider()

    # ── FIFO: oldest lots first ──
    sorted_lots = lots.sort_values("Date", ascending=True).reset_index(drop=True)

    remaining_target   = target_profit
    sell_plan          = []
    total_units_sell   = 0.0
    total_sell_value   = 0.0
    total_sell_cost    = 0.0
    total_sell_gain    = 0.0
    ltcg_gain_realised = 0.0
    stcg_gain_realised = 0.0

    for _, lot in sorted_lots.iterrows():
        if remaining_target <= 0:
            break

        lot_buy_nav   = lot["Amount"] / lot["Units"]
        gain_per_unit = sell_nav - lot_buy_nav

        if gain_per_unit <= 0:
            continue

        units_needed  = remaining_target / gain_per_unit
        units_to_sell = min(units_needed, lot["Units"])

        gain_from_lot  = units_to_sell * gain_per_unit
        cost_from_lot  = units_to_sell * lot_buy_nav
        value_from_lot = units_to_sell * sell_nav

        sell_plan.append({
            "SIP Date":        lot["Date"].date(),
            "Gain Type":       lot["Gain Type"],
            "Holding Days":    lot["Holding Days"],
            "Buy NAV":         round(lot_buy_nav, 4),
            "Units Available": round(lot["Units"], 4),
            "Units to Sell":   round(units_to_sell, 4),
            "Cost Basis":      round(cost_from_lot, 2),
            "Sell Value":      round(value_from_lot, 2),
            "Gain Realised":   round(gain_from_lot, 2),
        })

        total_units_sell   += units_to_sell
        total_sell_value   += value_from_lot
        total_sell_cost    += cost_from_lot
        total_sell_gain    += gain_from_lot

        if lot["Gain Type"] == "LTCG":
            ltcg_gain_realised += gain_from_lot
        else:
            stcg_gain_realised += gain_from_lot

        remaining_target -= gain_from_lot

    # ── Tax estimate ──
    taxable_ltcg = max(0.0, ltcg_gain_realised - LTCG_EXEMPTION)
    ltcg_tax     = taxable_ltcg * 0.125
    stcg_tax     = stcg_gain_realised * 0.20
    total_tax    = ltcg_tax + stcg_tax

    # ── Summary Cards ──
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)

    with col_r1:
        st.markdown(f"""
        <div class="harvest-result-card highlight">
            <div class="harvest-label">Units to Redeem</div>
            <div class="harvest-value">{total_units_sell:,.4f}</div>
            <div class="harvest-sub">of {total_units:,.4f} total units</div>
        </div>""", unsafe_allow_html=True)

    with col_r2:
        st.markdown(f"""
        <div class="harvest-result-card highlight">
            <div class="harvest-label">Redemption Amount</div>
            <div class="harvest-value">₹{total_sell_value:,.2f}</div>
            <div class="harvest-sub">at NAV ₹{sell_nav:,.4f}</div>
        </div>""", unsafe_allow_html=True)

    with col_r3:
        st.markdown(f"""
        <div class="harvest-result-card highlight">
            <div class="harvest-label">Profit Realised</div>
            <div class="harvest-value" style="color:#1D9E75;">₹{total_sell_gain:,.2f}</div>
            <div class="harvest-sub">LTCG ₹{ltcg_gain_realised:,.2f} · STCG ₹{stcg_gain_realised:,.2f}</div>
        </div>""", unsafe_allow_html=True)

    with col_r4:
        tax_color = "#EF9F27" if total_tax > 0 else "#1D9E75"
        st.markdown(f"""
        <div class="harvest-result-card warn">
            <div class="harvest-label">Estimated Tax</div>
            <div class="harvest-value" style="color:{tax_color};">₹{total_tax:,.2f}</div>
            <div class="harvest-sub">LTCG ₹{ltcg_tax:,.2f} · STCG ₹{stcg_tax:,.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Lot-wise Sell Plan ──
    if sell_plan:
        section_header("📑 Lot-wise Sell Plan")
        plan_df = pd.DataFrame(sell_plan)
        styled = (
            plan_df.style
            .map(style_gain_type, subset=["Gain Type"])
            .format({
                "Buy NAV":         "₹{:.4f}",
                "Units Available": "{:.4f}",
                "Units to Sell":   "{:.4f}",
                "Cost Basis":      "₹{:,.2f}",
                "Sell Value":      "₹{:,.2f}",
                "Gain Realised":   "₹{:,.2f}",
            })
        )
        st.dataframe(styled, use_container_width=True, height=260)
    else:
        st.info("No lots with gains found at the selected sell NAV.")

    st.divider()

    # ── All Lots Overview ──
    section_header("🗂️ All Lots Overview")

    lots_display = lots[[
        "Date", "Units", "Amount", "Gain Type", "Holding Days",
        "Current Value", "Gain", "Gain %", "Approx Tax"
    ]].copy()
    lots_display["Date"]          = lots_display["Date"].dt.date
    lots_display["Current Value"] = lots_display["Current Value"].round(2)
    lots_display["Gain"]          = lots_display["Gain"].round(2)
    lots_display["Approx Tax"]    = lots_display["Approx Tax"].round(2)

    lots_styled = (
        lots_display.style
        .map(color_gain, subset=["Gain", "Gain %"])
        .map(style_gain_type, subset=["Gain Type"])
        .format({
            "Amount":        "₹{:,.2f}",
            "Current Value": "₹{:,.2f}",
            "Gain":          "₹{:,.2f}",
            "Gain %":        "{:+.2f}%",
            "Approx Tax":    "₹{:,.2f}",
            "Units":         "{:.4f}",
        })
    )
    st.dataframe(lots_styled, use_container_width=True, height=300)

    # ── LTCG Exemption Bar ──
    st.divider()
    section_header("📊 LTCG Exemption Utilisation")

    used_pct  = min(ltcg_gain_realised / LTCG_EXEMPTION * 100, 100)
    bar_color = "#1D9E75" if used_pct <= 100 else "#E24B4A"

    st.markdown(f"""
    <div style="margin-bottom:8px;display:flex;justify-content:space-between;
        font-size:12px;color:rgba(255,255,255,0.5);font-family:'DM Mono',monospace;">
        <span>₹0</span>
        <span style="color:rgba(255,255,255,0.8);">
            ₹{ltcg_gain_realised:,.0f} of ₹{LTCG_EXEMPTION:,.0f} exempt limit used
        </span>
        <span>₹1,25,000</span>
    </div>
    <div style="background:rgba(255,255,255,0.07);border-radius:6px;height:10px;overflow:hidden;">
        <div style="width:{used_pct:.1f}%;background:{bar_color};height:100%;
            border-radius:6px;transition:width 0.4s ease;"></div>
    </div>
    <div style="margin-top:6px;font-size:11px;color:rgba(255,255,255,0.3);font-family:'DM Mono',monospace;">
        {used_pct:.1f}% of annual LTCG exemption consumed by this harvest plan
    </div>
    """, unsafe_allow_html=True)

    remaining_exempt = max(0.0, LTCG_EXEMPTION - ltcg_gain_realised)
    if remaining_exempt > 0:
        st.markdown(f"""
        <div style="margin-top:12px;background:rgba(29,158,117,0.07);border:1px solid rgba(29,158,117,0.2);
            border-radius:8px;padding:10px 14px;font-size:12px;color:rgba(255,255,255,0.55);">
            💡 <b style="color:#1D9E75;">₹{remaining_exempt:,.2f}</b> of your LTCG exemption is still unused this year.
            Consider harvesting more across other equity funds to fully utilise the ₹1.25L limit.
        </div>
        """, unsafe_allow_html=True)


# =========================
# FOOTER
# =========================
from utils.footer import show_footer
show_footer()
