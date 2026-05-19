import streamlit as st
import math
import os
import pandas as pd
from config import MUTUAL_FUNDS, CATEGORY_META

st.set_page_config(
    page_title="Portfolio",
    page_icon="🐂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Data loading ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_fund_latest(folder: str, code: str) -> dict:
    """
    Read the latest row from mutualfund/<folder>/daily_<code>.csv.
    Returns dict with: invested, current_value, gain_loss, return_pct, xirr, nav, date
    Falls back to zeros if file is missing.
    """
    path = os.path.join("mutualfund", folder, f"daily_{code}.csv")
    empty = {
        "invested": 0.0, "current_value": 0.0,
        "gain_loss": 0.0, "return_pct": 0.0,
        "xirr": 0.0, "nav": 0.0, "date": None
    }
    if not os.path.exists(path):
        return empty
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
        df = df.dropna(subset=["date"]).sort_values("date")
        if df.empty:
            return empty
        row = df.iloc[-1]

        def parse_pct(val):
            if isinstance(val, str):
                return float(val.replace("%", "").strip())
            return float(val)

        return {
            "invested":      float(row["total_invested"]),
            "current_value": float(row["current_value"]),
            "gain_loss":     float(row["absolute_gain_loss"]),
            "return_pct":    parse_pct(row["total_return_pct"]),
            "xirr":          parse_pct(row["xirr_annual"]),
            "nav":           float(row["nav"]),
            "date":          row["date"].date(),
        }
    except Exception:
        return empty


def build_portfolio_data():
    """
    Aggregate fund data into per-category and per-fund structures.
    Returns: funds_data (list of dicts), category_data (dict)
    """
    funds_data = []
    for fund_name, meta in MUTUAL_FUNDS.items():
        latest = load_fund_latest(meta["folder"], meta["code"])
        funds_data.append({
            "name":     fund_name,
            "code":     meta["code"],
            "category": meta["category"],
            "folder":   meta["folder"],
            **latest,
        })

    category_data = {}
    for cat in CATEGORY_META:
        cat_funds = [f for f in funds_data if f["category"] == cat]
        category_data[cat] = {
            "funds":         cat_funds,
            "fund_names":    [f["name"] for f in cat_funds],
            "invested":      sum(f["invested"] for f in cat_funds),
            "current_value": sum(f["current_value"] for f in cat_funds),
            "gain_loss":     sum(f["gain_loss"] for f in cat_funds),
            **CATEGORY_META[cat],
        }

    return funds_data, category_data


funds_data, category_data = build_portfolio_data()

# ── Portfolio totals ────────────────────────────────────────────────────────────
total_invested    = sum(f["invested"]      for f in funds_data)
total_current     = sum(f["current_value"] for f in funds_data)
total_gain        = total_current - total_invested
total_return_pct  = (total_gain / total_invested * 100) if total_invested > 0 else 0
total_funds_count = len(MUTUAL_FUNDS)
high_risk_count   = sum(
    1 for f in funds_data
    if CATEGORY_META.get(f["category"], {}).get("risk") == "HIGH"
)

def cat_pct_of_portfolio(cat: str) -> float:
    if total_current == 0:
        return 0.0
    return category_data[cat]["current_value"] / total_current * 100


# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background: #060910;
    color: #E8EDF5;
}
.stApp { background: #060910; min-height: 100vh; }
[data-testid="stSidebar"] {
    background: #0A0E17 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
.block-container { padding-top: 2.5rem !important; max-width: 1400px !important; }
#MainMenu, footer { visibility: hidden; }

.bg-grid {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridShift 25s linear infinite;
}
@keyframes gridShift {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}
.stApp > * { position: relative; z-index: 1; }

.page-title { font-size: 2.2rem; font-weight: 700; letter-spacing: -0.02em; color: #F0F4FF; line-height: 1; }
.page-sub   { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(255,255,255,0.3);
              letter-spacing: 0.2em; text-transform: uppercase; margin-top: 6px; }

.stat-row  { display: flex; gap: 12px; margin: 20px 0; flex-wrap: wrap; }
.stat-chip {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 12px 20px;
    display: flex; flex-direction: column; align-items: flex-start;
    animation: fadeUp 0.6s ease both;
}
.stat-chip-val {
    font-size: 1.6rem; font-weight: 700; line-height: 1;
    background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.6) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-chip-lbl {
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    color: rgba(255,255,255,0.35); letter-spacing: 0.15em;
    text-transform: uppercase; margin-top: 4px;
}
.stat-chip-val-green  { font-size:1.3rem;font-weight:700;line-height:1;color:#69F0AE; }
.stat-chip-val-red    { font-size:1.3rem;font-weight:700;line-height:1;color:#FF6B6B; }

.cat-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 20px 22px; margin-bottom: 12px;
    position: relative; overflow: hidden;
    transition: border-color 0.3s, transform 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.5s ease both; cursor: default;
}
.cat-card:hover {
    border-color: var(--cat-color, rgba(255,255,255,0.2));
    transform: translateY(-2px);
    box-shadow: 0 8px 32px var(--cat-glow, rgba(0,0,0,0.3));
}
.cat-card-bar { position: absolute; top: 0; left: 0; bottom: 0; width: 3px; border-radius: 16px 0 0 16px; }
.cat-name  { font-size: 1rem; font-weight: 600; color: #F0F4FF; margin-bottom: 4px; }
.cat-meta  { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: rgba(255,255,255,0.3);
             letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px; }
.cat-pct   { font-size: 1.8rem; font-weight: 700; line-height: 1; }
.cat-values { display:flex; gap:16px; margin-top:8px; flex-wrap:wrap; }
.cat-val-item { display:flex; flex-direction:column; }
.cat-val-label { font-family:'JetBrains Mono',monospace; font-size:9px; color:rgba(255,255,255,0.3);
                 letter-spacing:0.12em; text-transform:uppercase; margin-bottom:2px; }
.cat-val-num   { font-family:'JetBrains Mono',monospace; font-size:12px; color:rgba(220,230,245,0.8); }
.cat-gain-pos  { font-family:'JetBrains Mono',monospace; font-size:12px; color:#69F0AE; }
.cat-gain-neg  { font-family:'JetBrains Mono',monospace; font-size:12px; color:#FF6B6B; }

.fund-tag {
    display: inline-block; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 6px;
    padding: 3px 9px; margin: 3px 3px 0 0; font-size: 11px;
    color: rgba(220,230,245,0.65); font-family: 'JetBrains Mono', monospace;
    transition: background 0.2s;
}
.cat-card:hover .fund-tag { background: rgba(255,255,255,0.08); }

.prog-wrap { height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; margin: 10px 0 14px; }
.prog-fill { height: 100%; border-radius: 3px; transition: width 1s cubic-bezier(0.4,0,0.2,1); animation: fillBar 1.2s ease both; }
@keyframes fillBar { from { width: 0 !important; } }

.risk-badge  { display: inline-block; border-radius: 20px; padding: 2px 10px;
               font-family: 'JetBrains Mono', monospace; font-size: 9px; font-weight: 500; letter-spacing: 0.15em; }
.risk-HIGH   { background: rgba(255,107,107,0.12); color: #FF6B6B; border: 1px solid rgba(255,107,107,0.25); }
.risk-MEDIUM { background: rgba(255,179,71,0.12);  color: #FFB347; border: 1px solid rgba(255,179,71,0.25); }
.risk-LOW    { background: rgba(105,240,174,0.12); color: #69F0AE; border: 1px solid rgba(105,240,174,0.25); }

.donut-wrap { position: relative; width: 220px; height: 220px; margin: 0 auto 20px; }
.donut-wrap svg { width: 100%; height: 100%; }
.donut-center { position: absolute; inset: 0; display: flex; flex-direction: column;
                align-items: center; justify-content: center; pointer-events: none; }
.donut-total { font-size: 1.3rem; font-weight: 700; color: #F0F4FF; line-height: 1; font-family:'JetBrains Mono',monospace; }
.donut-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: rgba(255,255,255,0.35);
               letter-spacing: 0.2em; text-transform: uppercase; margin-top: 4px; }

.legend-row { display: flex; align-items: center; gap: 10px; padding: 8px 0;
              border-bottom: 1px solid rgba(255,255,255,0.04); animation: fadeUp 0.4s ease both; }
.legend-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-name { font-size: 13px; color: rgba(255,255,255,0.8); flex: 1; }
.legend-pct  { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 500; }
.legend-val  { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(255,255,255,0.3); width: 80px; text-align: right; }

.section-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.2em;
                 text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 16px; }

.calc-header {
    display: grid;
    grid-template-columns: 140px 1fr 110px 90px 110px 120px;
    gap: 10px; padding: 4px 12px;
    font-family: 'JetBrains Mono', monospace; font-size: 9px;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: rgba(255,255,255,0.25); margin-bottom: 6px;
}
.calc-row {
    display: grid;
    grid-template-columns: 140px 1fr 110px 90px 110px 120px;
    gap: 10px; align-items: center; padding: 10px 12px;
    border-radius: 8px; margin-bottom: 4px;
    border: 1px solid rgba(255,255,255,0.04);
    background: rgba(255,255,255,0.02); transition: background 0.2s;
}
.calc-row:hover { background: rgba(255,255,255,0.04); }

.action-buy  { color: #69F0AE; font-weight: 600; font-size: 12px; font-family:'JetBrains Mono',monospace; }
.action-sell { color: #FF6B6B; font-weight: 600; font-size: 12px; font-family:'JetBrains Mono',monospace; }
.action-hold { color: rgba(255,255,255,0.3); font-size: 12px; font-family:'JetBrains Mono',monospace; }

.result-card { border-radius: 12px; padding: 16px 18px; text-align: center; }
.result-val  { font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.result-lbl  { font-size: 10px; color: rgba(255,255,255,0.4); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 4px; }

.fund-table { width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:11px; }
.fund-table th { color:rgba(255,255,255,0.3); font-size:9px; letter-spacing:0.12em; text-transform:uppercase;
                 padding:6px 10px; border-bottom:1px solid rgba(255,255,255,0.06); text-align:left; }
.fund-table td { padding:8px 10px; border-bottom:1px solid rgba(255,255,255,0.04); color:rgba(220,230,245,0.75); vertical-align:middle; }
.fund-table tr:hover td { background:rgba(255,255,255,0.02); }
.fund-table .pos { color:#69F0AE; }
.fund-table .neg { color:#FF6B6B; }

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

/* profit target tab */
.pt-fund-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 20px 22px; margin-bottom: 10px;
    transition: border-color 0.3s, box-shadow 0.3s;
    animation: fadeUp 0.5s ease both;
}
.pt-fund-card:hover {
    border-color: rgba(255,255,255,0.14);
    box-shadow: 0 6px 24px rgba(0,0,0,0.4);
}
.pt-fund-name { font-size: 13px; font-weight: 600; color: #F0F4FF; margin-bottom: 2px; }
.pt-fund-meta { font-family: 'JetBrains Mono', monospace; font-size: 10px;
                color: rgba(255,255,255,0.3); letter-spacing: 0.1em; margin-bottom: 12px; }
.pt-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px; margin-bottom: 14px;
}
.pt-kv { display: flex; flex-direction: column; }
.pt-kv-label { font-family: 'JetBrains Mono', monospace; font-size: 9px;
               color: rgba(255,255,255,0.28); letter-spacing: 0.12em;
               text-transform: uppercase; margin-bottom: 3px; }
.pt-kv-val   { font-family: 'JetBrains Mono', monospace; font-size: 13px;
               color: rgba(220,230,245,0.85); font-weight: 500; }
.pt-result-banner {
    border-radius: 10px; padding: 14px 18px;
    display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}
.pt-result-item { display: flex; flex-direction: column; }
.pt-result-val  { font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 700; line-height: 1; }
.pt-result-lbl  { font-family: 'JetBrains Mono', monospace; font-size: 9px;
                  color: rgba(255,255,255,0.35); letter-spacing: 0.12em;
                  text-transform: uppercase; margin-top: 3px; }
.pt-warn { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #FF6B6B; margin-top: 8px; }
.pt-sep  { width: 1px; height: 40px; background: rgba(255,255,255,0.08); flex-shrink: 0; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.cat-card:nth-child(1) { animation-delay: 0.05s; }
.cat-card:nth-child(2) { animation-delay: 0.10s; }
.cat-card:nth-child(3) { animation-delay: 0.15s; }
.cat-card:nth-child(4) { animation-delay: 0.20s; }
.cat-card:nth-child(5) { animation-delay: 0.25s; }
.cat-card:nth-child(6) { animation-delay: 0.30s; }
</style>
<div class="bg-grid"></div>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-title">My Portfolio</div>
<div class="page-sub">◈ Category Overview &amp; Rebalancing · Live NAV</div>
""", unsafe_allow_html=True)

# ── Stat chips ──────────────────────────────────────────────────────────────────
gain_color = "stat-chip-val-green" if total_gain >= 0 else "stat-chip-val-red"
gain_sign  = "+" if total_gain >= 0 else ""
ret_sign   = "+" if total_return_pct >= 0 else ""

st.markdown(f"""
<div class="stat-row">
  <div class="stat-chip">
    <div class="stat-chip-val">₹{total_invested/1e5:.2f}L</div>
    <div class="stat-chip-lbl">Total Invested</div>
  </div>
  <div class="stat-chip">
    <div class="stat-chip-val">₹{total_current/1e5:.2f}L</div>
    <div class="stat-chip-lbl">Current Value</div>
  </div>
  <div class="stat-chip">
    <div class="{gain_color}">{gain_sign}₹{abs(total_gain)/1e5:.2f}L</div>
    <div class="stat-chip-lbl">Unrealised P&amp;L</div>
  </div>
  <div class="stat-chip">
    <div class="{gain_color}">{ret_sign}{total_return_pct:.2f}%</div>
    <div class="stat-chip-lbl">Absolute Return</div>
  </div>
  <div class="stat-chip">
    <div class="stat-chip-val">{total_funds_count}</div>
    <div class="stat-chip-lbl">Total Funds</div>
  </div>
  <div class="stat-chip">
    <div class="stat-chip-val">{len(CATEGORY_META)}</div>
    <div class="stat-chip-lbl">Categories</div>
  </div>
  <div class="stat-chip">
    <div class="stat-chip-val">{high_risk_count}</div>
    <div class="stat-chip-lbl">High Risk Funds</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────────────────────────
tab_overview, tab_funds, tab_calc, tab_profit = st.tabs([
    "◈  Portfolio Overview",
    "≡  Fund Details",
    "⇌  Rebalancing Calculator",
    "⊕  Profit Target",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    left_col, right_col = st.columns([5, 3], gap="large")

    sorted_cats = sorted(
        category_data.items(),
        key=lambda x: x[1]["current_value"],
        reverse=True
    )

    with left_col:
        st.markdown('<div class="section-label">▸ Fund Categories  (sorted by current value)</div>', unsafe_allow_html=True)

        for cat, info in sorted_cats:
            p          = cat_pct_of_portfolio(cat)
            funds_html = "".join(f'<span class="fund-tag">{f}</span>' for f in info["fund_names"])
            gain_cls   = "cat-gain-pos" if info["gain_loss"] >= 0 else "cat-gain-neg"
            gain_sign  = "+" if info["gain_loss"] >= 0 else ""
            cat_ret    = (info["gain_loss"] / info["invested"] * 100) if info["invested"] > 0 else 0

            st.markdown(f"""
            <div class="cat-card" style="--cat-color:{info['color']};--cat-glow:{info['glow']};">
              <div class="cat-card-bar" style="background:{info['color']};box-shadow:0 0 12px {info['glow']};"></div>
              <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
                <div style="flex:1;">
                  <div style="display:flex;align-items:center;gap:10px;margin-bottom:2px;">
                    <div class="cat-name">{cat}</div>
                    <span class="risk-badge risk-{info['risk']}">{info['risk']}</span>
                  </div>
                  <div class="cat-meta">{len(info['funds'])} fund{'s' if len(info['funds'])>1 else ''} &nbsp;·&nbsp; {p:.1f}% of portfolio</div>
                  <div class="prog-wrap">
                    <div class="prog-fill" style="width:{p:.1f}%;background:linear-gradient(90deg,{info['color']},{info['color']}88);"></div>
                  </div>
                  <div class="cat-values">
                    <div class="cat-val-item">
                      <div class="cat-val-label">Invested</div>
                      <div class="cat-val-num">₹{info['invested']:,.0f}</div>
                    </div>
                    <div class="cat-val-item">
                      <div class="cat-val-label">Current</div>
                      <div class="cat-val-num">₹{info['current_value']:,.0f}</div>
                    </div>
                    <div class="cat-val-item">
                      <div class="cat-val-label">P&amp;L</div>
                      <div class="{gain_cls}">{gain_sign}₹{abs(info['gain_loss']):,.0f} ({gain_sign}{cat_ret:.1f}%)</div>
                    </div>
                  </div>
                  <div style="margin-top:10px;">{funds_html}</div>
                </div>
                <div class="cat-pct" style="color:{info['color']};min-width:64px;text-align:right;">{p:.1f}%</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="section-label">▸ Allocation by Current Value</div>', unsafe_allow_html=True)

        cx, cy, r_outer, r_inner = 110, 110, 95, 58
        slices_svg = ""
        cumulative = 0.0
        gap_deg    = 1.5

        for cat, info in sorted_cats:
            p = cat_pct_of_portfolio(cat)
            if p < 0.5:
                cumulative += p
                continue
            slice_deg = (p / 100) * 360 - gap_deg
            start_rad = math.radians(cumulative * 360 / 100 - 90)
            end_rad   = math.radians((cumulative + p) * 360 / 100 - 90 - gap_deg)

            x1 = cx + r_outer * math.cos(start_rad); y1 = cy + r_outer * math.sin(start_rad)
            x2 = cx + r_outer * math.cos(end_rad);   y2 = cy + r_outer * math.sin(end_rad)
            x3 = cx + r_inner * math.cos(end_rad);   y3 = cy + r_inner * math.sin(end_rad)
            x4 = cx + r_inner * math.cos(start_rad); y4 = cy + r_inner * math.sin(start_rad)
            large_arc = 1 if slice_deg > 180 else 0

            path = (
                f"M {x1:.2f} {y1:.2f} "
                f"A {r_outer} {r_outer} 0 {large_arc} 1 {x2:.2f} {y2:.2f} "
                f"L {x3:.2f} {y3:.2f} "
                f"A {r_inner} {r_inner} 0 {large_arc} 0 {x4:.2f} {y4:.2f} Z"
            )
            slices_svg += f'<path d="{path}" fill="{info["color"]}" opacity="0.85" style="filter:drop-shadow(0 0 6px {info["glow"]})"><title>{cat}: {p:.1f}%</title></path>'
            cumulative += p

        donut_svg = f"""
        <svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
          <circle cx="{cx}" cy="{cy}" r="{r_outer+4}" fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
          {slices_svg}
          <circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#060910"/>
        </svg>"""

        total_lakh = total_current / 1e5
        st.markdown(f"""
        <div class="donut-wrap">
          {donut_svg}
          <div class="donut-center">
            <div class="donut-total">₹{total_lakh:.1f}L</div>
            <div class="donut-label">portfolio</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        for cat, info in sorted_cats:
            p = cat_pct_of_portfolio(cat)
            st.markdown(f"""
            <div class="legend-row">
              <div class="legend-dot" style="background:{info['color']};box-shadow:0 0 6px {info['glow']};"></div>
              <div class="legend-name">{cat}</div>
              <div class="legend-pct" style="color:{info['color']};">{p:.1f}%</div>
              <div class="legend-val">₹{info['current_value']/1e3:.0f}k</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        high_val = sum(info["current_value"] for c, info in category_data.items() if CATEGORY_META[c]["risk"] == "HIGH")
        med_val  = sum(info["current_value"] for c, info in category_data.items() if CATEGORY_META[c]["risk"] == "MEDIUM")
        low_val  = total_current - high_val - med_val
        high_p   = high_val / total_current * 100 if total_current else 0
        med_p    = med_val  / total_current * 100 if total_current else 0
        low_p    = low_val  / total_current * 100 if total_current else 0

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
          border-radius:12px;padding:16px 18px;margin-top:4px;">
          <div class="section-label" style="margin-bottom:12px;">▸ Risk Split (by value)</div>
          <div style="display:flex;height:8px;border-radius:4px;overflow:hidden;gap:2px;margin-bottom:10px;">
            <div style="width:{high_p:.1f}%;background:#FF6B6B;border-radius:4px 0 0 4px;"></div>
            <div style="width:{med_p:.1f}%;background:#FFB347;"></div>
            <div style="width:{low_p:.1f}%;background:#69F0AE;border-radius:0 4px 4px 0;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:11px;">
            <span style="color:#FF6B6B;">{high_p:.1f}% High</span>
            <span style="color:#FFB347;">{med_p:.1f}% Med</span>
            <span style="color:#69F0AE;">{low_p:.1f}% Low</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FUND DETAILS
# ══════════════════════════════════════════════════════════════════════════════
with tab_funds:
    st.markdown('<div class="section-label">▸ Individual Fund Breakdown</div>', unsafe_allow_html=True)

    for cat, info in sorted_cats:
        if not info["funds"]:
            continue
        color    = info["color"]
        risk     = info["risk"]
        cat_ret  = (info["gain_loss"] / info["invested"] * 100) if info["invested"] > 0 else 0
        gain_clr = "#69F0AE" if info["gain_loss"] >= 0 else "#FF6B6B"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px;">
          <div style="width:10px;height:10px;border-radius:50%;background:{color};
            box-shadow:0 0 8px {info['glow']};flex-shrink:0;"></div>
          <div style="font-size:14px;font-weight:600;color:{color};">{cat}</div>
          <span class="risk-badge risk-{risk}">{risk}</span>
          <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.3);margin-left:auto;">
            ₹{info['current_value']:,.0f} &nbsp;·&nbsp;
            <span style="color:{gain_clr};">{'+' if info['gain_loss']>=0 else ''}{cat_ret:.1f}%</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        rows_html = ""
        for f in info["funds"]:
            gl_cls   = "pos" if f["gain_loss"] >= 0 else "neg"
            gl_sign  = "+" if f["gain_loss"] >= 0 else ""
            xirr_cls = "pos" if f["xirr"] >= 0 else "neg"
            date_str = str(f["date"]) if f["date"] else "—"
            rows_html += f"""
            <tr>
              <td style="color:#F0F4FF;font-size:12px;">{f['name']}</td>
              <td>₹{f['invested']:,.0f}</td>
              <td>₹{f['current_value']:,.0f}</td>
              <td class="{gl_cls}">{gl_sign}₹{abs(f['gain_loss']):,.0f}</td>
              <td class="{gl_cls}">{gl_sign}{(f['gain_loss']/f['invested']*100) if f['invested']>0 else 0:.1f}%</td>
              <td class="{xirr_cls}">{f['xirr']:.2f}%</td>
              <td>{f['nav']:.2f}</td>
              <td style="color:rgba(255,255,255,0.4);">{date_str}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
          border-radius:12px;overflow:hidden;margin-bottom:8px;">
          <table class="fund-table">
            <thead>
              <tr>
                <th>Fund</th><th>Invested</th><th>Current</th>
                <th>P&amp;L (₹)</th><th>Return %</th><th>XIRR</th>
                <th>NAV</th><th>As of</th>
              </tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — REBALANCING CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_calc:
    st.markdown('<div class="section-label">▸ Rebalancing Calculator — based on your actual portfolio</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
      border-radius:10px;padding:12px 18px;margin-bottom:20px;
      font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.45);">
      ▸ Current portfolio value: &nbsp;
      <span style="color:#F0F4FF;">₹{total_current:,.0f}</span> &nbsp;|&nbsp;
      Invested: <span style="color:#F0F4FF;">₹{total_invested:,.0f}</span> &nbsp;|&nbsp;
      Current allocations reflect <span style="color:#FFB347;">live NAV values</span> from your daily CSV files
    </div>
    """, unsafe_allow_html=True)

    inp1, inp2, inp3 = st.columns(3)
    with inp1:
        profile = st.selectbox("Risk Profile", ["Aggressive", "Moderate", "Conservative"])
    with inp2:
        fresh_capital = st.number_input(
            "Additional Capital to Deploy (₹)",
            min_value=0, value=0, step=5_000, format="%d",
            help="New money you want to invest during rebalancing"
        )
    with inp3:
        monthly_sip = st.number_input("Monthly SIP (₹)", min_value=0, value=0, step=1_000, format="%d")

    rebal_total = total_current + fresh_capital

    TARGETS = {
        "Aggressive":   {"Small Cap": 25, "Mid Cap": 30, "Flexi Cap": 20, "Large Cap": 10, "International": 10, "Hybrid": 5},
        "Moderate":     {"Small Cap": 12, "Mid Cap": 22, "Flexi Cap": 20, "Large Cap": 25, "International": 8,  "Hybrid": 13},
        "Conservative": {"Small Cap": 5,  "Mid Cap": 10, "Flexi Cap": 20, "Large Cap": 40, "International": 5,  "Hybrid": 20},
    }

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
      border-radius:10px;padding:10px 16px;margin-bottom:16px;
      font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.4);">
      ▸ Preset targets for <span style="color:#F0F4FF;">{profile}</span> profile loaded.
      Drag sliders to customise target allocation.
      {f'Fresh capital of <span style="color:#69F0AE;">₹{fresh_capital:,}</span> included in rebalancing total.' if fresh_capital > 0 else ''}
    </div>
    """, unsafe_allow_html=True)

    target_allocs = {}
    sl_cols = st.columns(3)
    for i, cat in enumerate(CATEGORY_META.keys()):
        default = TARGETS[profile].get(cat, 0)
        curr_p  = cat_pct_of_portfolio(cat)
        with sl_cols[i % 3]:
            target_allocs[cat] = st.slider(
                cat, 0, 60, default, 1,
                key=f"rebal_{cat}",
                help=f"Your current: {curr_p:.1f}%  |  {profile} preset: {default}%"
            )

    total_tgt = sum(target_allocs.values())
    tgt_valid = abs(total_tgt - 100) <= 2
    tgt_color = "#69F0AE" if tgt_valid else "#FF6B6B"

    st.markdown(f"""
    <div style="text-align:right;font-family:'JetBrains Mono',monospace;font-size:13px;
      color:{tgt_color};margin-bottom:20px;">
      Target total: {total_tgt}% &nbsp; {'✓ valid' if tgt_valid else '✗ must sum to ~100%'}
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="calc-header">
      <div>Category</div>
      <div>Current → Target</div>
      <div>Current Value</div>
      <div>Current %</div>
      <div>Target Value</div>
      <div>Action</div>
    </div>""", unsafe_allow_html=True)

    total_buy = 0.0; total_sell = 0.0
    for cat, info in category_data.items():
        curr_val = info["current_value"]
        curr_p   = cat_pct_of_portfolio(cat)
        tgt_p    = target_allocs[cat]
        tgt_val  = rebal_total * tgt_p / 100
        diff     = tgt_val - curr_val

        if diff > 500:
            action_html = f'<span class="action-buy">▲ BUY ₹{abs(diff):,.0f}</span>'
            total_buy  += diff
        elif diff < -500:
            action_html = f'<span class="action-sell">▼ SELL ₹{abs(diff):,.0f}</span>'
            total_sell += abs(diff)
        else:
            action_html = '<span class="action-hold">— HOLD</span>'

        bar_curr = f'<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;"><div style="width:{min(curr_p,100):.1f}%;height:100%;background:{info["color"]};opacity:0.5;border-radius:2px;"></div></div>'
        bar_tgt  = f'<div style="height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;margin-top:3px;"><div style="width:{min(tgt_p,100):.1f}%;height:100%;background:{info["color"]};border-radius:2px;"></div></div>'

        st.markdown(f"""
        <div class="calc-row">
          <div style="font-size:13px;color:{info['color']};font-weight:600;">{cat}</div>
          <div>{bar_curr}{bar_tgt}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;">
            <span style="color:rgba(255,255,255,0.7);">₹{curr_val:,.0f}</span>
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,0.5);">
            {curr_p:.1f}% → {tgt_p}%
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,0.8);">
            ₹{tgt_val:,.0f}
          </div>
          <div>{action_html}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
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
        net   = total_buy - total_sell - fresh_capital
        nc    = "#69F0AE" if net <= 0 else "#FFB347"
        label = "Net Cash Free" if net <= 0 else "Net Cash Needed"
        st.markdown(f"""
        <div class="result-card" style="background:rgba(255,179,71,0.06);border:1px solid rgba(255,179,71,0.15);">
          <div class="result-val" style="color:{nc};">₹{abs(net):,.0f}</div>
          <div class="result-lbl">{label}</div>
        </div>""", unsafe_allow_html=True)
    with r4:
        st.markdown(f"""
        <div class="result-card" style="background:rgba(79,195,247,0.06);border:1px solid rgba(79,195,247,0.15);">
          <div class="result-val" style="color:#4FC3F7;">₹{rebal_total:,.0f}</div>
          <div class="result-lbl">Rebalancing Base</div>
        </div>""", unsafe_allow_html=True)

    if tgt_valid:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">▸ Fund-level Guidance (proportional within category)</div>', unsafe_allow_html=True)

        for cat, info in category_data.items():
            tgt_p    = target_allocs[cat]
            tgt_val  = rebal_total * tgt_p / 100
            curr_val = info["current_value"]
            diff     = tgt_val - curr_val
            if abs(diff) <= 500 or not info["funds"]:
                continue

            action_word  = "BUY INTO" if diff > 0 else "REDUCE"
            action_color = "#69F0AE" if diff > 0 else "#FF6B6B"
            n_funds      = len(info["funds"])
            per_fund     = abs(diff) / n_funds

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
              border-radius:12px;padding:16px 18px;margin-bottom:10px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
                <div style="width:8px;height:8px;border-radius:50%;background:{info['color']};"></div>
                <div style="font-size:13px;font-weight:600;color:{info['color']};">{cat}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{action_color};margin-left:auto;">
                  {action_word} ₹{abs(diff):,.0f} &nbsp;·&nbsp; ≈ ₹{per_fund:,.0f} / fund
                </div>
              </div>
            """, unsafe_allow_html=True)

            for f in info["funds"]:
                fund_curr  = f["current_value"]
                fund_share = fund_curr / curr_val if curr_val > 0 else 1 / n_funds
                fund_diff  = diff * fund_share
                act_c      = "#69F0AE" if fund_diff > 0 else "#FF6B6B"
                act_txt    = f"▲ +₹{fund_diff:,.0f}" if fund_diff > 0 else f"▼ -₹{abs(fund_diff):,.0f}"

                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;
                  padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.02);">
                  <div style="font-size:11px;color:rgba(255,255,255,0.6);flex:1;">{f['name']}</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.35);">
                    ₹{f['current_value']:,.0f}
                  </div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                    font-weight:600;color:{act_c};min-width:120px;text-align:right;">{act_txt}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    if monthly_sip > 0 and tgt_valid:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
          border-radius:14px;padding:20px 22px;">
          <div class="section-label" style="margin-bottom:14px;">▸ Monthly SIP Split — ₹{monthly_sip:,}</div>
        """, unsafe_allow_html=True)

        for cat, info in category_data.items():
            tgt     = target_allocs[cat]
            amt     = monthly_sip * tgt / 100
            if amt <= 0:
                continue
            n_funds  = len(info["funds"])
            per_fund = amt / n_funds if n_funds > 0 else 0

            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
              <div style="width:100px;font-size:12px;color:rgba(255,255,255,0.6);">{cat}</div>
              <div style="flex:1;height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;">
                <div style="width:{tgt}%;height:100%;background:{info['color']};border-radius:2px;"></div>
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
                color:{info['color']};width:160px;text-align:right;">
                ₹{amt:,.0f} / mo &nbsp;<span style="color:rgba(255,255,255,0.3);font-size:10px;">(≈₹{per_fund:,.0f}/fund)</span>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROFIT TARGET CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_profit:
    st.markdown('<div class="section-label">▸ Profit Target Calculator — units to sell for desired profit</div>', unsafe_allow_html=True)

    # ── Inputs ───────────────────────────────────────────────────────────────
    gc1, gc2, gc3 = st.columns([2, 1, 1])
    with gc1:
        profit_target = st.number_input(
            "Desired Profit (₹)",
            min_value=1_000, value=125_000, step=5_000, format="%d",
            help="The profit (gain) amount you want to realise by selling units"
        )
    with gc2:
        tax_rate = st.number_input(
            "Tax Rate on Gains (%)",
            min_value=0.0, max_value=40.0, value=12.5, step=0.5, format="%.1f",
            help="LTCG = 12.5%, STCG = 20% for equity funds"
        )
    with gc3:
        sort_by = st.selectbox(
            "Sort funds by",
            ["Absolute P&L (↓)", "Return % (↓)", "XIRR (↓)", "Fund Name (A-Z)"]
        )

    # gross profit needed before tax to net the desired amount
    gross_target = profit_target / (1 - tax_rate / 100) if tax_rate < 100 else profit_target

    # ── Sorting ──────────────────────────────────────────────────────────────
    def sort_key(f):
        if sort_by == "Absolute P&L (↓)": return -f["gain_loss"]
        if sort_by == "Return % (↓)":     return -f["return_pct"]
        if sort_by == "XIRR (↓)":         return -f["xirr"]
        return f["name"]

    sorted_funds = sorted([f for f in funds_data if f["current_value"] > 0], key=sort_key)

    # ── Info strip ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
      border-radius:10px;padding:10px 18px;margin:12px 0 18px;
      font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.4);">
      ▸ Profit target: &nbsp;<span style="color:#69F0AE;">₹{profit_target:,}</span>
      &nbsp;·&nbsp; Tax rate: <span style="color:#FFB347;">{tax_rate}%</span>
      &nbsp;·&nbsp; Gross sale needed before tax:
      <span style="color:#F0F4FF;">₹{gross_target:,.0f}</span>
      &nbsp;·&nbsp; Units = gross_profit_target ÷ gain_per_unit
    </div>
    """, unsafe_allow_html=True)

    # ── Per-fund cards ───────────────────────────────────────────────────────
    for f in sorted_funds:
        invested     = f["invested"]
        curr_val     = f["current_value"]
        gain_total   = f["gain_loss"]
        nav          = f["nav"]
        cat          = f["category"]
        color        = CATEGORY_META.get(cat, {}).get("color", "#888")
        glow         = CATEGORY_META.get(cat, {}).get("glow",  "rgba(136,136,136,0.2)")
        risk         = CATEGORY_META.get(cat, {}).get("risk",  "—")

        total_units   = curr_val / nav if nav > 0 else 0
        avg_cost      = invested / total_units if total_units > 0 else 0
        gain_per_unit = nav - avg_cost
        return_pct    = (gain_total / invested * 100) if invested > 0 else 0

        if gain_per_unit > 0:
            units_to_sell  = gross_target / gain_per_unit
            sale_value     = units_to_sell * nav
            tax_amount     = (units_to_sell * gain_per_unit) * (tax_rate / 100)
            net_profit     = (units_to_sell * gain_per_unit) - tax_amount
            feasible       = units_to_sell <= total_units
            pct_of_holding = (units_to_sell / total_units * 100) if total_units > 0 else 0
        else:
            units_to_sell  = None
            sale_value     = None
            tax_amount     = None
            net_profit     = None
            feasible       = False
            pct_of_holding = 0

        gl_color = "#69F0AE" if gain_total >= 0 else "#FF6B6B"

        if gain_per_unit <= 0:
            banner_html = '<div class="pt-warn">⚠ No profit per unit — fund is at a loss or break-even. Cannot achieve target from this fund.</div>'
        elif not feasible:
            banner_html = f"""
            <div class="pt-result-banner" style="background:rgba(255,107,107,0.07);border:1px solid rgba(255,107,107,0.18);">
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#FF6B6B;">{units_to_sell:,.2f}</div>
                <div class="pt-result-lbl">Units needed</div>
              </div>
              <div class="pt-sep"></div>
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#FF6B6B;">{total_units:,.2f}</div>
                <div class="pt-result-lbl">Units available</div>
              </div>
              <div class="pt-sep"></div>
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#FF6B6B;">₹{sale_value:,.0f}</div>
                <div class="pt-result-lbl">Sale value needed</div>
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                color:#FF6B6B;margin-left:auto;">✗ Insufficient — sell all {total_units:,.2f} units for ₹{curr_val:,.0f}</div>
            </div>"""
        else:
            banner_html = f"""
            <div class="pt-result-banner" style="background:rgba(105,240,174,0.06);border:1px solid rgba(105,240,174,0.18);">
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#69F0AE;">{units_to_sell:,.2f}</div>
                <div class="pt-result-lbl">Units to sell</div>
              </div>
              <div class="pt-sep"></div>
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#4FC3F7;">₹{sale_value:,.0f}</div>
                <div class="pt-result-lbl">Sale proceeds</div>
              </div>
              <div class="pt-sep"></div>
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#FFB347;">₹{tax_amount:,.0f}</div>
                <div class="pt-result-lbl">Tax (~{tax_rate}%)</div>
              </div>
              <div class="pt-sep"></div>
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:#69F0AE;">₹{net_profit:,.0f}</div>
                <div class="pt-result-lbl">Net profit</div>
              </div>
              <div class="pt-sep"></div>
              <div class="pt-result-item">
                <div class="pt-result-val" style="color:rgba(255,255,255,0.5);">{pct_of_holding:.1f}%</div>
                <div class="pt-result-lbl">of holding sold</div>
              </div>
              <div style="margin-left:auto;">
                <div style="height:5px;width:120px;background:rgba(255,255,255,0.07);border-radius:3px;overflow:hidden;">
                  <div style="width:{min(pct_of_holding,100):.1f}%;height:100%;background:#69F0AE;border-radius:3px;"></div>
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                  color:rgba(255,255,255,0.3);margin-top:4px;text-align:right;">{total_units - units_to_sell:,.2f} units remain</div>
              </div>
            </div>"""

        st.markdown(f"""
        <div class="pt-fund-card" style="border-left: 3px solid {color};">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:6px;">
            <div>
              <div class="pt-fund-name">{f['name']}</div>
              <div class="pt-fund-meta">{cat} &nbsp;·&nbsp; <span class="risk-badge risk-{risk}">{risk}</span></div>
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              color:rgba(255,255,255,0.25);text-align:right;white-space:nowrap;">
              NAV ₹{nav:.4f} &nbsp;·&nbsp; as of {f['date']}
            </div>
          </div>
          <div class="pt-grid">
            <div class="pt-kv">
              <div class="pt-kv-label">Invested</div>
              <div class="pt-kv-val">₹{invested:,.0f}</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">Current Value</div>
              <div class="pt-kv-val">₹{curr_val:,.0f}</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">Total Gain</div>
              <div class="pt-kv-val" style="color:{gl_color};">{"+" if gain_total >= 0 else ""}₹{gain_total:,.0f} ({return_pct:.1f}%)</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">XIRR</div>
              <div class="pt-kv-val" style="color:{'#69F0AE' if f['xirr']>=0 else '#FF6B6B'};">{f['xirr']:.2f}%</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">Est. Units Held</div>
              <div class="pt-kv-val">{total_units:,.3f}</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">Avg. Cost/Unit</div>
              <div class="pt-kv-val">₹{avg_cost:.4f}</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">Gain / Unit</div>
              <div class="pt-kv-val" style="color:{gl_color};">₹{gain_per_unit:.4f}</div>
            </div>
            <div class="pt-kv">
              <div class="pt-kv-label">Current NAV</div>
              <div class="pt-kv-val" style="color:{color};">₹{nav:.4f}</div>
            </div>
          </div>
          {banner_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,0.15);
      border-top:1px solid rgba(255,255,255,0.05);padding-top:12px;margin-top:20px;letter-spacing:0.08em;">
      ⚠ Units estimated as current_value ÷ NAV (point-in-time approximation).
      Avg cost = total_invested ÷ estimated_units. Tax shown is simplified — actual LTCG/STCG depends on
      holding period per lot. Consult a SEBI-registered advisor for redemption planning.
    </div>
    """, unsafe_allow_html=True)


# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(255,255,255,0.15);border-top:1px solid rgba(255,255,255,0.05);
  padding-top:14px;letter-spacing:0.1em;">
  FOR INFORMATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE · CONSULT A SEBI-REGISTERED ADVISOR
</div>
""", unsafe_allow_html=True)
