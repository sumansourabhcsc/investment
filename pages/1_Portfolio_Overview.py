import streamlit as st
import pandas as pd
from utils.data_loader import load_nav, get_all_funds, load_fund
from utils.calculations import calculate_current_value, calculate_invested_amount, calculate_profit

st.title("🏠 Portfolio Overview")

nav_df = load_nav()

funds = get_all_funds()

total_invested = 0
total_current = 0

summary = []

for fund in funds:
    fund_df = load_fund(fund)

    scheme_name = fund
    scheme_code = None

    # get latest NAV
    latest_nav = nav_df[nav_df["SchemeName"].str.contains(fund, case=False)]["NAV"]
    if len(latest_nav) > 0:
        nav = latest_nav.values[0]
    else:
        continue

    invested = calculate_invested_amount(fund_df)
    current = calculate_current_value(fund_df, nav)

    total_invested += invested
    total_current += current

    summary.append([fund, invested, current, current - invested])

df = pd.DataFrame(summary, columns=["Fund", "Invested", "Current", "P&L"])

st.dataframe(df)

st.metric("Total Invested", f"₹{total_invested:,.2f}")
st.metric("Current Value", f"₹{total_current:,.2f}")
st.metric("Total P&L", f"₹{total_current-total_invested:,.2f}")
