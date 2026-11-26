# App.py — Taurus home
import time
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

# ─────────────────────────────────────────────
# Page config — MUST be the first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus: Home",
    page_icon="🐂",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.add_units import show_add_units
from utils.sidebar_style import render_sidebar, scale_component_html
from utils.market_history_chart import show_market_history_chart

render_sidebar("home")

IST   = ZoneInfo("Asia/Kolkata")
TEAL  = "#00f5d4"
UP    = "#00f5d4"
DOWN  = "#ff4d6d"

# ─────────────────────────────────────────────
# Global styles
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; color: #e8e2d5; }

.stApp {
    background-color: #080b0f;
    background-image:
        radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(0, 245, 212, 0.07) 0%, transparent 65%),
        radial-gradient(ellipse 60% 80% at 85% 75%,  rgba(0, 180, 245, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 50% 100%, rgba(0, 245, 212, 0.04) 0%, transparent 55%),
        radial-gradient(ellipse 100% 100% at 50% 0%,  rgba(8, 11, 15, 0.9)  0%, #080b0f 70%);
    background-size: cover;
    background-attachment: fixed;
    position: relative;
    min-height: 100vh;
}
.stApp::before {
    content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 70% 55% at 8%  18%,  rgba(0, 245, 212, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 55% 70% at 88% 72%,  rgba(0, 140, 255, 0.05) 0%, transparent 55%),
        radial-gradient(ellipse 45% 35% at 52% 98%,  rgba(0, 245, 212, 0.04) 0%, transparent 50%);
    animation: taurus-pulse 8s ease-in-out infinite;
}
.stApp::after {
    content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image: radial-gradient(circle, rgba(0,245,212,0.16) 1px, transparent 1px);
    background-size: 38px 38px; opacity: 0.4;
}
@keyframes taurus-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.55; } }
.stApp > * { position: relative; z-index: 1; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
    border-right: 1px solid rgba(0, 245, 212, 0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(12px);
    visibility: visible !important;
    display: block !important;
}
[data-testid="stSidebarCollapsedControl"] { visibility: visible !important; display: flex !important; }
[data-testid="stSidebarNav"] { display: block !important; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
}
hr { border-color: rgba(0, 245, 212, 0.1) !important; }

/* ── Section labels ── */
.tz-section { display:flex; align-items:center; gap:14px; margin: 2rem 0 0.9rem; }
.tz-section-title {
    font-family:'Syne',sans-serif; font-size:0.85rem; font-weight:700;
    letter-spacing:0.16em; text-transform:uppercase; color:rgba(0,245,212,0.85); white-space:nowrap;
}
.tz-section-sub {
    font-family:'DM Mono',monospace; font-size:0.72rem; letter-spacing:0.08em;
    color:rgba(200,230,225,0.5); white-space:nowrap;
}
.tz-section-line { flex:1; height:1px; background:linear-gradient(90deg, rgba(0,245,212,0.25), transparent); }
.tz-sublabel {
    height:38px; display:flex; align-items:center; gap:10px;
    font-family:'Syne',sans-serif; font-size:0.75rem; font-weight:700;
    letter-spacing:0.12em; text-transform:uppercase; color:rgba(200,230,225,0.75);
}
.tz-sublabel small {
    font-family:'DM Mono',monospace; font-weight:400; letter-spacing:0.06em;
    text-transform:none; color:rgba(200,230,225,0.45); font-size:0.7rem;
}
.tz-badge {
    display:inline-flex; align-items:center; gap:6px; padding:4px 10px; border-radius:20px;
    font-family:'DM Mono',monospace; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase;
}

/* ── Buttons ── */
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 0.9rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important;
    background: linear-gradient(135deg, rgba(0,245,212,0.12), rgba(0,201,255,0.08)) !important;
    color: #00f5d4 !important; border: 1px solid rgba(0,245,212,0.4) !important;
    border-radius: 8px !important; padding: 0.65rem 1.8rem !important;
    transition: all 0.25s !important; box-shadow: 0 0 20px rgba(0,245,212,0.07) !important;
}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, rgba(0,245,212,0.22), rgba(0,201,255,0.15)) !important;
    border-color: rgba(0,245,212,0.7) !important;
    box-shadow: 0 0 30px rgba(0,245,212,0.18), 0 0 60px rgba(0,245,212,0.06) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"], [data-testid="stBaseButton-secondary"] {
    font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important;
    background: rgba(255,255,255,0.04) !important; color: #cfeee8 !important;
    border: 1px solid rgba(0,245,212,0.25) !important; border-radius: 8px !important;
}
.stButton > button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover {
    border-color: rgba(0,245,212,0.6) !important; color: #fff !important;
}

/* ── Alerts ── */
.stSuccess > div, .stError > div, .stInfo > div, .stSpinner > div {
    font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important;
}
.stInfo    { background: rgba(0,201,255,0.06) !important; border-left-color: #00c9ff !important; }
.stSuccess { background: rgba(0,245,212,0.07) !important; border-left-color: #00f5d4 !important; }
.stError   { background: rgba(255,70,70,0.07) !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# Navigation cards: the whole card is clickable via an invisible button laid over it.
# Needs st.container(key=...) (Streamlit >= 1.39), which adds a "st-key-<key>" CSS class.
st.markdown("""
<style>
div[class*="st-key-navcard_"] { position: relative; gap: 0 !important; }
div[class*="st-key-navcard_"] .stElementContainer,
div[class*="st-key-navcard_"] .element-container { position: static !important; }

.tz-nav {
    position: relative; overflow: hidden;
    background: rgba(8,14,20,0.78);
    border: 1px solid rgba(0,245,212,0.2);
    border-radius: 12px; padding: 1.3rem 1.4rem 1.2rem;
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    pointer-events: none;
    transition: background 0.25s, border-color 0.25s, transform 0.22s;
}
.tz-nav .bar {
    position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#00f5d4,#00c9ff); opacity:0.4; transition:opacity 0.3s;
}
.tz-nav .dot {
    position:absolute; top:1rem; right:1rem; width:7px; height:7px; border-radius:50%;
    background:rgba(0,245,212,0.35); animation:pdot 2.2s ease-in-out infinite;
}
.tz-nav .num  { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800;
                color:rgba(0,245,212,0.25); line-height:1; margin-bottom:0.55rem; transition:color 0.3s; }
.tz-nav .name { font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700;
                color:#e6f8f4; margin-bottom:0.3rem; transition:color 0.3s; }
.tz-nav .desc { font-family:'DM Mono',monospace; font-size:0.76rem; line-height:1.5;
                color:rgba(210,240,235,0.7); letter-spacing:0.02em; transition:color 0.3s; }
.tz-nav .go   { margin-top:0.85rem; display:flex; align-items:center; gap:2px;
                font-family:'DM Mono',monospace; font-size:0.85rem; color:rgba(0,245,212,0.75); }
.tz-nav .go span { display:inline-block; animation:chevron-slide 1.1s ease-in-out infinite; }
.tz-nav .go span:nth-child(2) { animation-delay:0.18s; }
.tz-nav .go span:nth-child(3) { animation-delay:0.36s; }

div[class*="st-key-navcard_"]:hover .tz-nav { background:rgba(0,245,212,0.09); border-color:rgba(0,245,212,0.65); transform:translateY(-3px); }
div[class*="st-key-navcard_"]:hover .tz-nav .bar  { opacity:1; }
div[class*="st-key-navcard_"]:hover .tz-nav .num  { color:rgba(0,245,212,0.6); }
div[class*="st-key-navcard_"]:hover .tz-nav .name { color:#fff; }
div[class*="st-key-navcard_"]:hover .tz-nav .desc { color:rgba(210,240,235,0.92); }

div[class*="st-key-navcard_"] [data-testid="stButton"],
div[class*="st-key-navcard_"] .stButton {
    position:absolute !important; inset:0 !important; z-index:9 !important;
}
div[class*="st-key-navcard_"] [data-testid="stButton"] button,
div[class*="st-key-navcard_"] .stButton > button {
    width:100% !important; height:100% !important; background:transparent !important;
    border:none !important; box-shadow:none !important; opacity:0 !important;
    cursor:pointer !important; padding:0 !important;
}
@keyframes chevron-slide {
    0%   { opacity:0.15; transform:translateX(-4px); }
    50%  { opacity:1;    transform:translateX(2px);  }
    100% { opacity:0.15; transform:translateX(-4px); }
}
@keyframes pdot {
    0%   { box-shadow:0 0 0 0   rgba(0,245,212,0.6); }
    60%  { box-shadow:0 0 0 6px rgba(0,245,212,0);   }
    100% { box-shadow:0 0 0 0   rgba(0,245,212,0);   }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
WORKFLOWS = [
    {"name": "Fetch NAV Daily",     "file": "fetch_nav_daily.yml",         "num": "01"},
    {"name": "Portfolio Overview",  "file": "update_fund_snapshots.yml",   "num": "02"},
    {"name": "Individual Funds",    "file": "update_portfolio_daily.yml",  "num": "03"},
    {"name": "capture_market_close",    "file": "capture_market_close.yml",    "num": "04"},
]

PAGES = [
    {"num": "01", "name": "Portfolio Overview", "description": "Overall fund snapshot",
     "page": "pages/1_Portfolio_Overview.py"},
    {"num": "02", "name": "Individual Funds",   "description": "Individual fund details",
     "page": "pages/2_Fund_Details.py"},
    {"num": "03", "name": "Tools",              "description": "Calculators & utilities",
     "page": "pages/4_Tools.py"},
    {"num": "04", "name": "Smart SIP",          "description": "SIP planner & projections",
     "page": "pages/6_smart_sip.py"},
]

DELAY_SECONDS = 60


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def section(title: str, sub: str = ""):
    sub_html = f'<span class="tz-section-sub">{sub}</span>' if sub else ""
    st.markdown(
        f'<div class="tz-section"><span class="tz-section-title">{title}</span>'
        f'{sub_html}<span class="tz-section-line"></span></div>',
        unsafe_allow_html=True,
    )


def sublabel(title: str, note: str = ""):
    note_html = f"<small>{note}</small>" if note else ""
    st.markdown(f'<div class="tz-sublabel">{title}{note_html}</div>', unsafe_allow_html=True)


def trigger_workflow(workflow_filename: str) -> dict:
    try:
        token = st.secrets["GITHUB_TOKEN"]
        owner = st.secrets["GITHUB_OWNER"]
        repo  = st.secrets["GITHUB_REPO"]
    except Exception as e:
        return {"success": False, "message": f"Missing secret: {e}"}

    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_filename}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        response = requests.post(url, headers=headers, json={"ref": "main"}, timeout=20)
    except requests.RequestException as e:
        return {"success": False, "message": f"Request failed: {e}"}

    if response.status_code == 204:
        return {"success": True, "message": "Triggered successfully ✅"}
    return {"success": False, "message": f"Error {response.status_code}: {response.text}"}


def nse_session_open(now: datetime) -> bool:
    """Mon–Fri 09:15–15:30 IST. Does not know about exchange holidays."""
    return now.weekday() < 5 and dtime(9, 15) <= now.time() <= dtime(15, 30)


# ─────────────────────────────────────────────
# Header: wordmark + live IST clock in one row
# ─────────────────────────────────────────────
components.html(scale_component_html("""
<!DOCTYPE html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@300;400;500&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: transparent; font-family: 'DM Mono', monospace; padding: 0.6rem 0 0; overflow: hidden; }
  .row { position:relative; width:100%; }
  .brand { display:flex; align-items:center; gap:1rem; }
  h1 {
    font-family:'Syne',sans-serif; font-weight:800; letter-spacing:-0.03em; line-height:1;
    white-space:nowrap; font-size:clamp(2rem, 8vw, 4rem);
    background:linear-gradient(135deg,#00f5d4 0%,#00c9ff 55%,#a78bfa 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  }
  .sub {
    font-size:0.72rem; letter-spacing:0.26em; color:rgba(0,245,212,0.65);
    text-transform:uppercase; margin-top:0.5rem; white-space:nowrap;
  }
  .pulser { position:relative; width:44px; height:44px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
  .ring { position:absolute; width:20px; height:20px; border-radius:50%; border:1px solid #00f5d4; opacity:0; animation:ripple 1.5s ease-out infinite; }
  .ring:nth-child(2) { animation-delay:0.3s; } .ring:nth-child(3) { animation-delay:0.6s; }
  @keyframes ripple { 0% { transform:scale(1); opacity:0.65; } 100% { transform:scale(2.4); opacity:0; } }
  .core { width:13px; height:13px; border-radius:50%; z-index:2;
          background:radial-gradient(circle at 35% 35%, #00f5d4cc, #00f5d444);
          animation:throb 0.9s ease-in-out infinite alternate; }
  @keyframes throb { from { box-shadow:0 0 5px #00f5d499; } to { box-shadow:0 0 12px #00f5d4dd, 0 0 20px #00f5d466; } }
  .live { font-size:0.68rem; letter-spacing:0.22em; color:rgba(0,245,212,0.7); text-transform:uppercase; animation:blink 1.4s step-start infinite; }
  @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.2; } }
  /* Mobile first: clock sits under the wordmark, time and date on one line */
  .clock { display:flex; align-items:baseline; flex-wrap:wrap; gap:0.2rem 0.9rem; margin-top:0.8rem; }
  .time { font-size:1.35rem; font-weight:500; color:#eef9f6; letter-spacing:0.06em; font-variant-numeric:tabular-nums; white-space:nowrap; }
  .time small { font-size:0.7rem; color:rgba(0,245,212,0.65); letter-spacing:0.16em; margin-left:6px; }
  .date { font-family:'Syne',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:0.1em; color:rgba(200,230,225,0.65); text-transform:uppercase; white-space:nowrap; }
  .sub { white-space:normal; letter-spacing:0.14em; font-size:0.66rem; }
  /* Wide screens: clock moves to the top-right, aligned with the subtitle */
  @media (min-width: 640px) {
    .clock { position:absolute; right:0; bottom:0; display:block; text-align:right; margin-top:0; }
    .time { font-size:1.6rem; }
    .date { display:block; font-size:0.75rem; letter-spacing:0.14em; margin-top:0.3rem; }
    .sub { white-space:nowrap; letter-spacing:0.26em; font-size:0.72rem; }
  }
  .divider { width:100%; height:1px; margin-top:1rem; background:linear-gradient(90deg, rgba(0,245,212,0.4), rgba(0,201,255,0.2) 50%, transparent); }
</style></head>
<body>
<div class="row">
  <div>
    <div class="brand">
      <h1>TAURUS</h1>
      <div class="pulser"><div class="ring"></div><div class="ring"></div><div class="ring"></div><div class="core"></div></div>
      <span class="live">live</span>
    </div>
    <div class="sub">Portfolio Intelligence System</div>
  </div>
  <div class="clock">
    <div class="time"><span id="t">--:--:--</span><small>IST</small></div>
    <div class="date" id="d">--</div>
  </div>
</div>
<div class="divider"></div>
<script>
  const dF = new Intl.DateTimeFormat('en-GB', {timeZone:'Asia/Kolkata', weekday:'long', day:'2-digit', month:'short', year:'numeric'});
  const tF = new Intl.DateTimeFormat('en-GB', {timeZone:'Asia/Kolkata', hour:'2-digit', minute:'2-digit', second:'2-digit', hourCycle:'h23'});
  const parts = (f, d) => { const o = {}; f.formatToParts(d).forEach(p => o[p.type] = p.value); return o; };
  function tick() {
    const now = new Date(), dp = parts(dF, now), tp = parts(tF, now);
    document.getElementById('d').textContent = `${dp.weekday}, ${dp.day} ${dp.month} ${dp.year}`;
    document.getElementById('t').textContent = `${tp.hour}:${tp.minute}:${tp.second}`;
  }
  tick(); setInterval(tick, 1000);
</script>
</body></html>
"""), height=155, scrolling=False)


# ─────────────────────────────────────────────
# Shared ticker card renderer
# ─────────────────────────────────────────────
TICKER_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@300;400;500&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { background: transparent; font-family: 'DM Mono', monospace; padding: 2px 0; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; width: 100%; }
.card {
  position: relative; overflow: hidden; background: rgba(8,14,20,0.78);
  border: 1px solid rgba(255,255,255,0.09); border-radius: 12px;
  padding: 0.8rem 1rem 0.75rem; backdrop-filter: blur(12px);
}
.card::before { content:""; position:absolute; top:0; left:0; right:0; height:2px; background:var(--accent); opacity:0.65; }
.top { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem; }
.tag { font-family:'Syne',sans-serif; font-size:0.68rem; font-weight:700; letter-spacing:0.16em; color:var(--accent); text-transform:uppercase; }
.dot { width:6px; height:6px; border-radius:50%; background:var(--accent); animation:pdot 1.8s ease-in-out infinite; }
@keyframes pdot { 0% { box-shadow:0 0 0 0 rgba(0,245,212,0.7); } 60% { box-shadow:0 0 0 5px rgba(0,245,212,0); } 100% { box-shadow:0 0 0 0 rgba(0,245,212,0); } }
.name { font-family:'Syne',sans-serif; font-size:0.78rem; font-weight:700; color:rgba(220,240,235,0.75); letter-spacing:0.05em; margin-bottom:0.35rem; }
.price { font-family:'DM Mono',monospace; font-size:clamp(1.3rem, 3vw, 1.75rem); font-weight:500; color:#eef9f6; letter-spacing:-0.01em; line-height:1; white-space:nowrap; font-variant-numeric:tabular-nums; }
.foot { display:flex; justify-content:space-between; align-items:baseline; gap:0.5rem; flex-wrap:wrap; margin-top:0.55rem; }
.delta { font-size:0.8rem; font-weight:500; }
.ts { font-size:0.64rem; color:rgba(200,230,225,0.5); letter-spacing:0.08em; text-transform:uppercase; }
"""


def card_html(tag, name, price_text, change, pct, decimals, accent, ts, live=False):
    up    = change >= 0
    color = UP if up else DOWN
    arrow = "▲" if up else "▼"
    sign  = "+" if up else "−"
    dot   = '<span class="dot"></span>' if live else ""
    return (
        f'<div class="card" style="--accent:{accent}">'
        f'<div class="top"><span class="tag">{tag}</span>{dot}</div>'
        f'<div class="name">{name}</div>'
        f'<div class="price">{price_text}</div>'
        f'<div class="foot">'
        f'<span class="delta" style="color:{color}">{arrow} {abs(change):,.{decimals}f} ({sign}{abs(pct):.2f}%)</span>'
        f'<span class="ts">{ts} IST</span></div></div>'
    )


def render_cards(cards: str, height: int = 135):
    components.html(
        scale_component_html(
            f"<!DOCTYPE html><html><head><meta charset='utf-8'/><style>{TICKER_CSS}</style></head>"
            f"<body><div class='grid'>{cards}</div></body></html>"
        ),
        height=height, scrolling=False,
    )


def _quote(symbol: str, decimals: int) -> dict:
    fi   = yf.Ticker(symbol).fast_info
    last = float(fi.last_price)
    prev = float(fi.previous_close)
    return {
        "price":  round(last, decimals),
        "change": round(last - prev, decimals),
        "pct":    round((last - prev) / prev * 100, 2),
    }


# ─────────────────────────────────────────────
# Market data (cached at module level)
# ─────────────────────────────────────────────
@st.cache_data(ttl=25)
def get_market_data():
    try:
        return {
            "nifty":  _quote("^NSEI", 2),
            "sensex": _quote("^BSESN", 2),
            "timestamp": datetime.now(IST).strftime("%H:%M:%S"),
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=300)
def get_currency_data():
    try:
        return {
            "usd": _quote("USDINR=X", 4),
            "eur": _quote("EURINR=X", 4),
            "timestamp": datetime.now(IST).strftime("%H:%M:%S"),
            "error": None,
        }
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────────────────────────
# Market ticker — auto-refreshes every 30s
# ─────────────────────────────────────────────
@st.fragment(run_every=30)
def market_ticker():
    now = datetime.now(IST)
    left, right = st.columns([3, 2])
    with left:
        sublabel("Indian indices", "auto · 30s")
    with right:
        if nse_session_open(now):
            badge = ('<span class="tz-badge" style="background:rgba(0,245,212,0.1);'
                     'border:1px solid rgba(0,245,212,0.3);color:#00f5d4;">● Session open</span>')
        else:
            badge = ('<span class="tz-badge" style="background:rgba(255,255,255,0.05);'
                     'border:1px solid rgba(255,255,255,0.15);color:rgba(220,235,230,0.7);">○ Session closed</span>')
        st.markdown(f'<div style="height:38px;display:flex;align-items:center;justify-content:flex-end;">{badge}</div>',
                    unsafe_allow_html=True)

    mkt = get_market_data()
    if mkt.get("error"):
        st.warning(f"⚠️ Market data unavailable: {mkt['error']}")
        return

    ni, se, ts = mkt["nifty"], mkt["sensex"], mkt["timestamp"]
    render_cards(
        card_html("NSE", "NIFTY 50", f"{ni['price']:,.2f}", ni["change"], ni["pct"], 2, "#00f5d4", ts, live=True)
        + card_html("BSE", "SENSEX", f"{se['price']:,.2f}", se["change"], se["pct"], 2, "#a78bfa", ts, live=True)
    )


# ─────────────────────────────────────────────
# Currency ticker — manual refresh
# ─────────────────────────────────────────────
@st.fragment
def currency_ticker():
    left, right = st.columns([3, 2])
    with left:
        sublabel("Currency", "vs INR · cached 5 min")
    with right:
        if st.button("↻ Refresh", key="refresh_currency", use_container_width=True):
            get_currency_data.clear()

    cur = get_currency_data()
    if cur.get("error"):
        st.warning(f"⚠️ Currency data unavailable: {cur['error']}")
        return

    usd, eur, ts = cur["usd"], cur["eur"], cur["timestamp"]
    render_cards(
        card_html("USD / INR", "US DOLLAR", f"₹{usd['price']:,.4f}", usd["change"], usd["pct"], 4, "#ffd166", ts)
        + card_html("EUR / INR", "EURO", f"₹{eur['price']:,.4f}", eur["change"], eur["pct"], 4, "#4cc9f0", ts)
    )


section("Markets")
col_mkt, col_cur = st.columns(2, gap="medium")
with col_mkt:
    market_ticker()
with col_cur:
    currency_ticker()


# ─────────────────────────────────────────────
# Market history chart
# ─────────────────────────────────────────────
section("Market history", "Nifty 50 · Sensex")
show_market_history_chart()


# ─────────────────────────────────────────────
# Navigation cards
# ─────────────────────────────────────────────
section("Navigate")

for col, pg in zip(st.columns(4, gap="medium"), PAGES):
    with col:
        with st.container(key=f"navcard_{pg['num']}"):
            st.markdown(
                f'<div class="tz-nav"><div class="bar"></div><div class="dot"></div>'
                f'<div class="num">{pg["num"]}</div>'
                f'<div class="name">{pg["name"]}</div>'
                f'<div class="desc">{pg["description"]}</div>'
                f'<div class="go"><span>›</span><span>›</span><span>›</span></div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Open", key=f"go_{pg['num']}"):
                st.switch_page(pg["page"])


# ─────────────────────────────────────────────
# Add units
# ─────────────────────────────────────────────
section("Add units")
show_add_units()


# ─────────────────────────────────────────────
# Data pipeline
# ─────────────────────────────────────────────
section("Data pipeline", f"{len(WORKFLOWS)} GitHub workflows · {DELAY_SECONDS}s between steps")

col_btn, col_btn2, _ = st.columns([1.2, 1.2, 3])
with col_btn:
    clicked = st.button("▶  Update Portfolio", type="primary", use_container_width=True)
with col_btn2:
    nav_clicked = st.button("📥  Fetch NAV History", type="primary", use_container_width=True)

if clicked:
    overall_success = True
    with st.status("Running pipeline…", expanded=True) as status:
        for i, wf in enumerate(WORKFLOWS):
            with st.spinner(f"[ {wf['num']} ] Triggering {wf['name']} ..."):
                result = trigger_workflow(wf["file"])

            if result["success"]:
                st.success(f"**{wf['num']} · {wf['name']}** → {result['message']}")
            else:
                st.error(f"**{wf['num']} · {wf['name']}** → {result['message']}")
                st.error(f"⛔ Pipeline halted at step {wf['num']}")
                overall_success = False
                break

            if i < len(WORKFLOWS) - 1:
                countdown = st.empty()
                for remaining in range(DELAY_SECONDS, 0, -1):
                    countdown.info(f"⏱  Next step in **{remaining}s** ...")
                    time.sleep(1)
                countdown.empty()

        if overall_success:
            status.update(label=f"All {len(WORKFLOWS)} pipeline steps triggered", state="complete")
        else:
            status.update(label="Pipeline stopped early — check errors", state="error")

if nav_clicked:
    with st.status("Fetching NAV history…", expanded=True) as status:
        with st.spinner("[ 01 ] Triggering Fetch NAV History ..."):
            result = trigger_workflow("fetch_nav_history.yml")

        if result["success"]:
            st.success(f"**01 · Fetch NAV History** → {result['message']}")
            st.info("⏱  Workflow running in background — NAVHistory/*.json files will update in ~1–2 min.")
            status.update(label="NAV history workflow triggered", state="complete")
        else:
            st.error(f"**01 · Fetch NAV History** → {result['message']}")
            status.update(label="NAV history workflow failed", state="error")

st.divider()

from utils.footer import show_footer
show_footer()
