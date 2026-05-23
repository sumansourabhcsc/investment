# utils/sidebar_style.py
import streamlit as st

def apply_sidebar_style():
    st.markdown("""
    <style>

    /* ── Hide default Streamlit page nav ── */
    [data-testid="stSidebarNav"] ul { display: none; }

    /* ── Sidebar base ── */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 26, 0.92) !important;
        border-right: 1px solid rgba(0, 245, 212, 0.12);
    }

    /* ── Custom nav container ── */
    .taurus-nav {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 1.4rem 0.8rem 1rem;
        gap: 4px;
    }

    /* ── Brand header ── */
    .taurus-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 0.4rem 1.2rem;
        border-bottom: 1px solid rgba(0,245,212,0.12);
        margin-bottom: 0.6rem;
    }
    .taurus-brand .bull { font-size: 26px; }
    .taurus-brand .name {
        font-size: 18px;
        font-weight: 700;
        color: #00f5d4;
        letter-spacing: 0.06em;
        text-shadow: 0 0 12px rgba(0,245,212,0.45);
    }

    /* ── Nav link base ── */
    .taurus-nav a {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        color: rgba(255,255,255,0.65);
        text-decoration: none;
        border: 1px solid transparent;
        transition: all 0.22s ease;
        position: relative;
        overflow: hidden;
    }

    /* glow sweep on hover */
    .taurus-nav a::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, rgba(0,245,212,0.07), transparent);
        opacity: 0;
        transition: opacity 0.22s ease;
    }
    .taurus-nav a:hover::before { opacity: 1; }

    .taurus-nav a:hover {
        color: #00f5d4;
        border-color: rgba(0,245,212,0.25);
        box-shadow: 0 0 14px rgba(0,245,212,0.12), inset 0 0 8px rgba(0,245,212,0.05);
        transform: translateX(3px);
    }

    /* ── Active page highlight ── */
    .taurus-nav a.active {
        color: #00f5d4;
        background: rgba(0,245,212,0.08);
        border-color: rgba(0,245,212,0.3);
        box-shadow: 0 0 18px rgba(0,245,212,0.15), inset 0 0 10px rgba(0,245,212,0.07);
    }
    .taurus-nav a.active::after {
        content: "";
        position: absolute;
        left: 0; top: 20%; bottom: 20%;
        width: 3px;
        background: #00f5d4;
        border-radius: 0 3px 3px 0;
        box-shadow: 0 0 8px #00f5d4;
    }

    /* ── Spacer pushes news to bottom ── */
    .taurus-spacer { flex: 1; min-height: 20px; }

    /* ── Fund News (bottom) special style ── */
    .taurus-nav a.news-link {
        color: rgba(255, 210, 80, 0.75);
        border-color: rgba(255,210,80,0.15);
        background: rgba(255,210,80,0.04);
        margin-top: 4px;
    }
    .taurus-nav a.news-link:hover {
        color: #ffd250;
        border-color: rgba(255,210,80,0.35);
        box-shadow: 0 0 14px rgba(255,210,80,0.15), inset 0 0 8px rgba(255,210,80,0.06);
    }
    .taurus-nav a.news-link.active {
        color: #ffd250;
        background: rgba(255,210,80,0.1);
        border-color: rgba(255,210,80,0.35);
        box-shadow: 0 0 18px rgba(255,210,80,0.18);
    }
    .taurus-nav a.news-link.active::after {
        background: #ffd250;
        box-shadow: 0 0 8px #ffd250;
    }

    /* ── News ticker at bottom ── */
    .ticker-wrap {
        margin-top: 0.8rem;
        padding: 8px 10px;
        border-radius: 8px;
        background: rgba(255,210,80,0.06);
        border: 1px solid rgba(255,210,80,0.15);
        overflow: hidden;
    }
    .ticker-label {
        font-size: 9px;
        letter-spacing: 0.12em;
        color: rgba(255,210,80,0.5);
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .ticker-text {
        font-size: 11px;
        color: rgba(255,210,80,0.75);
        white-space: nowrap;
        overflow: hidden;
        animation: ticker 18s linear infinite;
        display: block;
    }
    @keyframes ticker {
        0%   { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }

    /* ── Icon dots ── */
    .nav-icon { font-size: 15px; width: 18px; text-align: center; }

    </style>
    """, unsafe_allow_html=True)


def render_sidebar(current_page: str):
    """
    Call this at the top of every page.
    current_page: one of 'home', 'portfolio', 'fund_details', 'analysis', 'tools', 'news'
    """
    apply_sidebar_style()

    pages = [
        ("home",         "app",               "🏠", "app",                   ""),
        ("portfolio",    "Portfolio Overview", "📊", "Portfolio_Overview",    ""),
        ("fund_details", "Fund Details",       "📁", "Fund_Details",          ""),
        ("analysis",     "Fund Analysis",      "📈", "Fund_Analysis",         ""),
        ("tools",        "Tools",              "🔧", "Tools",                 ""),
    ]
    news = ("news", "Fund News", "📰", "Fund_News", "news-link")

    def link(key, label, icon, slug, extra_class):
        active = "active" if current_page == key else ""
        cls = f"{extra_class} {active}".strip()
        return f'<a href="/{slug}" class="{cls}"><span class="nav-icon">{icon}</span>{label}</a>'

    nav_html = '<div class="taurus-nav">'
    nav_html += '''
        <div class="taurus-brand">
            <span class="bull">🐂</span>
            <span class="name">TAURUS</span>
        </div>
    '''
    for item in pages:
        nav_html += link(*item)

    nav_html += '<div class="taurus-spacer"></div>'
    nav_html += link(*news)

    nav_html += '''
        <div class="ticker-wrap">
            <div class="ticker-label">📰 market pulse</div>
            <span class="ticker-text">Markets live · NAV updated daily · SIP auto-tracked · 16 funds monitored</span>
        </div>
    '''
    nav_html += '</div>'

    with st.sidebar:
        st.markdown(nav_html, unsafe_allow_html=True)
