
import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect


def get_kite():
    api_key = st.secrets["ZERODHA_API_KEY"]

    kite = KiteConnect(api_key=api_key)

    access_token = st.session_state.get("zerodha_access_token")

    if access_token:
        kite.set_access_token(access_token)
        return kite

    return None


def login_zerodha():
    api_key = st.secrets["ZERODHA_API_KEY"]
    kite = KiteConnect(api_key=api_key)

    return kite.login_url()


def authenticate(request_token):
    api_key = st.secrets["ZERODHA_API_KEY"]
    api_secret = st.secrets["ZERODHA_API_SECRET"]

    kite = KiteConnect(api_key=api_key)

    data = kite.generate_session(
        request_token,
        api_secret=api_secret
    )

    st.session_state["zerodha_access_token"] = data["access_token"]

    return data


def get_holdings(kite):
    holdings = kite.holdings()
    return pd.DataFrame(holdings)


def get_positions(kite):
    positions = kite.positions()
    return pd.DataFrame(positions["net"])


def get_profile(kite):
    return kite.profile()
