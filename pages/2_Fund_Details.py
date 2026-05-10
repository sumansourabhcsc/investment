import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import date, timedelta

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.xirr_helper import compute_fund_xirr


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Fund Details | Taurus", layout="wide", page_icon="📁")


# =========================
# GLOBAL STYLES
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

/* ── Page title ── */
.page-title {
    font-size: 26px;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: -0.4px;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.45);
    font-family: 'DM Mono', monospace;
    margin-bottom: 1.5rem;
}

/* ── NAV badge ── */
.nav-badge {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 14px 22px;
    display: inline-block;
    text-align: right;
}
.nav-badge .nav-val {
    font-size: 28px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    color: #ffffff;
    line-height: 1.1;
}
.nav-badge .nav-date {
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    margin-top: 3px;
    font-family: 'DM Mono', monospace;
}

/* ── Metric cards ── */
.metric-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.metric-card {
    flex: 1;
    min-width: 120px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 3px 0 0 3px;
}
.metric-card.c-blue::before   { background: #4F8BF9; }
.metric-card.c-green::before  { background: #1D9E75; }
.metric-card.c-red::before    { background: #E24B4A; }
.metric-card.c-amber::before  { background: #EF9F27; }
.metric-card.c-purple::before { background: #7F77DD; }
.metric-card.c-pink::before   { background: #D4537E; }
.metric-card.c-teal::before   { background: #00f5d4; }

.metric-label {
    font-size: 10px;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    font-weight: 500;
}
.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: #ffffff;
    font-family: 'DM Mono', monospace;
    line-height: 1.2;
}
.metric-value.pos { color: #1D9E75; }
.metric-value.neg { color: #E24B4A; }

/* ── Section headers ── */
.section-header {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header span {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
    display: inline-block;
}

/* ── Stat pills ── */
.stat-pill-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.stat-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 12px;
    color: rgba(255,255,255,0.45);
}
.stat-pill .pill-val {
    font-size: 16px;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    color: #ffffff;
    display: block;
    margin-top: 2px;
}
.stat-pill .pill-val.pos { color: #1D9E75; }
.stat-pill .pill-val.neg { color: #E24B4A; }

/* ── Dataframe tweaks ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Selectbox label ── */
[data-testid="stSelectbox"] label {
    font-size: 12px !important;
    color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
</style>
""", unsafe_allow_html=True)


# =========================
# HELPERS
# =========================
def inr(val):
    """Format a number as Indian Rupees with commas."""
    return f"₹{val:,.2f}"

def pct(val, decimals=2):
    """Format a float as a percentage string with sign."""
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.{decimals}f}%"

def metric_card(label, value_str, color_class, extra_class=""):
    st.markdown(f"""
    <div class="metric-card {color_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {extra_class}">{value_str}</div>
    </div>
    """, unsafe_allow_html=True)

def section_header(title):
    st.markdown(f"""
    <div class="section-header">{title} <span></span></div>
    """, unsafe_allow_html=True)


# =========================
# DATA LOADING
# =========================
nav_df = load_nav()

fund_options = list(mutual_funds.keys())
selected_fund = st.selectbox("Select Fund", fund_options)

scheme_code = mutual_funds[selected_fund]["code"]
folder      = mutual_funds[selected_fund]["folder"]
fund_df     = load_fund(folder)

daily_path  = f"mutualfund/{folder}/daily_{scheme_code}.csv"
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
# HEADER — Fund name + NAV badge
# =========================
col_title, col_nav = st.columns([3, 1])

with col_title:
    st.markdown(f"""
    <div class="page-title">📁 {selected_fund}</div>
    <div class="page-subtitle">Scheme Code: {scheme_code} &nbsp;·&nbsp; Direct Growth</div>
    """, unsafe_allow_html=True)

with col_nav:
    st.markdown(f"""
    <div class="nav-badge">
        <div class="nav-val">{inr(latest_nav)}</div>
        <div class="nav-date">as of {latest_date}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# METRIC CARDS — 7 KPIs in a row
# =========================
pnl_color  = "pos" if profit >= 0 else "neg"
pnl_accent = "c-green" if profit >= 0 else "c-red"
ret_color  = "pos" if absolute_return >= 0 else "neg"
xirr_color = "pos" if xirr_pct >= 0 else "neg"

st.markdown('<div class="metric-row">', unsafe_allow_html=True)

cards = [
    ("💰 Invested",        inr(invested),              "c-blue",   ""),
    ("📈 Current Value",   inr(current_value),          "c-green",  "pos"),
    ("📊 P&L",             ("+" if profit>=0 else "")+inr(profit), pnl_accent, pnl_color),
    ("📉 Abs. Return",     pct(absolute_return),        "c-amber",  ret_color),
    ("🧮 Avg Buy NAV",     inr(avg_buy_nav),            "c-purple", ""),
    ("📦 Total Units",     f"{total_units:,.2f}",       "c-pink",   ""),
    ("📌 XIRR",            pct(xirr_pct, 1),           "c-teal",   xirr_color),
]

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
# SIP HISTORY + DAILY NAV — side by side
# =========================
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


# =========================
# NAV HISTORY — range picker + chart
# =========================
section_header("📈 NAV History")

# ── Quick-range tabs first ──
range_choice = st.radio(
    "Quick Range",
    options=["Custom", "1M", "3M", "6M", "1Y", "3Y", "All"],
    index=4,
    horizontal=True,
    label_visibility="collapsed",
    key="nav_range_choice"
)

range_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "All": 9999}

if range_choice != "Custom":
    days = range_map[range_choice]
    default_start = date.today() - timedelta(days=days)
    default_end   = date.today()
else:
    default_start = date.today() - timedelta(days=365)
    default_end   = date.today()

# ── Date pickers or range label ──
col_d1, col_d2, col_spacer = st.columns([1, 1, 3])

if range_choice == "Custom":
    with col_d1:
        start_date = st.date_input(
            "Start Date",
            value=default_start,
            max_value=date.today(),
            key="start_date"
        )
    with col_d2:
        end_date = st.date_input(
            "End Date",
            value=default_end,
            min_value=start_date,
            max_value=date.today(),
            key="end_date"
        )
else:
    start_date = default_start
    end_date   = default_end
    with col_d1:
        st.markdown(f"""
        <div style="
            display:inline-flex; align-items:center; gap:8px;
            background:rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.07);
            border-radius:6px;
            padding:5px 12px;
            font-family:'DM Mono',monospace;
            font-size:13px;
            color:rgba(255,255,255,0.5);
        ">
            <span style="color:rgba(255,255,255,0.3);font-size:11px;">FROM</span>
            <span style="color:rgba(255,255,255,0.85);">{start_date.strftime("%d %b %Y")}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.markdown(f"""
        <div style="
            display:inline-flex; align-items:center; gap:8px;
            background:rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.07);
            border-radius:6px;
            padding:5px 12px;
            font-family:'DM Mono',monospace;
            font-size:13px;
            color:rgba(255,255,255,0.5);
        ">
            <span style="color:rgba(255,255,255,0.3);font-size:11px;">TO</span>
            <span style="color:rgba(255,255,255,0.85);">{end_date.strftime("%d %b %Y")}</span>
        </div>
        """, unsafe_allow_html=True)
if not nav_filtered.empty:
    max_row   = nav_filtered.loc[nav_filtered["NAV"].idxmax()]
    min_row   = nav_filtered.loc[nav_filtered["NAV"].idxmin()]
    nav_start = nav_filtered["NAV"].iloc[0]
    nav_end   = nav_filtered["NAV"].iloc[-1]
    range_chg = (nav_end - nav_start) / nav_start * 100

    chg_color = "#1D9E75" if range_chg >= 0 else "#E24B4A"
    chg_sign  = "+" if range_chg >= 0 else ""

    st.markdown(f"""
    <div style="display:flex; gap:10px; margin:14px 0 18px 0; flex-wrap:wrap;">
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px;padding:10px 16px;min-width:130px;">
            <div style="font-size:10px;color:rgba(255,255,255,0.35);font-family:'Outfit';
                        letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">
                Highest NAV
            </div>
            <div style="font-size:15px;color:#fff;font-family:'DM Mono';">₹{max_row['NAV']:.4f}</div>
            <div style="font-size:10px;color:rgba(255,255,255,0.25);font-family:'Outfit';margin-top:2px;">
                {max_row['Date'].strftime("%d %b %Y")}
            </div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px;padding:10px 16px;min-width:130px;">
            <div style="font-size:10px;color:rgba(255,255,255,0.35);font-family:'Outfit';
                        letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">
                Lowest NAV
            </div>
            <div style="font-size:15px;color:#fff;font-family:'DM Mono';">₹{min_row['NAV']:.4f}</div>
            <div style="font-size:10px;color:rgba(255,255,255,0.25);font-family:'Outfit';margin-top:2px;">
                {min_row['Date'].strftime("%d %b %Y")}
            </div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
                    border-radius:8px;padding:10px 16px;min-width:130px;">
            <div style="font-size:10px;color:rgba(255,255,255,0.35);font-family:'Outfit';
                        letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px;">
                Range Change
            </div>
            <div style="font-size:15px;color:{chg_color};font-family:'DM Mono';">
                {chg_sign}{range_chg:.2f}%
            </div>
            <div style="font-size:10px;color:rgba(255,255,255,0.25);font-family:'Outfit';margin-top:2px;">
                {start_date.strftime("%d %b")} → {end_date.strftime("%d %b %Y")}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
# ── Fetch NAV history ──
@st.cache_data(ttl=3600)
def fetch_nav_history(fund_code):
    url = f"https://api.mfapi.in/mf/{fund_code}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]:
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
            df = df.sort_values("date").reset_index(drop=True)
            df.rename(columns={"date": "Date", "nav": "NAV"}, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch NAV history: {e}")
        return pd.DataFrame()

nav_df_full = fetch_nav_history(scheme_code)

# ── Filter using Timestamps (avoids dtype mismatch) ──
if not nav_df_full.empty:
    start_ts = pd.Timestamp(start_date)
    end_ts   = pd.Timestamp(end_date)
    nav_filtered = nav_df_full[
        (nav_df_full["Date"] >= start_ts) &
        (nav_df_full["Date"] <= end_ts)
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

    chg_class = "pos" if range_chg >= 0 else "neg"
    chg_sign  = "+" if range_chg >= 0 else ""
    st.markdown(f"""
    <div class="stat-pill-row">
        <div class="stat-pill">
            Highest NAV
            <span class="pill-val">₹{max_row['NAV']:.4f}</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.3)">on {max_row['Date'].date()}</span>
        </div>
        <div class="stat-pill">
            Lowest NAV
            <span class="pill-val">₹{min_row['NAV']:.4f}</span>
            <span style="font-size:10px;color:rgba(255,255,255,0.3)">on {min_row['Date'].date()}</span>
        </div>
        <div class="stat-pill">
            Range Change
            <span class="pill-val {chg_class}">{chg_sign}{range_chg:.2f}%</span>
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
            x=nav_filtered["Date"],
            y=nav_filtered["NAV"],
            mode="lines",
            name="NAV",
            line=dict(color="#4F8BF9", width=2),
            fill="tozeroy",
            fillcolor="rgba(79,139,249,0.08)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>NAV: ₹%{y:.4f}<extra></extra>"
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Outfit, sans-serif", color="rgba(255,255,255,0.6)"),
            margin=dict(l=10, r=10, t=20, b=10),
            height=360,
            hovermode="x unified",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                zeroline=False,
                tickprefix="₹"
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
st.divider()


# =========================
# PORTFOLIO VALUE TREND
# =========================
section_header("📊 Portfolio Value Trend")

if daily_df.empty:
    st.info("No daily snapshot data available to plot.")
else:
    chart_df = daily_df.copy()
    chart_df["date"] = pd.to_datetime(chart_df["date"], format="%d-%m-%Y")
    chart_df = chart_df.sort_values("date")

    fig2 = go.Figure()

    # Current portfolio value line
    fig2.add_trace(go.Scatter(
        x=chart_df["date"],
        y=chart_df["current_value"],
        mode="lines+markers",
        name="Portfolio Value",
        line=dict(color="#1D9E75", width=2.5),
        marker=dict(size=5, color="#1D9E75"),
        fill="tozeroy",
        fillcolor="rgba(29,158,117,0.07)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.2f}<extra></extra>"
    ))

    # Invested amount line (if column exists)
    if "invested" in chart_df.columns:
        fig2.add_trace(go.Scatter(
            x=chart_df["date"],
            y=chart_df["invested"],
            mode="lines",
            name="Invested",
            line=dict(color="#4F8BF9", width=1.5, dash="dot"),
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Invested: ₹%{y:,.2f}<extra></extra>"
        ))

    fig2.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, sans-serif", color="rgba(255,255,255,0.6)"),
        margin=dict(l=10, r=10, t=20, b=10),
        height=380,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            font=dict(size=12),
        ),
        xaxis=dict(showgrid=False, zeroline=False, title="Date"),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
            title="Value (₹)",
            tickprefix="₹"
        ),
    )

    st.plotly_chart(fig2, use_container_width=True)



from utils.footer import show_footer

# ... all your page content ...

show_footer()
