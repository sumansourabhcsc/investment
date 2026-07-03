# utils/sidebar_style.py
import streamlit as st

def apply_sidebar_style():
    st.markdown("""
    <style>

    /* Hide ALL native Streamlit sidebar nav elements */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"],
    [data-testid="stSidebarNavLink"],
    section[data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(10, 14, 26, 0.92) !important;
        border-right: 1px solid rgba(0, 245, 212, 0.12);
    }

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

    /* Style the st.page_link buttons */
    [data-testid="stSidebar"] [data-testid="stPageLink"] a {
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.65) !important;
        text-decoration: none !important;
        border: 1px solid transparent !important;
        transition: all 0.22s ease !important;
        position: relative !important;
        overflow: hidden !important;
        background: transparent !important;
    }

    [data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
        color: #00f5d4 !important;
        border-color: rgba(0,245,212,0.25) !important;
        box-shadow: 0 0 14px rgba(0,245,212,0.12),
                    inset 0 0 8px rgba(0,245,212,0.05) !important;
        transform: translateX(3px) !important;
        background: rgba(0,245,212,0.05) !important;
    }

    /* Active page */
    [data-testid="stSidebar"] [data-testid="stPageLink-active"] a {
        color: #00f5d4 !important;
        background: rgba(0,245,212,0.08) !important;
        border-color: rgba(0,245,212,0.3) !important;
        box-shadow: 0 0 18px rgba(0,245,212,0.15),
                    inset 0 0 10px rgba(0,245,212,0.07) !important;
        border-left: 3px solid #00f5d4 !important;
    }

    /* News link gold colour */
    [data-testid="stSidebar"] .news-page [data-testid="stPageLink"] a,
    [data-testid="stSidebar"] .news-page [data-testid="stPageLink-active"] a {
        color: rgba(255, 210, 80, 0.75) !important;
        border-color: rgba(255,210,80,0.15) !important;
        background: rgba(255,210,80,0.04) !important;
    }
    [data-testid="stSidebar"] .news-page [data-testid="stPageLink"] a:hover {
        color: #ffd250 !important;
        border-color: rgba(255,210,80,0.35) !important;
        box-shadow: 0 0 14px rgba(255,210,80,0.15) !important;
    }

    /* Ticker */
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

    </style>
    """, unsafe_allow_html=True)


def render_sidebar(current_page: str):
    apply_sidebar_style()

    with st.sidebar:
        # Brand header
        st.markdown("""
            <div style="display:flex; flex-direction:column; align-items:center; gap:10px; margin-top:0.5rem;">
                <img 
                    src="https://raw.githubusercontent.com/sumansourabhcsc/investment/main/tauruss.png"
                    style="width:80%; max-width:180px; opacity:0.85; filter: drop-shadow(0 0 10px rgba(0,245,212,0.4));"
                />
            </div>
            
        """, unsafe_allow_html=True)
        st.markdown("<div style='flex:1; min-height:40px'></div>", unsafe_allow_html=True)
        # Main nav — use st.page_link so Streamlit handles routing (no new tab)
        st.page_link("app.py",                          label="Home",             icon="🏠")
        st.page_link("pages/1_Portfolio_Overview.py",   label="Dashboard", icon="📊")
        st.page_link("pages/7_Dashboard_Update.py",     label="Dashboard update", icon="🌿")
        st.page_link("pages/2_Fund_Details.py",         label="Funds",     icon="📁")
        st.page_link("pages/3_Fund_Analysis.py",        label="Analysis",    icon="📈")
        st.page_link("pages/4_Tools.py",                label="Tools",            icon="🔧")

        # Spacer to push news to bottom
        #st.markdown("<div style='flex:1; min-height:40px'></div>", unsafe_allow_html=True)
         # ── Smart SIP — new entry ──
        #st.markdown('<div class="sip-page">', unsafe_allow_html=True)
        st.page_link("pages/6_smart_sip.py",            label="Smart SIP",  icon="⚡")
        #st.markdown('</div>', unsafe_allow_html=True)
        # Fund News pinned at bottom with gold wrapper
        #st.markdown('<div class="news-page">', unsafe_allow_html=True)
        st.page_link("pages/5_Fund_News.py", label="News", icon="📰")
        #st.markdown('</div>', unsafe_allow_html=True)


            
       
