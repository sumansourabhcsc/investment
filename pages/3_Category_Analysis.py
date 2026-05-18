import streamlit as st
import json
import requests
import re
from config import mutual_funds

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus – Category Analysis",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    color: #e8e2d5;
}

.stApp {
    background-color: #080b0f;
    background-image:
        radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(0, 245, 212, 0.07) 0%, transparent 65%),
        radial-gradient(ellipse 60% 80% at 85% 75%,  rgba(0, 180, 245, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 50% 100%, rgba(0, 245, 212, 0.04) 0%, transparent 55%);
    background-attachment: fixed;
    min-height: 100vh;
    position: relative;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 55% at 8% 18%,  rgba(0,245,212,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 55% 70% at 88% 72%, rgba(0,140,255,0.05) 0%, transparent 55%);
    z-index: 0;
    pointer-events: none;
    animation: taurus-pulse 8s ease-in-out infinite;
}

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
    border-right: 1px solid rgba(0,245,212,0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(12px);
}

#MainMenu, footer { visibility: hidden; }

.block-container {
    padding-top: 2rem !important;
    max-width: 1200px !important;
}

.cat-card {
    background: rgba(8,14,20,0.82);
    border: 1px solid rgba(0,245,212,0.15);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.2s;
}
.cat-card:hover {
    border-color: rgba(0,245,212,0.4);
    transform: translateY(-2px);
}
.cat-card-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 14px 14px 0 0;
}
.cat-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    color: #dff5f0;
    margin-bottom: 4px;
}
.cat-count {
    font-size: 11px;
    color: rgba(0,245,212,0.55);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.fund-chip {
    display: inline-block;
    background: rgba(0,245,212,0.07);
    border: 1px solid rgba(0,245,212,0.18);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 11px;
    color: rgba(220,240,235,0.75);
    margin: 3px 3px 0 0;
}

.alloc-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}
.alloc-label {
    font-size: 11px;
    color: rgba(255,255,255,0.5);
    width: 130px;
    flex-shrink: 0;
}
.alloc-bar-wrap {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 3px;
    overflow: hidden;
}
.alloc-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.6s ease;
}
.alloc-pct {
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    width: 38px;
    text-align: right;
    flex-shrink: 0;
}

/* ── AI Analysis box ── */
.ai-box {
    background: rgba(6, 18, 30, 0.9);
    border: 1px solid rgba(0,245,212,0.25);
    border-radius: 14px;
    padding: 24px 26px;
    margin-top: 6px;
    position: relative;
    overflow: hidden;
}
.ai-box-header {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* ── Insight item card ── */
.insight-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.insight-tag {
    display: inline-block;
    border-radius: 5px;
    padding: 2px 9px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.insight-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #dff5f0;
    margin-bottom: 5px;
}
.insight-body {
    font-size: 12px;
    color: rgba(220,235,230,0.7);
    line-height: 1.7;
}

/* ── Overlap badge ── */
.overlap-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    margin: 4px 4px 4px 0;
    border: 1px solid;
}

/* ── Metric pill ── */
.metric-pill {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    background: rgba(0,245,212,0.07);
    border: 1px solid rgba(0,245,212,0.18);
    border-radius: 10px;
    padding: 10px 18px;
    margin: 4px;
}
.metric-pill-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #00f5d4;
    line-height: 1;
}
.metric-pill-lbl {
    font-size: 10px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}

.risk-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.risk-high   { background: rgba(255,107,107,0.15); border: 1px solid rgba(255,107,107,0.4); color: #ff6b6b; }
.risk-medium { background: rgba(255,190,80,0.15);  border: 1px solid rgba(255,190,80,0.4);  color: #ffbe50; }
.risk-low    { background: rgba(0,245,160,0.15);   border: 1px solid rgba(0,245,160,0.4);   color: #00f5a0; }

.stButton > button[kind="primary"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, rgba(0,245,212,0.12), rgba(0,201,255,0.08)) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0,245,212,0.4) !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.25s !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(0,245,212,0.22), rgba(0,201,255,0.15)) !important;
    border-color: rgba(0,245,212,0.7) !important;
    transform: translateY(-1px) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Secrets
# ─────────────────────────────────────────────
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# ─────────────────────────────────────────────
# Category metadata
# ─────────────────────────────────────────────
CATEGORY_META = {
    "Small Cap":     {"color": "#ff6b6b", "risk": "high",   "risk_label": "High Risk",   "gradient": "linear-gradient(90deg,#ff6b6b,#ff8c42)"},
    "Mid Cap":       {"color": "#ffbe50", "risk": "medium", "risk_label": "Medium Risk",  "gradient": "linear-gradient(90deg,#ffbe50,#ffd700)"},
    "Large Cap":     {"color": "#00f5a0", "risk": "low",    "risk_label": "Lower Risk",   "gradient": "linear-gradient(90deg,#00f5a0,#00c9ff)"},
    "Flexi Cap":     {"color": "#00c9ff", "risk": "medium", "risk_label": "Medium Risk",  "gradient": "linear-gradient(90deg,#00c9ff,#a78bfa)"},
    "International": {"color": "#a78bfa", "risk": "high",   "risk_label": "High Risk",   "gradient": "linear-gradient(90deg,#a78bfa,#f472b6)"},
    "Hybrid":        {"color": "#34d399", "risk": "low",    "risk_label": "Lower Risk",   "gradient": "linear-gradient(90deg,#34d399,#00f5d4)"},
    "ELSS":          {"color": "#f472b6", "risk": "medium", "risk_label": "Tax Saving",   "gradient": "linear-gradient(90deg,#f472b6,#a78bfa)"},
    "Index":         {"color": "#60a5fa", "risk": "low",    "risk_label": "Passive",      "gradient": "linear-gradient(90deg,#60a5fa,#00c9ff)"},
    "Debt":          {"color": "#6ee7b7", "risk": "low",    "risk_label": "Low Risk",     "gradient": "linear-gradient(90deg,#6ee7b7,#34d399)"},
    "Thematic":      {"color": "#fb923c", "risk": "high",   "risk_label": "High Risk",    "gradient": "linear-gradient(90deg,#fb923c,#ff6b6b)"},
}

# ─────────────────────────────────────────────
# Build enriched category data from config
# ─────────────────────────────────────────────
def build_category_data():
    """Group funds by category, carrying over any metadata from config."""
    cat_map = {}
    for fund_name, info in mutual_funds.items():
        cat = info.get("category", "Other")
        if cat not in cat_map:
            cat_map[cat] = []
        cat_map[cat].append({
            "name": fund_name,
            # Pull whatever extra keys exist in config — expense_ratio, returns, aum, etc.
            "expense_ratio": info.get("expense_ratio"),
            "cagr_3y": info.get("cagr_3y") or info.get("returns_3y"),
            "cagr_5y": info.get("cagr_5y") or info.get("returns_5y"),
            "aum_cr": info.get("aum_cr") or info.get("aum"),
            "fund_manager": info.get("fund_manager"),
            "benchmark": info.get("benchmark"),
            "style": info.get("style"),  # e.g. "Growth", "Value", "Blend"
            "allocation_pct": info.get("allocation_pct"),  # actual weight if available
        })
    return cat_map

category_data = build_category_data()
total_funds = sum(len(v) for v in category_data.values())

# Compute allocation weight per category (use allocation_pct if available, else equal weight)
def get_alloc_pct(funds_list):
    weights = [f.get("allocation_pct") for f in funds_list if f.get("allocation_pct") is not None]
    if weights and len(weights) == len(funds_list):
        return sum(weights)
    return len(funds_list) / total_funds * 100

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
    background:linear-gradient(135deg,#00f5d4 0%,#00c9ff 55%,#a78bfa 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;">🎯 Category Analysis & Rebalancing</span>
</div>
<div style="font-size:12px;color:rgba(255,255,255,0.4);
  letter-spacing:0.1em;text-transform:uppercase;margin-bottom:24px;">
  Portfolio breakdown by category · AI-powered rebalancing · Strategic insights
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Top metrics row
# ─────────────────────────────────────────────
m_cols = st.columns(5)
fund_count_per_cat = {cat: len(funds) for cat, funds in category_data.items()}
metrics = [
    (str(total_funds), "Total Funds"),
    (str(len(category_data)), "Categories"),
    (str(fund_count_per_cat.get("Small Cap", 0)), "Small Cap"),
    (str(fund_count_per_cat.get("Mid Cap", 0)), "Mid Cap"),
    (str(fund_count_per_cat.get("Flexi Cap", 0) + fund_count_per_cat.get("Large Cap", 0)), "Stable Funds"),
]
for col, (val, lbl) in zip(m_cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-pill" style="width:100%;box-sizing:border-box;">
          <div class="metric-pill-val">{val}</div>
          <div class="metric-pill-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Two-column layout
# ─────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("""
    <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
      color:#00f5d4;margin-bottom:14px;">⬡ Category Breakdown</div>
    """, unsafe_allow_html=True)

    for cat, funds in sorted(category_data.items(), key=lambda x: -len(x[1])):
        meta = CATEGORY_META.get(cat, {"color": "#888", "risk": "medium",
                                       "risk_label": "Medium Risk",
                                       "gradient": "linear-gradient(90deg,#888,#aaa)"})
        risk_cls = f"risk-{meta['risk']}"
        chips = " ".join(f'<span class="fund-chip">{f["name"]}</span>' for f in funds)
        alloc = get_alloc_pct(funds)

        st.markdown(f"""
        <div class="cat-card">
          <div class="cat-card-accent" style="background:{meta['gradient']};"></div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <div class="cat-title">{cat}</div>
            <span class="risk-badge {risk_cls}">{meta['risk_label']}</span>
          </div>
          <div class="cat-count">{len(funds)} fund{'s' if len(funds)>1 else ''} · {alloc:.0f}% of portfolio</div>
          <div>{chips}</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
      color:#00f5d4;margin-bottom:14px;">⬡ Allocation Weight</div>
    """, unsafe_allow_html=True)

    for cat, funds in sorted(category_data.items(), key=lambda x: -get_alloc_pct(x[1])):
        meta = CATEGORY_META.get(cat, {"color": "#888", "gradient": "linear-gradient(90deg,#888,#aaa)"})
        pct = get_alloc_pct(funds)
        st.markdown(f"""
        <div class="alloc-row">
          <div class="alloc-label" style="color:rgba(255,255,255,0.7);">{cat}</div>
          <div class="alloc-bar-wrap">
            <div class="alloc-bar-fill" style="width:{pct:.0f}%;background:{meta['gradient']};"></div>
          </div>
          <div class="alloc-pct">{pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Risk concentration
    high_risk_count = sum(len(v) for k, v in category_data.items()
                          if CATEGORY_META.get(k, {}).get("risk") == "high")
    high_risk_pct = high_risk_count / total_funds * 100
    color = "#ff6b6b" if high_risk_pct > 40 else "#ffbe50" if high_risk_pct > 25 else "#00f5a0"
    label = "⚠️ High Concentration" if high_risk_pct > 40 else "⚡ Moderate" if high_risk_pct > 25 else "✅ Balanced"
    st.markdown(f"""
    <div style="background:rgba(8,14,20,0.7);border:1px solid {color}44;border-radius:10px;
      padding:14px 16px;margin-top:12px;">
      <div style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;
        color:{color};margin-bottom:4px;">Risk Concentration</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:{color};">{high_risk_pct:.0f}%</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px;">
        in High-Risk categories<br>
        <span style="color:{color};font-weight:600;">{label}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ─────────────────────────────────────────────
# AI Analysis Section
# ─────────────────────────────────────────────
st.markdown("""
<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
  color:#00f5d4;margin-bottom:6px;">⬡ AI Portfolio Intelligence</div>
<div style="font-size:12px;color:rgba(255,255,255,0.35);margin-bottom:18px;">
  Powered by Claude · Deep analysis with actionable rebalancing advice
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    risk_profile = st.selectbox(
        "Your Risk Profile",
        ["Aggressive", "Moderate", "Conservative"],
        index=0,
    )
with c2:
    investment_horizon = st.selectbox(
        "Investment Horizon",
        ["< 3 Years", "3–5 Years", "5–10 Years", "10+ Years"],
        index=2,
    )
with c3:
    monthly_sip = st.number_input(
        "Monthly SIP Amount (₹) — optional",
        min_value=0,
        value=0,
        step=1000,
    )

# Advanced options expander
with st.expander("⚙️ Advanced Options"):
    ca, cb = st.columns(2)
    with ca:
        portfolio_value = st.number_input(
            "Total Portfolio Value (₹) — optional",
            min_value=0,
            value=0,
            step=10000,
        )
    with cb:
        tax_bracket = st.selectbox(
            "Income Tax Bracket",
            ["Not specified", "5%", "20%", "30%"],
            index=0,
        )

st.markdown("<br>", unsafe_allow_html=True)
analyse_btn = st.button("🤖  Run Deep AI Analysis", type="primary")

if not analyse_btn:
    st.markdown("""
    <div style="text-align:center;opacity:0.3;padding:60px 20px;">
      <div style="font-size:48px;">🎯</div>
      <div style="margin-top:12px;font-size:14px;">Set your profile and hit Run Analysis</div>
      <div style="font-size:12px;margin-top:6px;opacity:0.7;">
        Claude will dig into your category mix, flag overlaps, and suggest moves
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# Build enriched portfolio context for Claude
# ─────────────────────────────────────────────
portfolio_for_prompt = []
for cat, funds in category_data.items():
    meta = CATEGORY_META.get(cat, {})
    fund_details = []
    for f in funds:
        fd = {"name": f["name"]}
        if f.get("expense_ratio"):  fd["expense_ratio"] = f["expense_ratio"]
        if f.get("cagr_3y"):        fd["3y_cagr"] = f["cagr_3y"]
        if f.get("cagr_5y"):        fd["5y_cagr"] = f["cagr_5y"]
        if f.get("aum_cr"):         fd["aum_cr"] = f["aum_cr"]
        if f.get("fund_manager"):   fd["fund_manager"] = f["fund_manager"]
        if f.get("style"):          fd["style"] = f["style"]
        if f.get("benchmark"):      fd["benchmark"] = f["benchmark"]
        if f.get("allocation_pct"): fd["current_allocation_pct"] = f["allocation_pct"]
        fund_details.append(fd)

    portfolio_for_prompt.append({
        "category": cat,
        "risk_level": meta.get("risk_label", "Medium Risk"),
        "fund_count": len(funds),
        "allocation_pct": round(get_alloc_pct(funds), 1),
        "funds": fund_details,
    })

sip_line     = f"₹{monthly_sip:,}/month" if monthly_sip > 0 else "not specified"
portval_line = f"₹{portfolio_value:,}" if portfolio_value > 0 else "not specified"
tax_line     = tax_bracket if tax_bracket != "Not specified" else "not specified"

# ─────────────────────────────────────────────
# Prompt — structured JSON output
# ─────────────────────────────────────────────
PROMPT = f"""You are a senior Indian mutual fund portfolio advisor with deep expertise in SEBI regulations, AMC fund strategies, and Indian market dynamics. Analyse this portfolio thoroughly and return ONLY a valid JSON object — no markdown, no explanation outside the JSON.

INVESTOR PROFILE:
- Risk Profile: {risk_profile}
- Investment Horizon: {investment_horizon}
- Monthly SIP: {sip_line}
- Total Portfolio Value: {portval_line}
- Tax Bracket: {tax_line}

PORTFOLIO (by category):
{json.dumps(portfolio_for_prompt, indent=2)}

Return exactly this JSON structure (fill every field with specific, actionable content):

{{
  "health_score": {{
    "score": <integer 0-100>,
    "grade": "<A/B/C/D>",
    "summary": "<2-3 sentence overall health assessment>",
    "strengths": ["<specific strength 1>", "<specific strength 2>"],
    "weaknesses": ["<specific weakness 1>", "<specific weakness 2>"]
  }},

  "category_analysis": [
    {{
      "category": "<category name>",
      "verdict": "<Overweight | Underweight | Optimal | Missing>",
      "current_pct": <number>,
      "ideal_pct_for_profile": <number>,
      "commentary": "<2-3 sentences: what's good/bad about this category's weight given the investor's profile, horizon, and market conditions in 2025-26>",
      "overlap_risk": "<High | Medium | Low | None>",
      "overlap_note": "<if High or Medium: which funds overlap and why>"
    }}
  ],

  "rebalancing_moves": [
    {{
      "priority": "<High | Medium | Low>",
      "action": "<Increase SIP | Reduce SIP | Exit | Add New Fund | Switch | Merge>",
      "category": "<category>",
      "fund": "<specific fund name or 'any in category'>",
      "target_fund": "<if switching/merging — the fund to move into>",
      "reason": "<specific 2-3 sentence rationale referencing the investor's profile, current allocation, and market outlook>",
      "expected_impact": "<what this move achieves — e.g. reduces overlap, improves risk-adjusted return>"
    }}
  ],

  "fund_redundancies": [
    {{
      "funds": ["<fund A>", "<fund B>"],
      "category": "<category>",
      "overlap_type": "<Same benchmark | Same style | High portfolio overlap | Same fund house>",
      "recommendation": "<keep A, exit B — or merge into — and exactly why>",
      "urgency": "<Immediate | Next rebalancing | Optional>"
    }}
  ],

  "missing_categories": [
    {{
      "category": "<e.g. ELSS, Gold, Debt, Index Nifty 50, Thematic>",
      "reason_to_add": "<why this matters for the investor's specific profile and horizon>",
      "suggested_allocation_pct": <number>,
      "example_funds": ["<fund name 1>", "<fund name 2>"]
    }}
  ],

  "strategic_insights": [
    {{
      "theme": "<short title e.g. 'Tax Efficiency via ELSS', 'Index vs Active Balance', 'SIP Step-Up Strategy'>",
      "insight": "<3-4 sentences of specific, forward-looking advice relevant to Indian market 2025-26 and this investor's profile>",
      "action_item": "<one concrete next step>"
    }}
  ],

  "sip_allocation_advice": {{
    "commentary": "<if SIP was provided: how to split the monthly SIP across categories for best impact; if not provided: general advice on how to structure SIP given the profile>",
    "suggested_split": [
      {{"category": "<cat>", "pct": <number>, "rationale": "<brief>"}}
    ]
  }}
}}

Be brutally specific. Name actual funds from the portfolio. Reference real Indian AMCs, benchmarks (Nifty 50, Nifty Midcap 150, etc.), and 2025-26 market context (rate cycle, global macro, domestic consumption themes). Do not use placeholder text."""

# ─────────────────────────────────────────────
# Call Claude
# ─────────────────────────────────────────────
with st.spinner("Claude is analysing your portfolio in depth..."):
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 4000,   # increased for richer output
                "system":     "You are a senior Indian mutual fund advisor. Always respond with valid JSON only. No markdown code fences, no extra text.",
                "messages":   [{"role": "user", "content": PROMPT}],
            },
            timeout=90,
        )
        if resp.status_code != 200:
            st.error(f"API error {resp.status_code}: {resp.text}")
            st.stop()

        raw_text = resp.json()["content"][0]["text"].strip()

        # Strip markdown fences if model adds them despite instructions
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"\s*```$", "", raw_text)

        analysis = json.loads(raw_text)

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response as JSON: {e}")
        with st.expander("Raw response"):
            st.text(raw_text)
        st.stop()
    except Exception as e:
        st.error(f"Failed to get AI analysis: {e}")
        st.stop()

# ─────────────────────────────────────────────
# Render results
# ─────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)

# ── 1. Health Score ──────────────────────────
hs = analysis.get("health_score", {})
score_val = hs.get("score", 0)
grade     = hs.get("grade", "—")
score_color = "#00f5a0" if score_val >= 70 else "#ffbe50" if score_val >= 50 else "#ff6b6b"

st.markdown(f"""
<div class="ai-box" style="margin-bottom:20px;border-color:{score_color}44;">
  <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
    background:linear-gradient(90deg,{score_color},{score_color}44);"></div>
  <div class="ai-box-header" style="color:{score_color};">📊 Portfolio Health Score</div>
  <div style="display:flex;align-items:center;gap:28px;margin-bottom:18px;flex-wrap:wrap;">
    <div style="text-align:center;">
      <div style="font-family:'Syne',sans-serif;font-size:3.5rem;font-weight:800;
        color:{score_color};line-height:1;">{score_val}</div>
      <div style="font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:0.15em;
        text-transform:uppercase;">out of 100</div>
    </div>
    <div style="background:rgba(255,255,255,0.05);border-radius:12px;padding:10px 20px;
      text-align:center;">
      <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
        color:{score_color};">{grade}</div>
      <div style="font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:0.1em;">GRADE</div>
    </div>
    <div style="flex:1;min-width:180px;">
      <div style="height:8px;background:rgba(255,255,255,0.06);border-radius:4px;overflow:hidden;margin-bottom:8px;">
        <div style="width:{score_val}%;height:100%;border-radius:4px;
          background:linear-gradient(90deg,{score_color},{score_color}88);"></div>
      </div>
      <div style="font-size:12px;color:rgba(220,235,230,0.75);line-height:1.6;">{hs.get("summary","")}</div>
    </div>
  </div>
  <div style="display:flex;gap:12px;flex-wrap:wrap;">
    <div style="flex:1;min-width:200px;background:rgba(0,245,160,0.05);border:1px solid rgba(0,245,160,0.15);
      border-radius:10px;padding:12px 14px;">
      <div style="font-size:10px;color:#00f5a0;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:8px;">✅ Strengths</div>
      {"".join(f'<div style="font-size:12px;color:rgba(220,235,230,0.75);margin-bottom:5px;">· {s}</div>' for s in hs.get("strengths",[]))}
    </div>
    <div style="flex:1;min-width:200px;background:rgba(255,107,107,0.05);border:1px solid rgba(255,107,107,0.15);
      border-radius:10px;padding:12px 14px;">
      <div style="font-size:10px;color:#ff6b6b;letter-spacing:0.12em;text-transform:uppercase;
        margin-bottom:8px;">⚠️ Weaknesses</div>
      {"".join(f'<div style="font-size:12px;color:rgba(220,235,230,0.75);margin-bottom:5px;">· {w}</div>' for w in hs.get("weaknesses",[]))}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 2. Category Analysis ─────────────────────
cat_items = analysis.get("category_analysis", [])
if cat_items:
    st.markdown("""
    <div class="ai-box" style="margin-bottom:20px;border-color:rgba(0,201,255,0.3);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,#00c9ff,#00c9ff44);"></div>
      <div class="ai-box-header" style="color:#00c9ff;">🔍 Category Concentration Analysis</div>
    """, unsafe_allow_html=True)

    for item in cat_items:
        verdict = item.get("verdict", "")
        verdict_colors = {
            "Overweight": ("#ff6b6b", "rgba(255,107,107,0.1)"),
            "Underweight": ("#ffbe50", "rgba(255,190,80,0.1)"),
            "Optimal": ("#00f5a0", "rgba(0,245,160,0.1)"),
            "Missing": ("#a78bfa", "rgba(167,139,250,0.1)"),
        }
        vc, vbg = verdict_colors.get(verdict, ("#888", "rgba(255,255,255,0.05)"))
        overlap = item.get("overlap_risk", "None")
        overlap_colors = {"High": "#ff6b6b", "Medium": "#ffbe50", "Low": "#00f5a0", "None": "#888"}
        oc = overlap_colors.get(overlap, "#888")
        curr = item.get("current_pct", 0)
        ideal = item.get("ideal_pct_for_profile", 0)

        st.markdown(f"""
        <div class="insight-item" style="margin-bottom:10px;">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
            <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#dff5f0;">
              {item.get("category","")}
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
              <span style="background:{vbg};border:1px solid {vc}44;color:{vc};border-radius:6px;
                padding:2px 10px;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">
                {verdict}
              </span>
              <span style="font-size:11px;color:rgba(255,255,255,0.4);">
                Current: <b style="color:#dff5f0;">{curr:.0f}%</b>
                &nbsp;→&nbsp; Ideal: <b style="color:{vc};">{ideal:.0f}%</b>
              </span>
            </div>
          </div>
          <div style="font-size:12px;color:rgba(220,235,230,0.72);line-height:1.7;margin-bottom:8px;">
            {item.get("commentary","")}
          </div>
          {"" if overlap in ("None","Low") else f'''
          <div style="background:rgba(255,255,255,0.03);border-left:3px solid {oc};
            border-radius:0 6px 6px 0;padding:8px 12px;margin-top:6px;">
            <span style="font-size:10px;color:{oc};font-weight:700;letter-spacing:0.1em;
              text-transform:uppercase;">Overlap Risk: {overlap}</span>
            <div style="font-size:11px;color:rgba(220,235,230,0.65);margin-top:4px;">{item.get("overlap_note","")}</div>
          </div>'''}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── 3. Rebalancing Moves ─────────────────────
moves = analysis.get("rebalancing_moves", [])
if moves:
    st.markdown("""
    <div class="ai-box" style="margin-bottom:20px;border-color:rgba(255,190,80,0.3);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,#ffbe50,#ffbe5044);"></div>
      <div class="ai-box-header" style="color:#ffbe50;">⚖️ Rebalancing Recommendations</div>
    """, unsafe_allow_html=True)

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    moves_sorted = sorted(moves, key=lambda x: priority_order.get(x.get("priority","Low"), 2))

    action_colors = {
        "Exit":         ("#ff6b6b", "rgba(255,107,107,0.12)"),
        "Reduce SIP":   ("#ff8c42", "rgba(255,140,66,0.1)"),
        "Switch":       ("#ffbe50", "rgba(255,190,80,0.1)"),
        "Merge":        ("#ffbe50", "rgba(255,190,80,0.1)"),
        "Increase SIP": ("#00f5a0", "rgba(0,245,160,0.1)"),
        "Add New Fund": ("#00c9ff", "rgba(0,201,255,0.1)"),
    }
    priority_colors = {"High": "#ff6b6b", "Medium": "#ffbe50", "Low": "#00f5a0"}

    for m in moves_sorted:
        action = m.get("action", "")
        ac, abg = action_colors.get(action, ("#a78bfa", "rgba(167,139,250,0.1)"))
        pc = priority_colors.get(m.get("priority","Low"), "#888")
        target = m.get("target_fund")
        target_html = f'<span style="color:#00c9ff;"> → {target}</span>' if target else ""

        st.markdown(f"""
        <div class="insight-item" style="border-left:3px solid {ac};margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;">
            <span style="background:{abg};border:1px solid {ac}44;color:{ac};border-radius:6px;
              padding:3px 10px;font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">
              {action}
            </span>
            <span style="font-size:12px;color:#dff5f0;font-weight:600;">
              {m.get("fund","")}{target_html}
            </span>
            <span style="font-size:10px;color:rgba(255,255,255,0.4);">[{m.get("category","")}]</span>
            <span style="margin-left:auto;font-size:10px;color:{pc};font-weight:700;
              letter-spacing:0.1em;text-transform:uppercase;">{m.get("priority","")} Priority</span>
          </div>
          <div style="font-size:12px;color:rgba(220,235,230,0.72);line-height:1.7;margin-bottom:6px;">
            {m.get("reason","")}
          </div>
          <div style="font-size:11px;color:rgba(0,245,212,0.6);font-style:italic;">
            Impact: {m.get("expected_impact","")}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── 4. Fund Redundancies ─────────────────────
redundancies = analysis.get("fund_redundancies", [])
if redundancies:
    st.markdown("""
    <div class="ai-box" style="margin-bottom:20px;border-color:rgba(255,107,107,0.3);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,#ff6b6b,#ff6b6b44);"></div>
      <div class="ai-box-header" style="color:#ff6b6b;">🔄 Fund Redundancies & Overlaps</div>
    """, unsafe_allow_html=True)

    urgency_colors = {"Immediate": "#ff6b6b", "Next rebalancing": "#ffbe50", "Optional": "#888"}

    for r in redundancies:
        uc = urgency_colors.get(r.get("urgency","Optional"), "#888")
        funds_html = " + ".join(
            f'<span style="background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.2);'
            f'border-radius:6px;padding:2px 9px;font-size:11px;color:#ff9999;">{f}</span>'
            for f in r.get("funds", [])
        )
        st.markdown(f"""
        <div class="insight-item" style="margin-bottom:10px;">
          <div style="display:flex;align-items:center;justify-content:space-between;
            flex-wrap:wrap;gap:8px;margin-bottom:8px;">
            <div>{funds_html}</div>
            <span style="font-size:10px;color:{uc};font-weight:700;letter-spacing:0.1em;
              text-transform:uppercase;">{r.get("urgency","")}</span>
          </div>
          <div style="font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:0.1em;
            text-transform:uppercase;margin-bottom:6px;">{r.get("overlap_type","")}</div>
          <div style="font-size:12px;color:rgba(220,235,230,0.72);line-height:1.7;">
            {r.get("recommendation","")}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── 5. Missing Categories ────────────────────
missing = analysis.get("missing_categories", [])
if missing:
    st.markdown("""
    <div class="ai-box" style="margin-bottom:20px;border-color:rgba(167,139,250,0.3);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,#a78bfa,#a78bfa44);"></div>
      <div class="ai-box-header" style="color:#a78bfa;">🧩 Missing Categories to Consider</div>
    """, unsafe_allow_html=True)

    for mc in missing:
        example_chips = "".join(
            f'<span style="background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);'
            f'border-radius:6px;padding:2px 9px;font-size:11px;color:#c4b5fd;margin:2px 3px 0 0;'
            f'display:inline-block;">{ef}</span>'
            for ef in mc.get("example_funds", [])
        )
        st.markdown(f"""
        <div class="insight-item" style="margin-bottom:10px;">
          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
            <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#c4b5fd;">
              + {mc.get("category","")}
            </div>
            <span style="font-size:11px;color:rgba(255,255,255,0.4);">
              Suggested weight: <b style="color:#a78bfa;">{mc.get("suggested_allocation_pct",0):.0f}%</b>
            </span>
          </div>
          <div style="font-size:12px;color:rgba(220,235,230,0.72);line-height:1.7;margin-bottom:8px;">
            {mc.get("reason_to_add","")}
          </div>
          <div>{example_chips}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── 6. Strategic Insights ────────────────────
insights = analysis.get("strategic_insights", [])
if insights:
    st.markdown("""
    <div class="ai-box" style="margin-bottom:20px;border-color:rgba(0,245,212,0.3);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,#00f5d4,#a78bfa);"></div>
      <div class="ai-box-header" style="color:#00f5d4;">🚀 Strategic Insights</div>
    """, unsafe_allow_html=True)

    theme_colors = ["#00f5d4", "#00c9ff", "#a78bfa", "#ffbe50", "#34d399"]
    for idx, si in enumerate(insights):
        tc = theme_colors[idx % len(theme_colors)]
        st.markdown(f"""
        <div class="insight-item" style="border-left:3px solid {tc};margin-bottom:10px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;
            color:{tc};margin-bottom:7px;">{si.get("theme","")}</div>
          <div style="font-size:12px;color:rgba(220,235,230,0.72);line-height:1.75;margin-bottom:8px;">
            {si.get("insight","")}
          </div>
          <div style="background:rgba(255,255,255,0.04);border-radius:6px;padding:8px 12px;
            font-size:11px;color:rgba(0,245,212,0.8);">
            ▶ {si.get("action_item","")}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── 7. SIP Allocation ────────────────────────
sip_adv = analysis.get("sip_allocation_advice", {})
sip_split = sip_adv.get("suggested_split", [])
if sip_adv.get("commentary") or sip_split:
    st.markdown("""
    <div class="ai-box" style="margin-bottom:20px;border-color:rgba(52,211,153,0.3);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,#34d399,#00f5d4);"></div>
      <div class="ai-box-header" style="color:#34d399;">💸 SIP Allocation Strategy</div>
    """, unsafe_allow_html=True)

    if sip_adv.get("commentary"):
        st.markdown(f"""
        <div style="font-size:12px;color:rgba(220,235,230,0.75);line-height:1.75;margin-bottom:14px;">
          {sip_adv["commentary"]}
        </div>
        """, unsafe_allow_html=True)

    if sip_split:
        for s in sip_split:
            pct = s.get("pct", 0)
            amt = (monthly_sip * pct / 100) if monthly_sip > 0 else 0
            amt_str = f" · ₹{amt:,.0f}/mo" if amt > 0 else ""
            st.markdown(f"""
            <div class="alloc-row" style="margin-bottom:8px;">
              <div class="alloc-label" style="color:rgba(255,255,255,0.7);width:150px;">{s.get("category","")}</div>
              <div class="alloc-bar-wrap">
                <div class="alloc-bar-fill" style="width:{pct:.0f}%;background:linear-gradient(90deg,#34d399,#00f5d4);"></div>
              </div>
              <div class="alloc-pct" style="width:90px;">{pct:.0f}%{amt_str}</div>
            </div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4);margin:-4px 0 10px 160px;">
              {s.get("rationale","")}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size:11px;color:rgba(255,255,255,0.2);
  border-top:1px solid rgba(255,255,255,0.07);padding-top:16px;margin-top:8px;">
  🤖 Analysis generated by Claude Sonnet (Anthropic) · Based on fund category composition ·
  For informational purposes only · Not financial advice · Consult a SEBI-registered advisor
</div>
""", unsafe_allow_html=True)
