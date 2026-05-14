"""
utils/fund_prediction.py
─────────────────────────────────────────────
Prophet-based 90-day NAV forecasting tab.

Add to requirements.txt:
    prophet
    scikit-learn

Usage in Tools.py:
    from utils.fund_prediction import show_fund_prediction
    with tab_pred:
        show_fund_prediction()
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go


# ── Portfolio funds from config.py ────────────────────────────────────────────
def _get_portfolio_funds():
    import sys, os
    for candidate in [
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.getcwd(),
        "/mount/src/investment",
    ]:
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
    try:
        from config import mutual_funds
        return {name: info["code"] for name, info in mutual_funds.items()}
    except Exception:
        return {
            "Mirae Asset FANG+":                                "148928",
            "SBI Magnum Children's Benefit Fund":               "148490",
            "Bandhan Small Cap Fund":                           "147946",
            "Motilal Oswal Midcap Fund":                        "127042",
            "Edelweiss Flexi Cap Fund":                         "140353",
            "Parag Parikh Flexi Cap Fund":                      "122639",
            "Nippon India Large Cap Fund":                      "118632",
            "Axis Small Cap Fund":                              "125354",
            "SBI Small Cap Fund":                               "125497",
            "quant Small Cap Fund":                             "120828",
            "HSBC Midcap Fund":                                 "151034",
            "Kotak Midcap Fund":                                "119775",
            "quant Mid Cap Fund":                               "120841",
            "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": "150902",
            "Kotak Flexicap Fund":                              "112090",
            "ICICI Pru BHARAT 22 FOF":                         "143903",
        }


# ── Fetch NAV history ─────────────────────────────────────────────────────────
def _fetch_nav_history(fund_code: str) -> pd.DataFrame:
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=1095)   # 3 years — Prophet needs more data

    url = (
        f"https://api.mfapi.in/mf/{fund_code}"
        f"?startDate={start_date.strftime('%d-%m-%Y')}"
        f"&endDate={end_date.strftime('%d-%m-%Y')}"
    )
    try:
        resp = requests.get(url, timeout=20)
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
    fund_name = data.get("meta", {}).get("scheme_name", f"Fund {fund_code}")
    return df, fund_name


# ── Prophet Forecast ──────────────────────────────────────────────────────────
def _prophet_forecast(df: pd.DataFrame, horizon: int = 90):
    """
    Use Facebook Prophet for time-series forecasting.
    Prophet handles:
      - Non-linear trends with changepoints
      - Weekly/yearly seasonality
      - Holiday effects (Indian market holidays added)
      - Uncertainty intervals automatically
    """
    try:
        from prophet import Prophet
    except ImportError:
        st.error("❌ `prophet` package not installed. Add `prophet` to requirements.txt and redeploy.")
        return None, None

    # Prophet expects columns: ds (datetime), y (value)
    prophet_df = df.rename(columns={"date": "ds", "nav": "y"}).copy()

    # Indian market holidays (approximate — major ones)
    indian_holidays = pd.DataFrame({
        "holiday": "india_market_holiday",
        "ds": pd.to_datetime([
            # 2022
            "2022-01-26","2022-03-01","2022-03-18","2022-04-14","2022-04-15",
            "2022-05-03","2022-08-09","2022-08-15","2022-10-02","2022-10-05",
            "2022-10-24","2022-10-26","2022-11-08","2022-12-25",
            # 2023
            "2023-01-26","2023-03-07","2023-03-30","2023-04-04","2023-04-07",
            "2023-04-14","2023-05-01","2023-06-29","2023-08-15","2023-09-19",
            "2023-10-02","2023-10-24","2023-11-14","2023-11-27","2023-12-25",
            # 2024
            "2024-01-22","2024-01-26","2024-03-25","2024-04-09","2024-04-11",
            "2024-04-14","2024-04-17","2024-04-21","2024-05-01","2024-05-23",
            "2024-06-17","2024-07-17","2024-08-15","2024-10-02","2024-10-13",
            "2024-10-14","2024-11-01","2024-11-15","2024-12-25",
            # 2025
            "2025-01-26","2025-02-26","2025-03-14","2025-03-31","2025-04-10",
            "2025-04-14","2025-04-18","2025-05-01","2025-08-15","2025-08-27",
            "2025-10-02","2025-10-02","2025-10-20","2025-10-21","2025-11-05",
            "2025-12-25",
        ]),
        "lower_window": 0,
        "upper_window": 1,
    })

    model = Prophet(
        changepoint_prior_scale=0.15,      # flexibility of trend changes
        seasonality_prior_scale=10,        # strength of seasonality
        holidays_prior_scale=10,
        seasonality_mode="multiplicative", # better for financial data (% changes)
        yearly_seasonality=True,
        weekly_seasonality=False,          # MF NAVs don't have weekly patterns
        daily_seasonality=False,
        holidays=indian_holidays,
        interval_width=0.90,               # 90% confidence interval
    )

    # Add monthly seasonality (SIP inflows cause end-of-month patterns)
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

    with st.spinner("🤖 Training Prophet model on historical NAV data..."):
        model.fit(prophet_df)

    # Create future dataframe
    future = model.make_future_dataframe(periods=horizon, freq="D")
    forecast = model.predict(future)

    return model, forecast


# ── Metrics ───────────────────────────────────────────────────────────────────
def _compute_metrics(df: pd.DataFrame, forecast: pd.DataFrame) -> dict:
    current_nav = df["nav"].iloc[-1]
    last_date   = df["date"].iloc[-1]

    # Get prediction for day 90
    future_fc   = forecast[forecast["ds"] > last_date].head(90)
    pred_90     = future_fc["yhat"].iloc[-1] if len(future_fc) >= 90 else future_fc["yhat"].iloc[-1]
    upper_90    = future_fc["yhat_upper"].iloc[-1]
    lower_90    = future_fc["yhat_lower"].iloc[-1]
    change_pct  = (pred_90 - current_nav) / current_nav * 100

    # 1Y historical return
    one_yr = df[df["date"] >= last_date - timedelta(days=365)]
    hist_return = (
        (current_nav - one_yr["nav"].iloc[0]) / one_yr["nav"].iloc[0] * 100
        if len(one_yr) > 1 else None
    )

    # Annualised volatility
    ann_vol = df["nav"].pct_change().dropna().std() * np.sqrt(252) * 100

    # Model accuracy on historical data (MAPE)
    hist_fc  = forecast[forecast["ds"].isin(df["date"])][["ds", "yhat"]].copy()
    merged   = df.rename(columns={"date": "ds"}).merge(hist_fc, on="ds")
    mape     = (abs(merged["nav"] - merged["yhat"]) / merged["nav"]).mean() * 100 if len(merged) > 0 else None

    return {
        "current_nav": current_nav,
        "pred_nav_90": pred_90,
        "upper_90":    upper_90,
        "lower_90":    lower_90,
        "change_pct":  change_pct,
        "hist_return": hist_return,
        "ann_vol":     ann_vol,
        "mape":        mape,
    }


# ── Chart ─────────────────────────────────────────────────────────────────────
def _build_chart(df: pd.DataFrame, forecast: pd.DataFrame, fund_name: str) -> go.Figure:
    last_date  = df["date"].iloc[-1]
    hist_window = df[df["date"] >= last_date - timedelta(days=365)].copy()

    future_fc  = forecast[forecast["ds"] > last_date].copy()
    hist_fc    = forecast[forecast["ds"] <= last_date].copy()

    fig = go.Figure()

    # ── Confidence band ──
    fig.add_trace(go.Scatter(
        x=pd.concat([future_fc["ds"], future_fc["ds"][::-1]]),
        y=pd.concat([future_fc["yhat_upper"], future_fc["yhat_lower"][::-1]]),
        fill="toself",
        fillcolor="rgba(255,165,0,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip",
        name="90% Confidence Band",
    ))

    # ── Historical fitted line ──
    fig.add_trace(go.Scatter(
        x=hist_fc["ds"], y=hist_fc["yhat"],
        mode="lines", name="Prophet Fitted",
        line=dict(color="rgba(0,245,212,0.35)", width=1, dash="dot"),
        hovertemplate="Fitted: ₹%{y:.4f}<extra></extra>",
    ))

    # ── Actual historical NAV ──
    fig.add_trace(go.Scatter(
        x=hist_window["date"], y=hist_window["nav"],
        mode="lines", name="Actual NAV",
        line=dict(color="#00f5d4", width=2.5),
        hovertemplate="NAV: ₹%{y:.4f}<extra></extra>",
    ))

    # ── Forecast line ──
    fig.add_trace(go.Scatter(
        x=future_fc["ds"], y=future_fc["yhat"],
        mode="lines", name="Prophet Forecast",
        line=dict(color="#FFA500", width=2.5, dash="dash"),
        hovertemplate="Forecast: ₹%{y:.4f}<extra></extra>",
    ))

    # ── Upper / Lower band lines ──
    fig.add_trace(go.Scatter(
        x=future_fc["ds"], y=future_fc["yhat_upper"],
        mode="lines", name="Upper (90% CI)",
        line=dict(color="rgba(255,165,0,0.4)", width=1, dash="dot"),
        hovertemplate="Upper: ₹%{y:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=future_fc["ds"], y=future_fc["yhat_lower"],
        mode="lines", name="Lower (90% CI)",
        line=dict(color="rgba(255,165,0,0.4)", width=1, dash="dot"),
        hovertemplate="Lower: ₹%{y:.4f}<extra></extra>",
    ))

    # ── Today marker ──
    fig.add_vline(
        x=last_date.timestamp() * 1000,
        line_width=1, line_dash="dot",
        line_color="rgba(255,255,255,0.3)",
        annotation_text="Today",
        annotation_position="top left",
        annotation_font_color="rgba(255,255,255,0.5)",
    )

    fig.update_layout(
        title=dict(
            text=f"🤖 {fund_name} — Prophet 90-Day Forecast",
            font=dict(color="white", size=15),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            title="Date",
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            title="NAV (₹)",
            showgrid=True,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
            font=dict(size=11),
        ),
        hovermode="x unified",
        margin=dict(t=55, b=40, l=65, r=20),
    )
    return fig


def _build_components_chart(model, forecast, fund_name: str):
    """Show Prophet's trend and seasonality decomposition."""
    try:
        last_date = forecast["ds"].max() - timedelta(days=90)
        hist_fc   = forecast[forecast["ds"] <= last_date].copy()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_fc["ds"], y=hist_fc["trend"],
            mode="lines", name="Trend",
            line=dict(color="#00f5d4", width=2),
        ))
        if "yearly" in hist_fc.columns:
            fig.add_trace(go.Scatter(
                x=hist_fc["ds"], y=hist_fc["yearly"],
                mode="lines", name="Yearly Seasonality",
                line=dict(color="#FFA500", width=1.5),
                yaxis="y2",
            ))

        fig.update_layout(
            title=dict(text="📊 Trend Decomposition", font=dict(color="white", size=13)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Trend NAV (₹)"),
            yaxis2=dict(
                title="Seasonality", overlaying="y", side="right",
                gridcolor="rgba(255,255,255,0.03)",
            ),
            legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="rgba(255,255,255,0.15)", borderwidth=1),
            margin=dict(t=45, b=35, l=65, r=65),
        )
        return fig
    except Exception:
        return None


# ── Main entry point ──────────────────────────────────────────────────────────
def show_fund_prediction():
    """Render the Fund Prediction tab."""

    # Header
    st.markdown("## 🤖 AI Fund NAV Prediction — Next 90 Days")
    st.markdown(
        "Powered by **Facebook Prophet** — a production-grade time-series AI model "
        "that learns trend, seasonality, and market holiday patterns from historical NAV data."
    )

    # Model info box
    st.markdown(
        """
        <div style="background:rgba(0,245,212,0.06);border:1px solid rgba(0,245,212,0.2);
                    border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:13px;
                    line-height:1.8;">
        <b style="color:#00f5d4;">🧠 Model: Facebook Prophet</b><br>
        <span style="color:rgba(255,255,255,0.7);">
        ✦ Detects non-linear growth trends with automatic changepoint detection<br>
        ✦ Learns yearly seasonality patterns from NAV history<br>
        ✦ Accounts for Indian market holidays (Republic Day, Diwali, etc.)<br>
        ✦ Models monthly SIP-driven inflow patterns<br>
        ✦ Provides calibrated 90% confidence intervals<br>
        ✦ Trained on 3 years of daily NAV data
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    portfolio_funds = _get_portfolio_funds()

    # ── Fund selection ────────────────────────────────────────────────────────
    col_sel, col_manual = st.columns([3, 2])
    with col_sel:
        fund_options  = ["— Select from portfolio —"] + list(portfolio_funds.keys())
        selected_fund = st.selectbox("🔍 Choose from your portfolio", options=fund_options, index=0, key="pred_select")
    with col_manual:
        manual_code = st.text_input(
            "✏️ Or enter a fund code manually",
            placeholder="e.g. 120503",
            help="Find codes at https://api.mfapi.in/mf/search?q=<name>",
            key="pred_manual_code",
        )

    fund_code = fund_label = None
    if manual_code.strip():
        fund_code  = manual_code.strip()
        fund_label = f"Fund {fund_code}"
    elif selected_fund != "— Select from portfolio —":
        fund_code  = portfolio_funds[selected_fund]
        fund_label = selected_fund

    if fund_code:

        # ── Fetch data ────────────────────────────────────────────────────────
        with st.spinner(f"📡 Fetching 3 years of NAV history for **{fund_label}**…"):
            df, api_fund_name = _fetch_nav_history(fund_code)

        if df.empty:
            return
        # ADD THIS BLOCK:
        st.markdown(
            f'<div style="background:rgba(0,245,212,0.06);border:1px solid rgba(0,245,212,0.2);'
            f'border-radius:8px;padding:12px 16px;margin-bottom:16px;">'
            f'<div style="font-size:11px;letter-spacing:0.1em;text-transform:uppercase;'
            f'color:#00f5d4;">Fund</div>'
            f'<div style="font-size:15px;font-weight:600;margin-top:2px;">{api_fund_name}</div>'
            f'<div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:4px;">'
            f'Code: {fund_code} &nbsp;|&nbsp; {len(df):,} NAV records fetched</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if len(df) < 60:
            st.warning("⚠️ Fewer than 60 data points — Prophet needs more history for reliable predictions.")

        # ── Run Prophet ───────────────────────────────────────────────────────
        model, forecast = _prophet_forecast(df, horizon=90)
        if forecast is None:
            return

        metrics = _compute_metrics(df, forecast)

        # ── Model accuracy badge ──────────────────────────────────────────────
        mape_val = metrics["mape"]
        if mape_val is not None:
            acc_color = "#00f5d4" if mape_val < 3 else ("#ffc107" if mape_val < 7 else "#ff6b6b")
            acc_label = "Excellent" if mape_val < 3 else ("Good" if mape_val < 7 else "Fair")
            st.markdown(
                f'<div style="text-align:right;margin-bottom:4px;">'
                f'<span style="font-size:11px;color:rgba(255,255,255,0.5);">Model Accuracy (MAPE): </span>'
                f'<span style="color:{acc_color};font-weight:700;font-size:13px;">'
                f'{mape_val:.2f}% — {acc_label}</span></div>',
                unsafe_allow_html=True,
            )

        # ── Metric cards ──────────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Current NAV",         f"₹{metrics['current_nav']:.4f}")
        delta_color = "normal"
        m2.metric(
            "Predicted NAV (Day 90)",
            f"₹{metrics['pred_nav_90']:.4f}",
            delta=f"{metrics['change_pct']:+.2f}%",
        )
        m3.metric("Prediction Range",
                  f"₹{metrics['lower_90']:.2f} – ₹{metrics['upper_90']:.2f}",
                  help="90% confidence interval at Day 90")
        m4.metric("1Y Historical Return",
                  f"{metrics['hist_return']:.1f}%" if metrics["hist_return"] is not None else "N/A")
        m5.metric("Annualised Volatility", f"{metrics['ann_vol']:.1f}%")

        st.markdown("")

        # ── Main forecast chart ───────────────────────────────────────────────
        st.plotly_chart(_build_chart(df, forecast, fund_label), use_container_width=True)

        # ── Trend decomposition chart ─────────────────────────────────────────
        comp_fig = _build_components_chart(model, forecast, fund_label)
        if comp_fig:
            with st.expander("📊 View Trend Decomposition"):
                st.plotly_chart(comp_fig, use_container_width=True)
                st.caption(
                    "The trend line shows the underlying growth direction learned by Prophet. "
                    "Seasonality shows periodic patterns (e.g. year-end rally, budget season)."
                )

        # ── Forecast table ────────────────────────────────────────────────────
        with st.expander("📋 View 90-Day Forecast Table (weekly)"):
            last_date  = df["date"].iloc[-1]
            future_fc  = forecast[forecast["ds"] > last_date][["ds","yhat","yhat_lower","yhat_upper"]].head(90).copy()
            future_fc["ds"] = future_fc["ds"].dt.strftime("%d-%m-%Y")
            future_fc       = future_fc.rename(columns={
                "ds":          "Date",
                "yhat":        "Predicted NAV (₹)",
                "yhat_lower":  "Lower 90% CI (₹)",
                "yhat_upper":  "Upper 90% CI (₹)",
            })
            for col in ["Predicted NAV (₹)", "Lower 90% CI (₹)", "Upper 90% CI (₹)"]:
                future_fc[col] = future_fc[col].round(4)

            st.dataframe(future_fc.iloc[::7].reset_index(drop=True), use_container_width=True)
            st.download_button(
                label="⬇️ Download full 90-day forecast CSV",
                data=future_fc.to_csv(index=False).encode("utf-8"),
                file_name=f"{fund_label.replace(' ', '_')}_prophet_90day.csv",
                mime="text/csv",
            )

        # ── Disclaimer ────────────────────────────────────────────────────────
        st.info(
            "⚠️ **Disclaimer:** Prophet forecasts are based on historical patterns and statistical modelling. "
            "They do not account for sudden market events, regulatory changes, or black-swan scenarios. "
            "This is for informational purposes only and does not constitute financial advice. "
            "Mutual fund investments are subject to market risks."
        )

    else:
        st.markdown(
            """
            <div style="border:1px solid rgba(0,245,212,0.25);border-radius:10px;
                        padding:28px 32px;background:rgba(0,245,212,0.04);
                        color:rgba(255,255,255,0.75);line-height:2;">
            <b style="color:#00f5d4;">How to use:</b><br>
            1. Select a fund from your portfolio using the dropdown, <b>or</b><br>
            2. Enter any AMFI fund code manually (e.g. <code>120503</code>).<br><br>
            The AI model will fetch 3 years of NAV history, train on it, and predict
            the next <b>90 days</b> with a 90% confidence band.<br><br>
            💡 <b>Find fund codes:</b>
            <a href="https://api.mfapi.in/mf/search?q=mirae" target="_blank"
               style="color:#00f5d4;">api.mfapi.in/mf/search?q=&lt;name&gt;</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
