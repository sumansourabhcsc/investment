# pages/6_Smart_SIP.py

import streamlit as st
import math
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import mutual_funds
from utils.sidebar_style import render_sidebar

render_sidebar("smart_sip")

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus: Smart SIP",
    page_icon="🐂",
    layout="wide"
)

# ─────────────────────────────────────────────
# Background + Styling (identical to other pages)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Base: deep midnight navy ── */
    .stApp {
        background-color: #020d1a;
        background-image: none;
        position: relative;
        min-height: 100vh;
    }

    /* ── Layer 1: radial teal glow orbs ── */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background:
            radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(0, 245, 212, 0.07) 0%, transparent 65%),
            radial-gradient(ellipse 60% 80% at 85% 75%,  rgba(0, 180, 245, 0.06) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 50% 100%, rgba(0, 245, 212, 0.04) 0%, transparent 55%),
            radial-gradient(ellipse 100% 100% at 50% 0%,  rgba(2, 20, 40, 0.8)  0%, #020d1a 70%);
        z-index: 0;
        pointer-events: none;
    }

    /* ── Layer 2: fine dot-grid pattern ── */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(circle, rgba(0,245,212,0.18) 1px, transparent 1px);
        background-size: 38px 38px;
        z-index: 0;
        pointer-events: none;
        opacity: 0.55;
    }

    .stApp > * { position: relative; z-index: 1; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
        border-right: 1px solid rgba(0,245,212,0.1) !important;
        box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    }

    @keyframes taurus-pulse {
        0%   { opacity: 1; }
        50%  { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .stApp::before { animation: taurus-pulse 8s ease-in-out infinite; }

    [data-testid="stAppViewContainer"] > section.main > div.block-container {
        background: rgba(2, 16, 32, 0.45);
        border-left: 1px solid rgba(0,245,212,0.07);
        border-right: 1px solid rgba(0,245,212,0.07);
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
    }

    /* ── Custom card style ── */
    .sip-card {
        background: rgba(0, 245, 212, 0.04);
        border: 1px solid rgba(0,245,212,0.14);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        transition: border 0.2s;
    }
    .sip-card:hover { border-color: rgba(0,245,212,0.35); }

    .stat-box {
        background: rgba(0,245,212,0.05);
        border: 1px solid rgba(0,245,212,0.18);
        border-radius: 10px;
        padding: 16px 18px;
    }
    .stat-label {
        font-size: 10px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: rgba(0,245,212,0.55);
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 20px;
        font-weight: 700;
        color: #00f5d4;
        font-family: 'DM Mono', monospace;
    }
    .stat-value-purple {
        font-size: 20px;
        font-weight: 700;
        color: #a78bfa;
        font-family: 'DM Mono', monospace;
    }
    .cat-label {
        font-size: 10px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: rgba(0,245,212,0.6);
        margin-bottom: 2px;
    }
    .fund-name {
        font-size: 15px;
        font-weight: 600;
        color: #e8f4f0;
        margin-bottom: 8px;
    }
    .pill {
        display: inline-block;
        padding: 3px 11px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 5px;
    }
    .bar-track {
        background: rgba(255,255,255,0.07);
        border-radius: 4px;
        height: 8px;
        overflow: hidden;
        margin-top: 5px;
    }
    .disclaimer {
        font-size: 11px;
        color: rgba(255,255,255,0.28);
        line-height: 1.9;
        margin-top: 24px;
        border-top: 1px solid rgba(0,245,212,0.08);
        padding-top: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# Fund universe — your funds from config.py
# categorised + enriched with metadata
# ─────────────────────────────────────────────
FUND_META = {
    "Mirae Asset FANG+":                          {"category": "Thematic / Global",  "returns_3y": 14.1, "rating": 4, "risk": "Very High",     "risk_color": "#dc2626"},
    "SBI Magnum Children's Benefit Fund":         {"category": "Hybrid / Children",  "returns_3y": 17.9, "rating": 4, "risk": "Moderate",      "risk_color": "#eab308"},
    "Bandhan Small Cap Fund":                     {"category": "Small Cap",           "returns_3y": 28.1, "rating": 4, "risk": "Very High",     "risk_color": "#dc2626"},
    "Motilal Oswal Midcap Fund":                  {"category": "Mid Cap",             "returns_3y": 29.3, "rating": 5, "risk": "High",          "risk_color": "#ef4444"},
    "Edelweiss Flexi Cap Fund":                   {"category": "Flexi Cap",           "returns_3y": 18.2, "rating": 4, "risk": "Moderate-High", "risk_color": "#f97316"},
    "Parag Parikh Flexi Cap Fund":                {"category": "Flexi Cap",           "returns_3y": 19.7, "rating": 5, "risk": "Moderate-High", "risk_color": "#f97316"},
    "Nippon India Large Cap Fund":                {"category": "Large Cap",           "returns_3y": 16.4, "rating": 5, "risk": "Low-Moderate",  "risk_color": "#84cc16"},
    "Axis Small Cap Fund":                        {"category": "Small Cap",           "returns_3y": 26.1, "rating": 5, "risk": "Very High",     "risk_color": "#dc2626"},
    "SBI Small Cap Fund":                         {"category": "Small Cap",           "returns_3y": 27.8, "rating": 5, "risk": "Very High",     "risk_color": "#dc2626"},
    "quant Small Cap Fund":                       {"category": "Small Cap",           "returns_3y": 31.4, "rating": 5, "risk": "Very High",     "risk_color": "#dc2626"},
    "HSBC Midcap Fund":                           {"category": "Mid Cap",             "returns_3y": 22.4, "rating": 4, "risk": "High",          "risk_color": "#ef4444"},
    "Kotak Midcap Fund":                          {"category": "Mid Cap",             "returns_3y": 23.1, "rating": 4, "risk": "High",          "risk_color": "#ef4444"},
    "quant Mid Cap Fund":                         {"category": "Mid Cap",             "returns_3y": 27.6, "rating": 5, "risk": "High",          "risk_color": "#ef4444"},
    "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": {"category": "Mid Cap",       "returns_3y": 24.8, "rating": 4, "risk": "High",          "risk_color": "#ef4444"},
    "Kotak Flexicap Fund":                        {"category": "Flexi Cap",           "returns_3y": 17.3, "rating": 4, "risk": "Moderate-High", "risk_color": "#f97316"},
    "ICICI Pru BHARAT 22 FOF":                    {"category": "Thematic / Global",  "returns_3y": 22.7, "rating": 4, "risk": "Moderate-High", "risk_color": "#f97316"},
}

DEFAULT_ALLOC = {
    "Large Cap":          20,
    "Mid Cap":            25,
    "Small Cap":          25,
    "Flexi Cap":          15,
    "Thematic / Global":  10,
    "Hybrid / Children":   5,
}

BAR_COLORS = ["#00f5d4", "#3b82f6", "#a78bfa", "#f59e0b", "#ef4444", "#10b981"]


def best_fund_in_category(category: str) -> dict | None:
    candidates = [
        {"name": name, **meta}
        for name, meta in FUND_META.items()
        if meta["category"] == category
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda f: f["returns_3y"] * f["rating"])


def fmt_inr(amount: float) -> str:
    return f"₹{int(amount):,}"


def stars(n: int) -> str:
    return "★" * n + "☆" * (5 - n)


# ─────────────────────────────────────────────
# Page Header
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
    <span style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:rgba(0,245,212,0.55);">
        TAURUS · SMART SIP
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("## ⚡ Smart SIP Planner")
st.markdown(
    "<p style='color:rgba(255,255,255,0.4);font-size:13px;margin-top:-8px;'>"
    "Best fund from each category in your portfolio · ₹1,50,000 / month allocation</p>",
    unsafe_allow_html=True
)
st.divider()

# ─────────────────────────────────────────────
# Budget Input
# ─────────────────────────────────────────────
col_in, col_info = st.columns([1, 2])
with col_in:
    monthly_budget = st.number_input(
        "Monthly SIP Budget (₹)",
        min_value=10_000,
        max_value=10_000_000,
        value=150_000,
        step=5_000,
        format="%d",
    )
with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='color:rgba(0,245,212,0.6);font-size:13px;padding:10px 0;'>"
        f"Annual commitment: <b style='color:#00f5d4;'>{fmt_inr(monthly_budget * 12)}</b> &nbsp;·&nbsp; "
        f"Daily avg: <b style='color:#00f5d4;'>{fmt_inr(monthly_budget // 30)}</b>"
        f"</div>",
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# Allocation customiser
# ─────────────────────────────────────────────
with st.expander("⚙️  Customise allocation %", expanded=False):
    st.caption("Adjust category weights. Must total 100%.")
    alloc = {}
    c1, c2 = st.columns(2)
    for i, (cat, default) in enumerate(DEFAULT_ALLOC.items()):
        with (c1 if i % 2 == 0 else c2):
            alloc[cat] = st.slider(cat, 0, 60, default, step=5, key=f"sl_{cat}")
    total = sum(alloc.values())
    if total != 100:
        st.warning(f"Total = **{total}%** — must be exactly 100%.")
else:
    alloc = dict(DEFAULT_ALLOC)
    total = 100

# ─────────────────────────────────────────────
# Generate button
# ─────────────────────────────────────────────
if total != 100:
    st.error("Fix allocation percentages before generating.")
    st.stop()

generate = st.button("✦  Generate Investment Plan", type="primary", use_container_width=True)

if generate or "sip_plan" in st.session_state:

    if generate:
        plan = []
        for cat, pct in alloc.items():
            if pct == 0:
                continue
            pick = best_fund_in_category(cat)
            if not pick:
                continue
            amount = math.floor((monthly_budget * pct / 100) / 100) * 100
            plan.append({"category": cat, "pct": pct, "fund": pick, "amount": amount})
        st.session_state["sip_plan"] = plan
        st.session_state["sip_budget"] = monthly_budget

    plan     = st.session_state["sip_plan"]
    total_m  = sum(r["amount"] for r in plan)
    proj_1y  = sum(r["amount"] * 12 * (1 + r["fund"]["returns_3y"] / 100) for r in plan)

    st.divider()

    # ── Summary stats ──
    s1, s2, s3 = st.columns(3)
    for col, label, val, cls in [
        (s1, "Monthly SIP",       total_m,       "stat-value"),
        (s2, "Annual Investment",  total_m * 12,  "stat-value"),
        (s3, "Projected 1Y Value", proj_1y,       "stat-value-purple"),
    ]:
        with col:
            st.markdown(
                f"<div class='stat-box'>"
                f"<div class='stat-label'>{label}</div>"
                f"<div class='{cls}'>{fmt_inr(val)}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Allocation bars ──
    st.markdown("#### 📊 Allocation Breakdown")
    for i, row in enumerate(plan):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        st.markdown(f"""
        <div style='margin-bottom:10px;'>
            <div style='display:flex;justify-content:space-between;font-size:13px;'>
                <span style='color:rgba(255,255,255,0.7);'>{row['category']}</span>
                <span style='color:{color};font-weight:700;font-family:DM Mono,monospace;'>
                    {fmt_inr(row['amount'])}
                    <span style='color:rgba(255,255,255,0.3);font-size:11px;'> ({row['pct']}%)</span>
                </span>
            </div>
            <div class='bar-track'>
                <div style='height:100%;width:{row["pct"]}%;background:{color};border-radius:4px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Fund Cards ──
    st.markdown("#### 🏆 Best Fund Pick Per Category")
    st.caption("Ranked by 3Y CAGR × Star Rating across your portfolio funds.")

    for i, row in enumerate(plan):
        f     = row["fund"]
        color = BAR_COLORS[i % len(BAR_COLORS)]
        st.markdown(f"""
        <div class='sip-card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:12px;'>
                <div style='flex:1;'>
                    <div class='cat-label'>{row['category']} · {row['pct']}% of budget</div>
                    <div class='fund-name'>{f['name']}</div>
                    <div>
                        <span class='pill' style='background:rgba(0,245,212,0.1);color:#00f5d4;border:1px solid rgba(0,245,212,0.25);'>
                            📈 {f['returns_3y']}% 3Y CAGR
                        </span>
                        <span class='pill' style='background:rgba(255,210,80,0.08);color:#ffd250;border:1px solid rgba(255,210,80,0.2);'>
                            {stars(f['rating'])}
                        </span>
                        <span class='pill' style='background:{f["risk_color"]}18;color:{f["risk_color"]};border:1px solid {f["risk_color"]}44;'>
                            {f['risk']}
                        </span>
                    </div>
                </div>
                <div style='text-align:right;flex-shrink:0;'>
                    <div style='font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:0.1em;text-transform:uppercase;'>Monthly SIP</div>
                    <div style='font-size:22px;font-weight:700;color:{color};font-family:DM Mono,monospace;'>{fmt_inr(row['amount'])}</div>
                    <div style='font-size:10px;color:rgba(255,255,255,0.25);'>Annual: {fmt_inr(row['amount']*12)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Summary Table ──
    st.markdown("#### 📋 Full Summary")
    import pandas as pd
    df = pd.DataFrame([{
        "Category":    r["category"],
        "Best Fund":   r["fund"]["name"],
        "3Y CAGR":     f"{r['fund']['returns_3y']}%",
        "Rating":      stars(r["fund"]["rating"]),
        "Risk":        r["fund"]["risk"],
        "Monthly SIP": fmt_inr(r["amount"]),
        "Annual SIP":  fmt_inr(r["amount"] * 12),
    } for r in plan])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Disclaimer ──
    st.markdown("""
    <div class='disclaimer'>
    * Returns are historical 3Y CAGR estimates. Past performance does not guarantee future results.<br>
    * Best fund selection is scored by 3Y CAGR × Star Rating from your existing config.py portfolio.<br>
    * SIP amounts rounded to nearest ₹100. Consult a SEBI-registered advisor before investing.
    </div>
    """, unsafe_allow_html=True)
