#pages/1_Overall_Summary.py — OVERALL PORTFOLIO VIEW
import streamlit as st
from utils.nav_loader import load_nav_file
from utils.portfolio_loader import load_all_funds
from utils.calculations import merge_nav_with_portfolio, calculate_summary

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

st.title("📈 Overall Portfolio Summary")

nav_df = load_nav_file()
portfolio_df = load_all_funds()

merged = merge_nav_with_portfolio(portfolio_df, nav_df, mutual_funds)

#st.write("Merged columns:", merged.columns.tolist())
#st.write(merged.head(20))

summary = calculate_summary(merged)

# Show latest NAV and date for each fund
latest_nav_info = merged.groupby("FundName").agg({
    "LatestNAV": "last",
    "LatestNAVDate": "last"
}).reset_index()

st.subheader("Latest NAV (All Funds)")
st.dataframe(latest_nav_info)


st.dataframe(summary)

total_invested = summary["Invested"].sum()
total_value = summary["CurrentValue"].sum()
total_profit = total_value - total_invested

st.metric("Total Invested", f"₹{total_invested:,.2f}")
st.metric("Current Value", f"₹{total_value:,.2f}")
st.metric("Total Profit/Loss", f"₹{total_profit:,.2f}")
