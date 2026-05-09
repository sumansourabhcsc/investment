import streamlit as st
import streamlit.components.v1 as components
import requests
import time

# ─────────────────────────────────────────────
# Page Config — MUST be first, only once
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus",
    page_icon="🐂",
    layout="wide"
)

# ─────────────────────────────────────────────
# Background Image (Full Page)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Full page background */
    .stApp {
        background-image: url("https://raw.githubusercontent.com/sumansourabhcsc/investment/main/taurus.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Dark overlay so text stays readable */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.55);  /* ← adjust 0.55 to make darker/lighter */
        z-index: 0;
    }

    /* Make all content sit above the overlay */
    .stApp > * {
        position: relative;
        z-index: 1;
    }

    /* Make sidebar semi-transparent */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.6) !important;
    }

    /* Make text white for visibility */
    html, body, [class*="css"] {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)







# ─────────────────────────────────────────────
# GitHub Config
# ─────────────────────────────────────────────
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_OWNER = st.secrets["GITHUB_OWNER"]
GITHUB_REPO  = st.secrets["GITHUB_REPO"]

WORKFLOWS = [
    {
        "name": "1️⃣  Fetch NAV Daily",
        "file": "fetch_nav_daily.yml",
        "description": "Fetches latest NAV data for all funds"
    },
    {
        "name": "2️⃣  Update Fund Snapshots",
        "file": "update_fund_snapshots.yml",
        "description": "Updates fund snapshot records"
    },
    {
        "name": "3️⃣  Update Portfolio Daily",
        "file": "update_portfolio_daily.yml",
        "description": "Recalculates and updates portfolio values"
    },
]

DELAY_SECONDS = 60

# ─────────────────────────────────────────────
# Pulser Component
# ─────────────────────────────────────────────
def pulser(
    size: int = 80,
    color: str = "#00f5d4",
    pulse_count: int = 3,
    speed: float = 1.8,
    label: str = "",
    height: int = 200,
):
    delays = " ".join(
        f".ring:nth-child({i + 1}) {{ animation-delay: {i * (speed / pulse_count):.2f}s; }}"
        for i in range(pulse_count)
    )
    rings_html = "\n".join(f'<div class="ring"></div>' for _ in range(pulse_count))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
      *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        background: transparent;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: {height}px;
        font-family: 'Space Mono', monospace;
        overflow: hidden;
      }}
      .pulser-wrapper {{
        position: relative;
        width: {size * 4}px;
        height: {size * 4}px;
        display: flex;
        align-items: center;
        justify-content: center;
      }}
      .ring {{
        position: absolute;
        width: {size}px;
        height: {size}px;
        border-radius: 50%;
        border: 2px solid {color};
        opacity: 0;
        animation: ripple {speed}s ease-out infinite;
      }}
      {delays}
      @keyframes ripple {{
        0%   {{ transform: scale(1);   opacity: 0.8; }}
        100% {{ transform: scale({pulse_count + 1}.5); opacity: 0; }}
      }}
      .core {{
        position: relative;
        width: {size}px;
        height: {size}px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, {color}cc, {color}44);
        box-shadow:
          0 0 {size // 4}px {color}99,
          0 0 {size // 2}px {color}44,
          inset 0 0 {size // 6}px {color}66;
        animation: throb {speed * 0.6:.2f}s ease-in-out infinite alternate;
        z-index: 10;
      }}
      @keyframes throb {{
        from {{ box-shadow: 0 0 {size // 4}px {color}99, 0 0 {size // 2}px {color}44, inset 0 0 {size // 6}px {color}66; }}
        to   {{ box-shadow: 0 0 {size // 2}px {color}dd, 0 0 {size}px     {color}66, inset 0 0 {size // 4}px {color}aa; }}
      }}
      .core::before, .core::after {{
        content: '';
        position: absolute;
        background: {color}55;
        border-radius: 1px;
      }}
      .core::before {{
        width: 1px; height: 60%;
        top: 20%; left: 50%;
        transform: translateX(-50%);
      }}
      .core::after {{
        height: 1px; width: 60%;
        left: 20%; top: 50%;
        transform: translateY(-50%);
      }}
      .label {{
        margin-top: 12px;
        color: {color}cc;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        animation: blink 1.4s step-start infinite;
      }}
      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50%       {{ opacity: 0.2; }}
      }}
    </style>
    </head>
    <body>
      <div class="pulser-wrapper">
        {rings_html}
        <div class="core"></div>
      </div>
      {"<div class='label'>" + label + "</div>" if label else ""}
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)


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
# UI Layout
# ─────────────────────────────────────────────

# ── Taurus Image — centered in middle of page ──
# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     st.image(
#         "taurus.png",          # ← rename to whatever your image file is called
#         use_container_width=True
#     )

# st.markdown("---")

# ── Pulser animation ──
# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     pulser(
#         size=40,
#         color="#00f5d4",
#         pulse_count=6,
#         speed=1.5,
#         label="",
#         height=300,
#     )

# st.divider()

# # ── Workflow Trigger Button ──
# if st.button("▶️ Update Portfolio", type="primary", use_container_width=True):

#     st.markdown("### ⏳ Execution Log")
#     overall_success = True

#     for i, wf in enumerate(WORKFLOWS):
#         with st.spinner(f"Triggering {wf['name']} ..."):
#             result = trigger_workflow(wf["file"])

#         if result["success"]:
#             st.success(f"**{wf['name']}** → {result['message']}")
#         else:
#             st.error(f"**{wf['name']}** → {result['message']}")
#             overall_success = False
#             st.error(f"⛔ Pipeline stopped at: {wf['name']}")
#             break

#         if i < len(WORKFLOWS) - 1:
#             countdown_placeholder = st.empty()
#             for remaining in range(DELAY_SECONDS, 0, -1):
#                 countdown_placeholder.info(
#                     f"⏱️ Next workflow starts in **{remaining}** second{'s' if remaining > 1 else ''}..."
#                 )
#                 time.sleep(1)
#             countdown_placeholder.empty()

#     st.markdown("---")
#     if overall_success:
#         st.success("✅ All 3 workflows triggered successfully!")
#     else:
#         st.warning("⚠️ Pipeline stopped early. Check errors above.")



# ─────────────────────────────────────────────
# UI Layout
# ─────────────────────────────────────────────

# ── Pulser animation — centered ──
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    pulser(
        size=40,
        color="#00f5d4",
        pulse_count=6,
        speed=1.5,
        label="",
        height=300,
    )

# ── Push button to bottom-left using empty space ──
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

# ── Bottom row: button on left, empty space on right ──
col_btn, col_empty = st.columns([1, 4])

with col_btn:
    clicked = st.button("▶️ Update Portfolio", type="primary")

# ── Execution Log — shown below after click ──
if clicked:
    st.divider()
    st.markdown("### ⏳ Execution Log")
    overall_success = True

    for i, wf in enumerate(WORKFLOWS):
        with st.spinner(f"Triggering {wf['name']} ..."):
            result = trigger_workflow(wf["file"])

        if result["success"]:
            st.success(f"**{wf['name']}** → {result['message']}")
        else:
            st.error(f"**{wf['name']}** → {result['message']}")
            overall_success = False
            st.error(f"⛔ Pipeline stopped at: {wf['name']}")
            break

        if i < len(WORKFLOWS) - 1:
            countdown_placeholder = st.empty()
            for remaining in range(DELAY_SECONDS, 0, -1):
                countdown_placeholder.info(
                    f"⏱️ Next workflow starts in **{remaining}** second{'s' if remaining > 1 else ''}..."
                )
                time.sleep(1)
            countdown_placeholder.empty()

    st.markdown("---")
    if overall_success:
        st.success("✅ All 3 workflows triggered successfully!")
    else:
        st.warning("⚠️ Pipeline stopped early. Check errors above.")
