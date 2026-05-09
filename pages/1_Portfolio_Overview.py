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

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(page_title="Portfolio", layout="wide")

# ─────────────────────────────────────────────
# Global CSS — dark gold theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Raleway:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Raleway', sans-serif;
    background-color: #0a0a0f;
    color: #e8e0d0;
}

h1, h2, h3 { font-family: 'Cinzel', serif; }

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #c9a84c33;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #c9a84c, transparent);
}
.metric-label {
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #c9a84c;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f0ead6;
    font-family: 'Cinzel', serif;
}
.metric-sub {
    font-size: 0.78rem;
    color: #888;
    margin-top: 4px;
}

/* ── Section headers ── */
.section-header {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    letter-spacing: 0.1em;
    color: #c9a84c;
    border-left: 3px solid #c9a84c;
    padding-left: 12px;
    margin: 24px 0 16px 0;
}

/* ── Divider ── */
hr { border-color: #c9a84c22 !important; }

/* ── Positive/Negative colors ── */
.positive { color: #4caf7d; }
.negative { color: #e05c5c; }

/* ── Dataframe styling ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Page title ── */
.page-title {
    font-family: 'Cinzel', serif;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #c9a84c, #f0d080, #c9a84c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
}
.page-subtitle {
    color: #666;
    font-size: 0.85rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 28px;
}

/* ── Indicator badges ── */
.badge-up {
    background: #1a3a2a;
    color: #4caf7d;
    border: 1px solid #4caf7d44;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-down {
    background: #3a1a1a;
    color: #e05c5c;
    border: 1px solid #e05c5c44;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.8rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Page Title
# ─────────────────────────────────────────────
st.markdown('<div class="page-title">Portfolio Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Mutual Fund Investment Dashboard</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────
nav_df = load_nav()
summary = []
total_invested = 0
total_current = 0

for fund_name, meta in mutual_funds.items():
    try:
        code = meta["code"]
        folder = meta["folder"]
        fund_df = load_fund(folder)
        match = nav_df[nav_df["SchemeCode"] == str(code)]
        if match.empty:
            continue
        latest_row = match.sort_values("Date", ascending=False).iloc[0]
        latest_nav = float(latest_row["NAV"])
        latest_date = latest_row["Date"].date()
        invested = calculate_invested_amount(fund_df)
        current = calculate_current_value(fund_df, latest_nav)
        fund_xirr = compute_fund_xirr(fund_df, latest_nav)
        total_invested += invested
        total_current += current
        summary.append([
            fund_name, code, invested, current,
            current - invested, latest_nav, latest_date,
            f"{fund_xirr * 100:.2f}%"
        ])
    except Exception as e:
        st.error(f"{fund_name}: {e}")

pnl = total_current - total_invested
abs_return = ((pnl) / total_invested * 100) if total_invested > 0 else 0
all_funds_df = load_all_funds()
overall_xirr = compute_overall_xirr(all_funds_df)
pnl_color = "#4caf7d" if pnl >= 0 else "#e05c5c"
abs_color  = "#4caf7d" if abs_return >= 0 else "#e05c5c"
xirr_color = "#4caf7d" if overall_xirr >= 0 else "#e05c5c"

# ─────────────────────────────────────────────
# Metric Cards
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

def metric_card(col, label, value, sub="", color="#f0ead6"):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

metric_card(c1, "Total Invested",  f"₹{total_invested:,.0f}")
metric_card(c2, "Current Value",   f"₹{total_current:,.0f}")
metric_card(c3, "Total P&L",       f"₹{pnl:,.0f}",          color=pnl_color)
metric_card(c4, "Absolute Return", f"{abs_return:.2f}%",     color=abs_color)
metric_card(c5, "XIRR (Overall)",  f"{overall_xirr*100:.2f}%", color=xirr_color)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ─────────────────────────────────────────────
# Fund Table + Donut Chart
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Fund Details</div>', unsafe_allow_html=True)

df = pd.DataFrame(summary, columns=[
    "Fund", "Code", "Invested", "Current", "P&L", "Latest NAV", "NAV Date", "XIRR"
])

col_table, col_chart = st.columns([6, 2])

with col_table:
    # Color P&L column
    def style_pnl(val):
        color = "#4caf7d" if val >= 0 else "#e05c5c"
        return f"color: {color}; font-weight: 600"

    styled = (
        df.style
        .applymap(style_pnl, subset=["P&L"])
        .format({
            "Invested":    "₹{:,.0f}",
            "Current":     "₹{:,.0f}",
            "P&L":         "₹{:,.0f}",
            "Latest NAV":  "₹{:.2f}",
        })
        .set_properties(**{
            "background-color": "#0d1117",
            "color": "#e8e0d0",
            "border-color": "#c9a84c22"
        })
    )
    st.dataframe(styled, use_container_width=True, height=len(df) * 38 + 40)

with col_chart:
    fig_donut = px.pie(
        df, names="Fund", values="Current", hole=0.55,
    )
    fig_donut.update_traces(
        textinfo="percent",
        textposition="inside",
        marker=dict(colors=px.colors.sequential.Plasma_r),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
    )
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text="Allocation",
            x=0.5, y=0.5,
            font=dict(size=13, color="#c9a84c", family="Cinzel"),
            showarrow=False
        )],
        title=dict(
            text="Fund Allocation",
            font=dict(color="#c9a84c", family="Cinzel", size=14),
            x=0.5
        )
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ── Treemap ──
fig_tree = px.treemap(
    df, path=["Fund"], values="Current",
    color="P&L",
    color_continuous_scale=["#e05c5c", "#1a1a2e", "#4caf7d"],
    color_continuous_midpoint=0,
)
fig_tree.update_traces(
    textinfo="label+percent entry",
    textfont=dict(family="Raleway", size=13),
    hovertemplate="<b>%{label}</b><br>Current: ₹%{value:,.0f}<extra></extra>"
)
fig_tree.update_layout(
    title=dict(
        text="Fund Allocation — Treemap (colored by P&L)",
        font=dict(color="#c9a84c", family="Cinzel", size=14),
        x=0
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=10, l=10, r=10),
    coloraxis_showscale=False,
)
st.plotly_chart(fig_tree, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Daily Summary Chart
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Portfolio Performance — Daily</div>', unsafe_allow_html=True)

daily_path = "data/portfolio_daily.csv"
daily_df = pd.read_csv(daily_path)
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date")
daily_df["OneDayChangePct_val"] = daily_df["OneDayChangePct"].str.replace("%", "").astype(float)

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=daily_df["Date"],
        y=daily_df["OneDayChange"],
        name="Daily Change (₹)",
        marker_color=["#4caf7d" if x >= 0 else "#e05c5c" for x in daily_df["OneDayChange"]],
        opacity=0.75
    ),
    secondary_y=False
)

fig.add_trace(
    go.Scatter(
        x=daily_df["Date"],
        y=daily_df["TotalValue"],
        name="Total Value (₹)",
        mode="lines",
        line=dict(color="#c9a84c", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(201,168,76,0.06)"
    ),
    secondary_y=True
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,23,0.8)",
    font=dict(color="#e8e0d0", family="Raleway"),
    hovermode="x unified",
    legend=dict(
        orientation="h", y=-0.25, x=0.5,
        xanchor="center",
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c9a84c")
    ),
    xaxis=dict(gridcolor="#ffffff08", showgrid=True),
    yaxis=dict(gridcolor="#ffffff08", showgrid=True, title="Daily Change (₹)"),
    yaxis2=dict(title="Total Value (₹)", showgrid=False),
    margin=dict(t=20, b=40, l=10, r=10),
)

st.plotly_chart(fig, use_container_width=True)

# ── Daily summary table (collapsed by default) ──
with st.expander("📋 View Daily Data Table"):
    display_daily = daily_df.copy()
    display_daily["Date"] = display_daily["Date"].dt.strftime("%d-%m-%Y")
    display_daily = display_daily.sort_values("Date", ascending=False)
    st.dataframe(display_daily, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Monthly Investment Summary
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Monthly Investment Summary</div>', unsafe_allow_html=True)

monthly_data = []
for fund_name, meta in mutual_funds.items():
    try:
        folder = meta["folder"]
        code = meta["code"]
        df_f = load_fund(folder)
        df_f["Date"] = pd.to_datetime(df_f["Date"], errors="coerce")
        df_f = df_f.dropna(subset=["Date"])
        df_f["Year"] = df_f["Date"].dt.year
        df_f["Month"] = df_f["Date"].dt.month
        grouped = df_f.groupby(["Year", "Month"])["Amount"].sum().reset_index()
        for _, row in grouped.iterrows():
            monthly_data.append([code, fund_name, row["Year"], row["Month"], row["Amount"]])
    except:
        pass

if monthly_data:
    monthly_df = pd.DataFrame(monthly_data, columns=["Code", "Fund", "Year", "Month", "Amount"])
    years = sorted(monthly_df["Year"].dropna().astype(int).unique())

    col_yr, _ = st.columns([1, 4])
    with col_yr:
        selected_year = st.selectbox("Select Year", years, index=len(years) - 1)

    year_df = monthly_df[monthly_df["Year"] == selected_year]
    pivot_df = year_df.pivot_table(
        index=["Code", "Fund"], columns="Month",
        values="Amount", aggfunc="sum", fill_value=0
    ).reset_index()

    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    pivot_df = pivot_df.rename(columns=month_map)
    for m in month_map.values():
        if m not in pivot_df.columns:
            pivot_df[m] = 0
    month_cols = list(month_map.values())
    pivot_df = pivot_df[["Code", "Fund"] + month_cols]
    pivot_df["Total"] = pivot_df[month_cols].sum(axis=1)

    total_values = ["", "TOTAL"] + [pivot_df[m].sum() for m in month_cols] + [pivot_df["Total"].sum()]
    total_df = pd.DataFrame([total_values], columns=pivot_df.columns)
    final_df = pd.concat([pivot_df, total_df], ignore_index=True)

    numeric_cols = final_df.select_dtypes(include="number").columns

    def style_monthly(row):
        if row["Fund"] == "TOTAL":
            return ["background-color: #2a1f0a; color: #c9a84c; font-weight: 700"] * len(row)
        return [""] * len(row)

    def style_total_col(col):
        if col.name == "Total":
            return ["background-color: #1a150500; color: #c9a84c; font-weight: 600"] * len(col)
        return [""] * len(col)

    st.dataframe(
        final_df.style
            .apply(style_monthly, axis=1)
            .apply(style_total_col, axis=0)
            .format({col: "₹{:,.0f}" for col in numeric_cols}),
        use_container_width=True
    )

st.divider()

# ─────────────────────────────────────────────
# Daily Change Across Funds
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Daily Change Across Funds</div>', unsafe_allow_html=True)

latest_nav_date = nav_df["Date"].max().date()
col_date, _ = st.columns([1, 4])
with col_date:
    selected_date = st.date_input("Select Date", value=latest_nav_date)

selected_date_dt = pd.to_datetime(selected_date)
daily_rows = []

for fund_name, meta in mutual_funds.items():
    folder = meta["folder"]
    code = meta["code"]
    file_path = f"mutualfund/{folder}/daily_{code}.csv"
    if not os.path.exists(file_path):
        continue
    df_d = pd.read_csv(file_path)
    df_d.columns = df_d.columns.str.strip()
    df_d["date"] = pd.to_datetime(df_d["date"], format="%d-%m-%Y", errors="coerce")
    df_d = df_d.dropna(subset=["date"]).sort_values("date")

    today_rows = df_d[df_d["date"] == selected_date_dt]
    if today_rows.empty:
        continue
    row_today = today_rows.iloc[-1]
    prev_rows = df_d[df_d["date"] < selected_date_dt]
    if prev_rows.empty:
        continue
    row_prev = prev_rows.iloc[-1]

    change_val = float(row_today["absolute_gain_loss"]) - float(row_prev["absolute_gain_loss"])
    nav_today  = float(row_today["nav"])
    nav_prev   = float(row_prev["nav"])
    pct_nav    = ((nav_today - nav_prev) / nav_prev * 100) if nav_prev != 0 else 0
    direction  = "▲" if nav_today >= nav_prev else "▼"

    daily_rows.append([
        row_today["date"].strftime("%d-%m-%Y"),
        fund_name, code,
        change_val,
        pct_nav,
        direction
    ])

if daily_rows:
    df_daily_change = pd.DataFrame(daily_rows, columns=[
        "Date", "Fund Name", "Code", "Change (₹)", "NAV Change %", "Dir"
    ])

    total_change = df_daily_change["Change (₹)"].sum()

    # ── Summary strip ──
    total_color = "#4caf7d" if total_change >= 0 else "#e05c5c"
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid {total_color}44;
        border-left: 4px solid {total_color};
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="color:#888; font-size:0.85rem; letter-spacing:0.1em; text-transform:uppercase;">
            Total Change on {selected_date.strftime('%d %b %Y')}
        </span>
        <span style="color:{total_color}; font-size:1.6rem; font-weight:700; font-family:'Cinzel',serif;">
            ₹{total_change:,.2f}
        </span>
    </div>
    """, unsafe_allow_html=True)

    def style_change(val):
        color = "#4caf7d" if val >= 0 else "#e05c5c"
        return f"color: {color}; font-weight: 600"

    def style_dir(val):
        color = "#4caf7d" if val == "▲" else "#e05c5c"
        return f"color: {color}; font-weight: 700; font-size: 1rem"

    styled_daily = (
        df_daily_change.style
        .applymap(style_change, subset=["Change (₹)", "NAV Change %"])
        .applymap(style_dir, subset=["Dir"])
        .format({
            "Change (₹)":    "₹{:,.2f}",
            "NAV Change %":  "{:.2f}%",
        })
    )
    st.dataframe(styled_daily, use_container_width=True)
