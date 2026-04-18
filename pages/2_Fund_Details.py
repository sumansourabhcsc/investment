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

fund_df = merged[merged["FundName"] == selected_fund].copy()

# Extract values for display
fund_name = selected_fund
scheme_code = fund_df["SchemeCode"].iloc[0]
latest_nav = fund_df["LatestNAV"].iloc[-1]
latest_date = fund_df["LatestNAVDate"].iloc[-1]

# Show details on top
# Calculate invested + current value
#invested_amount = fund_df["Amount"].sum()
#current_value = (fund_df["Units"] * latest_nav).sum()

# Calculate invested + current value
invested_amount = fund_df["Amount"].sum()
current_value = (fund_df["Units"] * latest_nav).sum()
profit = current_value - invested_amount
return_pct = (profit / invested_amount) * 100

# XIRR calculation
cashflows = list(-fund_df["Amount"])
dates = list(fund_df["Date_Purchase"])

cashflows.append(current_value)
dates.append(latest_date)

try:
    fund_xirr = xirr(cashflows, dates) * 100
except:
    fund_xirr = None





# Show details on top
st.subheader(f"📌 {fund_name}")

col1, col2, col3 = st.columns(3)
col1.metric("Scheme Code", scheme_code)
col2.metric("Latest NAV", f"{latest_nav:.4f}")
col3.metric("NAV Date", latest_date.strftime("%d-%b-%Y"))

col4, col5, col6 = st.columns(3)
col4.metric("Total Invested", f"₹{invested_amount:,.2f}")
col5.metric("Current Value", f"₹{current_value:,.2f}")
col6.metric("Return %", f"{return_pct:.2f}%")

col7, col8 = st.columns(2)
col7.metric("Profit / Loss", f"₹{profit:,.2f}")
col8.metric("XIRR", f"{fund_xirr:.2f}%" if fund_xirr else "N/A")



# Remove columns from table
fund_df = fund_df.drop(columns=["FundName", "SchemeCode", "LatestNAV", "LatestNAVDate"])

# Show cleaned table
st.write("### Transaction History")
st.dataframe(fund_df)

