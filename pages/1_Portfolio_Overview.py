import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

from plotly.subplots import make_subplots

from config import mutual_funds
from utils.data_loader import load_fund, load_nav
from utils.calculations import calculate_invested_amount, calculate_current_value
from utils.load_funds import load_all_funds
from utils.xirr_overall import compute_overall_xirr
from utils.xirr_helper import compute_fund_xirr

st.divider()
# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Portfolio Dashboard | Taurus",
    layout="wide",
    page_icon="📊"
)

SUCCESS = "#1D9E75"
DANGER  = "#E24B4A"
BG_MAIN = "#0A0F1E"
CARD_BG = "#0F1629"

PALETTE = ["#7C3AED","#1D9E75","#06B6D4","#EF9F27","#E24B4A",
           "#D4537E","#4F8BF9","#00f5d4","#F59E0B","#8B5CF6"]


# =========================================================
# GOOGLE FONTS + MINIMAL SAFE CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 3rem !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0A0F1E; }
::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 6px; }
section[data-testid="stSidebar"] { background: #0D1526 !important; border-right: 1px solid rgba(255,255,255,0.05); }
[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden !important; border: 1px solid rgba(255,255,255,0.07) !important; }
.stSelectbox label, .stDateInput label { color: rgba(255,255,255,0.45) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500 !important; }
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }
@keyframes livepulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS — 100% inlined styles, no CSS class dependency
# =========================================================

def kpi_card(icon, label, value, value_color, sub, bottom_color):
    """KPI card with every style attribute inlined — renders correctly in st.markdown."""
    return f"""
    <div style="background:#0F1629; border:1px solid rgba(255,255,255,0.08);
        border-radius:16px; padding:20px 20px 16px; position:relative;
        overflow:hidden; box-sizing:border-box; height:100%;">
        <div style="position:absolute; bottom:0; left:0; right:0; height:3px;
            background:{bottom_color}; border-radius:0 0 16px 16px;"></div>
        <div style="font-size:18px; margin-bottom:10px; line-height:1;">{icon}</div>
        <div style="font-size:11px; color:rgba(255,255,255,0.4); text-transform:uppercase;
            letter-spacing:0.08em; font-weight:500; margin-bottom:8px;
            font-family:'Outfit',sans-serif;">{label}</div>
        <div style="font-size:26px; font-weight:700; font-family:'DM Mono',monospace;
            line-height:1.1; color:{value_color};">{value}</div>
        <div style="font-size:11px; color:rgba(255,255,255,0.3); margin-top:5px;
            font-family:'DM Mono',monospace;">{sub}</div>
    </div>"""


def sec_header(icon, title):
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:1rem; margin-top:0.5rem;">
        <div style="width:32px; height:32px; border-radius:8px; background:#1E293B;
            display:flex; align-items:center; justify-content:center;
            font-size:15px; flex-shrink:0;">{icon}</div>
        <div style="font-size:16px; font-weight:600; color:#F1F5F9;
            font-family:'Outfit',sans-serif;">{title}</div>
        <div style="flex:1; height:1px; background:rgba(255,255,255,0.06);"></div>
    </div>""", unsafe_allow_html=True)


def change_summary_box(total_change):
    sign  = "+" if total_change >= 0 else ""
    color = SUCCESS if total_change >= 0 else DANGER
    icon  = "📈" if total_change >= 0 else "📉"
    st.markdown(f"""
    <div style="margin-top:14px; background:#0F1629; padding:18px 24px;
        border-radius:14px; border:1px solid rgba(255,255,255,0.07);
        display:flex; align-items:center; justify-content:space-between;
        flex-wrap:wrap; gap:10px;">
        <div style="font-size:13px; color:rgba(255,255,255,0.45); font-weight:500;
            font-family:'Outfit',sans-serif;">{icon} Total Daily Change Across All Funds</div>
        <div style="font-size:24px; font-weight:700; font-family:'DM Mono',monospace;
            color:{color};">{sign}₹{abs(total_change):,.2f}</div>
    </div>""", unsafe_allow_html=True)


# =========================================================
# PAGE HERO
# =========================================================
st.markdown("""
<div style="display:flex; align-items:center; justify-content:space-between;
    margin-bottom:1.8rem; flex-wrap:wrap; gap:12px;">
    <div>
        <div style="font-size:28px; font-weight:700; color:#F1F5F9;
            letter-spacing:-0.5px; font-family:'Outfit',sans-serif;">
            📊 Portfolio Dashboard
        </div>
        <div style="font-size:13px; color:rgba(255,255,255,0.35); margin-top:4px;
            font-family:'DM Mono',monospace;">
            Taurus · Mutual Fund Tracker · Live NAV
        </div>
    </div>
    <div style="display:inline-flex; align-items:center; gap:7px;
        background:rgba(29,158,117,0.12); border:1px solid rgba(29,158,117,0.3);
        border-radius:20px; padding:6px 14px; font-size:12px; font-weight:500;
        color:#1D9E75; font-family:'Outfit',sans-serif;">
        <div style="width:7px; height:7px; border-radius:50%; background:#1D9E75;
            animation:livepulse 2s ease-in-out infinite;"></div>
        Live NAV
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# LOAD NAV + PROCESS FUNDS
# =========================================================
nav_df         = load_nav()
summary        = []
total_invested = 0
total_current  = 0

for fund_name, meta in mutual_funds.items():
    try:
        code      = meta["code"]
        folder    = meta["folder"]
        fund_df   = load_fund(folder)
        match     = nav_df[nav_df["SchemeCode"] == str(code)]
        if match.empty:
            st.warning(f"No NAV found for {fund_name} ({code})")
            continue
        latest_row  = match.sort_values("Date", ascending=False).iloc[0]
        latest_nav  = float(latest_row["NAV"])
        latest_date = latest_row["Date"].date()
        invested    = calculate_invested_amount(fund_df)
        current     = calculate_current_value(fund_df, latest_nav)
        fund_xirr   = compute_fund_xirr(fund_df, latest_nav)
        total_invested += invested
        total_current  += current
        summary.append([
            fund_name, code, invested, current,
            current - invested, latest_nav, latest_date,
            f"{fund_xirr * 100:.2f}%"
        ])
    except Exception as e:
        st.error(f"{fund_name} error: {e}")


# =========================================================
# COMPUTE OVERALL METRICS
# =========================================================
total_pnl           = total_current - total_invested
absolute_return_pct = ((total_pnl / total_invested) * 100) if total_invested > 0 else 0
all_funds_df        = load_all_funds()
overall_xirr        = compute_overall_xirr(all_funds_df)
overall_xirr_pct    = overall_xirr * 100

pnl_color  = SUCCESS if total_pnl >= 0 else DANGER
ret_color  = SUCCESS if absolute_return_pct >= 0 else DANGER
xirr_color = SUCCESS if overall_xirr_pct >= 0 else DANGER
pnl_sign   = "+" if total_pnl >= 0 else ""
ret_sign   = "+" if absolute_return_pct >= 0 else ""
xirr_sign  = "+" if overall_xirr_pct >= 0 else ""
xirr_bar   = SUCCESS if overall_xirr_pct >= 0 else DANGER


# =========================================================
# KPI CARDS — each rendered in its own st.column
# Using st.markdown per column — this is the CORRECT Streamlit approach
# =========================================================
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(kpi_card(
        "💰", "Total Invested",
        f"₹{total_invested:,.0f}",
        "#F1F5F9",
        f"across {len(summary)} funds",
        "#7C3AED"
    ), unsafe_allow_html=True)

with c2:
    st.markdown(kpi_card(
        "📈", "Current Value",
        f"₹{total_current:,.0f}",
        SUCCESS, "live NAV", SUCCESS
    ), unsafe_allow_html=True)

with c3:
    st.markdown(kpi_card(
        "📊", "Total P&L",
        f"{pnl_sign}₹{abs(total_pnl):,.0f}",
        pnl_color, "unrealised gain/loss", "#06B6D4"
    ), unsafe_allow_html=True)

with c4:
    st.markdown(kpi_card(
        "📉", "Absolute Return",
        f"{ret_sign}{absolute_return_pct:.2f}%",
        ret_color, "since first investment", "#EF9F27"
    ), unsafe_allow_html=True)

with c5:
    st.markdown(kpi_card(
        "📌", "Overall XIRR",
        f"{xirr_sign}{overall_xirr_pct:.2f}%",
        xirr_color, "annualised return", xirr_bar
    ), unsafe_allow_html=True)

st.divider()


# =========================================================
# FUND TABLE + DONUT CHART
# =========================================================
sec_header("📋", "Fund Details")

df = pd.DataFrame(summary, columns=[
    "Fund","SchemeCode","Invested","Current",
    "P&L","Latest NAV","NAV Date","XIRR"
])

col_tbl, col_donut = st.columns([7, 3])

with col_tbl:
    display_df = df.copy()
    display_df["Invested"]   = display_df["Invested"].map(lambda x: f"₹{x:,.0f}")
    display_df["Current"]    = display_df["Current"].map(lambda x: f"₹{x:,.0f}")
    display_df["P&L"]        = display_df["P&L"].map(lambda x: f"₹{x:,.0f}")
    display_df["Latest NAV"] = display_df["Latest NAV"].map(lambda x: f"{x:.2f}")
    st.dataframe(
        display_df,
        use_container_width=True,
        height=min((len(display_df) + 1) * 45, 520)
    )

with col_donut:
    fig_donut = go.Figure(go.Pie(
        labels=df["Fund"], values=df["Current"], hole=0.65,
        marker=dict(colors=PALETTE[:len(df)], line=dict(color="#0A0F1E", width=3)),
        textinfo="percent",
        textfont=dict(size=12, family="DM Mono"),
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Outfit"), showlegend=True,
        legend=dict(font=dict(size=11, color="rgba(255,255,255,0.6)"),
                    bgcolor="rgba(0,0,0,0)", x=0, y=-0.15, orientation="h"),
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(
            text=f"<b>₹{total_current/1e5:.1f}L</b>",
            x=0.5, y=0.5,
            font=dict(size=18, color="white", family="DM Mono"),
            showarrow=False
        )]
    )
    st.plotly_chart(fig_donut, use_container_width=True)


# =========================================================
# TREEMAP
# =========================================================
sec_header("🌳", "Portfolio Allocation")

fig_tree = px.treemap(
    df, path=["Fund"], values="Current", color="P&L",
    color_continuous_scale=[[0,"#E24B4A"],[0.5,"#1E293B"],[1,"#1D9E75"]],
    hover_data={"Invested": True, "XIRR": True}
)
fig_tree.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white", family="Outfit"),
    margin=dict(t=10, l=10, r=10, b=10), coloraxis_showscale=False
)
fig_tree.update_traces(
    textinfo="label+percent entry",
    textfont=dict(size=13, family="Outfit"),
    marker=dict(line=dict(width=2, color="#0A0F1E"))
)
st.plotly_chart(fig_tree, use_container_width=True)

st.divider()


# =========================================================
# DAILY PORTFOLIO SUMMARY
# =========================================================
sec_header("📊", "Daily Portfolio Summary")

daily_path = "data/portfolio_daily.csv"
daily_df   = pd.read_csv(daily_path)
daily_df["Date"] = pd.to_datetime(daily_df["Date"], format="%d-%m-%Y")
daily_df = daily_df.sort_values("Date", ascending=False)

display_daily = daily_df.copy()
display_daily["Date"] = display_daily["Date"].dt.strftime("%d-%m-%Y")
st.dataframe(display_daily, use_container_width=True)


# =========================================================
# PERFORMANCE CHART
# =========================================================
sec_header("📈", "Portfolio Performance")

chart_df = daily_df.sort_values("Date")
chart_df["OneDayChangePct_val"] = (
    chart_df["OneDayChangePct"].str.replace("%","",regex=False).astype(float)
)
bar_colors = [SUCCESS if x >= 0 else DANGER for x in chart_df["OneDayChange"]]

fig_perf = make_subplots(specs=[[{"secondary_y": True}]])
fig_perf.add_trace(go.Bar(
    x=chart_df["Date"], y=chart_df["OneDayChange"],
    name="Daily Change (₹)", marker_color=bar_colors, marker_line_width=0, opacity=0.75,
    hovertemplate="<b>%{x|%d %b %Y}</b><br>Daily Change: ₹%{y:,.2f}<extra></extra>"
), secondary_y=False)
fig_perf.add_trace(go.Scatter(
    x=chart_df["Date"], y=chart_df["TotalValue"],
    name="Total Value (₹)", mode="lines",
    line=dict(color="#4F8BF9", width=2.5),
    fill="tozeroy", fillcolor="rgba(79,139,249,0.06)",
    hovertemplate="<b>%{x|%d %b %Y}</b><br>Value: ₹%{y:,.0f}<extra></extra>"
), secondary_y=True)
fig_perf.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
    font=dict(color="rgba(255,255,255,0.6)", family="Outfit"),
    hovermode="x unified", height=460, margin=dict(t=20, b=10, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                font=dict(size=12, color="rgba(255,255,255,0.6)"), bgcolor="rgba(0,0,0,0)"),
    bargap=0.3, xaxis=dict(showgrid=False, zeroline=False),
)
fig_perf.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                      zeroline=False, tickprefix="₹", secondary_y=False)
fig_perf.update_yaxes(showgrid=False, zeroline=False, tickprefix="₹", secondary_y=True)
st.plotly_chart(fig_perf, use_container_width=True)

st.divider()


# =========================================================
# MONTHLY INVESTMENT SUMMARY
# =========================================================
sec_header("📅", "Monthly Investment Summary")

monthly_data = []
month_map    = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

for fund_name, meta in mutual_funds.items():
    try:
        folder   = meta["folder"]
        code     = meta["code"]
        df_month = load_fund(folder)
        df_month["Date"]  = pd.to_datetime(df_month["Date"], errors="coerce")
        df_month          = df_month.dropna(subset=["Date"])
        df_month["Year"]  = df_month["Date"].dt.year
        df_month["Month"] = df_month["Date"].dt.month
        grouped = df_month.groupby(["Year","Month"])["Amount"].sum().reset_index()
        for _, row in grouped.iterrows():
            monthly_data.append([code, fund_name, row["Year"], row["Month"], row["Amount"]])
    except Exception as e:
        st.warning(f"{fund_name} skipped: {e}")

if monthly_data:
    monthly_df    = pd.DataFrame(monthly_data, columns=["Code","Fund","Year","Month","Amount"])
    years         = sorted(monthly_df["Year"].dropna().astype(int).unique())
    selected_year = st.selectbox("Select Year", years, index=len(years)-1)

    year_df  = monthly_df[monthly_df["Year"] == selected_year]
    pivot_df = year_df.pivot_table(
        index=["Code","Fund"], columns="Month",
        values="Amount", aggfunc="sum", fill_value=0
    ).reset_index()
    pivot_df = pivot_df.rename(columns=month_map)
    for m in month_map.values():
        if m not in pivot_df.columns:
            pivot_df[m] = 0

    month_cols        = list(month_map.values())
    pivot_df          = pivot_df[["Code","Fund"] + month_cols]
    pivot_df["Total"] = pivot_df[month_cols].sum(axis=1)
    total_row = ["","TOTAL"] + [pivot_df[m].sum() for m in month_cols] + [pivot_df["Total"].sum()]
    final_df  = pd.concat(
        [pivot_df, pd.DataFrame([total_row], columns=pivot_df.columns)],
        ignore_index=True
    )
    for col in final_df.select_dtypes(include="number").columns:
        final_df[col] = final_df[col].map(lambda x: f"{x:,.0f}")
    st.dataframe(final_df, use_container_width=True)

    bar_data = year_df.copy()
    bar_data["Month_Name"] = bar_data["Month"].map(month_map)
    fig_month = px.bar(
        bar_data, x="Month_Name", y="Amount", color="Fund",
        barmode="stack", color_discrete_sequence=PALETTE,
        labels={"Month_Name":"Month","Amount":"Amount (₹)"}
    )
    fig_month.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,22,41,0.6)",
        font=dict(color="rgba(255,255,255,0.6)", family="Outfit"),
        height=340, margin=dict(t=20, b=10, l=10, r=10),
        legend=dict(font=dict(size=11, color="rgba(255,255,255,0.55)"),
                    bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.02, xanchor="left", x=0),
        bargap=0.25,
        xaxis=dict(showgrid=False, zeroline=False, categoryorder="array",
                   categoryarray=list(month_map.values())),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                   zeroline=False, tickprefix="₹"),
    )
    st.plotly_chart(fig_month, use_container_width=True)

st.divider()


# =========================================================
# DAILY CHANGE ACROSS FUNDS
# =========================================================
sec_header("💹", "Daily Change Across Funds")

latest_nav_date  = nav_df["Date"].max().date()
selected_date    = st.date_input("Select Date", value=latest_nav_date)
selected_date_dt = pd.to_datetime(selected_date)

daily_rows = []

for fund_name, meta in mutual_funds.items():
    folder    = meta["folder"]
    code      = meta["code"]
    file_path = f"mutualfund/{folder}/daily_{code}.csv"
    if not os.path.exists(file_path):
        continue
    df_daily         = pd.read_csv(file_path)
    df_daily.columns = df_daily.columns.str.strip()
    df_daily["date"] = pd.to_datetime(df_daily["date"], format="%d-%m-%Y", errors="coerce")
    df_daily         = df_daily.dropna(subset=["date"]).sort_values("date")

    today_rows = df_daily[df_daily["date"] == selected_date_dt]
    if today_rows.empty:
        continue
    row_today  = today_rows.iloc[-1]
    prev_rows  = df_daily[df_daily["date"] < selected_date_dt]
    if prev_rows.empty:
        continue
    row_prev       = prev_rows.iloc[-1]
    change_in_val  = float(row_today["absolute_gain_loss"]) - float(row_prev["absolute_gain_loss"])
    nav_today      = float(row_today["nav"])
    nav_prev       = float(row_prev["nav"])
    pct_change_nav = ((nav_today - nav_prev) / nav_prev * 100) if nav_prev != 0 else 0
    indicator      = "🟢 ↑" if nav_today > nav_prev else "🔴 ↓"

    daily_rows.append([
        row_today["date"].strftime("%d-%m-%Y"),
        fund_name, code,
        round(change_in_val, 2),
        f"{pct_change_nav:.2f}%",
        indicator
    ])

df_daily_change = pd.DataFrame(daily_rows, columns=[
    "Date","Fund Name","Fund Code",
    "Change in Value","% Change in NAV","Indicator"
])
st.dataframe(df_daily_change, use_container_width=True)

total_change = df_daily_change["Change in Value"].sum() if not df_daily_change.empty else 0
change_summary_box(total_change)
