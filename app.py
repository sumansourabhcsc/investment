import streamlit as st
import requests
import time
import pandas as pd
from pathlib import Path
from utils.add_units import show_add_units

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
        background: rgba(0, 0, 0, 0.55);
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
    /* Summary card styling */
    .summary-card {
        background: rgba(0, 245, 212, 0.08);
        border: 1px solid rgba(0, 245, 212, 0.3);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 8px;
    }
    .summary-label {
        font-size: 11px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: rgba(0, 245, 212, 0.7);
        margin-bottom: 4px;
    }
    .summary-value {
        font-size: 22px;
        font-weight: 700;
        color: white;
    }
    .summary-gain { color: #00f5a0; }
    .summary-loss { color: #ff6b6b; }
    .freshness-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: rgba(255,255,255,0.5);
        margin-top: 4px;
    }
    .dot-fresh  { width: 8px; height: 8px; border-radius: 50%; background: #00f5a0; display: inline-block; }
    .dot-stale  { width: 8px; height: 8px; border-radius: 50%; background: #ffa94d; display: inline-block; }
    .dot-unknown{ width: 8px; height: 8px; border-radius: 50%; background: #868e96; display: inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# GitHub Config
# ─────────────────────────────────────────────
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_OWNER = st.secrets["GITHUB_OWNER"]
GITHUB_REPO  = st.secrets["GITHUB_REPO"]

WORKFLOWS = [
    {
        "name": "1️⃣ Fetch NAV Daily",
        "file": "fetch_nav_daily.yml",
        "description": "Fetches latest NAV data for all funds",
    },
    {
        "name": "2️⃣ Update Fund Snapshots",
        "file": "update_fund_snapshots.yml",
        "description": "Updates fund snapshot records",
    },
    {
        "name": "3️⃣ Update Portfolio Daily",
        "file": "update_portfolio_daily.yml",
        "description": "Recalculates and updates portfolio values",
    },
]

DELAY_SECONDS = 60

# ─────────────────────────────────────────────
# GitHub Actions — last run timestamp
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)   # re-fetch at most every 5 min
def get_last_workflow_run(workflow_filename: str) -> dict:
    """Returns the most recent completed run for a workflow."""
    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/actions/workflows/{workflow_filename}/runs"
        f"?per_page=1&status=completed"
    )
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            runs = resp.json().get("workflow_runs", [])
            if runs:
                run = runs[0]
                return {
                    "updated_at": run.get("updated_at"),   # ISO 8601
                    "conclusion": run.get("conclusion"),   # success / failure / etc.
                    "run_number": run.get("run_number"),
                }
    except Exception:
        pass
    return {}


def fmt_age(iso_ts: str) -> str:
    """Turn an ISO 8601 timestamp into a human-friendly 'X ago' string."""
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        minutes = int(delta.total_seconds() // 60)
        if minutes < 1:
            return "just now"
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        return f"{hours // 24}d ago"
    except Exception:
        return iso_ts


# ─────────────────────────────────────────────
# Portfolio summary  (reads data/portfolio.csv)
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_portfolio_summary() -> dict | None:
    """
    Reads data/portfolio.csv and returns aggregated totals.
    Expected columns (flexible): invested / current_value  OR
                                  amount_invested / current_value  OR
                                  purchase_value / current_value
    Returns None if the file is missing or unreadable.
    """
    csv_path = Path("data/portfolio.csv")
    if not csv_path.exists():
        return None
    try:
        df = pd.read_csv(csv_path)
        # Normalise column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Find the "invested" column
        invested_col = next(
            (c for c in df.columns if c in ("invested", "amount_invested", "purchase_value", "cost")),
            None,
        )
        current_col = next(
            (c for c in df.columns if c in ("current_value", "value", "market_value")),
            None,
        )
        if invested_col is None or current_col is None:
            return None

        total_invested = pd.to_numeric(df[invested_col], errors="coerce").sum()
        total_current  = pd.to_numeric(df[current_col],  errors="coerce").sum()
        gain_loss      = total_current - total_invested
        pct            = (gain_loss / total_invested * 100) if total_invested else 0.0

        return {
            "total_invested": total_invested,
            "total_current":  total_current,
            "gain_loss":      gain_loss,
            "pct":            pct,
        }
    except Exception:
        return None


# ─────────────────────────────────────────────
# Pulser Component  (uses st.html — no deprecated components.html)
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
    rings_html = "\n".join('<div class="ring"></div>' for _ in range(pulse_count))

    html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    .pulser-root {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: {height}px;
        font-family: 'Space Mono', monospace;
        overflow: hidden;
        background: transparent;
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
        0%   {{ transform: scale(1);              opacity: 0.8; }}
        100% {{ transform: scale({pulse_count + 1}.5); opacity: 0;   }}
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
        to   {{ box-shadow: 0 0 {size // 2}px {color}dd, 0 0 {size}px  {color}66, inset 0 0 {size // 4}px {color}aa; }}
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
    .pulser-label {{
        margin-top: 12px;
        color: {color}cc;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        animation: blink 1.4s step-start infinite;
    }}
    @keyframes blink {{
        0%, 100% {{ opacity: 1;   }}
        50%       {{ opacity: 0.2; }}
    }}
    </style>
    <div class="pulser-root">
        <div class="pulser-wrapper">
            {rings_html}
            <div class="core"></div>
        </div>
        {"<div class='pulser-label'>" + label + "</div>" if label else ""}
    </div>
    """
    # st.html is the stable replacement for st.components.v1.html
    st.html(html)


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

# ── Portfolio Summary Card (top of page) ──────
summary = load_portfolio_summary()

if summary:
    gain_class = "summary-gain" if summary["gain_loss"] >= 0 else "summary-loss"
    sign       = "+" if summary["gain_loss"] >= 0 else ""

    st.markdown(
        f"""
        <div class="summary-card">
            <div style="display:flex; gap:40px; flex-wrap:wrap;">
                <div>
                    <div class="summary-label">Total Invested</div>
                    <div class="summary-value">₹{summary['total_invested']:,.0f}</div>
                </div>
                <div>
                    <div class="summary-label">Current Value</div>
                    <div class="summary-value">₹{summary['total_current']:,.0f}</div>
                </div>
                <div>
                    <div class="summary-label">Overall Gain / Loss</div>
                    <div class="summary-value {gain_class}">
                        {sign}₹{summary['gain_loss']:,.0f}
                        &nbsp;<span style="font-size:14px;">({sign}{summary['pct']:.1f}%)</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Portfolio data not found. Run **▶️ Update Portfolio** to generate it.", icon="📊")

# ── Last-updated freshness indicator ──────────
last_run = get_last_workflow_run(WORKFLOWS[-1]["file"])   # check the final pipeline step

if last_run.get("updated_at"):
    age_str    = fmt_age(last_run["updated_at"])
    conclusion = last_run.get("conclusion", "unknown")
    dot_class  = "dot-fresh" if conclusion == "success" else ("dot-stale" if conclusion else "dot-unknown")
    conclusion_label = conclusion.replace("_", " ").title() if conclusion else "Unknown"
    st.markdown(
        f"""
        <div class="freshness-bar">
            <span class="{dot_class}"></span>
            Data last refreshed <strong style="color:rgba(255,255,255,0.75)">{age_str}</strong>
            &nbsp;·&nbsp; pipeline {conclusion_label}
            &nbsp;·&nbsp; run #{last_run.get('run_number', '?')}
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="freshness-bar"><span class="dot-unknown"></span> Last refresh time unavailable</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Pulser animation + Add Units side-by-side ──
col1, col2 = st.columns([1, 3])

with col1:
    pulser(
        size=40,
        color="#00f5d4",
        pulse_count=6,
        speed=1.5,
        label="",
        height=300,
    )

with col2:
    show_add_units()

# ── Update Portfolio button ────────────────────
st.markdown("<br>", unsafe_allow_html=True)
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
        # Bust the cache so the freshness bar updates immediately
        get_last_workflow_run.clear()
        load_portfolio_summary.clear()
        st.rerun()
    else:
        st.warning("⚠️ Pipeline stopped early. Check errors above.")
