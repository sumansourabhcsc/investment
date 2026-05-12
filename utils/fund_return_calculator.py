# utils/fund_return_calculator.py
# ─────────────────────────────────────────────
# Fetches NAV history from mfapi.in and calculates
# SIP returns + XIRR for a given fund and date range.
# Also provides 3-year rolling returns analysis.
# ─────────────────────────────────────────────

import requests
import pandas as pd
from datetime import date, datetime
from scipy.optimize import brentq


# ─────────────────────────────────────────────
# NAV helpers
# ─────────────────────────────────────────────

def get_nav_on_or_after(nav_df: pd.DataFrame, target_date: date):
    """First available NAV on or after target_date. Returns None if not found."""
    future = nav_df[nav_df["date"] >= target_date]
    return future.iloc[0] if not future.empty else None


def get_nav_on_or_before(nav_df: pd.DataFrame, target_date: date):
    """Most recent NAV on or before target_date. Returns None if not found."""
    past = nav_df[nav_df["date"] <= target_date]
    return past.iloc[-1] if not past.empty else None


# ─────────────────────────────────────────────
# XIRR
# ─────────────────────────────────────────────

def xirr(cashflows: list, guess: float = 0.1) -> float:
    """
    Calculate XIRR (annualised IRR for irregular cashflows).

    cashflows : list of (date, amount) tuples
                Investments are NEGATIVE, final redemption/value is POSITIVE.
    Returns annualised rate as a float (e.g. 0.15 = 15%).
    """
    if not cashflows:
        raise ValueError("No cashflows provided for XIRR calculation.")

    dates = [cf[0] for cf in cashflows]
    amounts = [cf[1] for cf in cashflows]
    base_date = dates[0]

    def npv(rate):
        return sum(
            amt / ((1 + rate) ** ((d - base_date).days / 365.0))
            for d, amt in zip(dates, amounts)
        )

    try:
        return brentq(npv, -0.9999, 100.0, xtol=1e-8, maxiter=1000)
    except ValueError:
        raise ValueError(
            "XIRR could not converge. Try a longer investment period."
        )


# ─────────────────────────────────────────────
# 3-Year Rolling Returns
# ─────────────────────────────────────────────

def calculate_rolling_returns(
    nav_df: pd.DataFrame,
    window_years: int = 3,
    step_months: int = 1,
) -> dict:
    """
    Calculate rolling point-to-point annualised returns for a NAV series.

    For each month (step_months apart), takes a window of `window_years` years
    and computes the CAGR from window-start NAV to window-end NAV.

    Parameters
    ----------
    nav_df       : DataFrame with columns ['date', 'nav'], sorted ascending.
    window_years : Rolling window size in years (default 3).
    step_months  : How many months to advance between windows (default 1 = monthly).

    Returns
    -------
    dict with keys:
        data         — list of dicts: {start_date, end_date, start_nav, end_nav, cagr_pct}
        best         — dict with highest cagr_pct entry
        worst        — dict with lowest cagr_pct entry
        average_pct  — mean CAGR across all windows
        positive_pct — % of windows with positive return
        window_years — echoed back for labelling
        insufficient_data — True if history < window_years (no rows computed)
    """
    window_days = window_years * 365  # approximate; we use nearest-date matching

    if nav_df.empty:
        return {
            "data": [], "best": None, "worst": None,
            "average_pct": None, "positive_pct": None,
            "window_years": window_years, "insufficient_data": True,
        }

    min_date = nav_df["date"].min()
    max_date = nav_df["date"].max()

    total_days = (max_date - min_date).days
    if total_days < window_days:
        return {
            "data": [], "best": None, "worst": None,
            "average_pct": None, "positive_pct": None,
            "window_years": window_years, "insufficient_data": True,
        }

    rows = []

    # Walk through each month in the NAV series as a possible window-end
    # Start from the earliest date where a window_years-back start also exists
    from datetime import timedelta

    # Generate candidate end dates: every step_months months from earliest viable end
    earliest_end = min_date + timedelta(days=window_days)

    # Build a quick lookup: for any date, find nearest NAV
    # We'll iterate through nav_df rows as anchor points (monthly sampling)
    sampled = nav_df.copy()
    # Downsample to approximately monthly: keep last NAV of each month
    sampled["ym"] = sampled["date"].apply(lambda d: (d.year, d.month))
    sampled = sampled.groupby("ym").last().reset_index(drop=True)
    sampled = sampled[sampled["date"] >= earliest_end].reset_index(drop=True)

    for _, end_row in sampled.iterrows():
        end_date = end_row["date"]
        end_nav = float(end_row["nav"])

        # Target start date = exactly window_years before end_date
        from dateutil.relativedelta import relativedelta
        target_start = end_date - relativedelta(years=window_years)

        # Find closest available NAV to target_start
        start_row = get_nav_on_or_before(nav_df, target_start)
        if start_row is None:
            continue
        start_date = start_row["date"]
        start_nav = float(start_row["nav"])

        if start_nav <= 0:
            continue

        actual_years = (end_date - start_date).days / 365.25
        if actual_years < (window_years * 0.8):  # skip if actual window is too short
            continue

        cagr = ((end_nav / start_nav) ** (1.0 / actual_years) - 1) * 100

        rows.append({
            "start_date": start_date,
            "end_date": end_date,
            "start_nav": round(start_nav, 4),
            "end_nav": round(end_nav, 4),
            "cagr_pct": round(cagr, 2),
        })

    if not rows:
        return {
            "data": [], "best": None, "worst": None,
            "average_pct": None, "positive_pct": None,
            "window_years": window_years, "insufficient_data": True,
        }

    cagrs = [r["cagr_pct"] for r in rows]
    best = max(rows, key=lambda r: r["cagr_pct"])
    worst = min(rows, key=lambda r: r["cagr_pct"])
    average_pct = round(sum(cagrs) / len(cagrs), 2)
    positive_pct = round(sum(1 for c in cagrs if c >= 0) / len(cagrs) * 100, 1)

    return {
        "data": rows,
        "best": best,
        "worst": worst,
        "average_pct": average_pct,
        "positive_pct": positive_pct,
        "window_years": window_years,
        "insufficient_data": False,
    }


# ─────────────────────────────────────────────
# Fetch full NAV history (shared helper)
# ─────────────────────────────────────────────

def fetch_nav_history(fund_code: str) -> tuple[dict, pd.DataFrame]:
    """
    Fetch full NAV history for a fund from mfapi.in.

    Returns (meta dict, nav_df sorted ascending).
    Raises ValueError on any network or parse error.
    """
    url = f"https://api.mfapi.in/mf/{fund_code}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError(f"Request timed out for fund code '{fund_code}'. Please try again.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error for fund '{fund_code}': {e}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error: {e}")

    payload = resp.json()
    meta = payload.get("meta", {})

    records = []
    for entry in payload.get("data", []):
        try:
            records.append({
                "date": datetime.strptime(entry["date"], "%d-%m-%Y").date(),
                "nav": float(entry["nav"]),
            })
        except (ValueError, KeyError):
            continue

    if not records:
        raise ValueError(f"No NAV data returned for fund code '{fund_code}'. Verify the code.")

    nav_df = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    return meta, nav_df


# ─────────────────────────────────────────────
# Main SIP calculator
# ─────────────────────────────────────────────

def calculate_sip_returns(
    fund_code: str,
    monthly_amount: float,
    sip_start_date: date,
    sip_end_date: date,
    valuation_date: date = None,
) -> dict:
    """
    Simulate monthly SIP investments in a fund and compute returns.

    SIP is invested on the 1st of each month (or next available NAV date).
    Current value is computed at valuation_date NAV (defaults to today).

    Returns
    -------
    dict with keys:
        fund_code, fund_name
        sip_rows            — list of per-instalment dicts (includes running corpus)
        total_invested, total_units
        current_nav, current_value, total_gains, abs_return_pct
        xirr_pct, xirr_error
        valuation_date
        latest_nav, latest_nav_date   — most recent NAV in the dataset
    """
    if valuation_date is None:
        valuation_date = date.today()

    # ── Fetch NAV history ──
    meta, full_nav_df = fetch_nav_history(fund_code)
    fund_name = meta.get("scheme_name", f"Fund {fund_code}")

    # Latest NAV = most recent entry in the full unfiltered dataset
    latest_nav_row = full_nav_df.iloc[-1]
    latest_nav = float(latest_nav_row["nav"])
    latest_nav_date = latest_nav_row["date"]

    # Filter to the window we care about
    nav_df = full_nav_df[
        (full_nav_df["date"] >= sip_start_date) & (full_nav_df["date"] <= valuation_date)
    ].reset_index(drop=True)

    if nav_df.empty:
        raise ValueError(
            f"No NAV data between {sip_start_date} and {valuation_date} "
            f"for fund '{fund_code}'. Try a wider date range."
        )

    # ── Valuation NAV (needed inside the loop for running corpus) ──
    val_nav_row = get_nav_on_or_before(nav_df, valuation_date)
    if val_nav_row is None:
        raise ValueError(
            f"No NAV available on or before {valuation_date}. Try adjusting the end date."
        )
    current_nav = float(val_nav_row["nav"])
    actual_val_date = val_nav_row["date"]

    # ── Generate 1st-of-month SIP dates ──
    sip_dates = []
    cur = sip_start_date.replace(day=1)
    end = sip_end_date.replace(day=1)
    while cur <= end:
        sip_dates.append(cur)
        cur = cur.replace(month=cur.month + 1) if cur.month < 12 else cur.replace(year=cur.year + 1, month=1)

    # ── Simulate instalments ──
    sip_rows = []
    cashflows = []
    total_units = 0.0
    total_invested = 0.0

    for sip_date in sip_dates:
        nav_row = get_nav_on_or_after(nav_df, sip_date)
        if nav_row is None:
            continue

        actual_date = nav_row["date"]
        nav_val = float(nav_row["nav"])
        units = monthly_amount / nav_val

        total_units += units
        total_invested += monthly_amount

        # Running corpus = all units accumulated so far × current valuation NAV
        running_corpus = total_units * current_nav
        running_gain = running_corpus - total_invested

        sip_rows.append({
            "SIP Date": sip_date,
            "NAV Date": actual_date,
            "NAV at Investment (₹)": round(nav_val, 4),
            "Amount Invested (₹)": monthly_amount,
            "Units Purchased": round(units, 4),
            "Cumulative Units": round(total_units, 4),
            "Total Invested (₹)": round(total_invested, 2),
            "Current Value (₹)": round(running_corpus, 2),
            "Gain / Loss (₹)": round(running_gain, 2),
        })

        cashflows.append((actual_date, -monthly_amount))

    if not sip_rows:
        raise ValueError(
            "No SIP transactions could be matched to NAV data. "
            "Check your date range and fund code."
        )

    # ── Final summary numbers ──
    current_value = total_units * current_nav
    total_gains = current_value - total_invested
    abs_return_pct = (total_gains / total_invested * 100) if total_invested > 0 else 0.0

    # ── XIRR ──
    cashflows.append((actual_val_date, current_value))
    try:
        xirr_val = xirr(cashflows)
        xirr_pct = xirr_val * 100
        xirr_error = None
    except ValueError as e:
        xirr_pct = None
        xirr_error = str(e)

    return {
        "fund_code": fund_code,
        "fund_name": fund_name,
        "sip_rows": sip_rows,
        "total_invested": total_invested,
        "total_units": round(total_units, 4),
        "current_nav": current_nav,
        "current_value": current_value,
        "total_gains": total_gains,
        "abs_return_pct": abs_return_pct,
        "xirr_pct": xirr_pct,
        "xirr_error": xirr_error,
        "valuation_date": actual_val_date,
        "latest_nav": latest_nav,
        "latest_nav_date": latest_nav_date,
        # Pass through full NAV history so the rolling returns tab can use it
        # without a second API call
        "_full_nav_df": full_nav_df,
    }
