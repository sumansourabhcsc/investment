# utils/xirr_overall.py
from datetime import datetime
from utils.xirr import xirr
from utils.data_loader import load_nav
from config import mutual_funds

def compute_overall_xirr(all_funds_df):
    nav_df = load_nav()
    valuation_date = datetime.now().date()

    cashflows = []
    dates = []

    # Add all SIP transactions (negative cashflows)
    for _, row in all_funds_df.iterrows():
        cashflows.append(-row["Amount"])
        dates.append(row["Date"].date())

    # Add final value for each fund
    for fund_name, info in mutual_funds.items():
        folder = info["folder"]
        code = str(info["code"])

        # Filter SIPs for this fund
        fdf = all_funds_df[all_funds_df["FundName"] == folder]
        if fdf.empty:
            continue

        # Get latest NAV for this fund
        match = nav_df[nav_df["SchemeCode"] == code]
        if match.empty:
            continue

        latest_nav = float(match.sort_values("Date", ascending=False).iloc[0]["NAV"])

        total_units = fdf["Units"].sum()
        final_value = total_units * latest_nav

        cashflows.append(final_value)
        dates.append(valuation_date)

    return xirr(cashflows, dates)
