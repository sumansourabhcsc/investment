import streamlit as st
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus – Tools",
    page_icon="🐂",
    layout="wide"
)

# ─────────────────────────────────────────────
# Background + Styling (matches app.py)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Full page background */
    .stApp {
        #background-image: url("https://raw.githubusercontent.com/sumansourabhcsc/investment/main/taurus.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Dark overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.65);
        z-index: 0;
    }

    /* Content above overlay */
    .stApp > * {
        position: relative;
        z-index: 1;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.6) !important;
    }

    /* Text color */
    html, body, [class*="css"] {
        color: white;
    }

    /* Result card */
    .result-card {
        background: rgba(0, 245, 212, 0.08);
        border: 1px solid rgba(0, 245, 212, 0.35);
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 8px;
    }

    .result-card h3 {
        color: #00f5d4;
        margin-bottom: 4px;
        font-size: 14px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .result-card p {
        font-size: 28px;
        font-weight: 700;
        color: white;
        margin: 0;
    }

    .result-card .sub {
        font-size: 12px;
        color: rgba(255,255,255,0.5);
        margin-top: 4px;
    }

    /* Growth tag */
    .gain-positive { color: #00f5d4; font-weight: 600; }
    .gain-negative { color: #ff6b6b; font-weight: 600; }

    /* Year table styling */
    .year-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .year-table th {
        color: #00f5d4;
        text-align: left;
        padding: 8px 12px;
        border-bottom: 1px solid rgba(0,245,212,0.2);
        font-size: 11px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .year-table td {
        padding: 8px 12px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.85);
    }
    .year-table tr:hover td { background: rgba(0,245,212,0.05); }

    /* Section divider */
    .section-label {
        font-size: 11px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #00f5d4;
        margin-bottom: 12px;
        margin-top: 4px;
    }

    /* Tab override */
    button[data-baseweb="tab"] {
        color: white !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00f5d4 !important;
        border-bottom: 2px solid #00f5d4 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def fmt_inr(amount: float) -> str:
    """Format number as Indian Rupee with ₹ symbol and commas."""
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"


def calc_sip(monthly_sip: float, annual_rate: float, years: int,
             stepup_pct: float = 0.0, lumpsum: float = 0.0) -> dict:
    """
    SIP calculator with optional step-up and lumpsum.

    Returns a dict with summary figures and a year-by-year breakdown list.
    """
    monthly_rate = annual_rate / 100 / 12
    total_months = years * 12
    breakdown = []

    invested = lumpsum
    corpus = lumpsum
    current_sip = monthly_sip

    for yr in range(1, years + 1):
        yr_invested_start = invested
        for _ in range(12):
            corpus = corpus * (1 + monthly_rate) + current_sip
            invested += current_sip

        gains = corpus - invested
        breakdown.append({
            "Year": yr,
            "Monthly SIP": current_sip,
            "Total Invested": invested,
            "Corpus Value": corpus,
            "Gains": gains,
        })

        # Apply step-up at end of each year
        if stepup_pct > 0:
            current_sip = current_sip * (1 + stepup_pct / 100)

    total_invested = invested
    final_corpus = corpus
    total_gains = final_corpus - total_invested
    abs_return = (total_gains / total_invested * 100) if total_invested > 0 else 0

    return {
        "total_invested": total_invested,
        "final_corpus": final_corpus,
        "total_gains": total_gains,
        "abs_return": abs_return,
        "breakdown": breakdown,
    }


def calc_lumpsum(principal: float, annual_rate: float, years: int) -> dict:
    """Simple lumpsum compound interest calculator with year-by-year breakdown."""
    breakdown = []
    for yr in range(1, years + 1):
        corpus = principal * ((1 + annual_rate / 100) ** yr)
        gains = corpus - principal
        breakdown.append({
            "Year": yr,
            "Corpus Value": corpus,
            "Gains": gains,
        })
    final_corpus = breakdown[-1]["Corpus Value"]
    total_gains = final_corpus - principal
    abs_return = (total_gains / principal * 100) if principal > 0 else 0
    return {
        "principal": principal,
        "final_corpus": final_corpus,
        "total_gains": total_gains,
        "abs_return": abs_return,
        "breakdown": breakdown,
    }


def render_result_cards(cols_data: list):
    """Render a row of result metric cards."""
    cols = st.columns(len(cols_data))
    for col, (label, value, sub) in zip(cols, cols_data):
        with col:
            st.markdown(
                f"""
                <div class="result-card">
                    <h3>{label}</h3>
                    <p>{value}</p>
                    <div class="sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_breakdown_table(breakdown: list, currency_keys: list):
    """Render year-by-year breakdown as a styled HTML table."""
    if not breakdown:
        return

    headers = list(breakdown[0].keys())
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for row in breakdown:
        row_html = ""
        for k, v in row.items():
            if k in currency_keys:
                cell = fmt_inr(v)
            elif k == "Year":
                cell = str(int(v))
            elif isinstance(v, float):
                cell = fmt_inr(v)
            else:
                cell = str(v)
            row_html += f"<td>{cell}</td>"
        rows_html += f"<tr>{row_html}</tr>"

    table_html = f"""
    <div style="overflow-x:auto; max-height:380px; overflow-y:auto; margin-top:16px;
                border: 1px solid rgba(0,245,212,0.15); border-radius:8px;">
      <table class="year-table">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Page Header
# ─────────────────────────────────────────────
st.markdown("## 🛠️ Tools")
st.markdown(
    "<div style='color:rgba(255,255,255,0.5); font-size:13px; margin-bottom:24px;'>"
    "Financial calculators to plan your investments</div>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab_sip, tab_lumpsum, tab_more = st.tabs(
    ["📈  SIP Calculator", "💰  Lumpsum Calculator", "🔧  More (Coming Soon)"]
)


# ══════════════════════════════════════════════
# TAB 1 – SIP CALCULATOR
# ══════════════════════════════════════════════
with tab_sip:
    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="section-label">Basic Details</div>', unsafe_allow_html=True)

        monthly_sip = st.number_input(
            "Monthly SIP Amount (₹)",
            min_value=100,
            max_value=10_000_000,
            value=5000,
            step=500,
            key="sip_amount",
            help="Amount you invest every month"
        )

        annual_rate = st.slider(
            "Expected Annual Return (%)",
            min_value=1.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            key="sip_rate",
        )

        years = st.slider(
            "Investment Duration (Years)",
            min_value=1,
            max_value=40,
            value=10,
            step=1,
            key="sip_years",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Optional: Lumpsum Top-up</div>', unsafe_allow_html=True)

        lumpsum = st.number_input(
            "Initial Lumpsum (₹)",
            min_value=0,
            max_value=100_000_000,
            value=0,
            step=1000,
            key="sip_lumpsum",
            help="One-time amount invested at the start alongside SIP"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Optional: Step-Up SIP</div>', unsafe_allow_html=True)

        enable_stepup = st.toggle("Enable Annual Step-Up", value=False, key="sip_stepup_toggle")

        stepup_pct = 0.0
        if enable_stepup:
            stepup_pct = st.slider(
                "Annual Step-Up (%)",
                min_value=1.0,
                max_value=50.0,
                value=10.0,
                step=1.0,
                key="sip_stepup_pct",
                help="Percentage increase in SIP amount every year"
            )
            st.caption(
                f"Your SIP grows: ₹{monthly_sip:,} → "
                f"₹{monthly_sip * ((1 + stepup_pct/100) ** years):,.0f} by Year {years}"
            )

        st.markdown("<br>", unsafe_allow_html=True)
        calculate_sip = st.button("📊 Calculate", type="primary", key="calc_sip", use_container_width=True)

    # ── Results ──
    with right:
        if calculate_sip:
            result = calc_sip(
                monthly_sip=monthly_sip,
                annual_rate=annual_rate,
                years=years,
                stepup_pct=stepup_pct,
                lumpsum=lumpsum,
            )

            gain_class = "gain-positive" if result["total_gains"] >= 0 else "gain-negative"
            abs_ret_str = f'<span class="{gain_class}">{result["abs_return"]:+.1f}% absolute return</span>'

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

            render_result_cards([
                ("Total Invested", fmt_inr(result["total_invested"]), "Principal contributed"),
                ("Final Corpus", fmt_inr(result["final_corpus"]), abs_ret_str),
                ("Total Gains", fmt_inr(result["total_gains"]), f"At {annual_rate}% p.a."),
            ])

            # Simple bar chart
            st.markdown("<br>", unsafe_allow_html=True)
            chart_df = pd.DataFrame({
                "Year": [r["Year"] for r in result["breakdown"]],
                "Invested": [r["Total Invested"] for r in result["breakdown"]],
                "Corpus": [r["Corpus Value"] for r in result["breakdown"]],
            }).set_index("Year")
            st.line_chart(chart_df, color=["#4a9eff", "#00f5d4"])

            # Year-by-year table
            st.markdown('<div class="section-label" style="margin-top:16px;">Year-by-Year Breakdown</div>', unsafe_allow_html=True)
            render_breakdown_table(
                result["breakdown"],
                currency_keys=["Monthly SIP", "Total Invested", "Corpus Value", "Gains"]
            )

        else:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="text-align:center; opacity:0.4; padding: 60px 20px;">
                    <div style="font-size:48px;">📈</div>
                    <div style="margin-top:12px; font-size:14px;">Fill in the details and hit Calculate</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════
# TAB 2 – LUMPSUM CALCULATOR
# ══════════════════════════════════════════════
with tab_lumpsum:
    st.markdown("<br>", unsafe_allow_html=True)

    left2, right2 = st.columns([1, 1], gap="large")

    with left2:
        st.markdown('<div class="section-label">Investment Details</div>', unsafe_allow_html=True)

        principal = st.number_input(
            "Investment Amount (₹)",
            min_value=1000,
            max_value=100_000_000,
            value=1_00_000,
            step=1000,
            key="ls_principal",
            help="One-time lumpsum amount to invest"
        )

        ls_rate = st.slider(
            "Expected Annual Return (%)",
            min_value=1.0,
            max_value=30.0,
            value=12.0,
            step=0.5,
            key="ls_rate",
        )

        ls_years = st.slider(
            "Investment Duration (Years)",
            min_value=1,
            max_value=40,
            value=10,
            step=1,
            key="ls_years",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        calculate_ls = st.button("📊 Calculate", type="primary", key="calc_ls", use_container_width=True)

    with right2:
        if calculate_ls:
            result_ls = calc_lumpsum(
                principal=principal,
                annual_rate=ls_rate,
                years=ls_years,
            )

            gain_class_ls = "gain-positive" if result_ls["total_gains"] >= 0 else "gain-negative"
            abs_ret_str_ls = f'<span class="{gain_class_ls}">{result_ls["abs_return"]:+.1f}% absolute return</span>'

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

            render_result_cards([
                ("Principal", fmt_inr(result_ls["principal"]), "One-time investment"),
                ("Final Corpus", fmt_inr(result_ls["final_corpus"]), abs_ret_str_ls),
                ("Total Gains", fmt_inr(result_ls["total_gains"]), f"At {ls_rate}% p.a."),
            ])

            # Chart
            st.markdown("<br>", unsafe_allow_html=True)
            chart_df_ls = pd.DataFrame({
                "Year": [r["Year"] for r in result_ls["breakdown"]],
                "Principal": [result_ls["principal"]] * ls_years,
                "Corpus": [r["Corpus Value"] for r in result_ls["breakdown"]],
            }).set_index("Year")
            st.line_chart(chart_df_ls, color=["#4a9eff", "#00f5d4"])

            # Breakdown table
            st.markdown('<div class="section-label" style="margin-top:16px;">Year-by-Year Breakdown</div>', unsafe_allow_html=True)
            render_breakdown_table(
                result_ls["breakdown"],
                currency_keys=["Corpus Value", "Gains"]
            )

        else:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="text-align:center; opacity:0.4; padding: 60px 20px;">
                    <div style="font-size:48px;">💰</div>
                    <div style="margin-top:12px; font-size:14px;">Fill in the details and hit Calculate</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════
# TAB 3 – COMING SOON
# ══════════════════════════════════════════════
with tab_more:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align:center; padding: 80px 20px; opacity:0.5;">
            <div style="font-size:56px;">🔧</div>
            <div style="font-size:18px; margin-top:16px; font-weight:600;">More Calculators Coming Soon</div>
            <div style="font-size:13px; margin-top:8px; color:rgba(255,255,255,0.5);">
                Fund Return Calculator · XIRR · Goal Planner · Tax Estimator
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
