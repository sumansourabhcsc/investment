import streamlit as st
import pandas as pd

from config import mutual_funds
from utils.data_loader import load_fund, load_nav, get_latest_nav
from utils.calculations import calculate_invested_amount, calculate_current_value

st.set_page_config(page_title="Portfolio", layout="wide")

st.title("🏠 Mutual Fund Portfolio (SchemeCode Driven)")

nav_df = load_nav()

summary = []

total_invested = 0
total_current = 0

for fund_name, meta in mutual_funds.items():

    try:
        code = meta["code"]
        folder = meta["folder"]

        # 📁 Load investment data
        fund_df = load_fund(folder)

        # 📈 Get NAV by SchemeCode
        nav = get_latest_nav(nav_df, code)

        if nav is None:
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue

        invested = calculate_invested_amount(fund_df)
        current = calculate_current_value(fund_df, nav)

        total_invested += invested
        total_current += current

        summary.append([
            fund_name,
            code,
            invested,
            current,
            current - invested
        ])

    except Exception as e:
        st.error(f"{fund_name} error: {e}")

df = pd.DataFrame(summary, columns=[
    "Fund", "SchemeCode", "Invested", "Current", "P&L"
])

st.dataframe(df, use_container_width=True)

st.divider()

st.metric("💰 Total Invested", f"₹{total_invested:,.2f}")
st.metric("📈 Current Value", f"₹{total_current:,.2f}")
st.metric("📊 Total P&L", f"₹{total_current - total_invested:,.2f}")
