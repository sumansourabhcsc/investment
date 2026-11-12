
import streamlit as st
import pandas as pd

from zerodha import (
    get_kite,
    login_zerodha,
    authenticate,
    get_holdings,
    get_positions,
    get_profile
)


import streamlit as st
from utils.sidebar_style import render_sidebar

st.set_page_config(page_title="Taurus: Zerodha", page_icon="🐂", layout="wide")
render_sidebar("zerodha")

st.title("Zerodha Investment Tracker")

# Step 1: Handle Zerodha redirect
request_token = st.query_params.get("request_token")

if request_token and not st.session_state.get(
    "zerodha_access_token"
):
    try:
        user = authenticate(request_token)
        st.query_params.clear()
        st.success("Zerodha connected successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Authentication failed: {e}")

# Step 2: Login
kite = get_kite()

if kite is None:
    st.info("Please connect your Zerodha account.")

    login_url = login_zerodha()

    st.link_button(
        "Login with Zerodha",
        login_url
    )

    st.stop()

# Step 3: Fetch portfolio
try:
    profile = get_profile(kite)
    holdings_df = get_holdings(kite)
    positions_df = get_positions(kite)

    st.success(
        f"Connected: {profile['user_name']}"
    )

    st.subheader("Portfolio Holdings")

    if not holdings_df.empty:

        invested = (
            holdings_df["quantity"] *
            holdings_df["average_price"]
        ).sum()

        current = (
            holdings_df["quantity"] *
            holdings_df["last_price"]
        ).sum()

        pnl = current - invested

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Invested Value",
            f"₹{invested:,.2f}"
        )

        col2.metric(
            "Current Value",
            f"₹{current:,.2f}"
        )

        col3.metric(
            "Profit / Loss",
            f"₹{pnl:,.2f}",
            f"{pnl / invested * 100:.2f}%"
            if invested else None
        )

        st.dataframe(
            holdings_df,
            use_container_width=True
        )

    else:
        st.info("No holdings found.")

    st.subheader("Open & Net Positions")
    st.dataframe(
        positions_df,
        use_container_width=True
    )

except Exception as e:
    st.error(f"Unable to fetch Zerodha data: {e}")
    st.warning("Your access token may have expired. Please log in again.")
    if st.button("Disconnect"):
        st.session_state.pop("zerodha_access_token", None)
        st.rerun()
