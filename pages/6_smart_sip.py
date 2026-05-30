"""
pages/smart_sip.py  —  Drop this file into your `pages/` folder.
Uses your actual funds from config.py and matches the Taurus dark theme.
"""

import streamlit as st
import math

# ─────────────────────────────────────────────
# Your actual funds from config.py, with
# category tagging + enriched metadata
# ─────────────────────────────────────────────
FUND_UNIVERSE = {
    "Small Cap": [
        {"name": "Bandhan Small Cap Fund",             "code": "147946", "returns_3y": 28.1, "rating": 4, "risk": "Very High"},
        {"name": "Axis Small Cap Fund",                "code": "125354", "returns_3y": 26.1, "rating": 5, "risk": "Very High"},
        {"name": "SBI Small Cap Fund",                 "code": "125497", "returns_3y": 27.8, "rating": 5, "risk": "Very High"},
        {"name": "quant Small Cap Fund",               "code": "120828", "returns_3y": 31.4, "rating": 5, "risk": "Very High"},
    ],
    "Mid Cap": [
        {"name": "Motilal Oswal Midcap Fund",          "code": "127042", "returns_3y": 29.3, "rating": 5, "risk": "High"},
        {"name": "HSBC Midcap Fund",                   "code": "151034", "returns_3y": 22.4, "rating": 4, "risk": "High"},
        {"name": "Kotak Midcap Fund",                  "code": "119775", "returns_3y": 23.1, "rating": 4, "risk": "High"},
        {"name": "quant Mid Cap Fund",                 "code": "120841", "returns_3y": 27.6, "rating": 5, "risk": "High"},
        {"name": "Edelweiss Nifty Midcap150 Momentum 50 Index Fund",
                                                       "code": "150902", "returns_3y": 24.8, "rating": 4, "risk": "High"},
    ],
    "Flexi Cap": [
        {"name": "Edelweiss Flexi Cap Fund",           "code": "140353", "returns_3y": 18.2, "rating": 4, "risk": "Moderate-High"},
        {"name": "Parag Parikh Flexi Cap Fund",        "code": "122639", "returns_3y": 19.7, "rating": 5, "risk": "Moderate-High"},
        {"name": "Kotak Flexicap Fund",                "code": "112090", "returns_3y": 17.3, "rating": 4, "risk": "Moderate-High"},
    ],
    "Large Cap": [
        {"name": "Nippon India Large Cap Fund",        "code": "118632", "returns_3y": 16.4, "rating": 5, "risk": "Low-Moderate"},
    ],
    "Thematic / Global": [
        {"name": "Mirae Asset FANG+",                  "code": "148928", "returns_3y": 14.1, "rating": 4, "risk": "Very High"},
        {"name": "ICICI Pru BHARAT 22 FOF",            "code": "143903", "returns_3y": 22.7, "rating": 4, "risk": "Moderate-High"},
    ],
    "Hybrid / Children": [
        {"name": "SBI Magnum Children's Benefit Fund", "code": "148490", "returns_3y": 17.9, "rating": 4, "risk": "Moderate"},
    ],
}

# Default allocation weights (must sum to 100)
DEFAULT_ALLOC = {
    "Large Cap":          20,
    "Mid Cap":            25,
    "Small Cap":          25,
    "Flexi Cap":          15,
    "Thematic / Global":  10,
    "Hybrid / Children":   5,
}

RISK_COLOR = {
    "Low":           "#22c55e",
    "Low-Moderate":  "#84cc16",
    "Moderate":      "#eab308",
    "Moderate-High": "#f97316",
    "High":          "#ef4444",
    "Very High":     "#dc2626",
}

BAR_COLORS = ["#00f5d4", "#3b82f6", "#a78bfa", "#f59e0b", "#ef4444", "#10b981"]


def best_fund(funds: list) -> dict:
    """Score = returns_3y × rating  → pick highest."""
    return max(funds, key=lambda f: f["returns_3y"] * f["rating"])


def fmt_inr(amount: float) -> str:
    return f"₹{int(amount):,}"


def stars(rating: int) -> str:
    return "★" * rating + "☆" * (5 - rating)


# ─────────────────────────────────────────────
# Taurus-style CSS injected once
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

    /* ── fund card ── */
    .fund-card {
        background: rgba(0,0,0,0.55);
        border: 1px solid rgba(0,245,212,0.18);
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: border 0.25s;
    }
    .fund-card:hover { border-color: rgba(0,245,212,0.55); }

    /* ── stat pill ── */
    .stat-pill {
        display: inline-block;
        background: rgba(0,245,212,0.10);
        border: 1px solid rgba(0,245,212,0.25);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        color: #00f5d4;
        margin-right: 6px;
        margin-bottom: 4px;
        font-family: 'Space Mono', monospace;
    }
    .risk-pill {
        display: inline-block;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
    }
    .amount-big {
        font-family: 'Space Mono', monospace;
        font-size: 22px;
        font-weight: 700;
        color: #00f5d4;
    }
    .category-label {
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: rgba(0,245,212,0.7);
        margin-bottom: 4px;
    }
    .summary-box {
        background: rgba(0,245,212,0.06);
        border: 1px solid rgba(0,245,212,0.20);
        border-radius: 14px;
        padding: 20px 22px;
        margin-bottom: 16px;
        font-family: 'Space Mono', monospace;
    }
    .bar-wrap {
        background: rgba(255,255,255,0.07);
        border-radius: 6px;
        height: 10px;
        overflow: hidden;
        margin-top: 6px;
    }
    .bar-fill {
        height: 100%;
        border-radius: 6px;
    }
    .disclaimer {
        font-size: 11px;
        color: rgba(255,255,255,0.35);
        margin-top: 20px;
        font-family: 'Space Mono', monospace;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Page
# ─────────────────────────────────────────────
inject_css()

st.markdown("## ⚡ Smart SIP Planner")
st.markdown(
    "<p style='color:rgba(255,255,255,0.5);font-size:13px;margin-top:-10px;'>"
    "Best fund picks from your portfolio · Monthly allocation at a glance"
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Budget Input ──
col_a, col_b = st.columns([2, 3])
with col_a:
    monthly_budget = st.number_input(
        "Monthly SIP Budget (₹)",
        min_value=10_000,
        max_value=10_000_000,
        value=150_000,
        step=5_000,
        format="%d",
    )

with col_b:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        f"**Annual commitment:** {fmt_inr(monthly_budget * 12)}  ·  "
        f"**Daily equivalent:** {fmt_inr(monthly_budget / 30)}"
    )

st.markdown("---")

# ── Allocation Sliders (optional expand) ──
with st.expander("⚙️ Customise Category Allocation %", expanded=False):
    st.caption("Adjust how much of your ₹1,50,000 goes into each category. Must total 100%.")
    alloc = {}
    slider_cols = st.columns(2)
    for i, (cat, default_pct) in enumerate(DEFAULT_ALLOC.items()):
        with slider_cols[i % 2]:
            alloc[cat] = st.slider(cat, 0, 60, default_pct, step=5, key=f"sl_{cat}")

    total_alloc = sum(alloc.values())
    if total_alloc != 100:
        st.warning(f"⚠️ Total allocation = **{total_alloc}%** (must be 100%). Adjust sliders.")
else:
    alloc = dict(DEFAULT_ALLOC)
    total_alloc = 100

# ── Generate button ──
if total_alloc == 100:
    generate = st.button("✦ Generate Investment Plan", type="primary", use_container_width=True)
else:
    generate = False
    st.error("Fix allocation percentages above before generating.")

if generate or ("sip_plan" in st.session_state and st.session_state.get("sip_budget") == monthly_budget):
    if generate:
        plan = []
        for cat, pct in alloc.items():
            if pct == 0:
                continue
            funds = FUND_UNIVERSE.get(cat, [])
            if not funds:
                continue
            pick = best_fund(funds)
            amount = math.floor((monthly_budget * pct / 100) / 100) * 100  # round to nearest ₹100
            plan.append({
                "category": cat,
                "pct": pct,
                "fund": pick,
                "amount": amount,
            })
        st.session_state["sip_plan"] = plan
        st.session_state["sip_budget"] = monthly_budget

    plan = st.session_state["sip_plan"]
    total_invested = sum(r["amount"] for r in plan)
    projected_1y   = sum(r["amount"] * 12 * (1 + r["fund"]["returns_3y"] / 100) for r in plan)

    # ── Summary stats ──
    st.markdown("<br>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class='summary-box'>
            <div class='category-label'>Monthly SIP</div>
            <div class='amount-big'>{fmt_inr(total_invested)}</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class='summary-box'>
            <div class='category-label'>Annual Investment</div>
            <div class='amount-big'>{fmt_inr(total_invested * 12)}</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class='summary-box'>
            <div class='category-label'>Projected 1Y Value</div>
            <div class='amount-big' style='color:#a78bfa'>{fmt_inr(projected_1y)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Allocation Bar ──
    st.markdown("#### 📊 Allocation at a Glance")
    for i, row in enumerate(plan):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
            <div style='display:flex;justify-content:space-between;font-size:13px;'>
                <span style='color:rgba(255,255,255,0.75);'>{row['category']}</span>
                <span style='font-family:Space Mono,monospace;color:{color};font-weight:700;'>
                    {fmt_inr(row['amount'])} &nbsp;<span style='color:rgba(255,255,255,0.35);font-size:11px;'>({row['pct']}%)</span>
                </span>
            </div>
            <div class='bar-wrap'>
                <div class='bar-fill' style='width:{row["pct"]}%;background:{color};'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Fund Cards ──
    st.markdown("#### 🏆 Best Fund Per Category")
    st.caption("Ranked by 3Y CAGR × Star Rating from your portfolio.")

    for i, row in enumerate(plan):
        f = row["fund"]
        color = BAR_COLORS[i % len(BAR_COLORS)]
        risk_col = RISK_COLOR.get(f["risk"], "#94a3b8")

        st.markdown(f"""
        <div class='fund-card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                <div>
                    <div class='category-label'>{row['category']} · {row['pct']}% allocation</div>
                    <div style='font-size:16px;font-weight:700;color:white;margin-bottom:8px;'>{f['name']}</div>
                    <span class='stat-pill'>📈 {f['returns_3y']}% 3Y CAGR</span>
                    <span class='stat-pill'>⭐ {stars(f['rating'])}</span>
                    <span class='risk-pill' style='background:{risk_col}22;color:{risk_col};border:1px solid {risk_col}55;'>{f['risk']}</span>
                </div>
                <div style='text-align:right;'>
                    <div style='font-size:11px;color:rgba(255,255,255,0.4);font-family:Space Mono,monospace;'>Monthly SIP</div>
                    <div style='font-size:24px;font-weight:700;color:{color};font-family:Space Mono,monospace;'>{fmt_inr(row['amount'])}</div>
                    <div style='font-size:10px;color:rgba(255,255,255,0.3);'>Code: {f['code']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Summary Table ──
    st.markdown("#### 📋 Full Plan Summary")
    table_data = {
        "Category": [r["category"] for r in plan],
        "Best Fund": [r["fund"]["name"] for r in plan],
        "3Y CAGR": [f"{r['fund']['returns_3y']}%" for r in plan],
        "Risk": [r["fund"]["risk"] for r in plan],
        "Monthly SIP": [fmt_inr(r["amount"]) for r in plan],
        "Annual SIP": [fmt_inr(r["amount"] * 12) for r in plan],
    }
    st.dataframe(table_data, use_container_width=True, hide_index=True)

    # ── Disclaimer ──
    st.markdown("""
    <div class='disclaimer'>
    * Returns shown are historical 3-year CAGR estimates. Past performance is not indicative of future results.<br>
    * Fund selection is based on returns × star rating scoring from your existing portfolio in config.py.<br>
    * Consult a SEBI-registered financial advisor before making investment decisions.<br>
    * SIP amounts are rounded to the nearest ₹100.
    </div>
    """, unsafe_allow_html=True)
