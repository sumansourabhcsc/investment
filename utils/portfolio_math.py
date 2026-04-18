# utils/portfolio_math.py
import pandas as pd
from datetime import datetime
from utils.xirr import xirr

def compute_xirr_for_df(df, current_nav, valuation_date=None):
    if valuation_date is None:
        valuation_date = datetime.now().date()

    # SIP cashflows (negative)
    cashflows = (-df["Amount"]).tolist()
    dates = pd.to_datetime(df["Date"]).dt.date.tolist()

    # Final value
    total_units = df["Units"].sum()
    final_value = total_units * current_nav

    # Add final cashflow
    cashflows.append(final_value)
    dates.append(valuation_date)

    return xirr(cashflows, dates)
