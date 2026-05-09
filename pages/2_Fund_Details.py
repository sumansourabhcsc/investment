import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import pandas as pd
import requests

from datetime import date, timedelta

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.xirr_helper import compute_fund_xirr


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Fund Details",
    layout="wide"
)

# =========================================================
# COLORS
# =========================================================
PRIMARY = "#8B5CF6"
SUCCESS = "#10B981"
INFO = "#06B6D4"
WARNING = "#F59E0B"
DANGER = "#EF4444"

BG_MAIN = "#0F172A"
CARD_BG = "#111827"
BORDER = "#1E293B"

TEXT = "#F8FAFC"
MUTED = "#94A3B8"

# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown(f"""
<style>

html, body, [class*="css"]  {{
    font-family: 'Segoe UI', sans-serif;
}}

.main {{
    background-color: {BG_MAIN};
    color: white;
}}

.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
}}

h1, h2, h3 {{
    color: {TEXT};
}}

section[data-testid="stSidebar"] {{
    background-color: {CARD_BG};
}}

[data-testid="stDataFrame"] {{
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid {BORDER};
}

.stSelectbox label,
.stDateInput label {{
    color: #CBD5E1 !important;
    font-weight: 600;
}}

hr {{
    margin-top: 2rem !important;
    margin-bottom: 2rem !important;
}}

::-webkit-scrollbar {{
    width: 10px;
}}

::-webkit-scrollbar-track {{
    background: {CARD_BG};
}}

::-webkit-scrollbar-thumb {{
    background: #374151;
    border-radius: 10px;
}}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.markdown("""
<h1 style='text-align:center; margin-bottom:30px;'>
📁 Mutual Fund Details Dashboard
</h1>
""", unsafe_allow_html=True)

# =========================================================
# METRIC CARD
# =========================================================
def metric_card(col, title, value, color):

    card_html = f"""
    <div style="
        background:{CARD_BG};
        padding:20px;
        border-radius:18px;
        border:1px solid {BORDER};
        box-shadow:0 4px 18px rgba(0,0,0,0.25);
        text-align:center;
        height:125px;
    ">

        <div style="
            color:{MUTED};
            font-size:14px;
            font-weight:600;
            margin-bottom:14px;
        ">
            {title}
        </div>

        <div style="
            color:{color};
            font-size:28px;
            font-weight:800;
            line-height:1.2;
        ">
            {value}
        </div>

    </div>
    """

    with col:
        components.html(card_html, height=145)

# =========================================================
# LOAD NAV DATA
# =========================================================
nav_master_df = load_nav()

# =========================================================
# FUND SELECTION
# =========================================================
fund_options = list(mutual_funds.keys())

selected_fund = st.selectbox(
    "Select Fund",
    fund_options
)

scheme_code = mutual_funds[selected_fund]["code"]
folder = mutual_funds[selected_fund]["folder"]

# =========================================================
# LOAD FUND DATA
# =========================================================
fund_df = load_fund(folder)

# =========================================================
# LOAD DAILY SNAPSHOT
# =========================================================
daily_path = f"mutualfund/{folder}/daily_{scheme_code}.csv"

try:

    daily_df = pd.read_csv(daily_path)

    daily_df["Date"] = pd.to_datetime(
        daily_df["date"],
        format="%d-%m-%Y"
    )

    daily_df = daily_df.sort_values(
        "Date",
        ascending=False
    ).reset_index(drop=True)

except FileNotFoundError:

    daily_df = pd.DataFrame()

# =========================================================
# GET LATEST NAV
# =========================================================
match = nav_master_df[
    nav_master_df["SchemeCode"] == str(scheme_code)
]

if match.empty:

    st.error("No NAV data found for this fund")
    st.stop()

latest_row = match.sort_values(
    "Date",
    ascending=False
).iloc[0]

latest_nav = float(latest_row["NAV"])
latest_date = latest_row["Date"].date()

# =========================================================
# CALCULATIONS
# =========================================================
total_units = fund_df["Units"].sum()

invested = fund_df["Amount"].sum()

current_value = total_units * latest_nav

profit = current_value - invested

avg_buy_nav = (
    invested / total_units
    if total_units > 0 else 0
)

absolute_return = (
    ((current_value - invested) / invested) * 100
    if invested > 0 else 0
)

fund_xirr = compute_fund_xirr(
    fund_df,
    latest_nav
)

# =========================================================
# NAV BANNER
# =========================================================
st.markdown(
    f"""
    <div style="
        background:{CARD_BG};
        padding:16px 20px;
        border-radius:14px;
        border:1px solid {BORDER};
        color:{TEXT};
        margin-bottom:20px;
        font-size:16px;
        font-weight:600;
    ">
        📅 Latest NAV:
        <span style="color:{SUCCESS};">
            ₹{latest_nav:.2f}
        </span>
        <span style="color:{MUTED};">
            (as of {latest_date})
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# METRIC CARDS
# =========================================================
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

metric_card(
    col1,
    "💰 Invested",
    f"₹ {invested:,.0f}",
    PRIMARY
)

metric_card(
    col2,
    "📈 Current Value",
    f"₹ {current_value:,.0f}",
    SUCCESS
)

metric_card(
    col3,
    "📊 Total P&L",
    f"₹ {profit:,.0f}",
    INFO if profit >= 0 else DANGER
)

metric_card(
    col4,
    "📉 Absolute Return",
    f"{absolute_return:.2f}%",
    WARNING
)

metric_card(
    col5,
    "🧮 Avg Buy NAV",
    f"₹ {avg_buy_nav:.2f}",
    "#38BDF8"
)

metric_card(
    col6,
    "📦 Total Units",
    f"{total_units:,.2f}",
    "#14B8A6"
)

metric_card(
    col7,
    "📌 XIRR",
    f"{fund_xirr*100:.2f}%",
    "#F43F5E"
)

# =========================================================
# TABLES SECTION
# =========================================================
st.divider()

col1, col2 = st.columns(2)

# =========================================================
# SIP HISTORY
# =========================================================
with col1:

    st.markdown("""
    <h3 style='margin-bottom:10px;'>
    📋 SIP History
    </h3>
    """, unsafe_allow_html=True)

    fund_df_sorted = fund_df.sort_values(
        by="Date",
        ascending=False
    ).reset_index(drop=True)

    fund_df_sorted["Date"] = (
        fund_df_sorted["Date"].dt.date
    )

    st.dataframe(
        fund_df_sorted,
        use_container_width=True,
        height=420
    )

# =========================================================
# DAILY NAV MOVEMENT
# =========================================================
with col2:

    st.markdown("""
    <h3 style='margin-bottom:10px;'>
    📅 Daily NAV Movement
    </h3>
    """, unsafe_allow_html=True)

    if daily_df.empty:

        st.info(
            "No daily snapshot data available"
        )

    else:

        df_display = daily_df.copy()

        df_display["Date"] = (
            df_display["Date"].dt.date
        )

        if "NAV" in df_display.columns:

            df_display["Daily Change %"] = (
                df_display["NAV"].pct_change(-1) * 100
            )

        st.dataframe(
            df_display,
            use_container_width=True,
            height=420
        )

# =========================================================
# NAV HISTORY
# =========================================================
st.divider()

st.markdown("""
<h2 style='margin-bottom:20px;'>
📈 NAV History
</h2>
""", unsafe_allow_html=True)

# =========================================================
# DATE RANGE
# =========================================================
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

# =========================================================
# FETCH NAV HISTORY
# =========================================================
@st.cache_data(ttl=3600)
def fetch_nav_history(fund_code):

    url = f"https://api.mfapi.in/mf/{fund_code}"

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "data" in data and data["data"]:

            df = pd.DataFrame(data["data"])

            df["date"] = pd.to_datetime(
                df["date"],
                format="%d-%m-%Y"
            )

            df["nav"] = pd.to_numeric(
                df["nav"],
                errors="coerce"
            )

            df = df.sort_values(
                "date",
                ascending=True
            ).reset_index(drop=True)

            df.rename(columns={
                "date": "Date",
                "nav": "NAV"
            }, inplace=True)

            return df

        return pd.DataFrame()

    except Exception as e:

        st.error(f"Failed to fetch NAV history: {e}")

        return pd.DataFrame()

# =========================================================
# LOAD NAV HISTORY
# =========================================================
nav_df_full = fetch_nav_history(
    scheme_code
)

if not nav_df_full.empty:

    nav_df = nav_df_full[
        (nav_df_full["Date"].dt.date >= start_date)
        &
        (nav_df_full["Date"].dt.date <= end_date)
    ].reset_index(drop=True)

else:

    nav_df = pd.DataFrame()

# =========================================================
# NAV DISPLAY
# =========================================================
if nav_df.empty:

    st.warning(
        "No NAV history available for selected range."
    )

else:

    max_row = nav_df.loc[
        nav_df["NAV"].idxmax()
    ]

    min_row = nav_df.loc[
        nav_df["NAV"].idxmin()
    ]

    col1, col2 = st.columns(2)

    metric_card(
        col1,
        "🔼 Highest NAV",
        f"₹ {max_row['NAV']:.2f}",
        SUCCESS
    )

    metric_card(
        col2,
        "🔽 Lowest NAV",
        f"₹ {min_row['NAV']:.2f}",
        DANGER
    )

    st.divider()

    col_table, col_chart = st.columns([1, 2])

    # =====================================================
    # NAV TABLE
    # =====================================================
    with col_table:

        st.markdown("""
        <h3 style='margin-bottom:10px;'>
        📋 NAV Table
        </h3>
        """, unsafe_allow_html=True)

        display_df = nav_df.copy()

        display_df = display_df.sort_values(
            "Date",
            ascending=False
        ).reset_index(drop=True)

        display_df["Date"] = (
            display_df["Date"].dt.date
        )

        display_df["NAV"] = (
            display_df["NAV"].round(4)
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            height=450
        )

    # =====================================================
    # NAV CHART
    # =====================================================
    with col_chart:

        st.markdown("""
        <h3 style='margin-bottom:10px;'>
        📈 NAV Trend
        </h3>
        """, unsafe_allow_html=True)

        fig = px.line(
            nav_df,
            x="Date",
            y="NAV",
            markers=True
        )

        fig.update_layout(
            paper_bgcolor=BG_MAIN,
            plot_bgcolor=CARD_BG,
            font_color="white",
            hovermode="x unified",
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            height=450
        )

        fig.update_traces(
            line_color="#8B5CF6",
            line_width=3
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================================================
# PORTFOLIO VALUE TREND
# =========================================================
st.divider()

st.markdown("""
<h2 style='margin-bottom:20px;'>
📈 Portfolio Value Trend
</h2>
""", unsafe_allow_html=True)

if daily_df.empty:

    st.info(
        "No data available to plot"
    )

else:

    chart_df = daily_df.copy()

    chart_df["date"] = pd.to_datetime(
        chart_df["date"],
        format="%d-%m-%Y"
    )

    chart_df = chart_df.sort_values(
        "date"
    )

    fig = px.line(
        chart_df,
        x="date",
        y="current_value",
        markers=True
    )

    fig.update_layout(
        paper_bgcolor=BG_MAIN,
        plot_bgcolor=CARD_BG,
        font_color="white",
        xaxis_title="Date",
        yaxis_title="Current Value (₹)",
        hovermode="x unified",
        height=500
    )

    fig.update_traces(
        line_color="#06B6D4",
        line_width=3
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
