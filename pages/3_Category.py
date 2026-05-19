import streamlit as st
import math

st.set_page_config(page_title="Portfolio", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ── Data ──────────────────────────────────────────────────────────────────────
PORTFOLIO = {
    "Small Cap": {
        "funds": ["Bandhan Small Cap Fund", "Axis Small Cap Fund", "SBI Small Cap Fund", "quant Small Cap Fund"],
        "color": "#FF6B6B", "glow": "rgba(255,107,107,0.3)", "risk": "HIGH",
    },
    "Mid Cap": {
        "funds": ["Motilal Oswal Midcap Fund", "HSBC Midcap Fund", "Kotak Midcap Fund",
                  "quant Mid Cap Fund", "Edelweiss Nifty Midcap150 Momentum 50 Index Fund"],
        "color": "#FFB347", "glow": "rgba(255,179,71,0.3)", "risk": "HIGH",
    },
    "Flexi Cap": {
        "funds": ["Edelweiss Flexi Cap Fund", "Parag Parikh Flexi Cap Fund", "Kotak Flexicap Fund"],
        "color": "#4FC3F7", "glow": "rgba(79,195,247,0.3)", "risk": "MEDIUM",
    },
    "Large Cap": {
        "funds": ["Nippon India Large Cap Fund", "ICICI Pru BHARAT 22 FOF"],
        "color": "#69F0AE", "glow": "rgba(105,240,174,0.3)", "risk": "LOW",
    },
    "International": {
        "funds": ["Mirae Asset FANG+"],
        "color": "#CE93D8", "glow": "rgba(206,147,216,0.3)", "risk": "HIGH",
    },
    "Hybrid": {
        "funds": ["SBI Magnum Children's Benefit Fund"],
        "color": "#80CBC4", "glow": "rgba(128,203,196,0.3)", "risk": "LOW",
    },
}

total_funds = sum(len(v["funds"]) for v in PORTFOLIO.values())

def pct(cat): return len(PORTFOLIO[cat]["funds"]) / total_funds * 100

# ── Styles ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background: #060910;
    color: #E8EDF5;
}
.stApp {
    background: #060910;
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: #0A0E17 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
.block-container { padding-top: 2.5rem !important; max-width: 1280px !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Animated background grid ── */
.bg-grid {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridShift 20s linear infinite;
}
@keyframes gridShift {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}

.stApp > * { position: relative; z-index: 1; }

/* ── Page title ── */
.page-title {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #F0F4FF;
    line-height: 1;
}
.page-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 6px;
}

/* ── Stat chips ── */
.stat-row { display: flex; gap: 12px; margin: 20px 0; flex-wrap: wrap; }
.stat-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 12px 20px;
    display: flex; flex-direction: column; align-items: flex-start;
    animation: fadeUp 0.6s ease both;
}
.stat-chip-val {
    font-size: 1.6rem; font-weight: 700; line-height: 1;
    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.6) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-chip-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: rgba(255,255,255,0.35);
    letter-spacing: 0.15em; text-transform: uppercase; margin-top: 4px;
}

/* ── Category card ── */
.cat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, transform 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.5s ease both;
    cursor: default;
}
.cat-card:hover {
    border-color: var(--cat-color, rgba(255,255,255,0.2));
    transform: translateY(-2px);
    box-shadow: 0 8px 32px var(--cat-glow, rgba(0,0,0,0.3));
}
.cat-card-bar {
    position: absolute; top: 0; left: 0; bottom: 0;
    width: 3px;
    border-radius: 16px 0 0 16px;
}
.cat-name {
    font-size: 1rem; font-weight: 600; color: #F0F4FF; margin-bottom: 4px;
}
.cat-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; color: rgba(255,255,255,0.3);
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 12px;
}
.cat-pct {
    font-size: 2rem; font-weight: 700; line-height: 1;
}
.fund-tag {
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 3px 9px; margin: 3px 3px 0 0;
    font-size: 11px; color: rgba(220,230,245,0.65);
    font-family: 'JetBrains Mono', monospace;
    transition: background 0.2s;
}
.cat-card:hover .fund-tag {
    background: rgba(255,255,255,0.08);
}

/* ── Progress bar ── */
.prog-wrap {
    height: 5px; background: rgba(255,255,255,0.06);
    border-radius: 3px; overflow: hidden; margin: 10px 0 14px;
}
.prog-fill {
    height: 100%; border-radius: 3px;
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
    animation: fillBar 1.2s ease both;
}
@keyframes fillBar {
    from { width: 0 !important; }
}

/* ── Risk badge ── */
.risk-badge {
    display: inline-block;
    border-radius: 20px; padding: 2px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; font-weight: 500; letter-spacing: 0.15em;
}
.risk-HIGH   { background: rgba(255,107,107,0.12); color: #FF6B6B; border: 1px solid rgba(255,107,107,0.25); }
.risk-MEDIUM { background: rgba(255,179,71,0.12);  color: #FFB347; border: 1px solid rgba(255,179,71,0.25); }
.risk-LOW    { background: rgba(105,240,174,0.12); color: #69F0AE; border: 1px solid rgba(105,240,174,0.25); }

/* ── Donut chart ── */
.donut-wrap { position: relative; width: 220px; height: 220px; margin: 0 auto 20px; }
.donut-wrap svg { width: 100%; height: 100%; }
.donut-center {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    pointer-events: none;
}
.donut-total { font-size: 2rem; font-weight: 700; color: #F0F4FF; line-height: 1; }
.donut-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: rgba(255,255,255,0.35);
    letter-spacing: 0.2em; text-transform: uppercase; margin-top: 4px;
}

/* ── Legend ── */
.legend-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    animation: fadeUp 0.4s ease both;
}
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-name { font-size: 13px; color: rgba(255,255,255,0.8); flex: 1; }
.legend-pct  { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 500; }
.legend-count { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(255,255,255,0.3); width: 50px; text-align: right; }

/* ── Section label ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase;
    color: rgba(255,255,255,0.3); margin-bottom: 16px;
}

/* ── Rebalancing calculator ── */
.calc-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 24px;
    animation: fadeUp 0.5s ease both;
}
.calc-row {
    display: grid;
    grid-template-columns: 140px 1fr 90px 90px 110px;
    gap: 10px; align-items: center;
    padding: 10px 12px; border-radius: 8px;
    margin-bottom: 4px;
    border: 1px solid rgba(255,255,255,0.04);
    background: rgba(255,255,255,0.02);
    transition: background 0.2s;
}
.calc-row:hover { background: rgba(255,255,255,0.04); }
.calc-header {
    display: grid;
    grid-template-columns: 140px 1fr 90px 90px 110px;
    gap: 10px; padding: 4px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase;
    color: rgba(255,255,255,0.25); margin-bottom: 6px;
}
.action-buy  { color: #69F0AE; font-weight: 600; font-size: 12px; }
.action-sell { color: #FF6B6B; font-weight: 600; font-size: 12px; }
.action-hold { color: rgba(255,255,255,0.3); font-size: 12px; }

.stSlider > div > div > div { background: rgba(255,255,255,0.1) !important; }
.stSlider [data-testid="stThumbValue"] { display: none; }
.stNumberInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #F0F4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; color: #F0F4FF !important;
}

/* ── Summary result cards ── */
.result-card {
    border-radius: 12px; padding: 16px 18px; text-align: center;
}
.result-val { font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.result-lbl { font-size: 10px; color: rgba(255,255,255,0.4); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 4px; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* staggered delays */
.cat-card:nth-child(1) { animation-delay: 0.05s; }
.cat-card:nth-child(2) { animation-delay: 0.10s; }
.cat-card:nth-child(3) { animation-delay: 0.15s; }
.cat-card:nth-child(4) { animation-delay: 0.20s; }
.cat-card:nth-child(5) { animation-delay: 0.25s; }
.cat-card:nth-child(6) { animation-delay: 0.30s; }
</style>
<div class="bg-grid"></div>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-title">My Portfolio</div>
<div class="page-sub">◈ Category Overview &amp; Rebalancing</div>
""", unsafe_allow_html=True)

# ── Stat chips ─────────────────────────────────────────────────────────────────
high_risk_funds = sum(len(v["funds"]) for v in PORTFOLIO.values() if v["risk"] == "HIGH")
st.markdown(f"""
<div class="stat-row">
  <div class="stat-chip"><div class="stat-chip-val">{total_funds}</div><div class="stat-chip-lbl">Total Funds</div></div>
  <div class="stat-chip"><div class="stat-chip-val">{len(PORTFOLIO)}</div><div class="stat-chip-lbl">Categories</div></div>
  <div class="stat-chip"><div class="stat-chip-val">{high_risk_funds}</div><div class="stat-chip-lbl">High Risk Funds</div></div>
  <div class="stat-chip"><div class="stat-chip-val">{total_funds - high_risk_funds}</div><div class="stat-chip-lbl">Stable Funds</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_overview, tab_calc = st.tabs(["◈  Portfolio Overview", "⇌  Rebalancing Calculator"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    left_col, right_col = st.columns([5, 3], gap="large")

    # ── Left: category cards ──────────────────────────────────────────────────
    with left_col:
        st.markdown('<div class="section-label">▸ Fund Categories</div>', unsafe_allow_html=True)
        for cat, info in sorted(PORTFOLIO.items(), key=lambda x: -len(x[1]["funds"])):
            p = pct(cat)
            funds_html = "".join(f'<span class="fund-tag">{f}</span>' for f in info["funds"])
            st.markdown(f"""
            <div class="cat-card" style="--cat-color:{info['color']};--cat-glow:{info['glow']};">
              <div class="cat-card-bar" style="background:{info['color']};box-shadow:0 0 12px {info['glow']};"></div>
              <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
                <div style="flex:1;">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
                    <div class="cat-name">{cat}</div>
                    <span class="risk-badge risk-{info['risk']}">{info['risk']}</span>
                  </div>
                  <div class="cat-meta">{len(info['funds'])} fund{'s' if len(info['funds'])>1 else ''}</div>
                  <div class="prog-wrap">
                    <div class="prog-fill" style="width:{p:.1f}%;background:linear-gradient(90deg,{info['color']},{info['color']}88);"></div>
                  </div>
                  <div>{funds_html}</div>
                </div>
                <div class="cat-pct" style="color:{info['color']};min-width:64px;text-align:right;">{p:.0f}%</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Right: donut + legend ─────────────────────────────────────────────────
    with right_col:
        st.markdown('<div class="section-label">▸ Allocation</div>', unsafe_allow_html=True)

        # Build SVG donut
        cx, cy, r_outer, r_inner = 110, 110, 95, 58
        circumference = 2 * math.pi * r_outer
        sorted_cats = sorted(PORTFOLIO.items(), key=lambda x: -len(x[1]["funds"]))

        slices_svg = ""
        cumulative = 0
        gap_deg = 1.5  # gap between slices in degrees

        for cat, info in sorted_cats:
            p = pct(cat)
            slice_deg = (p / 100) * 360 - gap_deg
            slice_pct = slice_deg / 360

            start_rad = math.radians(cumulative * 360 / 100 - 90)
            end_rad   = math.radians((cumulative + p) * 360 / 100 - 90 - gap_deg)

            x1 = cx + r_outer * math.cos(start_rad)
            y1 = cy + r_outer * math.sin(start_rad)
            x2 = cx + r_outer * math.cos(end_rad)
            y2 = cy + r_outer * math.sin(end_rad)
            x3 = cx + r_inner * math.cos(end_rad)
            y3 = cy + r_inner * math.sin(end_rad)
            x4 = cx + r_inner * math.cos(start_rad)
            y4 = cy + r_inner * math.sin(start_rad)

            large_arc = 1 if slice_deg > 180 else 0

            path = (
                f"M {x1:.2f} {y1:.2f} "
                f"A {r_outer} {r_outer} 0 {large_arc} 1 {x2:.2f} {y2:.2f} "
                f"L {x3:.2f} {y3:.2f} "
                f"A {r_inner} {r_inner} 0 {large_arc} 0 {x4:.2f} {y4:.2f} Z"
            )
            slices_svg += f'<path d="{path}" fill="{info["color"]}" opacity="0.85" style="filter:drop-shadow(0 0 6px {info["glow"]})"><title>{cat}: {p:.0f}%</title></path>'
            cumulative += p

        donut_svg = f"""
        <svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
          <circle cx="{cx}" cy="{cy}" r="{r_outer+4}" fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
          {slices_svg}
          <circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#060910"/>
        </svg>"""

        st.markdown(f"""
        <div class="donut-wrap">
          {donut_svg}
          <div class="donut-center">
            <div class="donut-total">{total_funds}</div>
            <div class="donut-label">funds</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Legend
        for cat, info in sorted_cats:
            p = pct(cat)
            st.markdown(f"""
            <div class="legend-row">
              <div class="legend-dot" style="background:{info['color']};box-shadow:0 0 6px {info['glow']};"></div>
              <div class="legend-name">{cat}</div>
              <div class="legend-pct" style="color:{info['color']};">{p:.0f}%</div>
              <div class="legend-count">{len(info['funds'])} funds</div>
            </div>
            """, unsafe_allow_html=True)

        # Risk distribution summary
        st.markdown("<br>", unsafe_allow_html=True)
        high_pct = sum(pct(c) for c, v in PORTFOLIO.items() if v["risk"] == "HIGH")
        med_pct  = sum(pct(c) for c, v in PORTFOLIO.items() if v["risk"] == "MEDIUM")
        low_pct  = 100 - high_pct - med_pct
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
          border-radius:12px;padding:16px 18px;margin-top:4px;">
          <div class="section-label" style="margin-bottom:12px;">▸ Risk Split</div>
          <div style="display:flex;height:8px;border-radius:4px;overflow:hidden;gap:2px;margin-bottom:10px;">
            <div style="width:{high_pct:.0f}%;background:#FF6B6B;border-radius:4px 0 0 4px;"></div>
            <div style="width:{med_pct:.0f}%;background:#FFB347;"></div>
            <div style="width:{low_pct:.0f}%;background:#69F0AE;border-radius:0 4px 4px 0;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:11px;">
            <span style="color:#FF6B6B;">{high_pct:.0f}% High</span>
            <span style="color:#FFB347;">{med_pct:.0f}% Med</span>
            <span style="color:#69F0AE;">{low_pct:.0f}% Low</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REBALANCING CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_calc:
    st.markdown('<div class="section-label">▸ Rebalancing Calculator</div>', unsafe_allow_html=True)

    # Inputs
    inp1, inp2, inp3 = st.columns(3)
    with inp1:
        portfolio_value = st.number_input("Portfolio Value (₹)", min_value=10_000, value=5_00_000, step=10_000, format="%d")
    with inp2:
        profile = st.selectbox("Risk Profile", ["Aggressive", "Moderate", "Conservative"])
    with inp3:
        monthly_sip = st.number_input("Monthly SIP (₹)", min_value=0, value=0, step=1_000, format="%d")

    # Ideal targets per profile
    TARGETS = {
        "Aggressive":    {"Small Cap": 25, "Mid Cap": 30, "Flexi Cap": 20, "Large Cap": 10, "International": 10, "Hybrid": 5},
        "Moderate":      {"Small Cap": 12, "Mid Cap": 22, "Flexi Cap": 20, "Large Cap": 25, "International": 8,  "Hybrid": 13},
        "Conservative":  {"Small Cap": 5,  "Mid Cap": 10, "Flexi Cap": 20, "Large Cap": 40, "International": 5,  "Hybrid": 20},
    }

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
      border-radius:10px;padding:10px 16px;margin-bottom:20px;
      font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.4);">
      ▸ Targets below are for <span style="color:#F0F4FF;">{profile}</span> profile.
      Adjust sliders to customise. Current = equal weight per fund.
    </div>
    """, unsafe_allow_html=True)

    # Sliders for target allocation
    target_allocs = {}
    sl_cols = st.columns(3)
    for i, cat in enumerate(PORTFOLIO.keys()):
        default = TARGETS[profile][cat]
        color   = PORTFOLIO[cat]["color"]
        with sl_cols[i % 3]:
            target_allocs[cat] = st.slider(
                cat, 0, 60, default, 1,
                key=f"rebal_{cat}",
                help=f"Current: {pct(cat):.0f}%  |  {profile} ideal: {default}%"
            )

    total_tgt = sum(target_allocs.values())
    tgt_color = "#69F0AE" if abs(total_tgt - 100) <= 2 else "#FF6B6B"
    st.markdown(f"""
    <div style="text-align:right;font-family:'JetBrains Mono',monospace;font-size:13px;
      color:{tgt_color};margin-bottom:20px;">
      Total: {total_tgt}% {'✓' if abs(total_tgt-100)<=2 else '— must sum to ~100%'}
    </div>""", unsafe_allow_html=True)

    # ── Table ──
    st.markdown("""
    <div class="calc-header">
      <div>Category</div><div>Progress</div><div>Current</div><div>Target</div><div>Action</div>
    </div>""", unsafe_allow_html=True)

    total_buy = 0; total_sell = 0
    for cat, info in PORTFOLIO.items():
        curr_pct = pct(cat)
        tgt_pct  = target_allocs[cat]
        curr_val = portfolio_value * curr_pct / 100
        tgt_val  = portfolio_value * tgt_pct  / 100
        diff     = tgt_val - curr_val

        if diff > 200:
            action_html = f'<span class="action-buy">▲ BUY ₹{abs(diff):,.0f}</span>'
            total_buy  += diff
        elif diff < -200:
            action_html = f'<span class="action-sell">▼ SELL ₹{abs(diff):,.0f}</span>'
            total_sell += abs(diff)
        else:
            action_html = '<span class="action-hold">— HOLD</span>'

        bar_curr = f'<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;"><div style="width:{curr_pct:.0f}%;height:100%;background:{info["color"]};opacity:0.6;border-radius:2px;"></div></div>'
        bar_tgt  = f'<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;margin-top:3px;"><div style="width:{tgt_pct:.0f}%;height:100%;background:{info["color"]};border-radius:2px;"></div></div>'

        st.markdown(f"""
        <div class="calc-row">
          <div style="font-size:13px;color:{info['color']};font-weight:600;">{cat}</div>
          <div>{bar_curr}{bar_tgt}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,0.5);">
            {curr_pct:.0f}%<br><span style="font-size:10px;color:rgba(255,255,255,0.3);">₹{curr_val:,.0f}</span>
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,0.8);">
            {tgt_pct:.0f}%<br><span style="font-size:10px;color:rgba(255,255,255,0.3);">₹{tgt_val:,.0f}</span>
          </div>
          <div>{action_html}</div>
        </div>""", unsafe_allow_html=True)

    # ── Summary ──
    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div class="result-card" style="background:rgba(105,240,174,0.06);border:1px solid rgba(105,240,174,0.15);">
          <div class="result-val" style="color:#69F0AE;">₹{total_buy:,.0f}</div>
          <div class="result-lbl">Total to Buy</div>
        </div>""", unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
        <div class="result-card" style="background:rgba(255,107,107,0.06);border:1px solid rgba(255,107,107,0.15);">
          <div class="result-val" style="color:#FF6B6B;">₹{total_sell:,.0f}</div>
          <div class="result-lbl">Total to Sell</div>
        </div>""", unsafe_allow_html=True)
    with r3:
        net = total_buy - total_sell
        nc  = "#69F0AE" if net <= 0 else "#FFB347"
        st.markdown(f"""
        <div class="result-card" style="background:rgba(255,179,71,0.06);border:1px solid rgba(255,179,71,0.15);">
          <div class="result-val" style="color:{nc};">₹{abs(net):,.0f}</div>
          <div class="result-lbl">Net Cash {'Needed' if net > 0 else 'Free'}</div>
        </div>""", unsafe_allow_html=True)

    # ── SIP Split ──
    if monthly_sip > 0 and abs(total_tgt - 100) <= 2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
          border-radius:14px;padding:20px 22px;">
          <div class="section-label" style="margin-bottom:14px;">▸ Monthly SIP Split — ₹{monthly_sip:,}</div>
        """, unsafe_allow_html=True)
        for cat, info in PORTFOLIO.items():
            tgt = target_allocs[cat]
            amt = monthly_sip * tgt / 100
            if amt > 0:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                  <div style="width:110px;font-size:12px;color:rgba(255,255,255,0.6);">{cat}</div>
                  <div style="flex:1;height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;">
                    <div style="width:{tgt}%;height:100%;background:{info['color']};border-radius:2px;"></div>
                  </div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{info['color']};
                    width:140px;text-align:right;">₹{amt:,.0f} / mo</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(255,255,255,0.15);border-top:1px solid rgba(255,255,255,0.05);
  padding-top:14px;letter-spacing:0.1em;">
  FOR INFORMATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE · CONSULT A SEBI-REGISTERED ADVISOR
</div>
""", unsafe_allow_html=True)
