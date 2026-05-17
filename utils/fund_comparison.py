# ══════════════════════════════════════════════
# FUND COMPARISON TOOL
# utils/fund_comparison.py
# ══════════════════════════════════════════════

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta
from config import mutual_funds


# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────

def _parse_mfapi_date(d_str: str) -> date:
    parts = d_str.strip().replace("/", "-").split("-")
    if len(parts[0]) == 4:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    return date(int(parts[2]), int(parts[1]), int(parts[0]))


def _chart_layout(height: int = 420, margin: dict = None) -> dict:
    """
    Base Plotly layout.
    Pass margin= to override the default — avoids duplicate-key
    conflicts when callers need a custom margin.
    """
    return dict(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="DM Mono, monospace"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True),
        margin=margin if margin is not None else dict(t=28, b=28, l=12, r=12),
        legend=dict(
            bgcolor="rgba(8,14,20,0.75)",
            bordercolor="rgba(0,245,212,0.2)",
            borderwidth=1,
        ),
        height=height,
        hovermode="x unified",
    )


def fmt_inr(amount: float) -> str:
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    return f"₹{amount:,.0f}"


# ─────────────────────────────────────────────
# NAV fetcher
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_nav_series(fund_code: str) -> dict:
    try:
        r = requests.get(
            f"https://api.mfapi.in/mf/{fund_code}",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Taurus/1.0)"},
        )
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}"}

        data = r.json()
        nav_dict = {}
        for entry in data.get("data", []):
            try:
                nav_dict[_parse_mfapi_date(entry["date"])] = float(entry["nav"])
            except Exception:
                pass

        if not nav_dict:
            return {"error": "No valid NAV entries returned"}

        series = pd.Series(nav_dict).sort_index()
        series.index = pd.to_datetime(series.index)
        name = data.get("meta", {}).get("scheme_name", f"Fund {fund_code}")
        return {"name": name, "navs": series}

    except requests.exceptions.Timeout:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Metric calculations
# ─────────────────────────────────────────────

def _calc_metrics(series: pd.Series, label: str) -> dict:
    if len(series) < 2:
        return {}

    start_nav = series.iloc[0]
    end_nav   = series.iloc[-1]
    years     = (series.index[-1] - series.index[0]).days / 365.25
    cagr      = ((end_nav / start_nav) ** (1 / years) - 1) * 100 if years > 0 else 0.0

    rolling_max = series.cummax()
    drawdown    = (series - rolling_max) / rolling_max * 100
    max_dd      = drawdown.min()

    daily_ret = series.pct_change().dropna()
    ann_vol   = daily_ret.std() * np.sqrt(252) * 100

    sharpe      = (cagr - 6.0) / ann_vol if ann_vol > 0 else None
    monthly     = series.resample("ME").last().pct_change().dropna() * 100
    best_month  = float(monthly.max()) if len(monthly) else None
    worst_month = float(monthly.min()) if len(monthly) else None
    abs_ret     = (end_nav / start_nav - 1) * 100

    return {
        "label":       label,
        "cagr":        cagr,
        "abs_ret":     abs_ret,
        "max_dd":      max_dd,
        "ann_vol":     ann_vol,
        "sharpe":      sharpe,
        "best_month":  best_month,
        "worst_month": worst_month,
        "years":       years,
        "start_nav":   start_nav,
        "end_nav":     end_nav,
    }


# ─────────────────────────────────────────────
# Metrics table
# ─────────────────────────────────────────────

_COLORS = ["#00f5d4", "#bf80ff", "#ffb347"]


def _metric_row(label: str, values: list, colors: list, bold_best_idx=None):
    cells = ""
    for i, (v, c) in enumerate(zip(values, colors)):
        weight = "700" if i == bold_best_idx else "400"
        cells += (
            f'<td style="padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.05);'
            f'color:{c};font-weight:{weight};font-size:14px;">{v}</td>'
        )
    st.markdown(
        f'<tr><td style="padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.05);'
        f'font-size:11px;letter-spacing:0.1em;text-transform:uppercase;'
        f'color:rgba(255,255,255,0.45);">{label}</td>{cells}</tr>',
        unsafe_allow_html=True,
    )


def _render_metrics_table(metrics_list: list, colors: list):
    header_cells = "".join(
        f'<th style="padding:10px 14px;text-align:left;font-size:12px;'
        f'letter-spacing:0.08em;color:{c};border-bottom:1px solid rgba(255,255,255,0.1);">'
        f'{m["label"][:28]}</th>'
        for m, c in zip(metrics_list, colors)
    )
    st.markdown(
        f'<div style="overflow-x:auto;margin-top:8px;">'
        f'<table style="width:100%;border-collapse:collapse;font-family:DM Mono,monospace;">'
        f'<thead><tr>'
        f'<th style="padding:10px 14px;border-bottom:1px solid rgba(255,255,255,0.1);'
        f'color:rgba(255,255,255,0.3);font-size:11px;">Metric</th>'
        f'{header_cells}</tr></thead><tbody>',
        unsafe_allow_html=True,
    )

    def _fmt(v, suffix="", decimals=2):
        return f"{v:.{decimals}f}{suffix}" if v is not None else "—"

    def _best_idx(vals, higher_is_better=True):
        filtered = [(i, v) for i, v in enumerate(vals) if v is not None]
        if not filtered:
            return None
        return max(filtered, key=lambda x: x[1] if higher_is_better else -x[1])[0]

    cagr_vals = [m["cagr"] for m in metrics_list]
    _metric_row("CAGR (p.a.)",
                [_fmt(v, "%") for v in cagr_vals], colors, _best_idx(cagr_vals))

    abs_vals = [m["abs_ret"] for m in metrics_list]
    _metric_row(f"Abs Return ({metrics_list[0]['years']:.1f}y)",
                [_fmt(v, "%") for v in abs_vals], colors, _best_idx(abs_vals))

    dd_vals = [m["max_dd"] for m in metrics_list]
    _metric_row("Max Drawdown",
                [_fmt(v, "%") for v in dd_vals], colors, _best_idx(dd_vals, True))

    vol_vals = [m["ann_vol"] for m in metrics_list]
    _metric_row("Volatility (ann.)",
                [_fmt(v, "%") for v in vol_vals], colors, _best_idx(vol_vals, False))

    sharpe_vals = [m["sharpe"] for m in metrics_list]
    _metric_row("Sharpe (proxy)",
                [_fmt(v) for v in sharpe_vals], colors, _best_idx(sharpe_vals))

    bm_vals = [m["best_month"] for m in metrics_list]
    _metric_row("Best Month",
                [_fmt(v, "%") for v in bm_vals], colors, _best_idx(bm_vals))

    wm_vals = [m["worst_month"] for m in metrics_list]
    _metric_row("Worst Month",
                [_fmt(v, "%") for v in wm_vals], colors, _best_idx(wm_vals, True))

    st.markdown("</tbody></table></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────

def show_fund_comparison():

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <style>
    .cmp-section-label {
        font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
        color: #00f5d4; margin-bottom: 10px; margin-top: 4px;
    }
    .cmp-info-box {
        background: rgba(0,245,212,0.05);
        border: 1px solid rgba(0,245,212,0.15);
        border-radius: 8px; padding: 10px 14px;
        font-size: 12px; color: rgba(255,255,255,0.55);
        margin-top: 6px;
    }
    .cmp-banner {
        background: rgba(0,245,212,0.07);
        border: 1px solid rgba(0,245,212,0.25);
        border-radius: 10px; padding: 10px 16px;
        font-size: 11px; letter-spacing: 0.14em;
        text-transform: uppercase; color: #00f5d4;
        margin: 16px 0 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown('<div class="cmp-section-label">Fund Selection</div>', unsafe_allow_html=True)

        num_funds = st.radio(
            "How many funds to compare?", [2, 3],
            horizontal=True, key="cmp_num_funds",
            label_visibility="collapsed",
        )

        portfolio_names = list(mutual_funds.keys())
        fund_selections = []

        for i in range(num_funds):
            color_dot = ["🟢", "🟣", "🟠"][i]
            st.markdown(f"**{color_dot} Fund {i + 1}**")

            source = st.radio(
                f"Source {i+1}", ["My Portfolio", "Custom Code"],
                horizontal=True, key=f"cmp_src_{i}",
                label_visibility="collapsed",
            )

            if source == "My Portfolio":
                chosen_codes = {s["code"] for s in fund_selections}
                available = [
                    n for n in portfolio_names
                    if mutual_funds[n]["code"] not in chosen_codes
                ]
                sel = st.selectbox(
                    f"Fund {i+1}", available,
                    key=f"cmp_fund_{i}",
                    label_visibility="collapsed",
                )
                fund_selections.append({
                    "label": sel[:30],
                    "code":  mutual_funds[sel]["code"],
                })
            else:
                code_in = st.text_input(
                    f"Fund code {i+1}", placeholder="e.g. 125497",
                    key=f"cmp_code_{i}",
                    label_visibility="collapsed",
                )
                fund_selections.append({
                    "label": code_in.strip() if code_in else f"Fund {i+1}",
                    "code":  code_in.strip() if code_in else "",
                })

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="cmp-section-label">Time Period</div>', unsafe_allow_html=True)

        period_opt = st.radio(
            "Period", ["1Y", "3Y", "5Y", "Max", "Custom"],
            horizontal=True, key="cmp_period",
            label_visibility="collapsed",
        )

        today = date.today()
        if period_opt == "1Y":
            start_date = today - timedelta(days=365)
        elif period_opt == "3Y":
            start_date = today - timedelta(days=3 * 365)
        elif period_opt == "5Y":
            start_date = today - timedelta(days=5 * 365)
        elif period_opt == "Max":
            start_date = date(2000, 1, 1)
        else:
            start_date = st.date_input(
                "From",
                value=today - timedelta(days=3 * 365),
                key="cmp_custom_start",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="cmp-section-label">Chart Options</div>', unsafe_allow_html=True)

        show_drawdown = st.toggle(
            "📉 Show Drawdown Chart", value=True,
            key="cmp_drawdown_toggle",
            help="Percentage fall from each fund's previous peak",
        )
        show_monthly_returns = st.toggle(
            "📊 Show Monthly Returns Heatmap", value=False,
            key="cmp_monthly_toggle",
            help="Calendar heatmap of monthly returns per fund",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        compare_btn = st.button(
            "📊 Compare Funds", type="primary",
            key="cmp_run", use_container_width=True,
            disabled=any(not s["code"] for s in fund_selections),
        )

    # ── Results ──
    with right:
        if not compare_btn:
            st.markdown(
                '<br><br><div style="text-align:center;opacity:0.35;padding:80px 20px;">'
                '<div style="font-size:52px;">📉</div>'
                '<div style="margin-top:14px;font-size:14px;">Select funds on the left and hit Compare</div>'
                '<div style="font-size:12px;margin-top:6px;opacity:0.7;">'
                'CAGR · Max Drawdown · Volatility · Sharpe · Best/Worst Month</div></div>',
                unsafe_allow_html=True,
            )
            return

        # ── Fetch ──
        raw_data = {}
        fetch_errors = []
        progress = st.progress(0, text="Fetching NAV data…")

        for idx, sel in enumerate(fund_selections):
            progress.progress(
                (idx + 1) / len(fund_selections),
                text=f"Fetching {sel['label'][:25]}…",
            )
            result = _fetch_nav_series(sel["code"])
            if "error" in result:
                fetch_errors.append(f"{sel['label']} ({sel['code']}): {result['error']}")
            else:
                raw_data[sel["code"]] = {
                    "name":  result["name"],
                    "label": sel["label"],
                    "navs":  result["navs"],
                }
        progress.empty()

        if fetch_errors:
            for err in fetch_errors:
                st.error(f"❌ {err}")
            if not raw_data:
                return

        # ── Clip to period ──
        clipped = {}
        for code, d in raw_data.items():
            s = d["navs"]
            s = s[s.index >= pd.Timestamp(start_date.isoformat())]
            if len(s) < 5:
                st.warning(f"⚠️ {d['label']}: not enough data in selected period — skipped.")
                continue
            clipped[code] = {**d, "navs": s}

        if len(clipped) < 2:
            st.error("Need at least 2 funds with data in the selected period.")
            return

        # ── Align to common start ──
        common_start = max(s["navs"].index[0] for s in clipped.values())
        for code in clipped:
            clipped[code]["navs"] = clipped[code]["navs"][
                clipped[code]["navs"].index >= common_start
            ]

        codes  = list(clipped.keys())
        colors = _COLORS[: len(codes)]

        # ── Banner ──
        fund_pills = " &nbsp;·&nbsp; ".join(
            f'<span style="color:{c};font-weight:600;">{clipped[cd]["label"]}</span>'
            for cd, c in zip(codes, colors)
        )
        st.markdown(
            f'<div style="background:rgba(0,245,212,0.05);border:1px solid rgba(0,245,212,0.15);'
            f'border-radius:8px;padding:12px 16px;margin-bottom:16px;font-size:13px;">'
            f'Comparing &nbsp;{fund_pills}&nbsp; '
            f'<span style="color:rgba(255,255,255,0.35);font-size:11px;">'
            f'from {common_start.strftime("%d %b %Y")} → {today.strftime("%d %b %Y")}'
            f'</span></div>',
            unsafe_allow_html=True,
        )

        # ══════════════════════════════════════════
        # CHART 1 — Rebased NAV Growth
        # ══════════════════════════════════════════
        st.markdown('<div class="cmp-banner">📈 NAV Growth — Rebased to 100</div>', unsafe_allow_html=True)

        fig_nav = go.Figure()
        for code, color in zip(codes, colors):
            s = clipped[code]["navs"]
            rebased = s / s.iloc[0] * 100
            fig_nav.add_trace(go.Scatter(
                x=rebased.index, y=rebased.values,
                name=clipped[code]["label"],
                line=dict(color=color, width=2),
                hovertemplate="%{y:.1f}<extra>" + clipped[code]["label"] + "</extra>",
            ))
        fig_nav.add_hline(
            y=100, line_dash="dot",
            line_color="rgba(255,255,255,0.15)",
            annotation_text="Base",
            annotation_font_color="rgba(255,255,255,0.3)",
        )
        fig_nav.update_layout(**_chart_layout(440), yaxis_title="Rebased NAV", xaxis_title=None)
        st.plotly_chart(fig_nav, use_container_width=True)

        st.markdown(
            '<div class="cmp-info-box">All NAVs rebased to 100 on the common start date so '
            'absolute NAV levels don\'t distort the comparison.</div>',
            unsafe_allow_html=True,
        )

        # ══════════════════════════════════════════
        # CHART 2 — Drawdown
        # ══════════════════════════════════════════
        if show_drawdown:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="cmp-banner">📉 Drawdown from Peak</div>', unsafe_allow_html=True)

            fig_dd = go.Figure()
            for code, color in zip(codes, colors):
                s = clipped[code]["navs"]
                rolling_max = s.cummax()
                dd = (s - rolling_max) / rolling_max * 100
                fig_dd.add_trace(go.Scatter(
                    x=dd.index, y=dd.values,
                    name=clipped[code]["label"],
                    line=dict(color=color, width=1.5),
                    fill="tozeroy",
                    opacity=0.4,
                    hovertemplate="%{y:.2f}%<extra>" + clipped[code]["label"] + "</extra>",
                ))
            fig_dd.update_layout(**_chart_layout(320), yaxis_title="Drawdown (%)", xaxis_title=None)
            st.plotly_chart(fig_dd, use_container_width=True)

        # ══════════════════════════════════════════
        # METRICS TABLE
        # ══════════════════════════════════════════
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="cmp-banner">📋 Side-by-Side Metrics</div>', unsafe_allow_html=True)

        metrics_list = [
            _calc_metrics(clipped[code]["navs"], clipped[code]["label"])
            for code in codes
        ]
        _render_metrics_table(metrics_list, colors)

        # ── Winner summary ──
        st.markdown("<br>", unsafe_allow_html=True)
        best_cagr_idx = max(range(len(metrics_list)), key=lambda i: metrics_list[i]["cagr"])
        best_dd_idx   = max(range(len(metrics_list)), key=lambda i: metrics_list[i]["max_dd"])
        best_vol_idx  = min(range(len(metrics_list)), key=lambda i: metrics_list[i]["ann_vol"])
        sharpe_vals   = [m["sharpe"] for m in metrics_list]
        best_sharpe_idx = max(
            (i for i, v in enumerate(sharpe_vals) if v is not None),
            key=lambda i: sharpe_vals[i], default=None,
        )

        def _winner_line(emoji, label, idx, metric_str):
            name  = metrics_list[idx]["label"]
            color = colors[idx]
            return (
                f'<div style="padding:6px 0;font-size:13px;">'
                f'{emoji} <span style="color:rgba(255,255,255,0.5);">{label}:</span> '
                f'<strong style="color:{color};">{name}</strong> '
                f'<span style="color:rgba(255,255,255,0.35);font-size:12px;">({metric_str})</span></div>'
            )

        summary_html = (
            '<div style="background:rgba(0,245,212,0.06);border:1px solid rgba(0,245,212,0.2);'
            'border-radius:10px;padding:14px 18px;margin-top:4px;">'
            '<div style="font-size:11px;letter-spacing:0.15em;text-transform:uppercase;'
            'color:#00f5d4;margin-bottom:10px;">Winner Summary</div>'
        )
        summary_html += _winner_line("🏆", "Best CAGR",             best_cagr_idx, f'{metrics_list[best_cagr_idx]["cagr"]:.2f}% p.a.')
        summary_html += _winner_line("🛡️", "Least Drawdown",        best_dd_idx,   f'{metrics_list[best_dd_idx]["max_dd"]:.2f}%')
        summary_html += _winner_line("📐", "Lowest Volatility",     best_vol_idx,  f'{metrics_list[best_vol_idx]["ann_vol"]:.2f}% ann.')
        if best_sharpe_idx is not None:
            summary_html += _winner_line("⚖️", "Best Risk-Adjusted", best_sharpe_idx, f'{sharpe_vals[best_sharpe_idx]:.2f}')
        summary_html += "</div>"
        st.markdown(summary_html, unsafe_allow_html=True)

        # ══════════════════════════════════════════
        # CHART 3 — Monthly Heatmap (optional)
        # ══════════════════════════════════════════
        if show_monthly_returns:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="cmp-banner">📅 Monthly Returns (%)</div>', unsafe_allow_html=True)

            for code, color in zip(codes, colors):
                s = clipped[code]["navs"]
                monthly = s.resample("ME").last().pct_change().dropna() * 100
                if len(monthly) < 2:
                    continue

                df_m = pd.DataFrame({
                    "year":  monthly.index.year,
                    "month": monthly.index.month,
                    "ret":   monthly.values,
                })
                pivot = df_m.pivot_table(index="year", columns="month", values="ret")
                month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                               "Jul","Aug","Sep","Oct","Nov","Dec"]
                pivot.columns = [month_names[m - 1] for m in pivot.columns]

                # ── THE FIX: pass margin into _chart_layout so there
                #    is only ever ONE margin key in the layout dict ──
                heatmap_layout = _chart_layout(
                    height=max(180, len(pivot) * 36 + 60),
                    margin=dict(t=60, b=10, l=40, r=40),
                )
                heatmap_layout["title"] = dict(
                    text=clipped[code]["label"],
                    font=dict(color=color, size=13),
                    x=0,
                )
                heatmap_layout["xaxis"] = dict(
                    side="top",
                    gridcolor="rgba(255,255,255,0.06)",
                )
                heatmap_layout["yaxis"] = dict(
                    autorange="reversed",
                    gridcolor="rgba(255,255,255,0.06)",
                )

                fig_heat = go.Figure(go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns.tolist(),
                    y=[str(y) for y in pivot.index.tolist()],
                    colorscale=[
                        [0.0,  "#ff4444"],
                        [0.35, "#662222"],
                        [0.5,  "#111a22"],
                        [0.65, "#1a4433"],
                        [1.0,  "#00f5d4"],
                    ],
                    zmid=0,
                    text=np.round(pivot.values, 1),
                    texttemplate="%{text}%",
                    textfont={"size": 10},
                    hovertemplate="%{y} %{x}: %{z:.2f}%<extra></extra>",
                    showscale=True,
                    colorbar=dict(
                        tickfont=dict(color="white"),
                        outlinecolor="rgba(0,0,0,0)",
                    ),
                ))
                fig_heat.update_layout(heatmap_layout)
                st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown(
            '<div class="cmp-info-box" style="margin-top:16px;">'
            '⚠️ <strong>Disclaimer:</strong> Metrics computed from historical NAV data via mfapi.in. '
            'Past performance is not indicative of future returns. '
            'Sharpe uses 6% as the assumed risk-free rate.'
            '</div>',
            unsafe_allow_html=True,
        )
