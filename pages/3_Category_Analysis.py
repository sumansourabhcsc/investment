import streamlit as st
import json
import requests
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

/* ── Category Cards ── */
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

/* ── Allocation bar ── */
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
.ai-box::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00f5d4, #00c9ff, #a78bfa);
    border-radius: 14px 14px 0 0;
}
.ai-section-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #00f5d4;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 16px 0 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(0,245,212,0.1);
}
.ai-section-title:first-child { margin-top: 0; }
.ai-content {
    font-size: 13px;
    color: rgba(220,235,230,0.85);
    line-height: 1.75;
    white-space: pre-wrap;
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

/* ── Risk badge ── */
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
}

# ─────────────────────────────────────────────
# Build category breakdown from config
# ─────────────────────────────────────────────
def build_category_data():
    cat_map = {}
    for fund_name, info in mutual_funds.items():
        cat = info.get("category", "Other")
        if cat not in cat_map:
            cat_map[cat] = []
        cat_map[cat].append(fund_name)
    return cat_map

category_data = build_category_data()
total_funds   = len(mutual_funds)

# Equal-weight allocation per fund (since we don't have live values loaded here)
# Shows fund count-based allocation; AI will recommend value-based targets
fund_count_per_cat = {cat: len(funds) for cat, funds in category_data.items()}

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
metrics = [
    (str(total_funds),              "Total Funds"),
    (str(len(category_data)),       "Categories"),
    (str(fund_count_per_cat.get("Small Cap", 0)),  "Small Cap Funds"),
    (str(fund_count_per_cat.get("Mid Cap", 0)),    "Mid Cap Funds"),
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
# Two-column layout: breakdown left, allocation right
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
        chips = " ".join(f'<span class="fund-chip">{f}</span>' for f in funds)

        st.markdown(f"""
        <div class="cat-card">
          <div class="cat-card-accent" style="background:{meta['gradient']};"></div>
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <div class="cat-title">{cat}</div>
            <span class="risk-badge {risk_cls}">{meta['risk_label']}</span>
          </div>
          <div class="cat-count">{len(funds)} fund{'s' if len(funds)>1 else ''} · {len(funds)/total_funds*100:.0f}% of portfolio by count</div>
          <div>{chips}</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
      color:#00f5d4;margin-bottom:14px;">⬡ Allocation by Fund Count</div>
    """, unsafe_allow_html=True)

    sorted_cats = sorted(category_data.items(), key=lambda x: -len(x[1]))
    for cat, funds in sorted_cats:
        meta = CATEGORY_META.get(cat, {"color": "#888", "gradient": "linear-gradient(90deg,#888,#aaa)"})
        pct  = len(funds) / total_funds * 100
        st.markdown(f"""
        <div class="alloc-row">
          <div class="alloc-label" style="color:rgba(255,255,255,0.7);">{cat}</div>
          <div class="alloc-bar-wrap">
            <div class="alloc-bar-fill" style="width:{pct:.0f}%;background:{meta['gradient']};"></div>
          </div>
          <div class="alloc-pct">{pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Risk concentration warning
    high_risk_count = sum(len(v) for k, v in category_data.items()
                          if CATEGORY_META.get(k, {}).get("risk") == "high")
    high_risk_pct   = high_risk_count / total_funds * 100

    st.markdown("<br>", unsafe_allow_html=True)
    color = "#ff6b6b" if high_risk_pct > 40 else "#ffbe50" if high_risk_pct > 25 else "#00f5a0"
    label = "⚠️ High Concentration" if high_risk_pct > 40 else "⚡ Moderate" if high_risk_pct > 25 else "✅ Balanced"
    st.markdown(f"""
    <div style="background:rgba(8,14,20,0.7);border:1px solid {color}44;border-radius:10px;
      padding:14px 16px;margin-top:4px;">
      <div style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;
        color:{color};margin-bottom:4px;">Risk Concentration</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:{color};">{high_risk_pct:.0f}%</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:2px;">
        in High-Risk categories (Small Cap + International)<br>
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
  Powered by Claude · Personalized rebalancing & improvement suggestions
</div>
""", unsafe_allow_html=True)

# Risk profile selector
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
        "Monthly SIP Amount (₹) — optional, for allocation advice",
        min_value=0,
        value=0,
        step=1000,
    )

st.markdown("<br>", unsafe_allow_html=True)

analyse_btn = st.button("🤖  Run AI Category Analysis & Rebalancing", type="primary")

if not analyse_btn:
    st.markdown("""
    <div style="text-align:center;opacity:0.3;padding:60px 20px;">
      <div style="font-size:48px;">🎯</div>
      <div style="margin-top:12px;font-size:14px;">Set your risk profile and hit Run Analysis</div>
      <div style="font-size:12px;margin-top:6px;opacity:0.7;">
        Claude will analyse your category mix and suggest rebalancing moves
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# Build prompt
# ─────────────────────────────────────────────
portfolio_summary = []
for cat, funds in category_data.items():
    meta = CATEGORY_META.get(cat, {})
    portfolio_summary.append({
        "category": cat,
        "fund_count": len(funds),
        "funds": funds,
        "allocation_pct_by_count": round(len(funds) / total_funds * 100, 1),
        "risk_level": meta.get("risk_label", "Medium Risk"),
    })

sip_line = f"Monthly SIP: ₹{monthly_sip:,}" if monthly_sip > 0 else "Monthly SIP: Not specified"

prompt = f"""You are an expert Indian mutual fund portfolio advisor. Analyse this portfolio and provide comprehensive, actionable advice.

PORTFOLIO DETAILS:
- Total Funds: {total_funds}
- Investor Risk Profile: {risk_profile}
- Investment Horizon: {investment_horizon}
- {sip_line}

CATEGORY BREAKDOWN:
{json.dumps(portfolio_summary, indent=2)}

Please provide a structured analysis with EXACTLY these 5 sections. Use plain text only — no markdown, no bullet symbols like *, no bold (**), no headers with #. Just clean flowing text under each labelled section.

SECTION 1 — PORTFOLIO HEALTH SCORE
Give a score out of 100 for this portfolio. Explain what the score means in 2-3 sentences. Consider diversification, risk alignment with profile, category concentration, and overlap risk.

SECTION 2 — CATEGORY CONCENTRATION ANALYSIS
Analyse each category: Small Cap ({fund_count_per_cat.get('Small Cap',0)} funds), Mid Cap ({fund_count_per_cat.get('Mid Cap',0)} funds), Flexi Cap ({fund_count_per_cat.get('Flexi Cap',0)} funds), Large Cap ({fund_count_per_cat.get('Large Cap',0)} funds), International ({fund_count_per_cat.get('International',0)} funds), Hybrid ({fund_count_per_cat.get('Hybrid',0)} funds). Point out over-concentration or under-representation. Be specific.

SECTION 3 — REBALANCING RECOMMENDATIONS
Give 4-6 specific, actionable rebalancing moves. For each move say: what to do (increase/decrease/exit/add), which category, which specific fund if relevant, and why. Consider the investor's risk profile of {risk_profile} and horizon of {investment_horizon}.

SECTION 4 — FUNDS TO CONSIDER EXITING OR MERGING
Identify any redundant funds (same category, same style). Suggest which ones to consolidate and into which. Be direct.

SECTION 5 — STRATEGIC IMPROVEMENT SUGGESTIONS
Give 3-5 broader strategic suggestions beyond rebalancing. Think about: missing categories, international diversification, thematic opportunities, tax efficiency (ELSS), index vs active mix, SIP strategy. Make these forward-looking and specific to the Indian market in 2025-2026.

Be direct, specific, and act as a trusted advisor. Do not add disclaimers at the end."""

# ─────────────────────────────────────────────
# Call Claude
# ─────────────────────────────────────────────
with st.spinner("Claude is analysing your portfolio..."):
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
                "max_tokens": 2000,
                "messages":   [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        if resp.status_code != 200:
            st.error(f"API error {resp.status_code}: {resp.text}")
            st.stop()

        raw_text = resp.json()["content"][0]["text"].strip()

    except Exception as e:
        st.error(f"Failed to get AI analysis: {e}")
        st.stop()

# ─────────────────────────────────────────────
# Parse and render sections
# ─────────────────────────────────────────────
SECTION_KEYS = [
    ("SECTION 1 — PORTFOLIO HEALTH SCORE",          "📊 Portfolio Health Score"),
    ("SECTION 2 — CATEGORY CONCENTRATION ANALYSIS", "🔍 Category Concentration Analysis"),
    ("SECTION 3 — REBALANCING RECOMMENDATIONS",     "⚖️ Rebalancing Recommendations"),
    ("SECTION 4 — FUNDS TO CONSIDER EXITING OR MERGING", "🔄 Funds to Exit or Merge"),
    ("SECTION 5 — STRATEGIC IMPROVEMENT SUGGESTIONS",    "🚀 Strategic Improvement Suggestions"),
]

SECTION_COLORS = ["#00f5d4", "#00c9ff", "#ffbe50", "#ff6b6b", "#a78bfa"]

def parse_sections(text, keys):
    sections = {}
    key_labels = [k[0] for k in keys]
    for i, key in enumerate(key_labels):
        start = text.find(key)
        if start == -1:
            sections[key] = ""
            continue
        start += len(key)
        end = len(text)
        for j in range(i + 1, len(key_labels)):
            nxt = text.find(key_labels[j])
            if nxt != -1:
                end = nxt
                break
        sections[key] = text[start:end].strip()
    return sections

parsed = parse_sections(raw_text, SECTION_KEYS)

st.markdown("<br>", unsafe_allow_html=True)

for i, (section_key, display_title) in enumerate(SECTION_KEYS):
    content = parsed.get(section_key, "").strip()
    color   = SECTION_COLORS[i]

    # Extract health score number for visual display
    score_html = ""
    if i == 0:
        import re
        numbers = re.findall(r'\b(\d{2,3})\b', content[:80])
        if numbers:
            score_val = numbers[0]
            score_int = int(score_val)
            score_color = "#00f5a0" if score_int >= 70 else "#ffbe50" if score_int >= 50 else "#ff6b6b"
            score_html = f"""
            <div style="display:flex;align-items:center;gap:20px;margin-bottom:14px;">
              <div style="text-align:center;">
                <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
                  color:{score_color};line-height:1;">{score_val}</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.35);
                  letter-spacing:0.15em;text-transform:uppercase;">out of 100</div>
              </div>
              <div style="flex:1;height:8px;background:rgba(255,255,255,0.06);
                border-radius:4px;overflow:hidden;">
                <div style="width:{score_int}%;height:100%;border-radius:4px;
                  background:linear-gradient(90deg,{score_color},{score_color}88);
                  transition:width 1s ease;"></div>
              </div>
            </div>"""

    st.markdown(f"""
    <div class="ai-box" style="margin-bottom:16px;border-color:{color}33;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;border-radius:14px 14px 0 0;
        background:linear-gradient(90deg,{color},{color}44);"></div>
      <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;
        color:{color};letter-spacing:0.06em;text-transform:uppercase;margin-bottom:14px;">
        {display_title}
      </div>
      {score_html}
      <div class="ai-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size:11px;color:rgba(255,255,255,0.2);
  border-top:1px solid rgba(255,255,255,0.07);padding-top:16px;margin-top:8px;">
  🤖 Analysis generated by Claude (Anthropic) · Based on fund category composition ·
  For informational purposes only · Not financial advice · Consult a SEBI-registered advisor
</div>
""", unsafe_allow_html=True)
