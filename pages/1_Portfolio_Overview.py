import streamlit as st
import pandas as pd

from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_current_value, calculate_invested_amount
from config import mutual_funds

st.set_page_config(page_title="Portfolio Overview", layout="wide")

st.title("🏠 Mutual Fund Portfolio Overview")

nav_df = load_nav()

summary = []

total_invested = 0
total_current = 0

for fund_name, folder in mutual_funds.items():

    try:
        fund_df = load_fund(folder)

        match = nav_df[nav_df["SchemeName"].str.contains(fund_name, case=False, na=False)]

        if match.empty:
            st.warning(f"No NAV found for {fund_name}")
            continue

        latest_nav = match["NAV"].values[0]

        invested = calculate_invested_amount(fund_df)
        current = calculate_current_value(fund_df, latest_nav)

        total_invested += invested
        total_current += current

        summary.append([
            fund_name,
            invested,
            current,
            current - invested
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")

df = pd.DataFrame(summary, columns=["Fund", "Invested", "Current", "P&L"])

st.dataframe(df, use_container_width=True)

st.divider()

st.metric("💰 Total Invested", f"₹{total_invested:,.2f}")
st.metric("📈 Current Value", f"₹{total_current:,.2f}")
st.metric("📊 Total P&L", f"₹{total_current - total_invested:,.2f}")
