import streamlit as st
import pandas as pd
import os
import plotly.express as px

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value
from utils.load_funds import load_all_funds
from utils.xirr_overall import compute_overall_xirr
from utils.data_loader import load_fund, load_nav
from utils.xirr_helper import compute_fund_xirr



# ✅ MUST BE FIRST Streamlit command
st.set_page_config(page_title="Portfolio", layout="wide")

st.title("🏠 Mutual Fund Portfolio Overview")

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
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue

        latest_row = match.sort_values("Date", ascending=False).iloc[0]

        latest_nav = float(latest_row["NAV"])
        latest_date = latest_row["Date"].date()

        invested = calculate_invested_amount(fund_df)
        current = calculate_current_value(fund_df, latest_nav)

        fund_xirr = compute_fund_xirr(fund_df, latest_nav)
        fund_xirr_percent = fund_xirr * 100
        fund_xirr_display = f"{fund_xirr_percent:.2f}%"


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
            fund_xirr_display
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")


absolute_return_overall = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0

# Load all SIP transactions for XIRR
all_funds_df = load_all_funds()

# Compute overall XIRR
overall_xirr = compute_overall_xirr(all_funds_df)


# =========================
# 📊 METRICS (NOW ON TOP)
# =========================
def metric_normal(col, label, value):
    col.markdown(
        f"""
        <div style='padding:8px 0;'>
            <span style='font-weight:600;'>{label}</span><br>
            <span style='font-size:1.1rem;'>{value}</span>
        </div>
        """,
        unsafe_allow_html=True
    )



col1, col2, col3, col4, col5 = st.columns(5)

metric_normal(col1, "💰 **Total Invested**", f"₹{total_invested:,.2f}")
metric_normal(col2, "📈 **Current Value**", f"₹{total_current:,.2f}")
metric_normal(col3, "📊 **Total P&L**", f"₹{total_current - total_invested:,.2f}")
metric_normal(col4, "📉 **Absolute Return**", f"{absolute_return_overall:.2f}%")
metric_normal(col5, "📌 **XIRR (Overall)**", f"{overall_xirr*100:.2f}%")



st.divider()

# =========================
# 📋 TABLE BELOW & Pie Chart
# =========================
# =========================
# 📋 TABLE BELOW
# =========================
st.subheader("Fund Details")
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

# Layout: Table (left) + Donut Chart (right)
col1, col2 = st.columns([2, 1])

with col1:
    st.dataframe(df, use_container_width=True, height=len(df) * 45)

with col2:
    # Donut chart using Current Value
    fig = px.pie(
        df,
        names="Fund",
        values="Current",
        hole=0.5,
        title="Fund Allocation"
    )

    # Show percent inside slices
    fig.update_traces(
        textinfo="percent",
        textposition="inside"
    )

    # Hide legend
    fig.update_layout(showlegend=False)

    # Center text (optional)
    fig.update_layout(
        annotations=[
            dict(
                text="100%",
                x=0.5,
                y=0.5,
                font_size=28,
                showarrow=False
            )
        ]
    )

    # Render only once with unique key
    st.plotly_chart(fig, use_container_width=True, key="allocation_donut")


# =========================
# 📋 TABLE BELOW & Pie Chart - END
# =========================
st.divider()
# =========================
# 📊 DAILY SUMMARY (from portfolio_daily.csv)
# =========================

import pandas as pd

# Load daily summary file
daily_path = "data/portfolio_daily.csv"
daily_df = pd.read_csv(daily_path)

# Convert Date to proper datetime (handles dd-mm-yyyy)
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")

# Sort latest date on top
daily_df = daily_df.sort_values("Date", ascending=False)

# Format date back to dd-mm-yyyy for display
daily_df["Date"] = daily_df["Date"].dt.strftime("%d-%m-%Y")

st.subheader("Daily Summary Dataset")

st.dataframe(
    daily_df,
    use_container_width=True,
)

# =========================
# 📊 DAILY SUMMARY (from portfolio_daily.csv) - END
# =========================


st.divider()
st.subheader("📊 Monthly Investment Summary by Fund & Year")

monthly_data = []

for fund_name, meta in mutual_funds.items():
    try:
        folder = meta["folder"]
        code = meta["code"]

        df = load_fund(folder)

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])

        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month

        grouped = df.groupby(["Year", "Month"])["Amount"].sum().reset_index()

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
        "Code", "Fund", "Year", "Month", "Amount"
    ])

    years = sorted(monthly_df["Year"].dropna().astype(int).unique())
    selected_year = st.selectbox("Select Year", years, index=len(years)-1)

    year_df = monthly_df[monthly_df["Year"] == selected_year]

    pivot_df = year_df.pivot_table(
        index=["Code", "Fund"],
        columns="Month",
        values="Amount",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    # =========================
    # MONTH FORMAT
    # =========================
    month_map = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }

    pivot_df = pivot_df.rename(columns=month_map)

    # Ensure all months exist
    for m in month_map.values():
        if m not in pivot_df.columns:
            pivot_df[m] = 0

    # Column order
    month_cols = list(month_map.values())
    pivot_df = pivot_df[["Code", "Fund"] + month_cols]

    # =========================
    # ✅ CREATE TOTAL COLUMN (FIRST!)
    # =========================
    pivot_df["Total"] = pivot_df[month_cols].sum(axis=1)

    # =========================
    # ✅ NOW CREATE TOTAL ROW
    # =========================
    total_values = ["", "TOTAL"]

    for m in month_cols:
        total_values.append(pivot_df[m].sum())

    total_values.append(pivot_df["Total"].sum())

    total_df = pd.DataFrame([total_values], columns=pivot_df.columns)

    final_df = pd.concat([pivot_df, total_df], ignore_index=True)



    

    st.markdown(f"### Year {selected_year}")
    # =========================
    # STYLING
    # =========================
    def highlight_total_row(row):
        if row["Fund"] == "TOTAL":
            return ["background-color: #5c1a33; color: white; font-weight: bold"] * len(row)
        return [""] * len(row)

    def highlight_total_column(col):
        if col.name == "Total":
            return ["background-color: #5c1a33; color: white; font-weight: bold"] * len(col)
        return [""] * len(col)

    
    numeric_cols = final_df.select_dtypes(include="number").columns

    st.dataframe(
    final_df.style
        .apply(highlight_total_row, axis=1)
        .apply(highlight_total_column, axis=0)
        .format({col: "{:,.0f}" for col in numeric_cols}),
    use_container_width=True
)

############################################################

# ---------------------------------------------------------
# DAILY CHANGE TABLE
# ---------------------------------------------------------
st.divider()
st.subheader("📅 Daily Change Across Funds")

latest_nav_date = nav_df["Date"].max().date()
selected_date = st.date_input("Select Date", value=latest_nav_date)
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
    df_daily["date"] = pd.to_datetime(df_daily["date"], format="%d-%m-%Y", errors="coerce")
    df_daily = df_daily.dropna(subset=["date"]).sort_values("date")

    today_rows = df_daily[df_daily["date"] == selected_date_dt]
    if today_rows.empty:
        continue

    row_today = today_rows.iloc[-1]
    prev_rows = df_daily[df_daily["date"] < selected_date_dt]
    if prev_rows.empty:
        continue

    row_prev = prev_rows.iloc[-1]

    change_in_value = float(row_today["absolute_gain_loss"]) - float(row_prev["absolute_gain_loss"])
    nav_today = float(row_today["nav"])
    nav_prev = float(row_prev["nav"])
    pct_change_nav = ((nav_today - nav_prev) / nav_prev * 100) if nav_prev != 0 else 0
    indicator = "🟢 ↑" if nav_today > nav_prev else "🔴 ↓"

    daily_rows.append([
        row_today["date"].strftime("%d-%m-%Y"),
        fund_name,
        code,
        round(change_in_value, 2),
        f"{pct_change_nav:.2f}%",
        indicator
    ])

df_daily = pd.DataFrame(daily_rows, columns=[
    "Date",
    "Fund Name",
    "Fund Code",
    "Change in Value",
    "% Change in NAV",
    "Indicator"
])

st.dataframe(df_daily, width="stretch")

st.markdown(
    f"### 💹 Total Change Across All Funds: **₹{df_daily['Change in Value'].sum():,.2f}**"
)
