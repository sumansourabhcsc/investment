import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import load_nav
from utils.load_funds import load_all_funds

OUTPUT_FILE = "data/daily_summary.csv"


def generate_daily_summary():

    nav_df = load_nav()
    funds_df = load_all_funds()

    # Clean column names
    nav_df.columns = nav_df.columns.str.strip()
    funds_df.columns = funds_df.columns.str.strip()

    # Convert dates
    nav_df["Date"] = pd.to_datetime(nav_df["Date"])
    funds_df["Date"] = pd.to_datetime(funds_df["Date"])

    # ✅ STEP 1: Get latest NAV date ONLY
    latest_date = nav_df["Date"].max()
    day_nav = nav_df[nav_df["Date"] == latest_date]

    total_invested = 0.0
    total_current = 0.0

    # Loop through funds
    for _, fund in funds_df.iterrows():

        scheme_code = str(fund.get("SchemeCode", "")).strip()
        if not scheme_code:
            continue

        nav_row = day_nav[day_nav["SchemeCode"] == scheme_code]

        if nav_row.empty:
            continue

        nav = float(nav_row.iloc[0]["NAV"])
        units = float(fund.get("Units", 0))
        amount = float(fund.get("Amount", 0))

        total_invested += amount
        total_current += units * nav

    total_gain = total_current - total_invested

    # Format date as dd-mm-yyyy
    formatted_date = latest_date.strftime("%d-%m-%Y")

    df = pd.DataFrame([[
        formatted_date,
        round(total_invested, 2),
        round(total_current, 2),
        round(total_gain, 2)
    ]], columns=["date", "total_invested", "total_current", "total_gain"])

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Daily summary generated for latest NAV date: {formatted_date}")


if __name__ == "__main__":
    generate_daily_summary()
