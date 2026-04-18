#pages/2_Fund_Details.py — INDIVIDUAL FUND VIEW
import streamlit as st
from utils.nav_loader import load_nav_file
from utils.portfolio_loader import load_all_funds
from utils.calculations import merge_nav_with_portfolio

mutual_funds = {
    "Bandhan Small Cap Fund": "147946",
    "Axis Small Cap Fund": "125354",
    "SBI Small Cap Fund": "125497",
    "quant Small Cap Fund": "120828",
    "Motilal Oswal Midcap Fund": "127042",
    "HSBC Midcap Fund": "151034",
    "Kotak Midcap Fund": "119775",
    "quant Mid Cap Fund": "120841",
    "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": "150902",
    "Parag Parikh Flexi Cap Fund": "122639",
    "Kotak Flexicap Fund": "112090",
    "Nippon India Large Cap Fund": "118632",
    "ICICI Pru BHARAT 22 FOF": "143903",
    "Mirae Asset FANG+": "148928",
    "SBI Magnum Children's Benefit Fund": "148490"
}

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
