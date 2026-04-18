#pages/2_Fund_Details.py — INDIVIDUAL FUND VIEW
import streamlit as st
from utils.nav_loader import load_nav_file
from utils.portfolio_loader import load_all_funds
from utils.calculations import merge_nav_with_portfolio

mutual_funds = {...}  # same dict

st.title("📄 Individual Fund Details")

nav_df = load_nav_file()
portfolio_df = load_all_funds()

merged = merge_nav_with_portfolio(portfolio_df, nav_df, mutual_funds)

fund_list = merged["FundName"].unique()
selected_fund = st.selectbox("Select a Fund", fund_list)

fund_df = merged[merged["FundName"] == selected_fund]

latest_nav = fund_df["LatestNAV"].iloc[-1]
latest_date = fund_df["LatestNAVDate"].iloc[-1]

st.metric("Latest NAV", f"{latest_nav}", latest_date.strftime("%d-%b-%Y"))

st.dataframe(fund_df)
