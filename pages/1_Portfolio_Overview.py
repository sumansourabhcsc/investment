import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value
from utils.load_funds import load_all_funds
from utils.xirr_overall import compute_overall_xirr
from utils.xirr_helper import compute_fund_xirr


# ✅ MUST BE FIRST Streamlit command
st.set_page_config(page_title="Portfolio", layout="wide")

# ── Cosmetic CSS ──────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=PlAayfair+Display:wght@600;700&family=Inter:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>

[data-testid="stAppViewContainer"] { background-color: #0e1117; font-family: 'Inter', sans-serif; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background-color: #0e1117; }
.block-container { padding-top: 2.2rem; max-width: 1380px; }

.port-title { font-family: 'Playfair Display', serif; font-size: 2.4rem; font-weight: 700; color: #f5f0e8; margin-bottom: 0; line-height: 1.1; }
.port-title em { color: #d4a843; font-style: normal; }
.port-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; letter-spacing: 0.2em; color: #5a5a72; text-transform: uppercase; margin-top: 4px; margin-bottom: 1.6rem; }

.metric-row { display: flex; gap: 14px; margin-bottom: 1.6rem; }
.mcard { flex: 1; background: #161b27; border: 1px solid #1e2535; border-top: 2px solid #d4a843; border-radius: 8px; padding: 16px 18px 14px; }
.mcard-label { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; letter-spacing: 0.16em; text-transform: uppercase; color: #5a5a72; margin-bottom: 6px; }
.mcard-value { font-family: 'Playfair Display', serif; font-size: 1.55rem; font-weight: 600; color: #f5f0e8; line-height: 1; }
.mcard-value.up   { color: #3fb97a; }
.mcard-value.down { color: #e05555; }
.mcard-value.gold { color: #d4a843; }

.sec-head { font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 600; color: #f5f0e8; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 10px; }
.sec-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; letter-spacing: 0.15em; text-transform: uppercase; color: #d4a843; background: rgba(212,168,67,0.08); border: 1px solid rgba(212,168,67,0.22); border-radius: 4px; padding: 2px 8px; }

.gold-div { height: 1px; background: linear-gradient(90deg, transparent, rgba(212,168,67,0.35), transparent); margin: 1.8rem 0; }

.total-box { background: #161b27; border: 1px solid #1e2535; border-left: 3px solid #d4a843; border-radius: 6px; padding: 12px 20px; font-family: 'Playfair Display', serif; font-size: 1.25rem; color: #f5f0e8; margin-top: 12px; }
.total-box .amt      { color: #d4a843; font-weight: 700; }
.total-box .amt.up   { color: #3fb97a; }
.total-box .amt.down { color: #e05555; }

h1 { display: none; }

</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ──────────────────────────────
nav_df = load_nav()

summary        = []
total_invested = 0
total_current  = 0

for fund_name, meta in mutual_funds.items():
    try:
        code    = meta["code"]
        folder  = meta["folder"]
        fund_df = load_fund(folder)

        match = nav_df[nav_df["SchemeCode"] == str(code)]
        if match.empty:
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue

        latest_row        = match.sort_values("Date", ascending=False).iloc[0]
        latest_nav        = float(latest_row["NAV"])
        latest_date       = latest_row["Date"].date()
        invested          = calculate_invested_amount(fund_df)
        current           = calculate_current_value(fund_df, latest_nav)
        fund_xirr         = compute_fund_xirr(fund_df, latest_nav)
        fund_xirr_display = f"{fund_xirr * 100:.2f}%"

        total_invested += invested
        total_current  += current

        summary.append([fund_name, code, invested, current,
                         current - invested, latest_nav, latest_date, fund_xirr_display])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")


absolute_return_overall = (
    (total_current - total_invested) / total_invested * 100
    if total_invested > 0 else 0
)
all_funds_df = load_all_funds()
overall_xirr = compute_overall_xirr(all_funds_df)
pnl          = total_current - total_invested


# ── PAGE TITLE ────────────────────────────────
st.markdown("""
<div class="port-title">Mutual Fund <em>Portfolio</em></div>
<div class="port-sub">Overview · Performance · Analytics</div>
""", unsafe_allow_html=True)


# ── METRIC CARDS ──────────────────────────────
pnl_cls = "up" if pnl >= 0 else "down"
ret_cls = "up" if absolute_return_overall >= 0 else "down"

st.markdown(f"""
<div class="metric-row">
  <div class="mcard">
    <div class="mcard-label">Total Invested</div>
    <div class="mcard-value">&#8377;{total_invested:,.0f}</div>
  </div>
  <div class="mcard">
    <div class="mcard-label">Current Value</div>
    <div class="mcard-value gold">&#8377;{total_current:,.0f}</div>
  </div>
  <div class="mcard">
    <div class="mcard-label">Total P &amp; L</div>
    <div class="mcard-value {pnl_cls}">&#8377;{pnl:,.0f}</div>
  </div>
  <div class="mcard">
    <div class="mcard-label">Absolute Return</div>
    <div class="mcard-value {ret_cls}">{absolute_return_overall:.2f}%</div>
  </div>
  <div class="mcard">
    <div class="mcard-label">XIRR (Overall)</div>
    <div class="mcard-value gold">{overall_xirr * 100:.2f}%</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)


# ── FUND DETAILS ──────────────────────────────
st.markdown('<div class="sec-head">Fund Details <span class="sec-badge">Holdings</span></div>', unsafe_allow_html=True)

df = pd.DataFrame(summary, columns=[
    "Fund", "SchemeCode", "Invested", "Current",
    "P&L", "Latest NAV", "NAV Date", "XIRR"
])

col_tbl, col_pie = st.columns([6, 4])

with col_tbl:
    st.dataframe(df, use_container_width=True, height=len(df) * 40 + 40)

with col_pie:
    COLORS = ["#d4a843","#3fb97a","#5b9bd5","#e05555","#a78bfa","#f97316","#06b6d4"]
    fig_donut = px.pie(df, names="Fund", values="Current", hole=0.55, title="Allocation by Value")
    fig_donut.update_traces(
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=11, color="#0e1117"),
        marker=dict(colors=COLORS, line=dict(color="#0e1117", width=2)),
    )
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#8a8a9a", size=11),
        title_font=dict(family="Playfair Display, serif", color="#f5f0e8", size=15),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8a8a9a", size=10), orientation="v", x=1.02, y=0.5),
        margin=dict(l=0, r=0, t=40, b=0),
        annotations=[dict(
            text=f"<b>&#8377;{total_current/1e5:.1f}L</b>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Playfair Display, serif", size=18, color="#d4a843"),
        )],
    )
    st.plotly_chart(fig_donut, use_container_width=True, key="allocation_donut")


fig_tree = px.treemap(
    df, path=["Fund"], values="Current",
    title="Fund Allocation — Treemap",
    color="Current",
    color_continuous_scale=["#161b27", "#d4a843"],
)
fig_tree.update_traces(
    textinfo="label+percent entry",
    textfont=dict(family="Inter, sans-serif", size=13, color="#f5f0e8"),
    marker=dict(line=dict(color="#0e1117", width=2)),
)
fig_tree.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#8a8a9a", size=11),
    title_font=dict(family="Playfair Display, serif", color="#f5f0e8", size=15),
    margin=dict(l=0, r=0, t=44, b=0),
    coloraxis_showscale=False,
)
st.plotly_chart(fig_tree, use_container_width=True, key="treemap")


# ── DAILY SUMMARY ─────────────────────────────
st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
st.markdown('<div class="sec-head">Daily Portfolio Summary <span class="sec-badge">Daily Data</span></div>', unsafe_allow_html=True)

daily_path = "data/portfolio_daily.csv"
daily_df   = pd.read_csv(daily_path)
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date", ascending=False)
daily_df["Date"] = daily_df["Date"].dt.strftime("%d-%m-%Y")

st.dataframe(daily_df, use_container_width=True)

daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date")
daily_df["OneDayChangePct_val"] = daily_df["OneDayChangePct"].str.replace("%", "").astype(float)

fig_perf = make_subplots(specs=[[{"secondary_y": True}]])

fig_perf.add_trace(
    go.Bar(
        x=daily_df["Date"],
        y=daily_df["OneDayChange"],
        name="Daily Change",
        marker_color=["#3fb97a" if x > 0 else "#e05555" for x in daily_df["OneDayChange"]],
        marker_line_width=0,
        opacity=0.8,
    ),
    secondary_y=False,
)
fig_perf.add_trace(
    go.Scatter(
        x=daily_df["Date"],
        y=daily_df["TotalValue"],
        name="Total Value",
        mode="lines",
        line=dict(color="#d4a843", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(212,168,67,0.07)",
    ),
    secondary_y=True,
)
fig_perf.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    title="Portfolio Performance",
    title_font=dict(family="Playfair Display, serif", color="#f5f0e8", size=15),
    font=dict(family="Inter, sans-serif", color="#8a8a9a", size=11),
    hovermode="x unified",
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8a8a9a"), orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
    margin=dict(l=12, r=12, t=44, b=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.04)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.04)"),
)
fig_perf.update_yaxes(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.04)")
st.plotly_chart(fig_perf, use_container_width=True)


# ── MONTHLY SUMMARY ───────────────────────────
st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
st.markdown('<div class="sec-head">Monthly Investment Summary <span class="sec-badge">By Fund &amp; Year</span></div>', unsafe_allow_html=True)

monthly_data = []

for fund_name, meta in mutual_funds.items():
    try:
        folder = meta["folder"]
        code   = meta["code"]
        df_f   = load_fund(folder)
        df_f["Date"] = pd.to_datetime(df_f["Date"], errors="coerce")
        df_f = df_f.dropna(subset=["Date"])
        df_f["Year"]  = df_f["Date"].dt.year
        df_f["Month"] = df_f["Date"].dt.month
        grouped = df_f.groupby(["Year", "Month"])["Amount"].sum().reset_index()
        for _, row in grouped.iterrows():
            monthly_data.append([code, fund_name, row["Year"], row["Month"], row["Amount"]])
    except Exception as e:
        st.warning(f"{fund_name} skipped: {e}")

if monthly_data:
    monthly_df = pd.DataFrame(monthly_data, columns=["Code", "Fund", "Year", "Month", "Amount"])
    years         = sorted(monthly_df["Year"].dropna().astype(int).unique())
    selected_year = st.selectbox("Select Year", years, index=len(years) - 1)
    year_df       = monthly_df[monthly_df["Year"] == selected_year]

    pivot_df = year_df.pivot_table(
        index=["Code", "Fund"], columns="Month",
        values="Amount", aggfunc="sum", fill_value=0,
    ).reset_index()

    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    pivot_df = pivot_df.rename(columns=month_map)
    for m in month_map.values():
        if m not in pivot_df.columns:
            pivot_df[m] = 0

    month_cols = list(month_map.values())
    pivot_df   = pivot_df[["Code", "Fund"] + month_cols]
    pivot_df["Total"] = pivot_df[month_cols].sum(axis=1)

    total_values = ["", "TOTAL"] + [pivot_df[m].sum() for m in month_cols] + [pivot_df["Total"].sum()]
    total_df  = pd.DataFrame([total_values], columns=pivot_df.columns)
    final_df  = pd.concat([pivot_df, total_df], ignore_index=True)

    st.markdown(f"##### Year {selected_year}")

    def highlight_total_row(row):
        if row["Fund"] == "TOTAL":
            return ["background-color: #1e2a14; color: #d4a843; font-weight: 700"] * len(row)
        return [""] * len(row)

    def highlight_total_column(col):
        if col.name == "Total":
            return ["background-color: #1a1e2e; color: #d4a843; font-weight: 600"] * len(col)
        return [""] * len(col)

    numeric_cols = final_df.select_dtypes(include="number").columns
    st.dataframe(
        final_df.style
            .apply(highlight_total_row, axis=1)
            .apply(highlight_total_column, axis=0)
            .format({col: "{:,.0f}" for col in numeric_cols}),
        use_container_width=True,
    )


# ── DAILY CHANGE TABLE ────────────────────────
st.markdown('<div class="gold-div"></div>', unsafe_allow_html=True)
st.markdown('<div class="sec-head">Daily Change Across Funds <span class="sec-badge">NAV Delta</span></div>', unsafe_allow_html=True)

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

    df_daily = pd.read_csv(file_path)
    df_daily.columns = df_daily.columns.str.strip()
    df_daily["date"] = pd.to_datetime(df_daily["date"], format="%d-%m-%Y", errors="coerce")
    df_daily = df_daily.dropna(subset=["date"]).sort_values("date")

    today_rows = df_daily[df_daily["date"] == selected_date_dt]
    if today_rows.empty:
        continue

    row_today = today_rows.iloc[-1]
    prev_rows = df_daily[df_daily["date"] < selected_date_dt]
    if prev_rows.empty:
        continue

    row_prev        = prev_rows.iloc[-1]
    change_in_value = float(row_today["absolute_gain_loss"]) - float(row_prev["absolute_gain_loss"])
    nav_today       = float(row_today["nav"])
    nav_prev        = float(row_prev["nav"])
    pct_change_nav  = ((nav_today - nav_prev) / nav_prev * 100) if nav_prev != 0 else 0
    indicator       = "🟢 ↑" if nav_today > nav_prev else "🔴 ↓"

    daily_rows.append([
        row_today["date"].strftime("%d-%m-%Y"),
        fund_name, code,
        round(change_in_value, 2),
        f"{pct_change_nav:.2f}%",
        indicator,
    ])

df_daily_out = pd.DataFrame(daily_rows, columns=[
    "Date", "Fund Name", "Fund Code",
    "Change in Value", "% Change in NAV", "Indicator",
])

st.dataframe(df_daily_out, use_container_width=True)

total_change = df_daily_out["Change in Value"].sum()
amt_cls      = "up" if total_change >= 0 else "down"
sign         = "+" if total_change >= 0 else ""

st.markdown(f"""
<div class="total-box">
    Total Change Across All Funds &nbsp;&nbsp;
    <span class="amt {amt_cls}">{sign}&#8377;{total_change:,.2f}</span>
</div>
""", unsafe_allow_html=True)
