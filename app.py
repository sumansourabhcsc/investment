import streamlit as st
import streamlit.components.v1 as components
import requests
import time

from utils.add_units import show_add_units


# ─────────────────────────────────────────────
# Page Config — MUST be first, only once
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus | Home",
    page_icon="🐂",
    layout="wide"
)

# ─────────────────────────────────────────────
# Full Redesign — Styles
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    color: #e8e2d5;
}

/* ── Base: deep midnight navy (replaces image background) ── */
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

/* ── Layer 1: animated teal orb pulse ── */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 55% at 8%  18%,  rgba(0, 245, 212, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 55% 70% at 88% 72%,  rgba(0, 140, 255, 0.05) 0%, transparent 55%),
        radial-gradient(ellipse 45% 35% at 52% 98%,  rgba(0, 245, 212, 0.04) 0%, transparent 50%);
    z-index: 0;
    pointer-events: none;
    animation: taurus-pulse 8s ease-in-out infinite;
}

/* ── Layer 2: dot-grid constellation ── */
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
    border-right: 1px solid rgba(0, 245, 212, 0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(12px);
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

.stButton > button[kind="primary"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, rgba(0,245,212,0.12), rgba(0,201,255,0.08)) !important;
    color: #00f5d4 !important;
    border: 1px solid rgba(0,245,212,0.4) !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.25s !important;
    box-shadow: 0 0 20px rgba(0,245,212,0.07) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, rgba(0,245,212,0.22), rgba(0,201,255,0.15)) !important;
    border-color: rgba(0,245,212,0.7) !important;
    box-shadow: 0 0 30px rgba(0,245,212,0.18), 0 0 60px rgba(0,245,212,0.06) !important;
    transform: translateY(-1px) !important;
}

.stSuccess > div, .stError > div, .stInfo > div, .stSpinner > div {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

hr { border-color: rgba(0, 245, 212, 0.1) !important; }

.stInfo {
    background: rgba(0,201,255,0.06) !important;
    border-left-color: #00c9ff !important;
}

.stSuccess {
    background: rgba(0,245,212,0.07) !important;
    border-left-color: #00f5d4 !important;
}

.stError { background: rgba(255,70,70,0.07) !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.2); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GitHub Config
# ─────────────────────────────────────────────
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_OWNER = st.secrets["GITHUB_OWNER"]
GITHUB_REPO  = st.secrets["GITHUB_REPO"]

WORKFLOWS = [
    {
        "name": "Fetch NAV Daily",
        "file": "fetch_nav_daily.yml",
        "description": "Fetches latest NAV data for all funds",
        "num": "01",
        "link": "https://taurus.streamlit.app/Portfolio_Overview",
        "link_label": "Portfolio Overview"
    },
    {
        "name": "Portfolio Overview",
        "file": "update_fund_snapshots.yml",
        "description": "Overall fund snapshot",
        "num": "02",
        "link": "https://taurus.streamlit.app/Portfolio_Overview",
        "link_label": "Portfolio Overview"
    },
    {
        "name": "Individual Funds",
        "file": "update_portfolio_daily.yml",
        "description": "Individual Fund Details",
        "num": "03",
        "link": "https://taurus.streamlit.app/Fund_Details",
        "link_label": "Fund Details"
    },
]


PAGES = [
    {
        "name": "Portfolio Overview",
        "file": "update_fund_snapshots.yml",
        "description": "Overall fund snapshot",
        "num": "01",
        "link": "https://taurus.streamlit.app/Portfolio_Overview",
        "link_label": "Portfolio Overview"
    },
    {
        "name": "Tools",
        "file": "update_fund_snapshots.yml",
        "description": "sip & fund calculator",
        "num": "01",
        "link": "https://taurus.streamlit.app/tools",
        "link_label": "Tools"
    },
    {
        "name": "Individual Funds",
        "file": "update_portfolio_daily.yml",
        "description": "Individual Fund Details",
        "num": "02",
        "link": "https://taurus.streamlit.app/Fund_Details",
        "link_label": "Fund Details"
    }
   
]

DELAY_SECONDS = 60


# ─────────────────────────────────────────────
# Trigger Workflow Helper
# ─────────────────────────────────────────────
def trigger_workflow(workflow_filename: str) -> dict:
    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/actions/workflows/{workflow_filename}/dispatches"
    )
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"ref": "main"}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 204:
        return {"success": True, "message": "Triggered successfully ✅"}
    else:
        return {"success": False, "message": f"Error {response.status_code}: {response.text}"}


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
components.html("""
<!DOCTYPE html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=DM+Mono:wght@300;400&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: transparent;
    font-family: 'DM Mono', monospace;
    padding: 1.2rem 0 0 0;
    overflow: hidden;
  }
  .header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    width: 100%;
  }
  .wordmark-block { flex: 1; min-width: 0; }
  h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
    white-space: nowrap;
    font-size: clamp(1.8rem, 10vw, 5rem);
    background: linear-gradient(135deg, #00f5d4 0%, #00c9ff 55%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .sub {
    font-size: clamp(0.5rem, 1.8vw, 0.68rem);
    font-weight: 300;
    letter-spacing: clamp(0.1em, 1vw, 0.28em);
    color: rgba(0, 245, 212, 0.5);
    text-transform: uppercase;
    margin-top: 0.4rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .divider {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,245,212,0.4) 0%, rgba(0,201,255,0.2) 50%, transparent 100%);
    margin: 1rem 0 0 0;
  }
  .pulser-wrap {
    flex-shrink: 0;
    width: clamp(50px, 8vw, 80px);
    height: clamp(50px, 8vw, 80px);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    margin-top: 4px;
  }
  .ring {
    position: absolute;
    width: clamp(22px, 3.5vw, 34px);
    height: clamp(22px, 3.5vw, 34px);
    border-radius: 50%;
    border: 1px solid #00f5d4;
    opacity: 0;
    animation: ripple 1.5s ease-out infinite;
  }
  .ring:nth-child(1) { animation-delay: 0s; }
  .ring:nth-child(2) { animation-delay: 0.25s; }
  .ring:nth-child(3) { animation-delay: 0.5s; }
  .ring:nth-child(4) { animation-delay: 0.75s; }
  @keyframes ripple {
    0%   { transform: scale(1); opacity: 0.65; }
    100% { transform: scale(3.4); opacity: 0; }
  }
  .core {
    position: relative;
    width: clamp(14px, 2.2vw, 22px);
    height: clamp(14px, 2.2vw, 22px);
    border-radius: 50%;
    z-index: 10;
    background: radial-gradient(circle at 35% 35%, #00f5d4cc, #00f5d444);
    animation: throb 0.9s ease-in-out infinite alternate;
  }
  @keyframes throb {
    from { box-shadow: 0 0 5px #00f5d499, 0 0 10px #00f5d444; }
    to   { box-shadow: 0 0 10px #00f5d4dd, 0 0 20px #00f5d466; }
  }
  .live-label {
    position: absolute;
    bottom: -14px;
    left: 50%;
    transform: translateX(-50%);
    font-size: clamp(7px, 1.2vw, 9px);
    letter-spacing: 0.22em;
    color: rgba(0, 245, 212, 0.5);
    text-transform: uppercase;
    white-space: nowrap;
    animation: blink 1.4s step-start infinite;
  }
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.15; }
  }
</style>
</head>
<body>
<div class="header-row">
  <div class="wordmark-block">
    <h1>TAURUS</h1>
    <div class="sub">Portfolio Intelligence System</div>
    <div class="divider"></div>
  </div>
  <div class="pulser-wrap">
    <div class="ring"></div>
    <div class="ring"></div>
    <div class="ring"></div>
    <div class="ring"></div>
    <div class="core"></div>
    <span class="live-label">live</span>
  </div>
</div>
</body></html>
""", height=130, scrolling=False)


# ── Pipeline navigation ──
PAGE_MAP = {
    "Portfolio_Overview": "pages/1_Portfolio_Overview.py",
    "Fund_Details":       "pages/2_Fund_Details.py",
    "Tools":              "pages/Tools.py",
}

st.markdown("""
<style>
.nav-btn-wrap { position: relative; margin-bottom: 0.5rem; }
.nav-btn-wrap .card-visual {
    background: rgba(8,14,20,0.78);
    border: 1px solid rgba(0,245,212,0.2);
    border-radius: 12px;
    padding: 1.4rem 1.5rem 1.35rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    pointer-events: none;
    transition: background 0.25s, border-color 0.25s, transform 0.22s;
}
.nav-btn-wrap:hover .card-visual {
    background: rgba(0,245,212,0.09);
    border-color: rgba(0,245,212,0.65);
    transform: translateY(-3px);
}
.nav-btn-wrap:hover .card-topbar { opacity: 1 !important; }
.nav-btn-wrap:hover .card-num    { color: rgba(0,245,212,0.55) !important; }
.nav-btn-wrap:hover .card-name   { color: #fff !important; }
.nav-btn-wrap:hover .card-desc   { color: rgba(210,240,235,0.88) !important; }

.nav-btn-wrap div[data-testid="stButton"] {
    position: absolute !important;
    inset: 0 !important;
    z-index: 9 !important;
}
.nav-btn-wrap div[data-testid="stButton"] button {
    width: 100% !important;
    height: 100% !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    opacity: 0 !important;
    cursor: pointer !important;
    padding: 0 !important;
}
@keyframes chevron-slide {
    0%   { opacity: 0.15; transform: translateX(-4px); }
    50%  { opacity: 1;    transform: translateX(2px);  }
    100% { opacity: 0.15; transform: translateX(-4px); }
}
@keyframes pdot {
    0%   { box-shadow: 0 0 0 0   rgba(0,245,212,0.6); }
    60%  { box-shadow: 0 0 0 6px rgba(0,245,212,0);   }
    100% { box-shadow: 0 0 0 0   rgba(0,245,212,0);   }
}
</style>
""", unsafe_allow_html=True)

col_c1, col_c2 = st.columns(2)

for col, wf in zip([col_c1, col_c2, col_c3], PAGES):
    page_key = wf["link"].rstrip("/").split("/")[-1]
    with col:
        st.markdown(f"""
        <div class="nav-btn-wrap">
          <div class="card-visual">
            <div class="card-topbar" style="
                position:absolute;top:0;left:0;right:0;height:2px;
                background:linear-gradient(90deg,#00f5d4,#00c9ff);
                opacity:0.4;border-radius:12px 12px 0 0;transition:opacity 0.3s;"></div>
            <div style="
                position:absolute;top:1rem;right:1rem;
                width:7px;height:7px;border-radius:50%;
                background:rgba(0,245,212,0.35);
                animation:pdot 2.2s ease-in-out infinite;"></div>
            <div class="card-num" style="
                font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
                color:rgba(0,245,212,0.22);line-height:1;margin-bottom:0.55rem;
                transition:color 0.3s;">{wf['num']}</div>
            <div class="card-name" style="
                font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                color:#dff5f0;margin-bottom:0.3rem;
                text-shadow:0 1px 10px rgba(0,0,0,1);
                transition:color 0.3s;">{wf['name']}</div>
            <div class="card-desc" style="
                font-family:'DM Mono',monospace;font-size:0.68rem;
                color:rgba(210,240,235,0.62);letter-spacing:0.03em;line-height:1.5;
                text-shadow:0 1px 8px rgba(0,0,0,1);
                transition:color 0.3s;">{wf['description']}</div>
            <div style="
                font-family:'DM Mono',monospace;font-size:0.8rem;
                color:rgba(0,245,212,0.7);letter-spacing:0.05em;
                margin-top:0.85rem;display:flex;align-items:center;gap:2px;">
              <span style="display:inline-block;animation:chevron-slide 1.1s ease-in-out infinite;">›</span>
              <span style="display:inline-block;animation:chevron-slide 1.1s ease-in-out 0.18s infinite;">›</span>
              <span style="display:inline-block;animation:chevron-slide 1.1s ease-in-out 0.36s infinite;">›</span>
            </div>
          </div>
        """, unsafe_allow_html=True)

        if st.button("›› ", key=f"nav_{wf['num']}"):
            st.switch_page(PAGE_MAP[page_key])

        st.markdown("</div></div>", unsafe_allow_html=True)

# ── Add Units section ──
show_add_units()

st.markdown("<br>", unsafe_allow_html=True)

# ── Update Portfolio Button ──
col_btn, col_spacer = st.columns([1, 4])

with col_btn:
    clicked = st.button("▶  Update Portfolio", type="primary", use_container_width=True)

# ── Execution Log ──
if clicked:
    st.divider()

    st.markdown(
        '<p style="font-family:\'DM Mono\',monospace;font-size:0.72rem;letter-spacing:0.2em;'
        'color:rgba(0,245,212,0.6);text-transform:uppercase;margin-bottom:0.8rem;">⬡ execution log</p>',
        unsafe_allow_html=True
    )

    overall_success = True

    for i, wf in enumerate(WORKFLOWS):
        with st.spinner(f"[ {wf['num']} ] Triggering {wf['name']} ..."):
            result = trigger_workflow(wf["file"])

        if result["success"]:
            st.success(f"**{wf['num']} · {wf['name']}** → {result['message']}")
        else:
            st.error(f"**{wf['num']} · {wf['name']}** → {result['message']}")
            overall_success = False
            st.error(f"⛔ Pipeline halted at step {wf['num']}")
            break

        if i < len(WORKFLOWS) - 1:
            countdown_placeholder = st.empty()
            for remaining in range(DELAY_SECONDS, 0, -1):
                countdown_placeholder.info(f"⏱  Next step in **{remaining}s** ...")
                time.sleep(1)
            countdown_placeholder.empty()

    st.divider()
    if overall_success:
        st.success("✅  All 3 pipeline steps completed successfully.")
    else:
        st.warning("⚠️  Pipeline stopped early — check errors above.")

st.divider()

from utils.footer import show_footer
show_footer()
