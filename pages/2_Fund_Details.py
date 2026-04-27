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
#st.title(fund_options )
selected_fund = st.selectbox("Select Fund", fund_options)
#st.title(selected_fund)
scheme_code = mutual_funds[selected_fund]["code"]
#st.title(scheme_code)
folder = mutual_funds[selected_fund]["folder"]
#st.title(folder)

# =========================
# LOAD DATA
# =========================
fund_df = load_fund(folder)


# =========================
# LOAD DAILY SNAPSHOT
# =========================
daily_path = f"mutualfund/{folder}/daily_{scheme_code}.csv"
#st.write("Selected Fund:", selected_fund)
#st.write("Folder:", folder)
#st.write("Daily Path:", daily_path)

try:
    daily_df = pd.read_csv(daily_path)

    # Convert date
    daily_df["Date"] = pd.to_datetime(daily_df["date"], format="%d-%m-%Y")

    # Sort latest first
    daily_df = daily_df.sort_values("Date", ascending=False).reset_index(drop=True)

except FileNotFoundError:
    daily_df = pd.DataFrame()



# =========================
# GET LATEST NAV (BY CODE)
# =========================
match = nav_df[nav_df["SchemeCode"] == str(scheme_code)]
#st.title(match)
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
#st.subheader("📋 SIP History (Latest → Oldest)")

#fund_df_sorted = fund_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
#fund_df_sorted["Date"] = fund_df_sorted["Date"].dt.date

#st.dataframe(fund_df_sorted, use_container_width=True)


#st.divider()

col1, col2 = st.columns(2)

with col1:
    # =========================
    # SIP HISTORY TABLE
    # =========================
    st.subheader("📋 SIP History (Latest → Oldest)")
    fund_df_sorted = fund_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
    fund_df_sorted["Date"] = fund_df_sorted["Date"].dt.date
    st.dataframe(fund_df_sorted, use_container_width=True)

with col2:
    # =========================
    # DAILY SNAPSHOT TABLE
    # =========================
    st.subheader("📅 Daily NAV Movement")
    if daily_df.empty:
        st.info("No daily snapshot data available for this fund")
    else:
        df_display = daily_df.copy()
        df_display["Date"] = df_display["Date"].dt.date
        if "NAV" in df_display.columns:
            df_display["Daily Change %"] = df_display["NAV"].pct_change(-1) * 100
        st.dataframe(df_display, use_container_width=True)

st.divider()

########################

import requests
from datetime import date, timedelta
import plotly.express as px

st.divider()

# =========================
# NAV HISTORY SECTION
# =========================
st.subheader("📈 NAV History")

# Date range selector - default last 1 year
col_d1, col_d2 = st.columns(2)
with col_d1:
    start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=365),
        max_value=date.today()
    )
with col_d2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        min_value=start_date,
        max_value=date.today()
    )

# Fetch NAV history
@st.cache_data(ttl=3600)
def fetch_nav_history(fund_code, start_date, end_date):
    url = f"https://api.mfapi.in/mf/{fund_code}"
    params = {
        "startDate": start_date.strftime("%d-%m-%Y"),
        "endDate": end_date.strftime("%d-%m-%Y")
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "data" in data and data["data"]:
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
            df = df.sort_values("date", ascending=True).reset_index(drop=True)
            df.rename(columns={"date": "Date", "nav": "NAV"}, inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch NAV history: {e}")
        return pd.DataFrame()

nav_df = fetch_nav_history(scheme_code, start_date, end_date)

if nav_df.empty:
    st.warning("No NAV history data available for the selected date range.")
else:
    col_table, col_chart = st.columns([1, 2])

    with col_table:
        st.markdown("**NAV Table**")
        display_df = nav_df.copy()
        display_df["Date"] = display_df["Date"].dt.date
        display_df["NAV"] = display_df["NAV"].round(4)
        st.dataframe(display_df, use_container_width=True, height=400)

    with col_chart:
        st.markdown("**NAV Trend**")
        fig = px.line(
            nav_df,
            x="Date",
            y="NAV",
            title="NAV Movement Over Time",
            labels={"NAV": "NAV (₹)", "Date": "Date"},
            template="plotly_white"
        )
        fig.update_traces(line_color="#4F8BF9", line_width=2)
        fig.update_layout(
            hovermode="x unified",
            margin=dict(l=10, r=10, t=40, b=10),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()



################################




# =========================
# 📈 CURRENT VALUE TREND
# =========================
st.subheader("📈 Portfolio Value Trend")

if daily_df.empty:
    st.info("No data available to plot")
else:
    chart_df = daily_df.copy()

    # Ensure sorted oldest → latest for proper graph
    chart_df = chart_df.sort_values("date")

    fig = px.line(
        chart_df,
        x="date",
        y="current_value",
        markers=True,
        title="Portfolio Value Over Time"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Current Value (₹)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
