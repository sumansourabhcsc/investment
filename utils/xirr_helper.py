# utils/xirr_helper.py
from datetime import datetime
from utils.xirr import xirr

def compute_fund_xirr(df, latest_nav, valuation_date=None):
    if valuation_date is None:
        valuation_date = datetime.now().date()

    # SIP cashflows (negative)
    cashflows = (-df["Amount"]).tolist()
    dates = df["Date"].dt.date.tolist()

    # Final value
    total_units = df["Units"].sum()
    final_value = total_units * latest_nav

    cashflows.append(final_value)
    dates.append(valuation_date)

    return xirr(cashflows, dates)
