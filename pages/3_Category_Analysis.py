import streamlit as st

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
        radial-gradient(ellipse 80% 60% at 15% 20%, rgba(0,245,212,0.07) 0%, transparent 65%),
        radial-gradient(ellipse 60% 80% at 85% 75%, rgba(0,180,245,0.06) 0%, transparent 60%);
    background-attachment: fixed;
}
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(0,245,212,0.13) 1px, transparent 1px);
    background-size: 38px 38px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.4;
}
.stApp > * { position: relative; z-index: 1; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
    border-right: 1px solid rgba(0,245,212,0.1) !important;
}
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 1300px !important; }

/* Cards */
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
.cat-card:hover { border-color: rgba(0,245,212,0.4); transform: translateY(-2px); }
.cat-card-accent { position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 14px 14px 0 0; }
.cat-title { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 800; color: #dff5f0; margin-bottom: 4px; }
.cat-count { font-size: 11px; color: rgba(0,245,212,0.55); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px; }
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

/* Alloc bar */
.alloc-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.alloc-label { font-size: 11px; color: rgba(255,255,255,0.7); width: 140px; flex-shrink: 0; }
.alloc-bar-wrap { flex: 1; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.alloc-bar-fill { height: 100%; border-radius: 3px; }
.alloc-pct { font-size: 11px; color: rgba(255,255,255,0.6); width: 38px; text-align: right; flex-shrink: 0; }

/* Section box */
.section-box {
    background: rgba(6,18,30,0.9);
    border: 1px solid rgba(0,245,212,0.2);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.section-accent { position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 14px 14px 0 0; }

/* Metric pill */
.metric-pill {
    display: inline-flex; flex-direction: column; align-items: center;
    background: rgba(0,245,212,0.07); border: 1px solid rgba(0,245,212,0.18);
    border-radius: 10px; padding: 10px 18px; margin: 4px; width: 100%; box-sizing: border-box;
}
.metric-pill-val { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; color: #00f5d4; line-height: 1; }
.metric-pill-lbl { font-size: 10px; color: rgba(255,255,255,0.4); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 4px; }

/* Risk badges */
.risk-high   { background: rgba(255,107,107,0.15); border: 1px solid rgba(255,107,107,0.4); color: #ff6b6b; border-radius: 20px; padding: 3px 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; display: inline-block; }
.risk-medium { background: rgba(255,190,80,0.15);  border: 1px solid rgba(255,190,80,0.4);  color: #ffbe50; border-radius: 20px; padding: 3px 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; display: inline-block; }
.risk-low    { background: rgba(0,245,160,0.15);   border: 1px solid rgba(0,245,160,0.4);   color: #00f5a0; border-radius: 20px; padding: 3px 12px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; display: inline-block; }

/* Fund stats table */
.fund-row {
    display: grid;
    grid-template-columns: 220px 80px 70px 70px 90px 90px 60px;
    gap: 8px;
    align-items: center;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 4px;
    border: 1px solid rgba(255,255,255,0.05);
    background: rgba(255,255,255,0.02);
    transition: background 0.2s;
}
.fund-row:hover { background: rgba(0,245,212,0.04); border-color: rgba(0,245,212,0.12); }
.fund-row-header {
    display: grid;
    grid-template-columns: 220px 80px 70px 70px 90px 90px 60px;
    gap: 8px;
    padding: 6px 14px;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(0,245,212,0.5);
    margin-bottom: 4px;
}
.risk-dot-high   { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #ff6b6b; }
.risk-dot-medium { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #ffbe50; }
.risk-dot-low    { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00f5a0; }

/* Drift tracker */
.drift-row { margin-bottom: 14px; }
.drift-bars { position: relative; height: 18px; background: rgba(255,255,255,0.04); border-radius: 9px; overflow: hidden; margin: 4px 0; }
.drift-current { position: absolute; top: 0; left: 0; height: 100%; border-radius: 9px; opacity: 0.85; }
.drift-ideal-line { position: absolute; top: 0; height: 100%; width: 2px; background: rgba(255,255,255,0.6); }

/* Rebalancing */
.rebal-row {
    display: grid;
    grid-template-columns: 200px 90px 90px 100px 1fr;
    gap: 10px;
    align-items: center;
    padding: 12px 14px;
    border-radius: 8px;
    margin-bottom: 6px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
}
.rebal-row:hover { background: rgba(0,245,212,0.04); }
.rebal-header {
    display: grid;
    grid-template-columns: 200px 90px 90px 100px 1fr;
    gap: 10px;
    padding: 6px 14px;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(0,245,212,0.5);
    margin-bottom: 4px;
}
.action-buy    { color: #00f5a0; font-weight: 700; font-size: 12px; }
.action-sell   { color: #ff6b6b; font-weight: 700; font-size: 12px; }
.action-hold   { color: #888;    font-weight: 700; font-size: 12px; }

/* Risk meter */
.risk-meter-wrap { position: relative; height: 12px; background: linear-gradient(90deg,#00f5a0,#ffbe50,#ff6b6b); border-radius: 6px; margin: 10px 0; }
.risk-meter-needle { position: absolute; top: -4px; width: 4px; height: 20px; background: #fff; border-radius: 2px; transform: translateX(-50%); box-shadow: 0 0 8px rgba(255,255,255,0.6); }

.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, rgba(0,245,212,0.12), rgba(0,201,255,0.08)) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0,245,212,0.4) !important;
    border-radius: 8px !important;
    transition: all 0.25s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,245,212,0.22), rgba(0,201,255,0.15)) !important;
    border-color: rgba(0,245,212,0.7) !important;
    transform: translateY(-1px) !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Data — hardcoded from published figures (May 2025)
# ─────────────────────────────────────────────
FUND_DATA = {
    "Mirae Asset FANG+": {
        "category": "International", "expense_ratio": 0.52, "cagr_3y": 12.4, "cagr_5y": 18.6,
        "aum_cr": 1842, "risk_score": 8, "style": "Growth", "benchmark": "NYSE FANG+ TR",
        "overlap_group": "international",
    },
    "SBI Magnum Children's Benefit Fund": {
        "category": "Hybrid", "expense_ratio": 0.91, "cagr_3y": 16.2, "cagr_5y": 15.8,
        "aum_cr": 1156, "risk_score": 5, "style": "Blend", "benchmark": "CRISIL Hybrid 35+65",
        "overlap_group": "hybrid",
    },
    "Bandhan Small Cap Fund": {
        "category": "Small Cap", "expense_ratio": 0.39, "cagr_3y": 22.1, "cagr_5y": 28.4,
        "aum_cr": 7842, "risk_score": 9, "style": "Growth", "benchmark": "Nifty Smallcap 250 TR",
        "overlap_group": "smallcap",
    },
    "Motilal Oswal Midcap Fund": {
        "category": "Mid Cap", "expense_ratio": 0.58, "cagr_3y": 28.6, "cagr_5y": 29.1,
        "aum_cr": 22485, "risk_score": 8, "style": "Growth", "benchmark": "Nifty Midcap 150 TR",
        "overlap_group": "midcap_active",
    },
    "Edelweiss Flexi Cap Fund": {
        "category": "Flexi Cap", "expense_ratio": 0.44, "cagr_3y": 14.8, "cagr_5y": 17.2,
        "aum_cr": 2103, "risk_score": 6, "style": "Blend", "benchmark": "Nifty 500 TR",
        "overlap_group": "flexicap",
    },
    "Parag Parikh Flexi Cap Fund": {
        "category": "Flexi Cap", "expense_ratio": 0.63, "cagr_3y": 17.9, "cagr_5y": 21.3,
        "aum_cr": 78642, "risk_score": 6, "style": "Value", "benchmark": "Nifty 500 TR",
        "overlap_group": "flexicap",
    },
    "Nippon India Large Cap Fund": {
        "category": "Large Cap", "expense_ratio": 0.73, "cagr_3y": 18.4, "cagr_5y": 17.9,
        "aum_cr": 31204, "risk_score": 5, "style": "Blend", "benchmark": "Nifty 100 TR",
        "overlap_group": "largecap",
    },
    "Axis Small Cap Fund": {
        "category": "Small Cap", "expense_ratio": 0.52, "cagr_3y": 18.3, "cagr_5y": 26.1,
        "aum_cr": 20876, "risk_score": 9, "style": "Growth", "benchmark": "Nifty Smallcap 250 TR",
        "overlap_group": "smallcap",
    },
    "SBI Small Cap Fund": {
        "category": "Small Cap", "expense_ratio": 0.64, "cagr_3y": 19.7, "cagr_5y": 25.8,
        "aum_cr": 30142, "risk_score": 9, "style": "Growth", "benchmark": "Nifty Smallcap 250 TR",
        "overlap_group": "smallcap",
    },
    "quant Small Cap Fund": {
        "category": "Small Cap", "expense_ratio": 0.62, "cagr_3y": 30.4, "cagr_5y": 44.2,
        "aum_cr": 24361, "risk_score": 10, "style": "Quant", "benchmark": "Nifty Smallcap 250 TR",
        "overlap_group": "smallcap",
    },
    "HSBC Midcap Fund": {
        "category": "Mid Cap", "expense_ratio": 0.52, "cagr_3y": 21.3, "cagr_5y": 22.6,
        "aum_cr": 10245, "risk_score": 8, "style": "Growth", "benchmark": "Nifty Midcap 150 TR",
        "overlap_group": "midcap_active",
    },
    "Kotak Midcap Fund": {
        "category": "Mid Cap", "expense_ratio": 0.44, "cagr_3y": 20.8, "cagr_5y": 21.4,
        "aum_cr": 15367, "risk_score": 8, "style": "Blend", "benchmark": "Nifty Midcap 150 TR",
        "overlap_group": "midcap_active",
    },
    "quant Mid Cap Fund": {
        "category": "Mid Cap", "expense_ratio": 0.58, "cagr_3y": 27.2, "cagr_5y": 31.8,
        "aum_cr": 8924, "risk_score": 9, "style": "Quant", "benchmark": "Nifty Midcap 150 TR",
        "overlap_group": "midcap_quant",
    },
    "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": {
        "category": "Mid Cap", "expense_ratio": 0.30, "cagr_3y": 24.1, "cagr_5y": 26.3,
        "aum_cr": 4218, "risk_score": 7, "style": "Momentum/Index", "benchmark": "Nifty Midcap150 Momentum 50",
        "overlap_group": "midcap_index",
    },
    "Kotak Flexicap Fund": {
        "category": "Flexi Cap", "expense_ratio": 0.55, "cagr_3y": 16.3, "cagr_5y": 16.8,
        "aum_cr": 48762, "risk_score": 6, "style": "Blend", "benchmark": "Nifty 500 TR",
        "overlap_group": "flexicap",
    },
    "ICICI Pru BHARAT 22 FOF": {
        "category": "Large Cap", "expense_ratio": 0.15, "cagr_3y": 21.6, "cagr_5y": 19.2,
        "aum_cr": 2841, "risk_score": 5, "style": "Index/Passive", "benchmark": "BSE Bharat 22 Index",
        "overlap_group": "largecap",
    },
}

CATEGORY_META = {
    "Small Cap":     {"color": "#ff6b6b", "risk": "high",   "risk_label": "High Risk",   "gradient": "linear-gradient(90deg,#ff6b6b,#ff8c42)", "ideal_aggressive": 20, "ideal_moderate": 12, "ideal_conservative": 5},
    "Mid Cap":       {"color": "#ffbe50", "risk": "high",   "risk_label": "High Risk",   "gradient": "linear-gradient(90deg,#ffbe50,#ffd700)", "ideal_aggressive": 30, "ideal_moderate": 22, "ideal_conservative": 10},
    "Large Cap":     {"color": "#00f5a0", "risk": "low",    "risk_label": "Lower Risk",  "gradient": "linear-gradient(90deg,#00f5a0,#00c9ff)", "ideal_aggressive": 15, "ideal_moderate": 25, "ideal_conservative": 40},
    "Flexi Cap":     {"color": "#00c9ff", "risk": "medium", "risk_label": "Medium Risk", "gradient": "linear-gradient(90deg,#00c9ff,#a78bfa)", "ideal_aggressive": 20, "ideal_moderate": 20, "ideal_conservative": 20},
    "International": {"color": "#a78bfa", "risk": "high",   "risk_label": "High Risk",   "gradient": "linear-gradient(90deg,#a78bfa,#f472b6)", "ideal_aggressive": 10, "ideal_moderate": 8,  "ideal_conservative": 5},
    "Hybrid":        {"color": "#34d399", "risk": "low",    "risk_label": "Lower Risk",  "gradient": "linear-gradient(90deg,#34d399,#00f5d4)", "ideal_aggressive": 5,  "ideal_moderate": 13, "ideal_conservative": 20},
}

OVERLAP_WARNINGS = [
    {"funds": ["Bandhan Small Cap Fund", "Axis Small Cap Fund", "SBI Small Cap Fund", "quant Small Cap Fund"],
     "note": "All 4 track Nifty Smallcap 250 TR — heavy portfolio overlap. Consider keeping max 2."},
    {"funds": ["Motilal Oswal Midcap Fund", "HSBC Midcap Fund", "Kotak Midcap Fund"],
     "note": "3 active mid cap funds with similar Nifty Midcap 150 TR benchmark. Likely 60-70% stock overlap."},
    {"funds": ["Edelweiss Flexi Cap Fund", "Parag Parikh Flexi Cap Fund", "Kotak Flexicap Fund"],
     "note": "3 flexi cap funds — all hold large cap core. Parag Parikh has ~35% international, rest are pure domestic."},
    {"funds": ["Nippon India Large Cap Fund", "ICICI Pru BHARAT 22 FOF"],
     "note": "Both large cap but different indices (Nifty 100 vs BSE Bharat 22). Low overlap — reasonable to hold both."},
]

# ─────────────────────────────────────────────
# Derived data
# ─────────────────────────────────────────────
total_funds = len(FUND_DATA)

# Group by category
category_data = {}
for fname, finfo in FUND_DATA.items():
    cat = finfo["category"]
    if cat not in category_data:
        category_data[cat] = []
    category_data[cat].append({"name": fname, **finfo})

def cat_pct(cat):
    return len(category_data.get(cat, [])) / total_funds * 100

def portfolio_risk_score():
    scores = [f["risk_score"] for f in FUND_DATA.values()]
    return sum(scores) / len(scores)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
    background:linear-gradient(135deg,#00f5d4 0%,#00c9ff 55%,#a78bfa 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
    🎯 Category Analysis & Rebalancing
  </span>
</div>
<div style="font-size:12px;color:rgba(255,255,255,0.4);
  letter-spacing:0.1em;text-transform:uppercase;margin-bottom:24px;">
  Portfolio breakdown · Fund stats · Risk scoring · Rebalancing calculator · Drift tracker
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Top metrics
# ─────────────────────────────────────────────
m_cols = st.columns(5)
avg_expense = sum(f["expense_ratio"] for f in FUND_DATA.values()) / total_funds
avg_3y = sum(f["cagr_3y"] for f in FUND_DATA.values()) / total_funds
port_risk = portfolio_risk_score()
metrics = [
    (str(total_funds), "Total Funds"),
    (str(len(category_data)), "Categories"),
    (f"{avg_expense:.2f}%", "Avg Expense Ratio"),
    (f"{avg_3y:.1f}%", "Avg 3Y CAGR"),
    (f"{port_risk:.1f}/10", "Portfolio Risk"),
]
for col, (val, lbl) in zip(m_cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-pill">
          <div class="metric-pill-val">{val}</div>
          <div class="metric-pill-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Category Overview",
    "📋 Fund Stats Table",
    "⚖️ Rebalancing Calculator",
    "📐 Drift Tracker",
])

# ══════════════════════════════════════════════
# TAB 1 — Category Overview
# ══════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#00f5d4;margin-bottom:14px;">⬡ Category Breakdown</div>', unsafe_allow_html=True)

        for cat, funds in sorted(category_data.items(), key=lambda x: -len(x[1])):
            meta = CATEGORY_META.get(cat, {"color": "#888", "risk": "medium", "risk_label": "Medium Risk", "gradient": "linear-gradient(90deg,#888,#aaa)"})
            risk_cls = "risk-high" if meta["risk"] == "high" else "risk-medium" if meta["risk"] == "medium" else "risk-low"
            chips = " ".join(f'<span class="fund-chip">{f["name"]}</span>' for f in funds)
            pct = cat_pct(cat)
            avg_cat_risk = sum(f["risk_score"] for f in funds) / len(funds)
            avg_cat_3y   = sum(f["cagr_3y"] for f in funds) / len(funds)

            st.markdown(f"""
            <div class="cat-card">
              <div class="cat-card-accent" style="background:{meta['gradient']};"></div>
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                <div class="cat-title">{cat}</div>
                <span class="{risk_cls}">{meta['risk_label']}</span>
              </div>
              <div class="cat-count">{len(funds)} fund{'s' if len(funds)>1 else ''} · {pct:.0f}% of portfolio</div>
              <div style="display:flex;gap:16px;margin-bottom:10px;">
                <span style="font-size:11px;color:rgba(255,255,255,0.45);">Avg Risk: <b style="color:{meta['color']};">{avg_cat_risk:.1f}/10</b></span>
                <span style="font-size:11px;color:rgba(255,255,255,0.45);">Avg 3Y CAGR: <b style="color:#00f5d4;">{avg_cat_3y:.1f}%</b></span>
              </div>
              <div>{chips}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#00f5d4;margin-bottom:14px;">⬡ Allocation Weight</div>', unsafe_allow_html=True)

        for cat, funds in sorted(category_data.items(), key=lambda x: -cat_pct(x[0])):
            meta = CATEGORY_META.get(cat, {"gradient": "linear-gradient(90deg,#888,#aaa)"})
            pct = cat_pct(cat)
            st.markdown(f"""
            <div class="alloc-row">
              <div class="alloc-label">{cat}</div>
              <div class="alloc-bar-wrap"><div class="alloc-bar-fill" style="width:{pct:.0f}%;background:{meta['gradient']};"></div></div>
              <div class="alloc-pct">{pct:.0f}%</div>
            </div>""", unsafe_allow_html=True)

        # Portfolio risk meter
        pr = portfolio_risk_score()
        needle_pct = (pr / 10) * 100
        risk_color = "#ff6b6b" if pr >= 7.5 else "#ffbe50" if pr >= 5 else "#00f5a0"
        risk_label = "High Risk" if pr >= 7.5 else "Moderate Risk" if pr >= 5 else "Low Risk"
        st.markdown(f"""
        <div style="background:rgba(8,14,20,0.7);border:1px solid {risk_color}44;border-radius:10px;padding:16px;margin-top:14px;">
          <div style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:{risk_color};margin-bottom:8px;">Portfolio Risk Meter</div>
          <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:10px;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:{risk_color};">{pr:.1f}</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.4);">/ 10 · {risk_label}</div>
          </div>
          <div class="risk-meter-wrap">
            <div class="risk-meter-needle" style="left:{needle_pct:.0f}%;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:9px;color:rgba(255,255,255,0.3);margin-top:4px;">
            <span>Low</span><span>Moderate</span><span>High</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Overlap warnings
        st.markdown('<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#ff6b6b;margin:18px 0 10px;">⬡ Overlap Warnings</div>', unsafe_allow_html=True)
        for ow in OVERLAP_WARNINGS:
            funds_html = "".join(f'<span style="background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.2);border-radius:5px;padding:2px 7px;font-size:10px;color:#ff9999;margin:2px 2px 0 0;display:inline-block;">{f}</span>' for f in ow["funds"])
            st.markdown(f"""
            <div style="background:rgba(255,107,107,0.05);border:1px solid rgba(255,107,107,0.15);border-radius:8px;padding:10px 12px;margin-bottom:8px;">
              <div style="margin-bottom:6px;">{funds_html}</div>
              <div style="font-size:11px;color:rgba(220,235,230,0.6);line-height:1.6;">{ow['note']}</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — Fund Stats Table
# ══════════════════════════════════════════════
with tab2:
    st.markdown('<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#00f5d4;margin-bottom:16px;">⬡ All Funds — Detailed Stats</div>', unsafe_allow_html=True)

    # Filter controls
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_cat = st.selectbox("Filter by Category", ["All"] + sorted(category_data.keys()))
    with fc2:
        sort_by = st.selectbox("Sort by", ["Category", "3Y CAGR ↓", "5Y CAGR ↓", "Expense Ratio ↑", "Risk Score ↓", "AUM ↓"])
    with fc3:
        filter_risk = st.selectbox("Filter by Risk", ["All", "High (8-10)", "Medium (5-7)", "Low (1-4)"])

    # Apply filters
    funds_to_show = list(FUND_DATA.items())
    if filter_cat != "All":
        funds_to_show = [(n, f) for n, f in funds_to_show if f["category"] == filter_cat]
    if filter_risk == "High (8-10)":
        funds_to_show = [(n, f) for n, f in funds_to_show if f["risk_score"] >= 8]
    elif filter_risk == "Medium (5-7)":
        funds_to_show = [(n, f) for n, f in funds_to_show if 5 <= f["risk_score"] <= 7]
    elif filter_risk == "Low (1-4)":
        funds_to_show = [(n, f) for n, f in funds_to_show if f["risk_score"] <= 4]

    # Sort
    sort_map = {
        "3Y CAGR ↓":       (lambda x: -x[1]["cagr_3y"]),
        "5Y CAGR ↓":       (lambda x: -x[1]["cagr_5y"]),
        "Expense Ratio ↑": (lambda x:  x[1]["expense_ratio"]),
        "Risk Score ↓":    (lambda x: -x[1]["risk_score"]),
        "AUM ↓":           (lambda x: -x[1]["aum_cr"]),
        "Category":        (lambda x:  x[1]["category"]),
    }
    funds_to_show.sort(key=sort_map.get(sort_by, lambda x: x[1]["category"]))

    st.markdown("""
    <div class="fund-row-header">
      <div>Fund</div><div>Category</div><div>3Y CAGR</div><div>5Y CAGR</div>
      <div>Expense Ratio</div><div>AUM (₹ Cr)</div><div>Risk</div>
    </div>""", unsafe_allow_html=True)

    for fname, finfo in funds_to_show:
        cat = finfo["category"]
        meta = CATEGORY_META.get(cat, {"color": "#888"})
        rs = finfo["risk_score"]
        risk_dot = "risk-dot-high" if rs >= 8 else "risk-dot-medium" if rs >= 5 else "risk-dot-low"
        risk_txt_color = "#ff6b6b" if rs >= 8 else "#ffbe50" if rs >= 5 else "#00f5a0"
        cagr3_color = "#00f5a0" if finfo["cagr_3y"] >= 20 else "#ffbe50" if finfo["cagr_3y"] >= 15 else "#ff6b6b"
        exp_color = "#00f5a0" if finfo["expense_ratio"] <= 0.5 else "#ffbe50" if finfo["expense_ratio"] <= 0.75 else "#ff6b6b"

        st.markdown(f"""
        <div class="fund-row">
          <div style="font-size:12px;color:#dff5f0;font-weight:600;line-height:1.3;">{fname}</div>
          <div style="font-size:11px;" ><span style="color:{meta['color']};font-size:10px;">{cat}</span></div>
          <div style="font-size:13px;font-weight:700;color:{cagr3_color};">{finfo['cagr_3y']:.1f}%</div>
          <div style="font-size:13px;font-weight:700;color:#00c9ff;">{finfo['cagr_5y']:.1f}%</div>
          <div style="font-size:12px;color:{exp_color};">{finfo['expense_ratio']:.2f}%</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.6);">₹{finfo['aum_cr']:,}</div>
          <div style="display:flex;align-items:center;gap:5px;">
            <span class="{risk_dot}"></span>
            <span style="font-size:12px;color:{risk_txt_color};font-weight:700;">{rs}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # Summary stats below table
    st.markdown("<br>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    shown_funds = [f for _, f in funds_to_show]
    if shown_funds:
        with s1:
            best_3y = max(shown_funds, key=lambda x: x["cagr_3y"])
            st.markdown(f"""<div style="background:rgba(0,245,160,0.06);border:1px solid rgba(0,245,160,0.15);border-radius:10px;padding:12px 14px;">
              <div style="font-size:10px;color:#00f5a0;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Best 3Y CAGR</div>
              <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:#00f5d4;">{best_3y['cagr_3y']:.1f}%</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-top:2px;">{[n for n,f in funds_to_show if f==best_3y][0]}</div>
            </div>""", unsafe_allow_html=True)
        with s2:
            cheapest = min(shown_funds, key=lambda x: x["expense_ratio"])
            st.markdown(f"""<div style="background:rgba(0,201,255,0.06);border:1px solid rgba(0,201,255,0.15);border-radius:10px;padding:12px 14px;">
              <div style="font-size:10px;color:#00c9ff;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Lowest Expense</div>
              <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:#00f5d4;">{cheapest['expense_ratio']:.2f}%</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-top:2px;">{[n for n,f in funds_to_show if f==cheapest][0]}</div>
            </div>""", unsafe_allow_html=True)
        with s3:
            biggest = max(shown_funds, key=lambda x: x["aum_cr"])
            st.markdown(f"""<div style="background:rgba(167,139,250,0.06);border:1px solid rgba(167,139,250,0.15);border-radius:10px;padding:12px 14px;">
              <div style="font-size:10px;color:#a78bfa;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Largest AUM</div>
              <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:#00f5d4;">₹{biggest['aum_cr']:,}Cr</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-top:2px;">{[n for n,f in funds_to_show if f==biggest][0]}</div>
            </div>""", unsafe_allow_html=True)
        with s4:
            riskiest = max(shown_funds, key=lambda x: x["risk_score"])
            st.markdown(f"""<div style="background:rgba(255,107,107,0.06);border:1px solid rgba(255,107,107,0.15);border-radius:10px;padding:12px 14px;">
              <div style="font-size:10px;color:#ff6b6b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Highest Risk</div>
              <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:#ff6b6b;">{riskiest['risk_score']}/10</div>
              <div style="font-size:10px;color:rgba(255,255,255,0.4);margin-top:2px;">{[n for n,f in funds_to_show if f==riskiest][0]}</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 3 — Rebalancing Calculator
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#00f5d4;margin-bottom:16px;">⬡ Rebalancing Calculator</div>', unsafe_allow_html=True)

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        portfolio_value = st.number_input("Total Portfolio Value (₹)", min_value=10000, value=500000, step=10000, format="%d")
    with rc2:
        risk_profile = st.selectbox("Risk Profile", ["Aggressive", "Moderate", "Conservative"])
    with rc3:
        monthly_sip = st.number_input("Monthly SIP (₹) — optional", min_value=0, value=0, step=1000, format="%d")

    profile_key = {"Aggressive": "ideal_aggressive", "Moderate": "ideal_moderate", "Conservative": "ideal_conservative"}[risk_profile]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(0,245,212,0.04);border:1px solid rgba(0,245,212,0.15);border-radius:10px;
      padding:12px 16px;margin-bottom:18px;font-size:12px;color:rgba(255,255,255,0.5);">
      💡 Based on <b style="color:#00f5d4;">{risk_profile}</b> profile. Ideal allocations below are per-category targets.
      Current = equal weight per fund. Adjust targets using sliders, then see buy/sell actions.
    </div>""", unsafe_allow_html=True)

    # Per-category sliders for target %
    st.markdown("**Set Target Allocation per Category:**")
    target_allocs = {}
    slider_cols = st.columns(3)
    cats_sorted = sorted(category_data.keys())
    for i, cat in enumerate(cats_sorted):
        meta = CATEGORY_META.get(cat, {})
        ideal = meta.get(profile_key, round(cat_pct(cat)))
        with slider_cols[i % 3]:
            target_allocs[cat] = st.slider(cat, 0, 60, ideal, 1, key=f"slider_{cat}")

    total_target = sum(target_allocs.values())
    target_color = "#00f5a0" if abs(total_target - 100) <= 2 else "#ff6b6b"
    st.markdown(f"""
    <div style="text-align:right;font-size:12px;margin-bottom:16px;">
      Total target: <b style="color:{target_color};font-family:'Syne',sans-serif;font-size:1.1rem;">{total_target}%</b>
      {'✅' if abs(total_target-100)<=2 else '⚠️ Must sum to ~100%'}
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="rebal-header">
      <div>Category</div><div>Current Value</div><div>Target Value</div><div>Difference</div><div>Action</div>
    </div>""", unsafe_allow_html=True)

    total_buy = 0; total_sell = 0
    for cat in cats_sorted:
        current_pct = cat_pct(cat)
        target_pct  = target_allocs[cat]
        current_val = portfolio_value * current_pct / 100
        target_val  = portfolio_value * target_pct / 100
        diff        = target_val - current_val
        meta = CATEGORY_META.get(cat, {"color": "#888"})

        if diff > 500:
            action_html = f'<span class="action-buy">▲ BUY ₹{abs(diff):,.0f}</span>'
            total_buy += diff
        elif diff < -500:
            action_html = f'<span class="action-sell">▼ SELL ₹{abs(diff):,.0f}</span>'
            total_sell += abs(diff)
        else:
            action_html = '<span class="action-hold">— HOLD</span>'

        funds_in_cat = len(category_data.get(cat, []))
        per_fund = abs(diff) / funds_in_cat if funds_in_cat else 0
        per_fund_note = f"~₹{per_fund:,.0f}/fund" if abs(diff) > 500 else ""

        st.markdown(f"""
        <div class="rebal-row">
          <div style="font-size:12px;color:{meta['color']};font-weight:600;">{cat}</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.6);">₹{current_val:,.0f} <span style="font-size:10px;color:rgba(255,255,255,0.3);">({current_pct:.0f}%)</span></div>
          <div style="font-size:12px;color:rgba(255,255,255,0.6);">₹{target_val:,.0f} <span style="font-size:10px;color:rgba(255,255,255,0.3);">({target_pct:.0f}%)</span></div>
          <div style="font-size:12px;color:{'#00f5a0' if diff>0 else '#ff6b6b' if diff<0 else '#888'};font-weight:700;">
            {'+ ' if diff>0 else ''}₹{diff:,.0f}
          </div>
          <div>{action_html} <span style="font-size:10px;color:rgba(255,255,255,0.3);">{per_fund_note}</span></div>
        </div>""", unsafe_allow_html=True)

    # Summary
    st.markdown("<br>", unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div style="background:rgba(0,245,160,0.07);border:1px solid rgba(0,245,160,0.2);border-radius:10px;padding:14px 16px;text-align:center;">
          <div style="font-size:10px;color:#00f5a0;text-transform:uppercase;letter-spacing:0.1em;">Total to Buy</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:#00f5a0;">₹{total_buy:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div style="background:rgba(255,107,107,0.07);border:1px solid rgba(255,107,107,0.2);border-radius:10px;padding:14px 16px;text-align:center;">
          <div style="font-size:10px;color:#ff6b6b;text-transform:uppercase;letter-spacing:0.1em;">Total to Sell</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:#ff6b6b;">₹{total_sell:,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        net = total_buy - total_sell
        nc = "#00f5a0" if net <= 0 else "#ffbe50"
        st.markdown(f"""<div style="background:rgba(255,190,80,0.07);border:1px solid rgba(255,190,80,0.2);border-radius:10px;padding:14px 16px;text-align:center;">
          <div style="font-size:10px;color:#ffbe50;text-transform:uppercase;letter-spacing:0.1em;">Net Cash Needed</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:{nc};">₹{abs(net):,.0f}</div>
        </div>""", unsafe_allow_html=True)

    # SIP split
    if monthly_sip > 0 and abs(total_target - 100) <= 2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(6,18,30,0.9);border:1px solid rgba(52,211,153,0.25);border-radius:12px;padding:18px 20px;">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#34d399;margin-bottom:14px;">💸 Monthly SIP Split — ₹{monthly_sip:,}</div>
        """, unsafe_allow_html=True)
        for cat in cats_sorted:
            tgt = target_allocs[cat]
            amt = monthly_sip * tgt / 100
            meta = CATEGORY_META.get(cat, {"gradient": "linear-gradient(90deg,#888,#aaa)"})
            if amt > 0:
                st.markdown(f"""
                <div class="alloc-row" style="margin-bottom:8px;">
                  <div class="alloc-label">{cat}</div>
                  <div class="alloc-bar-wrap"><div class="alloc-bar-fill" style="width:{tgt}%;background:{meta['gradient']};"></div></div>
                  <div style="font-size:11px;color:#34d399;width:140px;text-align:right;">₹{amt:,.0f}/mo ({tgt}%)</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — Drift Tracker
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#00f5d4;margin-bottom:6px;">⬡ Category Drift Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:rgba(255,255,255,0.35);margin-bottom:20px;">Compare your current allocation vs ideal targets. Green bar = current · White line = ideal target.</div>', unsafe_allow_html=True)

    dp1, dp2 = st.columns(2)
    with dp1:
        drift_profile = st.selectbox("Compare against", ["Aggressive", "Moderate", "Conservative"], key="drift_profile")

    drift_key = {"Aggressive": "ideal_aggressive", "Moderate": "ideal_moderate", "Conservative": "ideal_conservative"}[drift_profile]

    st.markdown("<br>", unsafe_allow_html=True)

    drift_rows = []
    for cat, funds in sorted(category_data.items(), key=lambda x: x[0]):
        meta = CATEGORY_META.get(cat, {"color": "#888", "gradient": "linear-gradient(90deg,#888,#aaa)"})
        current = cat_pct(cat)
        ideal   = meta.get(drift_key, current)
        drift   = current - ideal
        drift_rows.append((cat, current, ideal, drift, meta))

    # Sort by abs drift descending
    drift_rows.sort(key=lambda x: -abs(x[3]))

    for cat, current, ideal, drift, meta in drift_rows:
        drift_label = f"+{drift:.1f}% OVERWEIGHT" if drift > 2 else f"{drift:.1f}% UNDERWEIGHT" if drift < -2 else "✓ ON TARGET"
        drift_color = "#ff6b6b" if drift > 2 else "#ffbe50" if drift < -2 else "#00f5a0"
        needle_pos  = min(ideal / 60 * 100, 100)  # scale to 60% max for bar width

        st.markdown(f"""
        <div style="background:rgba(8,14,20,0.7);border:1px solid rgba(255,255,255,0.07);border-radius:10px;
          padding:14px 16px;margin-bottom:10px;border-left:3px solid {meta['color']};">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#dff5f0;">{cat}</div>
            <span style="font-size:11px;color:{drift_color};font-weight:700;letter-spacing:0.08em;">{drift_label}</span>
          </div>
          <div style="position:relative;height:16px;background:rgba(255,255,255,0.04);border-radius:8px;overflow:visible;margin:4px 0;">
            <div style="position:absolute;top:0;left:0;height:100%;width:{min(current/60*100,100):.1f}%;background:{meta['gradient']};border-radius:8px;opacity:0.85;"></div>
            <div style="position:absolute;top:-3px;height:22px;width:3px;background:rgba(255,255,255,0.7);border-radius:2px;left:{needle_pos:.1f}%;box-shadow:0 0 6px rgba(255,255,255,0.5);"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:11px;margin-top:6px;">
            <span style="color:rgba(255,255,255,0.5);">Current: <b style="color:{meta['color']};">{current:.0f}%</b></span>
            <span style="color:rgba(255,255,255,0.5);">Ideal ({drift_profile}): <b style="color:rgba(255,255,255,0.8);">{ideal:.0f}%</b></span>
            <span style="color:rgba(255,255,255,0.5);">Funds: <b style="color:#dff5f0;">{len(category_data.get(cat,[]))}</b></span>
          </div>
        </div>""", unsafe_allow_html=True)

    # Overall drift score
    total_drift = sum(abs(d) for _, _, _, d, _ in drift_rows) / len(drift_rows)
    drift_score_color = "#ff6b6b" if total_drift > 10 else "#ffbe50" if total_drift > 5 else "#00f5a0"
    drift_verdict = "Needs Rebalancing" if total_drift > 10 else "Minor Rebalancing Suggested" if total_drift > 5 else "Well Balanced"

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(8,14,20,0.8);border:1px solid {drift_score_color}44;border-radius:12px;padding:18px 20px;text-align:center;">
      <div style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:{drift_score_color};margin-bottom:8px;">Average Drift Score</div>
      <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:{drift_score_color};">{total_drift:.1f}%</div>
      <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:4px;">{drift_verdict} vs {drift_profile} profile</div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size:11px;color:rgba(255,255,255,0.2);border-top:1px solid rgba(255,255,255,0.07);padding-top:16px;">
  📊 Data based on published fund figures (May 2025) · For informational purposes only ·
  Not financial advice · Consult a SEBI-registered advisor before investing
</div>
""", unsafe_allow_html=True)
