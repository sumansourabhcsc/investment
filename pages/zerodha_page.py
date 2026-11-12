
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    color: #e8e2d5;
}

/* ── Base: deep midnight navy (replaces image background) ── */
.stApp {
    background-color: #080b0f;
    background-image:
        radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(0, 245, 212, 0.07) 0%, transparent 65%),
        radial-gradient(ellipse 60% 80% at 85% 75%,  rgba(0, 180, 245, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 50% 100%, rgba(0, 245, 212, 0.04) 0%, transparent 55%),
        radial-gradient(ellipse 100% 100% at 50% 0%,  rgba(8, 11, 15, 0.9)  0%, #080b0f 70%);
    background-size: cover;
    background-attachment: fixed;
    position: relative;
    min-height: 100vh;
}

/* ── Layer 1: animated teal orb pulse ── */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 55% at 8%  18%,  rgba(0, 245, 212, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 55% 70% at 88% 72%,  rgba(0, 140, 255, 0.05) 0%, transparent 55%),
        radial-gradient(ellipse 45% 35% at 52% 98%,  rgba(0, 245, 212, 0.04) 0%, transparent 50%);
    z-index: 0;
    pointer-events: none;
    animation: taurus-pulse 8s ease-in-out infinite;
}

/* ── Layer 2: dot-grid constellation ── */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(0,245,212,0.16) 1px, transparent 1px);
    background-size: 38px 38px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.45;
}

@keyframes taurus-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.55; }
}

.stApp > * { position: relative; z-index: 1; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
    border-right: 1px solid rgba(0, 245, 212, 0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(12px);
}

#MainMenu, footer { visibility: hidden; }

[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: flex !important;
}

[data-testid="stSidebar"] {
    visibility: visible !important;
    display: block !important;
}

[data-testid="stSidebarNav"] {
    display: block !important;
}



.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

.stButton > button[kind="primary"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, rgba(0,245,212,0.12), rgba(0,201,255,0.08)) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0,245,212,0.4) !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.25s !important;
    box-shadow: 0 0 20px rgba(0,245,212,0.07) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(0,245,212,0.22), rgba(0,201,255,0.15)) !important;
    border-color: rgba(0,245,212,0.7) !important;
    box-shadow: 0 0 30px rgba(0,245,212,0.18), 0 0 60px rgba(0,245,212,0.06) !important;
    transform: translateY(-1px) !important;
}

.stSuccess > div, .stError > div, .stInfo > div, .stSpinner > div {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

hr { border-color: rgba(0, 245, 212, 0.1) !important; }

.stInfo {
    background: rgba(0,201,255,0.06) !important;
    border-left-color: #00c9ff !important;
}

.stSuccess {
    background: rgba(0,245,212,0.07) !important;
    border-left-color: #00f5d4 !important;
}

.stError { background: rgba(255,70,70,0.07) !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.2); border-radius: 4px; }

/* ── Force readable text regardless of Streamlit theme ── */
h1, h2, h3, p, label,
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #e8e2d5 !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stAlert"] {
    background: rgba(0,245,212,0.07) !important;
    color: #e8e2d5 !important;
}


</style>
""", unsafe_allow_html=True)

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

      

    st.markdown(
        f'<a href="{login_url}" target="_self" '
        'style="display:inline-block;padding:0.6rem 1.6rem;border:1px solid rgba(0,245,212,0.4);'
        'border-radius:8px;color:#00f5d4;text-decoration:none;font-family:Syne,sans-serif;'
        'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">Login with Zerodha</a>',
        unsafe_allow_html=True,
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
