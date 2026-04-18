import streamlit as st
import plotly.express as px
import pandas as pd

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.xirr import xirr

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Fund Details", layout="wide")

st.title("📁 Fund Details")

nav_df = load_nav()

# =========================
# FUND SELECTION (SAFE)
# =========================
fund_options = list(mutual_funds.keys())

selected_fund = st.selectbox("Select Fund", fund_options)

scheme_code = mutual_funds[selected_fund]["code"]
folder = mutual_funds[selected_fund]["folder"]

# =========================
# LOAD DATA
# =========================
fund_df = load_fund(folder)

# =========================
# GET LATEST NAV (BY CODE)
# =========================
match = nav_df[nav_df["SchemeCode"] == str(scheme_code)]

if match.empty:
    st.error("No NAV data found for this fund")
    st.stop()

latest_row = match.sort_values("Date", ascending=False).iloc[0]

latest_nav = float(latest_row["NAV"])
latest_date = latest_row["Date"].date()

# =========================
# SUMMARY METRICS
# =========================
total_units = fund_df["Units"].sum()
invested = fund_df["Amount"].sum()
current_value = total_units * latest_nav
profit = current_value - invested

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Invested", f"₹{invested:,.2f}")
col2.metric("📈 Current Value", f"₹{current_value:,.2f}")
col3.metric("📊 P&L", f"₹{profit:,.2f}")
col4.metric("📅 Latest NAV", f"₹{latest_nav:.2f}")

st.caption(f"Last NAV Date: {latest_date}")

st.divider()

# =========================
# SIP HISTORY TABLE
# =========================
st.subheader("📋 SIP History (Latest → Oldest)")

fund_df_sorted = fund_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
fund_df_sorted["Date"] = fund_df_sorted["Date"].dt.date

st.dataframe(fund_df_sorted, use_container_width=True)

# =========================
# INVESTMENT TREND
# =========================
st.subheader("📈 Investment Over Time")

fig1 = px.line(
    fund_df,
    x="Date",
    y="Amount",
    title="Investment Amount Over Time"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================
# UNITS ACCUMULATION
# =========================
st.subheader("📦 Units Accumulation")

fig2 = px.line(
    fund_df,
    x="Date",
    y="Units",
    title="Units Accumulated Over Time"
)

st.plotly_chart(fig2, use_container_width=True)

# =========================
# FUND GROWTH VALUE (OPTIONAL VIEW)
# =========================

#st.subheader("💹 Fund Value Growth")

#fund_df_sorted = fund_df.sort_values("Date").copy()
#fund_df_sorted["Value"] = fund_df_sorted["Units"].cumsum() * latest_nav

#fig3 = px.line(
 #   fund_df_sorted,
  #  x="Date",
   # y="Value",
    #title="Estimated Portfolio Value Growth"
#)

#st.plotly_chart(fig3, use_container_width=True)

