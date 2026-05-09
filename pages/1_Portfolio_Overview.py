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
st.set_page_config(page_title="Portfolio", layout="wide", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">

<style>
/* ── Root palette ── */
:root {
    --bg:          #0d0f12;
    --surface:     #13161b;
    --card:        #191d24;
    --border:      rgba(200,165,80,0.18);
    --gold:        #c8a550;
    --gold-light:  #e2c278;
    --gold-dim:    rgba(200,165,80,0.08);
    --text-primary:#f0ead8;
    --text-muted:  #7a7a6e;
    --text-subtle: #4a4a42;
    --green:       #4caf82;
    --red:         #e05c5c;
    --radius:      10px;
}

/* ── App chrome ── */
.stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}
.stApp > header { background: transparent !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Remove top padding ── */
.block-container { padding-top: 2rem !important; max-width: 1400px !important; }

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.02em;
}

/* ── Page title ── */
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    line-height: 1.1;
}
.page-title span {
    color: var(--gold);
}
.page-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-top: 0.2rem;
    margin-bottom: 2rem;
}

/* ── Gold rule ── */
.gold-rule {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    margin: 0.5rem 0 1.8rem 0;
    opacity: 0.5;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.3rem 1.4rem 1.1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), var(--gold-light));
    opacity: 0.7;
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--text-primary);
    line-height: 1;
}
.metric-value.positive { color: var(--green); }
.metric-value.negative { color: var(--red); }
.metric-value.gold     { color: var(--gold-light); }

/* ── Section headers ── */
.section-header {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}
.section-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--gold);
    background: var(--gold-dim);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 7px;
    vertical-align: middle;
}

/* ── Dataframes ── */
.stDataFrame { border-radius: var(--radius); overflow: hidden; }
.stDataFrame iframe, .stDataFrame [data-testid="stDataFrameResizable"] {
    background: var(--card) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
}

/* ── Date input ── */
.stDateInput > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Divider override ── */
hr {
    border-color: rgba(200,165,80,0.12) !important;
    margin: 2rem 0 !important;
}

/* ── Plotly container background ── */
.js-plotly-plot, .plot-container { background: transparent !important; }

/* ── Streamlit warning/error ── */
.stAlert {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
}

/* ── Total change callout ── */
.total-callout {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.5rem;
    margin-top: 1rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    color: var(--text-primary);
}
.total-callout span { color: var(--gold-light); font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PLOTLY THEME HELPER
# ─────────────────────────────────────────────
# Base layout — safe for ALL chart types (no xaxis/yaxis)
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#a09880", size=11),
    title_font=dict(family="Cormorant Garamond, serif", color="#f0ead8", size=17),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a09880"),
        orientation="h",
        yanchor="bottom", y=-0.3,
        xanchor="center", x=0.5,
    ),
    margin=dict(l=12, r=12, t=44, b=12),
    colorway=["#c8a550", "#4caf82", "#7ecfe0", "#e2c278", "#e05c5c", "#a78bfa"],
)

# Extra axis styling — only for cartesian (bar, line, scatter, treemap) charts
AXIS_STYLE = dict(
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.08)",
        tickcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.08)",
        tickcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.06)",
    ),
)


# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────
st.markdown("""
<div class="page-title">Mutual Fund <span>Portfolio</span></div>
<div class="page-subtitle">Overview &nbsp;·&nbsp; Performance &nbsp;·&nbsp; Analytics</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
nav_df = load_nav()

summary = []
total_invested = 0
total_current = 0

for fund_name, meta in mutual_funds.items():
    try:
        code   = meta["code"]
        folder = meta["folder"]
        fund_df = load_fund(folder)

        match = nav_df[nav_df["SchemeCode"] == str(code)]
        if match.empty:
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue

        latest_row  = match.sort_values("Date", ascending=False).iloc[0]
        latest_nav  = float(latest_row["NAV"])
        latest_date = latest_row["Date"].date()

        invested = calculate_invested_amount(fund_df)
        current  = calculate_current_value(fund_df, latest_nav)

        fund_xirr         = compute_fund_xirr(fund_df, latest_nav)
        fund_xirr_percent = fund_xirr * 100
        fund_xirr_display = f"{fund_xirr_percent:.2f}%"

        total_invested += invested
        total_current  += current

        summary.append([
            fund_name, code, invested, current,
            current - invested, latest_nav, latest_date, fund_xirr_display
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")


absolute_return_overall = (
    (total_current - total_invested) / total_invested * 100
    if total_invested > 0 else 0
)

all_funds_df = load_all_funds()
overall_xirr = compute_overall_xirr(all_funds_df)

pnl        = total_current - total_invested
pnl_class  = "positive" if pnl >= 0 else "negative"
ret_class  = "positive" if absolute_return_overall >= 0 else "negative"


# ─────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────
def metric_card(label, value, value_class=""):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {value_class}">{value}</div>
    </div>
    """

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(metric_card("Total Invested", f"₹{total_invested:,.0f}"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Current Value", f"₹{total_current:,.0f}", "gold"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Total P & L", f"₹{pnl:,.0f}", pnl_class), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Absolute Return", f"{absolute_return_overall:.2f}%", ret_class), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("XIRR (Overall)", f"{overall_xirr*100:.2f}%", "gold"), unsafe_allow_html=True)

st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FUND DETAILS TABLE + DONUT
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    Fund Details <span class="section-tag">Holdings</span>
</div>
""", unsafe_allow_html=True)

df = pd.DataFrame(summary, columns=[
    "Fund", "SchemeCode", "Invested", "Current",
    "P&L", "Latest NAV", "NAV Date", "XIRR"
])

col_table, col_chart = st.columns([7, 3])

with col_table:
    st.dataframe(df, use_container_width=True, height=len(df) * 42 + 40)

with col_chart:
    # Donut — styled
    fig_donut = px.pie(
        df, names="Fund", values="Current",
        hole=0.58, title="Allocation"
    )
    fig_donut.update_traces(
        textinfo="percent",
        textposition="inside",
        textfont=dict(family="DM Mono, monospace", size=11, color="#0d0f12"),
        marker=dict(
            colors=["#c8a550","#4caf82","#7ecfe0","#e2c278","#e05c5c","#a78bfa","#f9a825"],
            line=dict(color="#0d0f12", width=2),
        ),
    )
    fig_donut.update_layout(
        **PLOT_LAYOUT,
        title_font_size=14,
        margin=dict(l=8, r=8, t=36, b=8),
        showlegend=False,
        annotations=[dict(
            text=f"<b>₹{total_current/1e5:.1f}L</b>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family="Cormorant Garamond, serif", size=20, color="#e2c278"),
        )],
    )
    st.plotly_chart(fig_donut, use_container_width=True, key="allocation_donut")

# Treemap
st.markdown("<br>", unsafe_allow_html=True)
fig_tree = px.treemap(
    df, path=["Fund"], values="Current",
    title="Fund Allocation — Treemap",
    color="Current",
    color_continuous_scale=["#13161b", "#c8a550"],
)
fig_tree.update_traces(
    textinfo="label+percent entry",
    textfont=dict(family="DM Sans, sans-serif", size=13),
    marker=dict(line=dict(color="#0d0f12", width=2)),
)
fig_tree.update_layout(**PLOT_LAYOUT, **AXIS_STYLE, coloraxis_showscale=False)
st.plotly_chart(fig_tree, use_container_width=True, key="treemap")


# ─────────────────────────────────────────────
# DAILY SUMMARY
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    Daily Portfolio Summary <span class="section-tag">Daily Data</span>
</div>
""", unsafe_allow_html=True)

daily_path = "data/portfolio_daily.csv"
daily_df   = pd.read_csv(daily_path)
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date", ascending=False)
daily_df["Date"] = daily_df["Date"].dt.strftime("%d-%m-%Y")

st.dataframe(daily_df, use_container_width=True)

# Dual-axis chart
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date")
daily_df["OneDayChangePct_val"] = (
    daily_df["OneDayChangePct"].str.replace("%", "").astype(float)
)

fig_perf = make_subplots(specs=[[{"secondary_y": True}]])

bar_colors = ["#4caf82" if x > 0 else "#e05c5c" for x in daily_df["OneDayChange"]]

fig_perf.add_trace(
    go.Bar(
        x=daily_df["Date"],
        y=daily_df["OneDayChange"],
        name="Daily Change",
        marker_color=bar_colors,
        marker_line_width=0,
        opacity=0.75,
    ),
    secondary_y=False,
)
fig_perf.add_trace(
    go.Scatter(
        x=daily_df["Date"],
        y=daily_df["TotalValue"],
        name="Total Value",
        mode="lines",
        line=dict(color="#c8a550", width=2),
        fill="tozeroy",
        fillcolor="rgba(200,165,80,0.06)",
    ),
    secondary_y=True,
)
fig_perf.update_layout(
    **PLOT_LAYOUT,
    **AXIS_STYLE,
    title="Portfolio Performance",
    hovermode="x unified",
)
fig_perf.update_yaxes(
    gridcolor="rgba(255,255,255,0.04)",
    linecolor="rgba(255,255,255,0.06)",
    zerolinecolor="rgba(255,255,255,0.06)",
)
st.plotly_chart(fig_perf, use_container_width=True)


# ─────────────────────────────────────────────
# MONTHLY INVESTMENT SUMMARY
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    Monthly Investment Summary <span class="section-tag">By Fund & Year</span>
</div>
""", unsafe_allow_html=True)

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

    month_map = {
        1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
        7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec",
    }
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
            return [f"background-color: #2a1f0e; color: #e2c278; font-weight: 700"] * len(row)
        return [""] * len(row)

    def highlight_total_column(col):
        if col.name == "Total":
            return ["background-color: rgba(200,165,80,0.06); color: #e2c278; font-weight: 600"] * len(col)
        return [""] * len(col)

    numeric_cols = final_df.select_dtypes(include="number").columns
    st.dataframe(
        final_df.style
            .apply(highlight_total_row, axis=1)
            .apply(highlight_total_column, axis=0)
            .format({col: "{:,.0f}" for col in numeric_cols}),
        use_container_width=True,
    )


# ─────────────────────────────────────────────
# DAILY CHANGE TABLE
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    Daily Change Across Funds <span class="section-tag">NAV Delta</span>
</div>
""", unsafe_allow_html=True)

latest_nav_date = nav_df["Date"].max().date()
selected_date   = st.date_input("Select Date", value=latest_nav_date)
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

    row_prev         = prev_rows.iloc[-1]
    change_in_value  = float(row_today["absolute_gain_loss"]) - float(row_prev["absolute_gain_loss"])
    nav_today        = float(row_today["nav"])
    nav_prev         = float(row_prev["nav"])
    pct_change_nav   = ((nav_today - nav_prev) / nav_prev * 100) if nav_prev != 0 else 0
    indicator        = "🟢 ↑" if nav_today > nav_prev else "🔴 ↓"

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
change_color = "positive" if total_change >= 0 else "negative"
sign         = "+" if total_change >= 0 else ""

st.markdown(f"""
<div class="total-callout">
    Total Change Across All Funds &nbsp;
    <span class="{change_color}">{sign}₹{total_change:,.2f}</span>
</div>
""", unsafe_allow_html=True)
