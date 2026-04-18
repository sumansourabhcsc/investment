import streamlit as st
import plotly.express as px
from utils.data_loader import load_fund, load_nav

st.title("📁 Fund Details")

funds = load_nav()["SchemeName"].unique()

selected_fund = st.selectbox("Select Fund", funds)

fund_df = load_fund(selected_fund)
nav_df = load_nav()

latest_nav = nav_df[nav_df["SchemeName"] == selected_fund]["NAV"].values

st.write("### SIP History")
st.dataframe(fund_df)

if len(latest_nav) > 0:
    st.write("Latest NAV:", latest_nav[0])

fig = px.line(fund_df, x="Date", y="Amount", title="Investment Over Time")
st.plotly_chart(fig)
