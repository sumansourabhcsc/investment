#new
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
# =========================================================
# MUSIC
# =========================================================
# from utils.music import play_background_music
# play_background_music(
#     "https://raw.githubusercontent.com/sumansourabhcsc/investment/main/music.mp3",
#     volume=0.02
# )
# pages/1_Portfolio_Overview.py  — add at top
from utils.sidebar_style import render_sidebar
render_sidebar("portfolio")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Taurus: Dashboard",
    layout="wide",
    page_icon="🐂"
)

SUCCESS = "#1D9E75"
DANGER  = "#E24B4A"
BG_MAIN = "#0A0F1E"
CARD_BG = "#0F1629"

# PALETTE = ["#7C3AED","#1D9E75","#06B6D4","#EF9F27","#E24B4A",
#            "#D4537E","#4F8BF9","#00f5d4","#F59E0B","#8B5CF6"]

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
# GOOGLE FONTS + MINIMAL SAFE CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
.stApp { background: #060910 !important; }
.block-container { padding-top: 2.5rem !important; padding-bottom: 3rem !important; max-width: 1400px !important; }
section[data-testid="stSidebar"] { background: #0A0E17 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(255,255,255,0.06) !important; }
.stSelectbox label, .stDateInput label {
    color: rgba(255,255,255,0.3) !important; font-size: 9px !important;
    text-transform: uppercase; letter-spacing: 0.15em;
    font-weight: 500 !important; font-family: 'JetBrains Mono', monospace !important;
}
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }
@keyframes livepulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }

/* DataFrames to match theme */
[data-testid="stDataFrame"] thead tr th {
    background: rgba(255,255,255,0.02) !important;
    color: rgba(255,255,255,0.3) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important; letter-spacing: 0.12em !important; text-transform: uppercase !important;
}
[data-testid="stDataFrame"] tbody tr td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: rgba(220,230,245,0.75) !important;
}
[data-testid="stDataFrame"] tbody tr:hover td { background: rgba(255,255,255,0.02) !important; }

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
# HELPERS — 100% inlined styles, no CSS class dependency
# =========================================================

def kpi_card(icon, label, value, value_color, sub, bottom_color):
    return f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07);
        border-radius:14px; padding:18px 18px 14px; position:relative;
        overflow:hidden; box-sizing:border-box; height:100%;">
        <div style="position:absolute; bottom:0; left:0; right:0; height:3px;
            background:{bottom_color}; border-radius:0 0 14px 14px;"></div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:9px;
            color:rgba(255,255,255,0.3); text-transform:uppercase;
            letter-spacing:0.15em; font-weight:500; margin-bottom:8px;">{label}</div>
        <div style="font-size:1.35rem; font-weight:700; font-family:'JetBrains Mono',monospace;
            line-height:1.1; color:{value_color};">{value}</div>
        <div style="font-size:9px; color:rgba(255,255,255,0.25); margin-top:5px;
            font-family:'JetBrains Mono',monospace;">{sub}</div>
    </div>"""


def sec_header(icon_svg, title, subtitle=""):
    icon_part = f'<div style="display:flex;align-items:center;justify-content:center;width:36px;height:36px;flex-shrink:0;">{icon_svg}</div>' if icon_svg else ""
    sub_part  = f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(255,255,255,0.3);letter-spacing:0.15em;text-transform:uppercase;margin-top:3px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:1.6rem;margin-top:0.4rem;">
        {icon_part}
        <div>
            <div style="font-size:17px;font-weight:700;color:#F0F4FF;font-family:'Space Grotesk',sans-serif;line-height:1.1;">{title}</div>
            {sub_part}
        </div>
        <div style="flex:1;height:1px;background:rgba(255,255,255,0.06);margin-left:6px;"></div>
    </div>""", unsafe_allow_html=True)


def change_summary_box(total_change):
    sign  = "+" if total_change >= 0 else ""
    color = "#69F0AE" if total_change >= 0 else "#FF6B6B"
    icon  = "▲" if total_change >= 0 else "▼"
    st.markdown(f"""
    <div style="margin-top:14px; background:rgba(255,255,255,0.02); padding:16px 22px;
        border-radius:12px; border:1px solid rgba(255,255,255,0.06);
        display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:10px;
            color:rgba(255,255,255,0.4); letter-spacing:0.12em; text-transform:uppercase;">
            {icon} Total Daily Change Across All Funds
        </div>
        <div style="font-size:1.4rem; font-weight:700; font-family:'JetBrains Mono',monospace;
            color:{color};">{sign}₹{abs(total_change):,.2f}</div>
    </div>""", unsafe_allow_html=True)


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
        <div style="font-family:'JetBrains Mono',monospace; font-size:10px;
            color:rgba(255,255,255,0.3); margin-top:5px; letter-spacing:0.2em; text-transform:uppercase;">
            ◈ Taurus · Mutual Fund Tracker · Live NAV
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
        fund_xirr   = compute_fund_xirr(fund_df, latest_nav)
        total_invested += invested
        total_current  += current
        summary.append([
            fund_name, code, invested, current,
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
xirr_bar   = SUCCESS if overall_xirr_pct >= 0 else DANGER


# =========================================================
# KPI CARDS — each rendered in its own st.column
# Using st.markdown per column — this is the CORRECT Streamlit approach
# =========================================================
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(kpi_card(
        "💰", "Total Invested",
        f"₹{total_invested:,.0f}",
        "#F1F5F9",
        f"across {len(summary)} funds",
        "#7C3AED"
    ), unsafe_allow_html=True)

with c2:
    st.markdown(kpi_card(
        "📈", "Current Value",
        f"₹{total_current:,.0f}",
        SUCCESS, "live NAV", SUCCESS
    ), unsafe_allow_html=True)

with c3:
    st.markdown(kpi_card(
        "📊", "Total P&L",
        f"{pnl_sign}₹{abs(total_pnl):,.0f}",
        pnl_color, "unrealised gain/loss", "#06B6D4"
    ), unsafe_allow_html=True)

with c4:
    st.markdown(kpi_card(
        "📉", "Absolute Return",
        f"{ret_sign}{absolute_return_pct:.2f}%",
        ret_color, "since first investment", "#EF9F27"
    ), unsafe_allow_html=True)

with c5:
    st.markdown(kpi_card(
        "📌", "Overall XIRR",
        f"{xirr_sign}{overall_xirr_pct:.2f}%",
        xirr_color, "annualised return", xirr_bar
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
        "Fund", "SchemeCode", "Invested", "Current",
        "P&L", "Latest NAV", "NAV Date", "XIRR"
    ])

    col_tbl, col_donut = st.columns([7, 3])

    with col_tbl:
        display_df = df.copy()
        display_df["Invested"]   = display_df["Invested"].map(lambda x: f"₹{x:,.0f}")
        display_df["Current"]    = display_df["Current"].map(lambda x: f"₹{x:,.0f}")
        display_df["P&L"]        = display_df["P&L"].map(lambda x: f"₹{x:,.0f}")
        display_df["Latest NAV"] = display_df["Latest NAV"].map(lambda x: f"{x:.2f}")
        st.dataframe(
            display_df,
            use_container_width=True,
            height=min((len(display_df) + 1) * 45, 520)
        )

    with col_donut:
        fig_donut = go.Figure(go.Pie(
            labels=df["Fund"], values=df["Current"], hole=0.65,
            marker=dict(colors=PALETTE[:len(df)], line=dict(color="#060910", width=3)),
            textinfo="percent",
            textfont=dict(size=12, family="JetBrains Mono"),
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
        ))
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", family="Space Grotesk"), showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[dict(
                text=f"<b>₹{total_current/1e5:.1f}L</b>",
                x=0.5, y=0.5,
                font=dict(size=18, color="white", family="JetBrains Mono"),
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
        font=dict(color="white", family="Space Grotesk"),
        margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False
    )
    fig_tree.update_traces(
        textinfo="label+percent entry",
        textfont=dict(size=13, family="Space Grotesk"),
        marker=dict(line=dict(width=2, color="#060910"))
    )
    st.plotly_chart(fig_tree, use_container_width=True)


# =========================================================
# TAB 2 — DAILY PORTFOLIO SUMMARY + PERFORMANCE CHART
# =========================================================
with tab2:
    sec_header(ICON_DAILY_SUMMARY, "Daily Portfolio Summary",  "sorted by date · all funds")

    daily_path = "data/portfolio_daily.csv"
    daily_df   = pd.read_csv(daily_path)
    daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
    daily_df = daily_df.sort_values("Date", ascending=False)

    display_daily = daily_df.copy()
    display_daily["Date"] = display_daily["Date"].dt.strftime("%d-%m-%Y")
    st.dataframe(display_daily, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sec_header(ICON_DAILY_SUMMARY, "Portfolio Performance",    "daily change · total value")

    chart_df = daily_df.sort_values("Date")
    chart_df["OneDayChangePct_val"] = (
        chart_df["OneDayChangePct"].str.replace("%", "", regex=False).astype(float)
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
        hovermode="x unified", height=460, margin=dict(t=20, b=10, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
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


# =========================================================
# FOOTER
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
from utils.footer import show_footer
show_footer()
