import streamlit as st
import pandas as pd
import requests
import base64
from datetime import datetime
import sys
import os

# ─────────────────────────────────────────────
# Import fund list from config.py
# ─────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import mutual_funds

# ─────────────────────────────────────────────
# Credentials (store in Streamlit secrets)
# ─────────────────────────────────────────────
VALID_USER = st.secrets["ADD_UNITS_USER"]
VALID_PASS = st.secrets["ADD_UNITS_PASS"]

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_OWNER = st.secrets["GITHUB_OWNER"]
GITHUB_REPO  = st.secrets["GITHUB_REPO"]
GITHUB_BRANCH = "main"


# ─────────────────────────────────────────────
# GitHub Helpers
# ─────────────────────────────────────────────
def get_file_from_github(file_path: str):
    """Fetch file content and SHA from GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        sha = data["sha"]
        return content, sha
    elif response.status_code == 404:
        return None, None  # File doesn't exist yet
    else:
        st.error(f"GitHub error: {response.status_code} — {response.text}")
        return None, None


def push_file_to_github(file_path: str, content: str, sha: str, commit_msg: str):
    """Push updated file content to GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {
        "message": commit_msg,
        "content": encoded,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha  # Required for updating existing file

    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]


def append_entry_to_csv(folder: str, date: str, units: float, nav: float, amount: float):
    """Read existing CSV from GitHub, append new row, push back."""
    file_path = f"mutualfund/{folder}/fund.csv"

    existing_content, sha = get_file_from_github(file_path)

    new_row = f"{date},{units:.3f},{nav:.2f},{amount:.2f}\n"

    if existing_content is None:
        # File doesn't exist — create with header
        new_content = "Date,Units,NAV,Amount\n" + new_row
    else:
        # File exists — append row (strip trailing newline first)
        new_content = existing_content.rstrip("\n") + "\n" + new_row

    commit_msg = f"Add units: {folder} on {date}"
    success = push_file_to_github(file_path, new_content, sha, commit_msg)
    return success


# ─────────────────────────────────────────────
# Main UI Function (called from app.py)
# ─────────────────────────────────────────────
def show_add_units():

    # ── Session state init ──
    if "au_authenticated" not in st.session_state:
        st.session_state.au_authenticated = False
    if "au_show_form" not in st.session_state:
        st.session_state.au_show_form = False

    # ── Trigger button ──
    if st.button("➕ Add Units", type="secondary"):
        st.session_state.au_show_form = True
        st.session_state.au_authenticated = False

    # ── Show login popup if button clicked ──
    if st.session_state.au_show_form and not st.session_state.au_authenticated:

        with st.expander("🔐 Authentication Required", expanded=True):
            st.markdown("Enter your credentials to proceed.")
            username = st.text_input("User ID", key="au_user")
            password = st.text_input("Password", type="password", key="au_pass")

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Login", key="au_login_btn"):
                    if username == VALID_USER and password == VALID_PASS:
                        st.session_state.au_authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
            with col2:
                if st.button("Cancel", key="au_cancel_btn"):
                    st.session_state.au_show_form = False
                    st.rerun()

    # ── Show fund selection and entry form after login ──
    if st.session_state.au_authenticated:

        st.markdown("---")
        st.subheader("📥 Add Fund Units")

        # Fund dropdown
        fund_names = sorted(mutual_funds.keys())
        selected_fund = st.selectbox(
            "Select Fund",
            options=fund_names,
            key="au_fund_select"
        )

        folder = mutual_funds[selected_fund]["folder"]

        st.markdown(f"📁 File: `mutualfund/{folder}/fund.csv`")
        st.markdown("---")

        # Entry form
        with st.form("add_units_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                date_input = st.date_input(
                    "Date",
                    value=datetime.today(),
                    key="au_date"
                )
                units_input = st.number_input(
                    "No. of Units",
                    min_value=0.001,
                    step=0.001,
                    format="%.3f",
                    key="au_units"
                )

            with col2:
                amount_input = st.number_input(
                    "Amount Invested (₹)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    key="au_amount"
                )
                nav_input = st.number_input(
                    "NAV",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    key="au_nav"
                )

            # Preview row
            date_str = date_input.strftime("%d-%m-%Y")
            st.markdown(
                f"**Preview:** `{date_str}, {units_input:.3f} units, "
                f"NAV ₹{nav_input:.2f}, Amount ₹{amount_input:.2f}`"
            )

            col_submit, col_logout = st.columns([1, 4])
            with col_submit:
                submitted = st.form_submit_button("✅ Submit", type="primary")
            with col_logout:
                logout = st.form_submit_button("🔒 Logout")

        # Handle submit
        if submitted:
            if units_input <= 0 or nav_input <= 0 or amount_input <= 0:
                st.error("❌ All values must be greater than zero.")
            else:
                with st.spinner(f"Saving to GitHub..."):
                    success = append_entry_to_csv(
                        folder=folder,
                        date=date_str,
                        units=units_input,
                        nav=nav_input,
                        amount=amount_input,
                    )
                if success:
                    st.success(
                        f"✅ Added successfully!\n\n"
                        f"**{selected_fund}** — {date_str} | "
                        f"{units_input:.3f} units | NAV ₹{nav_input:.2f} | "
                        f"₹{amount_input:.2f}"
                    )
                else:
                    st.error("❌ Failed to update file. Check GitHub token permissions.")

        # Handle logout
        if logout:
            st.session_state.au_authenticated = False
            st.session_state.au_show_form = False
            st.rerun()
