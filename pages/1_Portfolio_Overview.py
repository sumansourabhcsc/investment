import streamlit as st
import pandas as pd

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value
from utils.load_funds import load_all_funds
from utils.xirr_overall import compute_overall_xirr


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


