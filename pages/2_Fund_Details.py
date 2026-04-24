import streamlit as st
import plotly.express as px
import pandas as pd

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.xirr_helper import compute_fund_xirr




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
# LOAD DAILY SNAPSHOT
# =========================
daily_path = f"{folder}/daily_{scheme_code}.csv"

try:
    daily_df = pd.read_csv(daily_path)

    # Convert date
    daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")

    # Sort latest first
    daily_df = daily_df.sort_values("Date", ascending=False).reset_index(drop=True)

except FileNotFoundError:
    daily_df = pd.DataFrame()




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

# =========================
# SUMMARY METRICS
# =========================
total_units = fund_df["Units"].sum()
invested = fund_df["Amount"].sum()
current_value = total_units * latest_nav
profit = current_value - invested
avg_buy_nav = invested / total_units if total_units > 0 else 0
absolute_return = ((current_value - invested) / invested) * 100 if invested > 0 else 0
fund_xirr = compute_fund_xirr(fund_df, latest_nav)



#st.caption(f"Last NAV Date: {latest_date}")
st.caption(f"📅 **Latest NAV:** ₹{latest_nav:.2f}  (as of {latest_date})")

#st.caption(f"📅 Latest NAV", ₹{latest_nav:.2f})
col1, col2, col3, col4, col5, col6,col7 = st.columns(7)

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

metric_normal(col1, "💰 Invested", f"₹{invested:,.2f}")
metric_normal(col2, "📈 Current Value", f"₹{current_value:,.2f}")
metric_normal(col3, "📊 P&L", f"₹{profit:,.2f}")
metric_normal(col4, "📉 Absolute Return", f"{absolute_return:.2f}%")
metric_normal(col5, "🧮 Avg Buy NAV", f"₹{avg_buy_nav:,.2f}")
metric_normal(col6, "📦 Total Units", f"{total_units:,.2f}")
#metric_normal(col7, "📅 Latest NAV", f"₹{latest_nav:.2f}")


metric_normal(col7,"📌 XIRR (as of today)", f"{fund_xirr*100:.2f}%")







#st.caption(f"Last NAV Date: {latest_date}")

st.divider()

# =========================
# SIP HISTORY TABLE
# =========================
st.subheader("📋 SIP History (Latest → Oldest)")

fund_df_sorted = fund_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
fund_df_sorted["Date"] = fund_df_sorted["Date"].dt.date

st.dataframe(fund_df_sorted, use_container_width=True)

st.divider()


st.write("DEBUG PATH:", daily_path)
st.write("FILE EXISTS:", daily_path.exists())

# =========================
# DAILY SNAPSHOT TABLE
# =========================
st.subheader("📅 Daily NAV Movement")

if daily_df.empty:
    st.info("No daily snapshot data available for this fund")
else:
    df_display = daily_df.copy()

    # Format date nicely
    df_display["Date"] = df_display["Date"].dt.date

    # Optional: Calculate daily change %
    if "NAV" in df_display.columns:
        df_display["Daily Change %"] = df_display["NAV"].pct_change(-1) * 100

    st.dataframe(df_display, use_container_width=True)

