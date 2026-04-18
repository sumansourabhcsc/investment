import streamlit as st
import pandas as pd

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value

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

        total_invested += invested
        total_current += current

        summary.append([
            fund_name,
            code,
            invested,
            current,
            current - invested,
            latest_nav,
            latest_date
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")


# =========================
# 📊 METRICS (NOW ON TOP)
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Invested", f"₹{total_invested:,.2f}")
col2.metric("📈 Current Value", f"₹{total_current:,.2f}")
col3.metric("📊 Total P&L", f"₹{total_current - total_invested:,.2f}")


st.divider()

# =========================
# 📋 TABLE BELOW
# =========================

df = pd.DataFrame(summary, columns=[
    "Fund",
    "SchemeCode",
    "Invested",
    "Current",
    "P&L",
    "Latest NAV",
    "NAV Date"
])

st.dataframe(df, use_container_width=True)



# pages/1_Overall_Summary.py
import streamlit as st
from utils.load_funds import load_all_funds
from utils.portfolio_math import compute_xirr_for_df

st.title("📊 Overall Portfolio Summary")

df = load_all_funds()

# You can later fetch NAV dynamically per fund
current_nav = 37.27  

xirr_value = compute_xirr_for_df(df, current_nav)

st.metric("Portfolio XIRR (as of today)", f"{xirr_value*100:.2f}%")
st.metric("Total Invested", f"₹{df['Amount'].sum():,.0f}")
st.metric("Total Units", f"{df['Units'].sum():,.2f}")
st.metric("Current Value", f"₹{df['Units'].sum()*current_nav:,.2f}")

st.write("### All Transactions")
st.dataframe(df)
