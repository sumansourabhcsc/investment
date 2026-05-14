"""
utils/fund_prediction.py
─────────────────────────────────────────────
Drop this file into the `utils/` folder of your investment repo.

Then in your tools page, import and call:

    from utils.fund_prediction import show_fund_prediction

    tab1, tab2, ..., tabN = st.tabs([..., "📈 Fund Prediction"])
    with tabN:
        show_fund_prediction()

All dependencies are already in requirements.txt:
    streamlit, pandas, numpy, plotly, requests
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go


# ── Fund list from config.py ──────────────────────────────────────────────────
def _get_portfolio_funds():
    try:
        from config import mutual_funds
        return {name: info["code"] for name, info in mutual_funds.items()}
    except ImportError:
        return {}


# ── API helpers ───────────────────────────────────────────────────────────────

def _fetch_nav_history(fund_code: str) -> pd.DataFrame:
    """Fetch ~2 years of NAV history from mfapi.in."""
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=730)

    url = (
        f"https://api.mfapi.in/mf/{fund_code}"
        f"?startDate={start_date.strftime('%d-%m-%Y')}"
        f"&endDate={end_date.strftime('%d-%m-%Y')}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        st.error(f"❌ Could not fetch data for fund code `{fund_code}`: {exc}")
        return pd.DataFrame()

    if "data" not in data or not data["data"]:
        st.error(f"❌ No NAV data returned for fund code `{fund_code}`. Please verify the code.")
        return pd.DataFrame()

    df = pd.DataFrame(data["data"])
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna().sort_values("date").reset_index(drop=True)
    return df


# ── Forecasting ───────────────────────────────────────────────────────────────

def _linear_trend_forecast(df: pd.DataFrame, horizon: int = 90):
    """Log-linear OLS trend projected forward `horizon` calendar days."""
    df = df.copy()
    df["t"] = (df["date"] - df["date"].iloc[0]).dt.days
    log_nav  = np.log(df["nav"].values)
    t_vals   = df["t"].values.astype(float)

    A = np.vstack([t_vals, np.ones(len(t_vals))]).T
    slope, intercept = np.linalg.lstsq(A, log_nav, rcond=None)[0]

    fitted    = slope * t_vals + intercept
    sigma     = (log_nav - fitted).std()

    last_date = df["date"].iloc[-1]
    last_t    = df["t"].iloc[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, horizon + 1)]
    future_t     = np.array([last_t + i for i in range(1, horizon + 1)], dtype=float)

    pred_log  = slope * future_t + intercept
    forecast_df = pd.DataFrame({
        "date":      future_dates,
        "nav_pred":  np.exp(pred_log),
        "upper_95":  np.exp(pred_log + 1.96 * sigma),
        "lower_95":  np.exp(pred_log - 1.96 * sigma),
    })
    return forecast_df, slope, sigma


def _compute_metrics(df: pd.DataFrame, forecast_df: pd.DataFrame) -> dict:
    current_nav = df["nav"].iloc[-1]
    pred_90     = forecast_df["nav_pred"].iloc[-1]
    change_pct  = (pred_90 - current_nav) / current_nav * 100

    one_yr = df[df["date"] >= df["date"].iloc[-1] - timedelta(days=365)]
    hist_return = (
        (current_nav - one_yr["nav"].iloc[0]) / one_yr["nav"].iloc[0] * 100
        if len(one_yr) > 1 else None
    )
    ann_vol = df["nav"].pct_change().dropna().std() * np.sqrt(252) * 100

    return {
        "current_nav": current_nav,
        "pred_nav_90": pred_90,
        "change_pct":  change_pct,
        "hist_return": hist_return,
        "ann_vol":     ann_vol,
    }


# ── Chart ─────────────────────────────────────────────────────────────────────

def _build_chart(df: pd.DataFrame, forecast_df: pd.DataFrame, fund_name: str) -> go.Figure:
    hist = df[df["date"] >= df["date"].iloc[-1] - timedelta(days=180)].copy()

    fig = go.Figure()

    # Confidence band
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df["date"], forecast_df["date"][::-1]]),
        y=pd.concat([forecast_df["upper_95"], forecast_df["lower_95"][::-1]]),
        fill="toself",
        fillcolor="rgba(255,165,0,0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip",
        name="95% Confidence Band",
    ))

    # Historical NAV
    fig.add_trace(go.Scatter(
        x=hist["date"], y=hist["nav"],
        mode="lines", name="Historical NAV",
        line=dict(color="#00f5d4", width=2),
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df["date"], y=forecast_df["nav_pred"],
        mode="lines", name="90-Day Forecast",
        line=dict(color="#FFA500", width=2, dash="dash"),
    ))

    fig.add_vline(
        x=df["date"].iloc[-1].timestamp() * 1000,
        line_width=1, line_dash="dot", line_color="rgba(255,255,255,0.35)",
        annotation_text="Today", annotation_position="top left",
        annotation_font_color="rgba(255,255,255,0.55)",
    )

    fig.update_layout(
        title=dict(text=f"📈 {fund_name} — 90-Day NAV Forecast", font=dict(color="white")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", title="Date"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", title="NAV (₹)"),
        legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="rgba(255,255,255,0.2)", borderwidth=1),
        hovermode="x unified",
        margin=dict(t=55, b=40, l=60, r=20),
    )
    return fig


# ── Main entry point ──────────────────────────────────────────────────────────

def show_fund_prediction():
    """Render the Fund Prediction tab. Call inside `with tab:` on your tools page."""

    st.markdown("## 📈 Fund NAV Prediction — Next 90 Days")
    st.markdown(
        "Select a fund from your portfolio **or** enter any AMFI fund code. "
        "NAV history is fetched live from [mfapi.in](https://api.mfapi.in). "
        "Forecast uses a log-linear trend model with a ±95% confidence band."
    )
    st.divider()

    portfolio_funds = _get_portfolio_funds()

    col_sel, col_manual = st.columns([3, 2])
    with col_sel:
        fund_options  = ["— Select from portfolio —"] + list(portfolio_funds.keys())
        selected_fund = st.selectbox("🔍 Choose from your portfolio", options=fund_options, index=0)
    with col_manual:
        manual_code = st.text_input(
            "✏️ Or enter a fund code manually",
            placeholder="e.g. 120503",
            help="Find fund codes at https://api.mfapi.in/mf/search?q=<name>",
        )

    # Resolve fund code and label
    fund_code = fund_label = None
    if manual_code.strip():
        fund_code  = manual_code.strip()
        fund_label = f"Fund {fund_code}"
    elif selected_fund != "— Select from portfolio —":
        fund_code  = portfolio_funds[selected_fund]
        fund_label = selected_fund

    if fund_code:
        with st.spinner(f"Fetching NAV history for **{fund_label}** (code `{fund_code}`)…"):
            df = _fetch_nav_history(fund_code)

        if df.empty:
            return

        if len(df) < 30:
            st.warning("⚠️ Fewer than 30 NAV records found — forecast may be less reliable.")

        forecast_df, slope, sigma = _linear_trend_forecast(df, horizon=90)
        metrics = _compute_metrics(df, forecast_df)

        # Metric cards
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Current NAV",          f"₹{metrics['current_nav']:.4f}")
        m2.metric(
            "Predicted NAV (Day 90)",
            f"₹{metrics['pred_nav_90']:.4f}",
            delta=f"{metrics['change_pct']:+.2f}%",
        )
        m3.metric("1Y Historical Return",
                  f"{metrics['hist_return']:.1f}%" if metrics["hist_return"] is not None else "N/A")
        m4.metric("Annualised Volatility", f"{metrics['ann_vol']:.1f}%")
        m5.metric("Data Points Used",      f"{len(df):,}")

        st.markdown("")

        # Chart
        st.plotly_chart(_build_chart(df, forecast_df, fund_label), use_container_width=True)

        # Forecast table
        with st.expander("📋 View Forecast Data Table (weekly intervals shown)"):
            display_df = forecast_df.copy()
            display_df["date"]     = display_df["date"].dt.strftime("%d-%m-%Y")
            display_df             = display_df.rename(columns={
                "date":     "Date",
                "nav_pred": "Predicted NAV (₹)",
                "upper_95": "Upper 95% CI (₹)",
                "lower_95": "Lower 95% CI (₹)",
            })
            for col in ["Predicted NAV (₹)", "Upper 95% CI (₹)", "Lower 95% CI (₹)"]:
                display_df[col] = display_df[col].round(4)

            st.dataframe(display_df.iloc[::7].reset_index(drop=True), use_container_width=True)
            st.download_button(
                label="⬇️ Download full 90-day forecast CSV",
                data=display_df.to_csv(index=False).encode("utf-8"),
                file_name=f"{fund_label.replace(' ', '_')}_90day_forecast.csv",
                mime="text/csv",
            )

        st.info(
            "⚠️ **Disclaimer:** This forecast is statistical in nature and for informational purposes only. "
            "It does not constitute financial advice. Mutual fund investments are subject to market risks."
        )

    else:
        st.markdown(
            """
            <div style="border:1px solid rgba(0,245,212,0.3);border-radius:10px;
                        padding:24px 28px;background:rgba(0,245,212,0.05);
                        color:rgba(255,255,255,0.8);line-height:1.9;">
            <b>How to use:</b><br>
            1. Pick a fund from your portfolio using the dropdown above, <b>or</b><br>
            2. Enter any valid AMFI fund code in the text field (e.g. <code>120503</code>).<br><br>
            The tool fetches 2 years of NAV history, fits a log-linear trend, and projects
            the next <b>90 days</b> with a 95% confidence band.<br><br>
            💡 <b>Tip:</b> To look up fund codes visit
            <a href="https://api.mfapi.in/mf/search?q=mirae" target="_blank"
               style="color:#00f5d4;">api.mfapi.in/mf/search?q=&lt;name&gt;</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
