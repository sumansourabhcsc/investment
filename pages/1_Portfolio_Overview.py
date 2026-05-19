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

# =========================================================
# PAGE CONFIG  (must be first Streamlit call)
# =========================================================
st.set_page_config(
    page_title="Taurus | Dashboard",
    layout="wide",
    page_icon="🐂"
)

# ── Design tokens (shared with fund_analysis page) ───────────────────────────
SUCCESS  = "#69F0AE"
DANGER   = "#FF6B6B"
WARN     = "#FFB347"
ACCENT   = "#4FC3F7"
BG_MAIN  = "#060910"
CARD_BG  = "#0A0E17"

PALETTE = [
    "#2E7D8C", "#E8573F", "#D4A96A", "#4A7C59",
    "#5B6FA6", "#C4784A", "#7DB5B0", "#8B5E83",
    "#B5C85A", "#3D5A80",
]

# ── Global CSS (mirrors fund_analysis.py) ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background: #060910;
    color: #E8EDF5;
}
.stApp { background: #060910; min-height: 100vh; }
[data-testid="stSidebar"] {
    background: #0A0E17 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
.block-container { padding-top: 2.5rem !important; max-width: 1400px !important; }
#MainMenu, footer { visibility: hidden; }

/* animated grid background */
.bg-grid {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridShift 25s linear infinite;
}
@keyframes gridShift {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}
.stApp > * { position: relative; z-index: 1; }

/* page title */
.page-title { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em; color: #F0F4FF; line-height: 1; }
.page-sub   {
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    color: rgba(255,255,255,0.3); letter-spacing: 0.2em;
    text-transform: uppercase; margin-top: 6px;
}

/* live badge */
.live-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(105,240,174,0.10); border: 1px solid rgba(105,240,174,0.28);
    border-radius: 20px; padding: 5px 14px;
    font-size: 11px; font-weight: 500; color: #69F0AE;
    font-family: 'Space Grotesk', sans-serif;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%; background: #69F0AE;
    animation: livepulse 2s ease-in-out infinite;
}
@keyframes livepulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.35;transform:scale(0.65);} }

/* stat chips */
.stat-row  { display: flex; gap: 12px; margin: 22px 0 28px; flex-wrap: wrap; }
.stat-chip {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 14px 22px;
    display: flex; flex-direction: column; align-items: flex-start;
    animation: fadeUp 0.6s ease both;
}
.stat-chip-val {
    font-size: 1.55rem; font-weight: 700; line-height: 1;
    background: linear-gradient(135deg,#fff 0%,rgba(255,255,255,0.55) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-chip-lbl {
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    color: rgba(255,255,255,0.32); letter-spacing: 0.15em;
    text-transform: uppercase; margin-top: 5px;
}
.stat-chip-val-green { font-size:1.3rem;font-weight:700;line-height:1;color:#69F0AE; }
.stat-chip-val-red   { font-size:1.3rem;font-weight:700;line-height:1;color:#FF6B6B; }

/* section label */
.section-label {
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: rgba(255,255,255,0.3); margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: rgba(255,255,255,0.06);
}

/* info card */
.info-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 12px 18px; margin-bottom: 20px;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    color: rgba(255,255,255,0.4);
}

/* daily change summary */
.change-box {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 18px 24px; margin-top: 16px;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
}

/* result / summary cards */
.result-card { border-radius: 12px; padding: 18px 20px; text-align: center; }
.result-val  { font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.result-lbl  { font-size: 10px; color: rgba(255,255,255,0.4); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 6px; }

/* dataframe overrides */
[data-testid="stDataFrame"] {
    border-radius: 14px !important; overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stSelectbox label, .stDateInput label {
    color: rgba(255,255,255,0.35) !important; font-size: 10px !important;
    text-transform: uppercase; letter-spacing: 0.12em; font-weight: 500 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #060910; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 6px; }
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }

@keyframes fadeUp {
    from { opacity:0; transform:translateY(14px); }
    to   { opacity:1; transform:translateY(0); }
}
</style>
<div class="bg-grid"></div>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def sec_header(label: str):
    st.markdown(f'<div class="section-label">▸ {label}</div>', unsafe_allow_html=True)


def kpi_stat(value: str, label: str, value_class: str = "stat-chip-val") -> str:
    return f"""
    <div class="stat-chip">
      <div class="{value_class}">{value}</div>
      <div class="stat-chip-lbl">{label}</div>
    </div>"""


def result_card(value: str, label: str, color: str, bg_color: str, border_color: str) -> str:
    return f"""
    <div class="result-card" style="background:{bg_color};border:1px solid {border_color};">
      <div class="result-val" style="color:{color};">{value}</div>
      <div class="result-lbl">{label}</div>
    </div>"""


# =========================================================
# PAGE HERO
# =========================================================
col_hero, col_badge = st.columns([1, 0])   # badge floated via flex trick below
st.markdown("""
<div style="display:flex;align-items:flex-start;justify-content:space-between;
  flex-wrap:wrap;gap:12px;margin-bottom:4px;">
  <div>
    <div class="page-title">📊 Portfolio Dashboard</div>
    <div class="page-sub">◈ Taurus · Mutual Fund Tracker · Live NAV</div>
  </div>
  <div>
    <div class="live-badge"><div class="live-dot"></div>Live NAV</div>
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

pnl_sign  = "+" if total_pnl >= 0 else ""
ret_sign  = "+" if absolute_return_pct >= 0 else ""
xirr_sign = "+" if overall_xirr_pct >= 0 else ""

pnl_cls  = "stat-chip-val-green" if total_pnl >= 0 else "stat-chip-val-red"
ret_cls  = "stat-chip-val-green" if absolute_return_pct >= 0 else "stat-chip-val-red"
xirr_cls = "stat-chip-val-green" if overall_xirr_pct >= 0 else "stat-chip-val-red"


# =========================================================
# KPI STAT CHIPS
# =========================================================
st.markdown(f"""
<div class="stat-row">
  {kpi_stat(f"₹{total_invested/1e5:.2f}L", "Total Invested")}
  {kpi_stat(f"₹{total_current/1e5:.2f}L", "Current Value")}
  {kpi_stat(f"{pnl_sign}₹{abs(total_pnl)/1e5:.2f}L", "Unrealised P&L", pnl_cls)}
  {kpi_stat(f"{ret_sign}{absolute_return_pct:.2f}%", "Absolute Return", ret_cls)}
  {kpi_stat(f"{xirr_sign}{overall_xirr_pct:.2f}%", "Overall XIRR", xirr_cls)}
  {kpi_stat(str(len(summary)), "Active Funds")}
</div>
""", unsafe_allow_html=True)


# =========================================================
# FUND TABLE + DONUT CHART
# =========================================================
sec_header("Fund Details")

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
        textfont=dict(size=11, family="JetBrains Mono"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.6)", family="Space Grotesk"),
        showlegend=False,
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


# =========================================================
# TREEMAP
# =========================================================
sec_header("Portfolio Allocation")

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

st.divider()


# =========================================================
# DAILY PORTFOLIO SUMMARY
# =========================================================
sec_header("Daily Portfolio Summary")

daily_path = "data/portfolio_daily.csv"
daily_df   = pd.read_csv(daily_path)
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date", ascending=False)

display_daily = daily_df.copy()
display_daily["Date"] = display_daily["Date"].dt.strftime("%d-%m-%Y")
st.dataframe(display_daily, use_container_width=True)

st.divider()


# =========================================================
# PERFORMANCE CHART
# =========================================================
sec_header("Portfolio Performance")

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
    line=dict(color=ACCENT, width=2.5),
    fill="tozeroy", fillcolor="rgba(79,195,247,0.06)",
    hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.0f}<extra></extra>"
), secondary_y=True)
fig_perf.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,14,23,0.7)",
    font=dict(color="rgba(255,255,255,0.5)", family="Space Grotesk"),
    hovermode="x unified", height=460, margin=dict(t=20, b=10, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=12, color="rgba(255,255,255,0.5)"), bgcolor="rgba(0,0,0,0)"),
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

st.divider()


# =========================================================
# MONTHLY INVESTMENT SUMMARY
# =========================================================
sec_header("Monthly Investment Summary")

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
        grouped = df_month.groupby(["Year","Month"])["Amount"].sum().reset_index()
        for _, row in grouped.iterrows():
            monthly_data.append([code, fund_name, row["Year"], row["Month"], row["Amount"]])
    except Exception as e:
        st.warning(f"{fund_name} skipped: {e}")

if monthly_data:
    monthly_df    = pd.DataFrame(monthly_data, columns=["Code","Fund","Year","Month","Amount"])
    years         = sorted(monthly_df["Year"].dropna().astype(int).unique())
    selected_year = st.selectbox("Select Year", years, index=len(years)-1)

    year_df  = monthly_df[monthly_df["Year"] == selected_year]
    pivot_df = year_df.pivot_table(
        index=["Code","Fund"], columns="Month",
        values="Amount", aggfunc="sum", fill_value=0
    ).reset_index()
    pivot_df = pivot_df.rename(columns=month_map)
    for m in month_map.values():
        if m not in pivot_df.columns:
            pivot_df[m] = 0

    month_cols        = list(month_map.values())
    pivot_df          = pivot_df[["Code","Fund"] + month_cols]
    pivot_df["Total"] = pivot_df[month_cols].sum(axis=1)
    total_row = ["","TOTAL"] + [pivot_df[m].sum() for m in month_cols] + [pivot_df["Total"].sum()]
    final_df  = pd.concat(
        [pivot_df, pd.DataFrame([total_row], columns=pivot_df.columns)],
        ignore_index=True
    )
    for col in final_df.select_dtypes(include="number").columns:
        final_df[col] = final_df[col].map(lambda x: f"{x:,.0f}")
    st.dataframe(final_df, use_container_width=True)

    # Monthly stacked bar chart
    bar_data = year_df.copy()
    bar_data["Month_Name"] = bar_data["Month"].map(month_map)
    fig_month = px.bar(
        bar_data, x="Month_Name", y="Amount", color="Fund",
        barmode="stack", color_discrete_sequence=PALETTE,
        labels={"Month_Name": "Month", "Amount": "Amount (₹)"}
    )
    fig_month.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,14,23,0.7)",
        font=dict(color="rgba(255,255,255,0.5)", family="Space Grotesk"),
        height=340, margin=dict(t=20, b=10, l=10, r=10),
        legend=dict(font=dict(size=11, color="rgba(255,255,255,0.45)"),
                    bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.02, xanchor="left", x=0),
        bargap=0.25,
        xaxis=dict(showgrid=False, zeroline=False, categoryorder="array",
                   categoryarray=list(month_map.values())),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   zeroline=False, tickprefix="₹"),
    )
    st.plotly_chart(fig_month, use_container_width=True)

st.divider()


# =========================================================
# DAILY CHANGE ACROSS FUNDS
# =========================================================
sec_header("Daily Change Across Funds")

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
    row_today  = today_rows.iloc[-1]
    prev_rows  = df_daily[df_daily["date"] < selected_date_dt]
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

# ── Total daily change summary card ──────────────────────────────────────────
total_change = df_daily_change["Change in Value"].sum() if not df_daily_change.empty else 0
sign         = "+" if total_change >= 0 else ""
chg_color    = SUCCESS if total_change >= 0 else DANGER
chg_icon     = "📈" if total_change >= 0 else "📉"

st.markdown(f"""
<div class="change-box">
  <div style="font-size:12px;color:rgba(255,255,255,0.4);
    font-family:'JetBrains Mono',monospace;letter-spacing:0.08em;">
    {chg_icon} &nbsp;Total Daily Change Across All Funds
  </div>
  <div style="font-size:1.6rem;font-weight:700;
    font-family:'JetBrains Mono',monospace;color:{chg_color};">
    {sign}₹{abs(total_change):,.2f}
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
from utils.footer import show_footer
show_footer()
