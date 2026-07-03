# pages/6_smart_sip.py

import streamlit as st
import math
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import mutual_funds
from utils.sidebar_style import render_sidebar

# ─────────────────────────────────────────────
# Page Config — MUST be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus: Smart SIP",
    page_icon="🐂",
    layout="wide"
)

render_sidebar("smart_sip")

# ─────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background-color: #020d1a;
    background-image: none;
    position: relative;
    min-height: 100vh;
}
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
    animation: taurus-pulse 8s ease-in-out infinite;
}
.stApp::after {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: radial-gradient(circle, rgba(0,245,212,0.18) 1px, transparent 1px);
    background-size: 38px 38px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.55;
}
@keyframes taurus-pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
.stApp > * { position: relative; z-index: 1; }
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
    border-right: 1px solid rgba(0,245,212,0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
}
.sip-card {
    background: rgba(0,245,212,0.04);
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
.stat-label { font-size:10px; letter-spacing:0.15em; text-transform:uppercase; color:rgba(0,245,212,0.55); margin-bottom:4px; }
.stat-value { font-size:20px; font-weight:700; color:#00f5d4; font-family:'DM Mono',monospace; }
.stat-value-purple { font-size:20px; font-weight:700; color:#a78bfa; font-family:'DM Mono',monospace; }
.cat-label { font-size:10px; letter-spacing:0.14em; text-transform:uppercase; color:rgba(0,245,212,0.6); margin-bottom:2px; }
.fund-name { font-size:15px; font-weight:600; color:#e8f4f0; margin-bottom:8px; }
.pill { display:inline-block; padding:3px 11px; border-radius:20px; font-size:11px; font-weight:600; margin-right:5px; }
.bar-track { background:rgba(255,255,255,0.07); border-radius:4px; height:8px; overflow:hidden; margin-top:5px; }
.ai-reasoning {
    background: rgba(167,139,250,0.06);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 10px;
    font-size: 12px;
    color: rgba(220,210,255,0.75);
    line-height: 1.7;
}
.disclaimer { font-size:11px; color:rgba(255,255,255,0.28); line-height:1.9; margin-top:24px; border-top:1px solid rgba(0,245,212,0.08); padding-top:14px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NAV CAGR calculator — reads local NAVHistory/
# ─────────────────────────────────────────────
NAV_DIR = Path(__file__).parent.parent / "NAVHistory"

RISK_MAP = {
    "International":  ("Very High",     "#dc2626"),
    "Hybrid":         ("Moderate",       "#eab308"),
    "Small Cap":      ("Very High",     "#dc2626"),
    "Mid Cap":        ("High",           "#ef4444"),
    "Flexi Cap":      ("Moderate-High", "#f97316"),
    "Large Cap":      ("Low-Moderate",  "#84cc16"),
    "Thematic":       ("Very High",     "#dc2626"),
}

CATEGORY_DISPLAY = {
    "International": "Thematic / Global",
    "Hybrid":        "Hybrid / Children",
    "Small Cap":     "Small Cap",
    "Mid Cap":       "Mid Cap",
    "Flexi Cap":     "Flexi Cap",
    "Large Cap":     "Large Cap",
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


@st.cache_data(ttl=3600)
def load_all_fund_metrics() -> dict:
    """Load NAV files and compute real 3Y & 5Y CAGR for every fund."""
    def parse_date(s):
        return datetime.strptime(s, "%d-%m-%Y")

    def calc_cagr(nav_list, years):
        if not nav_list:
            return None
        today_nav  = float(nav_list[0]["nav"])
        today_date = parse_date(nav_list[0]["date"])
        target     = today_date - timedelta(days=int(years * 365.25))
        for entry in nav_list:
            d = parse_date(entry["date"])
            if d <= target:
                past_nav     = float(entry["nav"])
                actual_years = (today_date - d).days / 365.25
                return round(((today_nav / past_nav) ** (1 / actual_years) - 1) * 100, 2)
        return None  # not enough history

    metrics = {}
    for fund_name, meta in mutual_funds.items():
        code     = meta["code"]
        category = meta.get("category", "")
        nav_file = NAV_DIR / f"{code}.json"

        cagr_3y = cagr_5y = latest_nav = None
        if nav_file.exists():
            try:
                with open(nav_file) as f:
                    data = json.load(f)
                navs = data.get("data", [])
                if navs:
                    latest_nav = float(navs[0]["nav"])
                    cagr_3y    = calc_cagr(navs, 3)
                    cagr_5y    = calc_cagr(navs, 5)
            except Exception:
                pass

        risk, risk_color = RISK_MAP.get(category, ("Unknown", "#888"))
        display_cat      = CATEGORY_DISPLAY.get(category, category)

        metrics[fund_name] = {
            "code":         code,
            "category":     display_cat,
            "raw_category": category,
            "cagr_3y":      cagr_3y,
            "cagr_5y":      cagr_5y,
            "latest_nav":   latest_nav,
            "risk":         risk,
            "risk_color":   risk_color,
        }
    return metrics


# ─────────────────────────────────────────────
# AI fund selector — calls Claude API
# ─────────────────────────────────────────────
def ai_select_best_fund(category: str, candidates: list, monthly_amount: int) -> dict:
    """
    Ask Claude to pick the best fund from candidates for this category.
    Returns {winner_name, reasoning}
    """
    import anthropic

    fund_lines = "\n".join(
        f"  - {c['name']}: 3Y CAGR={c['cagr_3y']}%, 5Y CAGR={c['cagr_5y']}%, "
        f"Latest NAV=₹{c['latest_nav']}, Risk={c['risk']}"
        for c in candidates
    )

    prompt = f"""You are a mutual fund analyst. A SIP investor wants to invest ₹{monthly_amount:,}/month in the **{category}** category.

Here are the available funds with REAL CAGR calculated from actual NAV history:

{fund_lines}

Pick the SINGLE best fund for a long-term SIP investor. Consider:
1. 3Y CAGR (primary) and 5Y CAGR (consistency check)
2. Risk-adjusted returns
3. Consistency (if 5Y CAGR is significantly lower than 3Y, it may be a recent spike)

Respond in this EXACT JSON format (no markdown, no extra text):
{{
  "winner": "<exact fund name from the list>",
  "reasoning": "<2-3 sentence explanation of why this fund was chosen over the others>"
}}"""

    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.strip()
        # strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return result
    except Exception:
        # Fallback: pick highest 3Y CAGR
        best = max(candidates, key=lambda c: c["cagr_3y"] or 0)
        return {
            "winner": best["name"],
            "reasoning": f"Selected by highest 3Y CAGR: {best['cagr_3y']}%."
        }


def fmt_inr(amount: float) -> str:
    return f"₹{int(amount):,}"

def stars(r: float) -> str:
    full = int(round(r))
    return "★" * full + "☆" * (5 - full)


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
    "AI-powered fund selection · CAGR computed from real NAV history · Best fund per category</p>",
    unsafe_allow_html=True
)
st.divider()

# ─────────────────────────────────────────────
# Load real metrics
# ─────────────────────────────────────────────
with st.spinner("Loading NAV history & computing real returns..."):
    fund_metrics = load_all_fund_metrics()

# Show data freshness
nav_counts = sum(1 for m in fund_metrics.values() if m["cagr_3y"] is not None)
st.caption(f"📡 NAV data loaded for **{nav_counts}/{len(fund_metrics)}** funds · Returns computed from actual NAV history")

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

# Map each display category back to the fund names in that category,
# so the customiser can offer them for select/deselect.
DISPLAY_TO_RAW = {}
for raw_cat, disp_cat in CATEGORY_DISPLAY.items():
    DISPLAY_TO_RAW.setdefault(disp_cat, []).append(raw_cat)

FUNDS_BY_DISPLAY_CAT = {
    disp_cat: [
        name for name, meta in mutual_funds.items()
        if meta.get("category") in raw_cats
    ]
    for disp_cat, raw_cats in DISPLAY_TO_RAW.items()
}

alloc = dict(DEFAULT_ALLOC)
selected_funds = dict(FUNDS_BY_DISPLAY_CAT)
total = 100

with st.expander("⚙️  Customise allocation %", expanded=False):
    st.caption("Adjust category weights and pick which of your funds are eligible in each category. Weights must total 100%.")
    alloc = {}
    selected_funds = {}
    c1, c2 = st.columns(2)
    for i, (cat, default) in enumerate(DEFAULT_ALLOC.items()):
        with (c1 if i % 2 == 0 else c2):
            alloc[cat] = st.slider(cat, 0, 60, default, step=5, key=f"sl_{cat}")
            cat_funds = FUNDS_BY_DISPLAY_CAT.get(cat, [])
            selected_funds[cat] = st.multiselect(
                f"Eligible {cat} funds",
                options=cat_funds,
                default=cat_funds,
                key=f"funds_{cat}",
                label_visibility="collapsed",
            )
            st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)
    total = sum(alloc.values())
    if total != 100:
        st.warning(f"Total = **{total}%** — must be exactly 100%.")

# ─────────────────────────────────────────────
# Generate button
# ─────────────────────────────────────────────
if total != 100:
    st.error("Fix allocation percentages before generating.")
    st.stop()

generate = st.button("✦  Generate AI Investment Plan", type="primary", use_container_width=True)

if generate or "sip_plan" in st.session_state:

    if generate:
        plan = []
        st.session_state.pop("sip_plan", None)  # clear cache on regenerate

        for cat, pct in alloc.items():
            if pct == 0:
                continue

            # Get selected, eligible funds in this display category with valid 3Y CAGR
            eligible_names = selected_funds.get(cat, list(fund_metrics.keys()))
            candidates = [
                {"name": name, **meta}
                for name, meta in fund_metrics.items()
                if meta["category"] == cat
                and meta["cagr_3y"] is not None
                and name in eligible_names
            ]
            if not candidates:
                continue

            amount = math.floor((monthly_budget * pct / 100) / 100) * 100

            # AI selection
            with st.spinner(f"🤖 AI analysing {cat} funds..."):
                ai_result = ai_select_best_fund(cat, candidates, amount)

            winner_name = ai_result.get("winner", "").strip()
            reasoning   = ai_result.get("reasoning", "")

            # Match winner back to candidates dict (which always has "name" key)
            winner_meta = next(
                (c for c in candidates if c["name"] == winner_name),
                None
            )
            if not winner_meta:
                # AI returned a name that doesn't match exactly — fallback to highest 3Y CAGR
                winner_meta = max(candidates, key=lambda c: c["cagr_3y"] or 0)
                winner_name = winner_meta["name"]
                reasoning   = reasoning or f"Selected by highest 3Y CAGR: {winner_meta['cagr_3y']}%."

            plan.append({
                "category":  cat,
                "pct":       pct,
                "amount":    amount,
                "fund_name": winner_name,
                "fund":      winner_meta,
                "reasoning": reasoning,
                "candidates_count": len(candidates),
            })

        st.session_state["sip_plan"]   = plan
        st.session_state["sip_budget"] = monthly_budget

    plan = st.session_state["sip_plan"]
    # Guard: invalidate any stale plan that doesn't have the current fund dict shape (cagr_3y key)
    if plan and "cagr_3y" not in plan[0].get("fund", {}):
        del st.session_state["sip_plan"]
        st.info("🔄 Your previous plan used an older format. Click **Generate** to rebuild with real NAV data.")
        st.stop()
    total_m = sum(r["amount"] for r in plan)
    # Projected 1Y using real 3Y CAGR — use .get() as final safety net
    proj_1y = sum(r["amount"] * 12 * (1 + (r["fund"].get("cagr_3y") or 0) / 100) for r in plan)

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
    st.markdown("#### 🏆 AI-Selected Best Fund Per Category")
    st.caption("Claude AI analysed all funds per category using real 3Y & 5Y CAGR from NAV history.")

    for i, row in enumerate(plan):
        f     = row["fund"]
        color = BAR_COLORS[i % len(BAR_COLORS)]
        cagr3 = f.get("cagr_3y") or 0
        cagr5 = f.get("cagr_5y")
        cagr5_str = f"{cagr5}%" if cagr5 else "N/A"

        st.markdown(f"""
        <div class='sip-card'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:12px;'>
                <div style='flex:1;'>
                    <div class='cat-label'>{row['category']} · {row['pct']}% of budget · {row['candidates_count']} funds analysed</div>
                    <div class='fund-name'>{row['fund_name']}</div>
                    <div>
                        <span class='pill' style='background:rgba(0,245,212,0.1);color:#00f5d4;border:1px solid rgba(0,245,212,0.25);'>
                            📈 {cagr3}% 3Y CAGR
                        </span>
                        <span class='pill' style='background:rgba(59,130,246,0.1);color:#60a5fa;border:1px solid rgba(59,130,246,0.25);'>
                            📊 {cagr5_str} 5Y CAGR
                        </span>
                        <span class='pill' style='background:{f["risk_color"]}18;color:{f["risk_color"]};border:1px solid {f["risk_color"]}44;'>
                            {f['risk']}
                        </span>
                    </div>
                    <div class='ai-reasoning'>
                        🤖 <b style='color:rgba(167,139,250,0.9);'>AI Reasoning:</b> {row['reasoning']}
                    </div>
                </div>
                <div style='text-align:right;flex-shrink:0;'>
                    <div style='font-size:10px;color:rgba(255,255,255,0.3);letter-spacing:0.1em;text-transform:uppercase;'>Monthly SIP</div>
                    <div style='font-size:22px;font-weight:700;color:{color};font-family:DM Mono,monospace;'>{fmt_inr(row['amount'])}</div>
                    <div style='font-size:10px;color:rgba(255,255,255,0.25);'>Annual: {fmt_inr(row['amount']*12)}</div>
                    <div style='font-size:10px;color:rgba(255,255,255,0.2);margin-top:4px;'>NAV: ₹{f.get('latest_nav','—')}</div>
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
        "AI Pick":     r["fund_name"],
        "3Y CAGR":     f"{r['fund'].get('cagr_3y')}%" if r['fund'].get('cagr_3y') else "N/A",
        "5Y CAGR":     f"{r['fund'].get('cagr_5y')}%" if r['fund'].get('cagr_5y') else "N/A",
        "Latest NAV":  f"₹{r['fund'].get('latest_nav')}" if r['fund'].get('latest_nav') else "N/A",
        "Risk":        r["fund"].get("risk", "—"),
        "Monthly SIP": fmt_inr(r["amount"]),
        "Annual SIP":  fmt_inr(r["amount"] * 12),
    } for r in plan])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Disclaimer ──
    st.markdown("""
    <div class='disclaimer'>
    * 3Y & 5Y CAGR figures are computed directly from NAV history files in <code>NAVHistory/</code> — not estimated.<br>
    * AI fund selection uses Claude to weigh 3Y CAGR, 5Y CAGR consistency, and risk profile.<br>
    * SIP amounts rounded to nearest ₹100. Past performance does not guarantee future results.<br>
    * Consult a SEBI-registered advisor before investing.
    </div>
    """, unsafe_allow_html=True)
