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

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Portfolio", layout="wide")

st.title("🏠 Mutual Fund Portfolio")

# =========================
# LOAD DATA
# =========================
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
            fund_name,
            code,
            invested,
            current,
            current - invested,
            latest_nav,
            latest_date,
            f"{fund_xirr*100:.2f}%"
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")

df = pd.DataFrame(summary, columns=[
    "Fund", "SchemeCode", "Invested", "Current",
    "P&L", "Latest NAV", "NAV Date", "XIRR"
])

absolute_return = ((total_current - total_invested) / total_invested * 100) if total_invested else 0
overall_xirr = compute_overall_xirr(load_all_funds())

# =========================
# KPI CARDS
# =========================
def metric_card(label, value):
    return f"""
    <div style="
        padding:12px;
        border-radius:12px;
        background: linear-gradient(135deg, #1f2937, #111827);
        text-align:center;">
        <div style="font-size:13px; color:#9CA3AF;">{label}</div>
        <div style="font-size:20px; font-weight:bold;">{value}</div>
    </div>
    """

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "📈 Performance",
    "📅 Daily",
    "📆 Monthly"
])

# =========================
# 📊 TAB 1: OVERVIEW
# =========================
with tab1:

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.markdown(metric_card("Invested", f"₹{total_invested:,.0f}"), unsafe_allow_html=True)
    col2.markdown(metric_card("Current", f"₹{total_current:,.0f}"), unsafe_allow_html=True)
    col3.markdown(metric_card("P&L", f"₹{total_current-total_invested:,.0f}"), unsafe_allow_html=True)
    col4.markdown(metric_card("Return", f"{absolute_return:.2f}%"), unsafe_allow_html=True)
    col5.markdown(metric_card("XIRR", f"{overall_xirr*100:.2f}%"), unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        def color_pnl(val):
            if pd.isna(val):
                return ""
            return "color: green; font-weight: bold" if val > 0 else "color: red; font-weight: bold"

        styled_df = df.style \
            .format({
                "Invested": "₹{:,.0f}",
                "Current": "₹{:,.0f}",
                "P&L": "₹{:,.0f}",
                "Latest NAV": "{:.2f}"
            }) \
            .map(color_pnl, subset=["P&L"])

        st.dataframe(styled_df, use_container_width=True, height=350)

    with col2:
        fig = px.pie(df, names="Fund", values="Current", hole=0.5)
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =========================
# 📈 TAB 2: PERFORMANCE
# =========================
with tab2:

    daily_df = pd.read_csv("data/portfolio_daily.csv")
    daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
    daily_df = daily_df.sort_values("Date")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=daily_df["Date"],
            y=daily_df["OneDayChange"],
            name="Daily Change",
            marker_color=["green" if x > 0 else "red" for x in daily_df["OneDayChange"]],
            opacity=0.6
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=daily_df["Date"],
            y=daily_df["TotalValue"],
            name="Total Value",
            mode="lines"
        ),
        secondary_y=True
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# 📅 TAB 3: DAILY
# =========================
with tab3:

    st.subheader("Daily Summary")

    daily_df = pd.read_csv("data/portfolio_daily.csv")
    daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
    daily_df = daily_df.sort_values("Date", ascending=False)

    st.dataframe(daily_df, use_container_width=True, height=400)

    st.divider()

    st.subheader("Daily Change")

    latest_nav_date = nav_df["Date"].max().date()
    selected_date = st.date_input("Select Date", value=latest_nav_date)

    rows = []

    for fund_name, meta in mutual_funds.items():
        file_path = f"mutualfund/{meta['folder']}/daily_{meta['code']}.csv"
        if not os.path.exists(file_path):
            continue

        df_d = pd.read_csv(file_path)
        df_d["date"] = pd.to_datetime(df_d["date"], format="%d-%m-%Y", errors="coerce")
        df_d = df_d.dropna().sort_values("date")

        today = df_d[df_d["date"] == pd.to_datetime(selected_date)]
        prev = df_d[df_d["date"] < pd.to_datetime(selected_date)]

        if today.empty or prev.empty:
            continue

        t = today.iloc[-1]
        p = prev.iloc[-1]

        change = float(t["absolute_gain_loss"]) - float(p["absolute_gain_loss"])

        rows.append([
            fund_name,
            round(change, 2)
        ])

    df_change = pd.DataFrame(rows, columns=["Fund", "Change"])

    st.dataframe(df_change, use_container_width=True)

    st.markdown(f"### 💹 Total Change: ₹{df_change['Change'].sum():,.2f}")

# =========================
# 📆 TAB 4: MONTHLY
# =========================
with tab4:

    monthly_data = []

    for fund_name, meta in mutual_funds.items():
        try:
            df = load_fund(meta["folder"])
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

            df["Year"] = df["Date"].dt.year
            df["Month"] = df["Date"].dt.month

            grouped = df.groupby(["Year", "Month"])["Amount"].sum().reset_index()

            for _, r in grouped.iterrows():
                monthly_data.append([
                    fund_name,
                    int(r["Year"]),
                    int(r["Month"]),
                    r["Amount"]
                ])
        except:
            pass

    monthly_df = pd.DataFrame(monthly_data, columns=["Fund", "Year", "Month", "Amount"])

    years = sorted(monthly_df["Year"].unique())
    selected_year = st.selectbox("Year", years, index=len(years)-1)

    df_year = monthly_df[monthly_df["Year"] == selected_year]

    pivot = df_year.pivot_table(index="Fund", columns="Month", values="Amount", fill_value=0)

    st.dataframe(pivot, use_container_width=True)
