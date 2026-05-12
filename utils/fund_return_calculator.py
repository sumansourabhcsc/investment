# utils/fund_return_calculator.py
# ─────────────────────────────────────────────
# Fetches NAV history from mfapi.in and calculates
# SIP returns + XIRR for a given fund and date range.
# ─────────────────────────────────────────────

import requests
import pandas as pd
from datetime import date, datetime, timedelta
from scipy.optimize import brentq


# ─────────────────────────────────────────────
# NAV Fetch
# ─────────────────────────────────────────────

def fetch_nav_history(fund_code: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Fetch NAV history from mfapi.in for a given fund code and date range.

    Returns a DataFrame with columns: ['date', 'nav']
    sorted ascending by date.

    Raises ValueError if the response is invalid or no data found.
    """
    url = f"https://api.mfapi.in/mf/{fund_code}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError(f"Request timed out for fund code {fund_code}. Please try again.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error fetching NAV for fund {fund_code}: {e}")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error: {e}")

    data = response.json()

    if "data" not in data or not data["data"]:
        raise ValueError(f"No NAV data found for fund code '{fund_code}'. Please verify the code.")

    records = []
    for entry in data["data"]:
        try:
            nav_date = datetime.strptime(entry["date"], "%d-%m-%Y").date()
            nav_val = float(entry["nav"])
            records.append({"date": nav_date, "nav": nav_val})
        except (ValueError, KeyError):
            continue

    if not records:
        raise ValueError(f"Could not parse NAV data for fund code '{fund_code}'.")

    df = pd.DataFrame(records)
    df = df.sort_values("date").reset_index(drop=True)

    # Filter to requested date range
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    if df.empty:
        raise ValueError(
            f"No NAV data found between {start_date} and {end_date} for fund '{fund_code}'. "
            "Try a wider date range."
        )

    return df


def get_nav_on_or_after(nav_df: pd.DataFrame, target_date: date):
    """
    Return the NAV row on the given date or the next available trading day.
    Returns None if no date is found at or after target_date.
    """
    future = nav_df[nav_df["date"] >= target_date]
    if future.empty:
        return None
    return future.iloc[0]


def get_nav_on_or_before(nav_df: pd.DataFrame, target_date: date):
    """
    Return the NAV row on the given date or the most recent previous trading day.
    Returns None if no date is found at or before target_date.
    """
    past = nav_df[nav_df["date"] <= target_date]
    if past.empty:
        return None
    return past.iloc[-1]


# ─────────────────────────────────────────────
# XIRR
# ─────────────────────────────────────────────

def xirr(cashflows: list[tuple[date, float]], guess: float = 0.1) -> float:
    """
    Calculate XIRR (annualised IRR for irregular cashflows).

    cashflows: list of (date, amount) tuples
        - Investments are NEGATIVE amounts
        - Final redemption / current value is POSITIVE

    Returns annualised rate as a float (e.g. 0.15 = 15%).
    Raises ValueError if XIRR cannot be computed.
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
        result = brentq(npv, -0.9999, 100.0, xtol=1e-8, maxiter=1000)
        return result
    except ValueError:
        raise ValueError(
            "XIRR could not converge. This can happen if the investment is very short "
            "or the returns are extreme. Try a longer investment period."
        )


# ─────────────────────────────────────────────
# SIP Return Calculator
# ─────────────────────────────────────────────

def calculate_sip_returns(
    fund_code: str,
    monthly_amount: float,
    sip_start_date: date,
    sip_end_date: date,
    valuation_date: date | None = None,
) -> dict:
    """
    Simulate monthly SIP investments in a fund and compute returns.

    - SIP is invested on the 1st of each month (or next available NAV date).
    - Current value is calculated using the NAV on valuation_date
      (defaults to today or last available NAV date).

    Returns a dict with:
        fund_meta       : dict with fund name and code
        sip_rows        : list of dicts — each monthly SIP transaction
        total_invested  : float
        total_units     : float
        current_nav     : float
        current_value   : float
        total_gains     : float
        abs_return_pct  : float
        xirr_pct        : float  (annualised, as percentage)
        valuation_date  : date
    """
    if valuation_date is None:
        valuation_date = date.today()

    # Fetch NAV from earliest SIP date to valuation date
    fetch_start = sip_start_date
    fetch_end = valuation_date

    # We need a wider window for NAV lookup
    nav_df = fetch_nav_history(fund_code, fetch_start, fetch_end)

    # Fund meta from API response
    url = f"https://api.mfapi.in/mf/{fund_code}"
    resp = requests.get(url, timeout=15)
    meta = resp.json().get("meta", {})
    fund_name = meta.get("scheme_name", f"Fund {fund_code}")

    # ── Generate monthly SIP dates (1st of each month) ──
    sip_dates = []
    current = sip_start_date.replace(day=1)
    end = sip_end_date.replace(day=1)
    while current <= end:
        sip_dates.append(current)
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # ── Simulate each SIP instalment ──
    sip_rows = []
    cashflows = []  # for XIRR: (date, amount) — negative for investments
    total_units = 0.0
    total_invested = 0.0

    for sip_date in sip_dates:
        nav_row = get_nav_on_or_after(nav_df, sip_date)
        if nav_row is None:
            # No NAV available on or after this date (before valuation date) — skip
            continue

        actual_date = nav_row["date"]
        nav_val = nav_row["nav"]
        units = monthly_amount / nav_val

        total_units += units
        total_invested += monthly_amount

        sip_rows.append({
            "SIP Date": sip_date,
            "NAV Date": actual_date,
            "NAV (₹)": round(nav_val, 4),
            "Amount (₹)": monthly_amount,
            "Units Purchased": round(units, 4),
            "Cumulative Units": round(total_units, 4),
        })

        cashflows.append((actual_date, -monthly_amount))

    if not sip_rows:
        raise ValueError(
            "No SIP transactions could be matched to NAV data. "
            "Check your date range and fund code."
        )

    # ── Current value using valuation date NAV ──
    val_nav_row = get_nav_on_or_before(nav_df, valuation_date)
    if val_nav_row is None:
        raise ValueError(
            f"No NAV available on or before {valuation_date} for valuation. "
            "Try adjusting the end date."
        )

    current_nav = val_nav_row["nav"]
    actual_val_date = val_nav_row["date"]
    current_value = total_units * current_nav
    total_gains = current_value - total_invested
    abs_return_pct = (total_gains / total_invested * 100) if total_invested > 0 else 0.0

    # ── XIRR ──
    cashflows.append((actual_val_date, current_value))
    try:
        xirr_val = xirr(cashflows)
        xirr_pct = xirr_val * 100
    except ValueError as e:
        xirr_pct = None
        xirr_error = str(e)
    else:
        xirr_error = None

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
    }
