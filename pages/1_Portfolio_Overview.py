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

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Portfolio Dashboard",
    layout="wide"
)

# =========================================================
# COLORS
# =========================================================
PRIMARY = "#7C3AED"
SECONDARY = "#06B6D4"
SUCCESS = "#10B981"
DANGER = "#EF4444"
WARNING = "#F59E0B"

CARD_BG = "#111827"
BG_MAIN = "#0F172A"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"

# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown("""
<style>

html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background-color: #0F172A;
    color: white;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    color: #F8FAFC;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #1F2937;
}

.stSelectbox label,
.stDateInput label {
    color: #CBD5E1 !important;
    font-weight: 600;
}

hr {
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
}

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #111827;
}

::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.markdown("""
<h1 style='text-align:center; margin-bottom:30px;'>
📊 Mutual Fund Portfolio Dashboard
</h1>
""", unsafe_allow_html=True)

# =========================================================
# METRIC CARD
# =========================================================
def metric_card(col, title, value, color):

    card_html = f"""
    <div style="
        background:#111827;
        padding:20px;
        border-radius:18px;
        border:1px solid #1F2937;
        box-shadow:0 4px 18px rgba(0,0,0,0.25);
        text-align:center;
        min-height:120px;
    ">

        <div style="
            color:#94A3B8;
            font-size:15px;
            font-weight:600;
            margin-bottom:12px;
        ">
            {title}
        </div>

        <div style="
            color:{color};
            font-size:30px;
            font-weight:700;
        ">
            {value}
        </div>

    </div>
    """

    col.markdown(card_html, unsafe_allow_html=True)

# =========================================================
# LOAD NAV
# =========================================================
nav_df = load_nav()

summary = []

total_invested = 0
total_current = 0

# =========================================================
# PROCESS FUNDS
# =========================================================
for fund_name, meta in mutual_funds.items():

    try:

        code = meta["code"]
        folder = meta["folder"]

        fund_df = load_fund(folder)

        match = nav_df[nav_df["SchemeCode"] == str(code)]

        if match.empty:
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue

        latest_row = match.sort_values("Date", ascending=False).iloc[0]

        latest_nav = float(latest_row["NAV"])
        latest_date = latest_row["Date"].date()

        invested = calculate_invested_amount(fund_df)

        current = calculate_current_value(
            fund_df,
            latest_nav
        )

        fund_xirr = compute_fund_xirr(
            fund_df,
            latest_nav
        )

        total_invested += invested
        total_current += current

        summary.append([
            fund_name,
            code,
            invested,
            current,
            current - invested,
            latest_nav,
            latest_date,
            f"{fund_xirr * 100:.2f}%"
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")

# =========================================================
# OVERALL VALUES
# =========================================================
absolute_return_overall = (
    ((total_current - total_invested) / total_invested) * 100
    if total_invested > 0 else 0
)

all_funds_df = load_all_funds()

overall_xirr = compute_overall_xirr(all_funds_df)

# =========================================================
# METRICS
# =========================================================
col1, col2, col3, col4, col5 = st.columns(5)

metric_card(
    col1,
    "💰 Total Invested",
    f"₹{total_invested:,.0f}",
    PRIMARY
)

metric_card(
    col2,
    "📈 Current Value",
    f"₹{total_current:,.0f}",
    SUCCESS
)

metric_card(
    col3,
    "📊 Total P&L",
    f"₹{total_current-total_invested:,.0f}",
    SUCCESS if total_current >= total_invested else DANGER
)

metric_card(
    col4,
    "📉 Absolute Return",
    f"{absolute_return_overall:.2f}%",
    SECONDARY
)

metric_card(
    col5,
    "📌 Overall XIRR",
    f"{overall_xirr*100:.2f}%",
    WARNING
)

st.divider()

# =========================================================
# FUND DETAILS
# =========================================================
st.markdown("## 📋 Fund Details")

df = pd.DataFrame(summary, columns=[
    "Fund",
    "SchemeCode",
    "Invested",
    "Current",
    "P&L",
    "Latest NAV",
    "NAV Date",
    "XIRR"
])

col1, col2 = st.columns([7, 2])

# =========================================================
# TABLE
# =========================================================
with col1:

    display_df = df.copy()

    display_df["Invested"] = display_df["Invested"].map(
        lambda x: f"₹{x:,.0f}"
    )

    display_df["Current"] = display_df["Current"].map(
        lambda x: f"₹{x:,.0f}"
    )

    display_df["P&L"] = display_df["P&L"].map(
        lambda x: f"₹{x:,.0f}"
    )

    display_df["Latest NAV"] = display_df["Latest NAV"].map(
        lambda x: f"{x:.2f}"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        height=min((len(display_df) + 1) * 42, 500)
    )

# =========================================================
# DONUT CHART
# =========================================================
with col2:

    fig = px.pie(
        df,
        names="Fund",
        values="Current",
        hole=0.62
    )

    fig.update_traces(
        textinfo="percent",
        textfont_size=13,
        marker=dict(
            line=dict(color=BG_MAIN, width=2)
        )
    )

    fig.update_layout(
        paper_bgcolor=BG_MAIN,
        plot_bgcolor=BG_MAIN,
        font_color="white",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        annotations=[
            dict(
                text="Portfolio",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False
            )
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# TREEMAP
# =========================================================
fig_tree = px.treemap(
    df,
    path=["Fund"],
    values="Current",
    color="P&L",
    color_continuous_scale="RdYlGn"
)

fig_tree.update_layout(
    paper_bgcolor=BG_MAIN,
    plot_bgcolor=BG_MAIN,
    font_color="white",
    margin=dict(t=40, l=10, r=10, b=10)
)

fig_tree.update_traces(
    textinfo="label+percent entry"
)

st.plotly_chart(
    fig_tree,
    use_container_width=True
)

st.divider()

# =========================================================
# DAILY SUMMARY
# =========================================================
st.markdown("## 📊 Daily Portfolio Summary")

daily_path = "data/portfolio_daily.csv"

daily_df = pd.read_csv(daily_path)

daily_df["Date"] = pd.to_datetime(
    daily_df["Date"],
    format="%d-%m-%Y"
)

daily_df = daily_df.sort_values(
    "Date",
    ascending=False
)

display_daily = daily_df.copy()

display_daily["Date"] = display_daily["Date"].dt.strftime("%d-%m-%Y")

st.dataframe(
    display_daily,
    use_container_width=True
)

# =========================================================
# PERFORMANCE CHART
# =========================================================
daily_df = daily_df.sort_values("Date")

daily_df["OneDayChangePct_val"] = (
    daily_df["OneDayChangePct"]
    .str.replace("%", "")
    .astype(float)
)

fig = make_subplots(
    specs=[[{"secondary_y": True}]]
)

# BAR CHART
fig.add_trace(
    go.Bar(
        x=daily_df["Date"],
        y=daily_df["OneDayChange"],
        name="Daily Change",
        marker_color=[
            SUCCESS if x > 0 else DANGER
            for x in daily_df["OneDayChange"]
        ],
        opacity=0.7
    ),
    secondary_y=False
)

# LINE CHART
fig.add_trace(
    go.Scatter(
        x=daily_df["Date"],
        y=daily_df["TotalValue"],
        name="Total Value",
        mode="lines+markers"
    ),
    secondary_y=True
)

fig.update_layout(
    title={
        "text": "📈 Portfolio Performance",
        "x": 0.5
    },
    hovermode="x unified",
    paper_bgcolor=BG_MAIN,
    plot_bgcolor=CARD_BG,
    font_color="white",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    ),
    height=520
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="rgba(255,255,255,0.08)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# =========================================================
# MONTHLY INVESTMENT SUMMARY
# =========================================================
st.markdown("## 📅 Monthly Investment Summary")

monthly_data = []

for fund_name, meta in mutual_funds.items():

    try:

        folder = meta["folder"]
        code = meta["code"]

        df_month = load_fund(folder)

        df_month["Date"] = pd.to_datetime(
            df_month["Date"],
            errors="coerce"
        )

        df_month = df_month.dropna(subset=["Date"])

        df_month["Year"] = df_month["Date"].dt.year
        df_month["Month"] = df_month["Date"].dt.month

        grouped = (
            df_month
            .groupby(["Year", "Month"])["Amount"]
            .sum()
            .reset_index()
        )

        for _, row in grouped.iterrows():

            monthly_data.append([
                code,
                fund_name,
                row["Year"],
                row["Month"],
                row["Amount"]
            ])

    except Exception as e:
        st.warning(f"{fund_name} skipped: {e}")

if monthly_data:

    monthly_df = pd.DataFrame(monthly_data, columns=[
        "Code",
        "Fund",
        "Year",
        "Month",
        "Amount"
    ])

    years = sorted(
        monthly_df["Year"]
        .dropna()
        .astype(int)
        .unique()
    )

    selected_year = st.selectbox(
        "Select Year",
        years,
        index=len(years)-1
    )

    year_df = monthly_df[
        monthly_df["Year"] == selected_year
    ]

    pivot_df = year_df.pivot_table(
        index=["Code", "Fund"],
        columns="Month",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    month_map = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec"
    }

    pivot_df = pivot_df.rename(columns=month_map)

    for m in month_map.values():

        if m not in pivot_df.columns:
            pivot_df[m] = 0

    month_cols = list(month_map.values())

    pivot_df = pivot_df[
        ["Code", "Fund"] + month_cols
    ]

    pivot_df["Total"] = pivot_df[
        month_cols
    ].sum(axis=1)

    total_values = ["", "TOTAL"]

    for m in month_cols:
        total_values.append(
            pivot_df[m].sum()
        )

    total_values.append(
        pivot_df["Total"].sum()
    )

    total_df = pd.DataFrame(
        [total_values],
        columns=pivot_df.columns
    )

    final_df = pd.concat(
        [pivot_df, total_df],
        ignore_index=True
    )

    st.markdown(f"### Year {selected_year}")

    numeric_cols = final_df.select_dtypes(
        include="number"
    ).columns

    for col in numeric_cols:
        final_df[col] = final_df[col].map(
            lambda x: f"{x:,.0f}"
        )

    st.dataframe(
        final_df,
        use_container_width=True
    )

# =========================================================
# DAILY CHANGE TABLE
# =========================================================
st.divider()

st.markdown("## 💹 Daily Change Across Funds")

latest_nav_date = nav_df["Date"].max().date()

selected_date = st.date_input(
    "Select Date",
    value=latest_nav_date
)

selected_date_dt = pd.to_datetime(selected_date)

daily_rows = []

for fund_name, meta in mutual_funds.items():

    folder = meta["folder"]
    code = meta["code"]

    file_path = f"mutualfund/{folder}/daily_{code}.csv"

    if not os.path.exists(file_path):
        continue

    df_daily = pd.read_csv(file_path)

    df_daily.columns = df_daily.columns.str.strip()

    df_daily["date"] = pd.to_datetime(
        df_daily["date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    df_daily = (
        df_daily
        .dropna(subset=["date"])
        .sort_values("date")
    )

    today_rows = df_daily[
        df_daily["date"] == selected_date_dt
    ]

    if today_rows.empty:
        continue

    row_today = today_rows.iloc[-1]

    prev_rows = df_daily[
        df_daily["date"] < selected_date_dt
    ]

    if prev_rows.empty:
        continue

    row_prev = prev_rows.iloc[-1]

    change_in_value = (
        float(row_today["absolute_gain_loss"])
        - float(row_prev["absolute_gain_loss"])
    )

    nav_today = float(row_today["nav"])

    nav_prev = float(row_prev["nav"])

    pct_change_nav = (
        ((nav_today - nav_prev) / nav_prev) * 100
        if nav_prev != 0 else 0
    )

    indicator = (
        "🟢 ↑"
        if nav_today > nav_prev
        else "🔴 ↓"
    )

    daily_rows.append([
        row_today["date"].strftime("%d-%m-%Y"),
        fund_name,
        code,
        round(change_in_value, 2),
        f"{pct_change_nav:.2f}%",
        indicator
    ])

df_daily_change = pd.DataFrame(daily_rows, columns=[
    "Date",
    "Fund Name",
    "Fund Code",
    "Change in Value",
    "% Change in NAV",
    "Indicator"
])

st.dataframe(
    df_daily_change,
    use_container_width=True
)

# =========================================================
# TOTAL DAILY CHANGE
# =========================================================
total_change = df_daily_change[
    "Change in Value"
].sum()

st.markdown(
    f"""
    <div style="
        margin-top:15px;
        background:{CARD_BG};
        padding:18px;
        border-radius:14px;
        border:1px solid #1F2937;
        text-align:center;
        font-size:1.3rem;
        font-weight:700;
        color:{SUCCESS if total_change >= 0 else DANGER};
    ">
        💹 Total Daily Change Across All Funds:
        ₹{total_change:,.2f}
    </div>
    """,
    unsafe_allow_html=True
)
