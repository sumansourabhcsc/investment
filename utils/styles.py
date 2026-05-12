"""
Taurus – Shared Background Style
─────────────────────────────────
Paste the TAURUS_BG_STYLE markdown call into any page file,
replacing the old image-based .stApp block.

Usage:
    from background_style_snippet import TAURUS_BG_CSS
    st.markdown(TAURUS_BG_CSS, unsafe_allow_html=True)

Or just copy-paste the CSS string into your existing st.markdown() call,
replacing everything from '.stApp {' through '[data-testid="stSidebar"] {...}'.
"""

TAURUS_BG_CSS = """
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
    animation: taurus-pulse 8s ease-in-out infinite;
}

/* ── Layer 2: fine dot-grid pattern ── */
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

@keyframes taurus-pulse {
    0%   { opacity: 1; }
    50%  { opacity: 0.6; }
    100% { opacity: 1; }
}

.stApp > * { position: relative; z-index: 1; }

/* ── Sidebar: dark glass panel ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
    border-right: 1px solid rgba(0,245,212,0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
}

/* ── Streamlit main block: slight glass backdrop ── */
[data-testid="stAppViewContainer"] > section.main > div.block-container {
    background: rgba(2, 16, 32, 0.45);
    border-left: 1px solid rgba(0,245,212,0.07);
    border-right: 1px solid rgba(0,245,212,0.07);
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(0,245,212,0.04) !important;
    border-bottom: 1px solid rgba(0,245,212,0.15) !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: rgba(255,255,255,0.5) !important;
    font-size: 13px !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #00f5d4 !important;
    background: rgba(0,245,212,0.08) !important;
    border-bottom: 2px solid #00f5d4 !important;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input {
    background: rgba(0,245,212,0.04) !important;
    border: 1px solid rgba(0,245,212,0.2) !important;
    color: white !important;
    border-radius: 8px !important;
}

/* ── Primary button ── */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #00c9a7 0%, #00f5d4 100%) !important;
    color: #020d1a !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 20px rgba(0,245,212,0.25) !important;
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 6px 28px rgba(0,245,212,0.40) !important;
    transform: translateY(-1px) !important;
}
</style>
"""
