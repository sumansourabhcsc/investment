import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import load_nav
from utils.load_funds import load_all_funds

OUTPUT_FILE = "data/daily_summary.csv"


def generate_daily_summary():

    nav_df = load_nav()
    funds_df = load_all_funds()

    # Clean column names (important for CI)
    nav_df.columns = nav_df.columns.str.strip()
    funds_df.columns = funds_df.columns.str.strip()

    nav_df["Date"] = pd.to_datetime(nav_df["Date"])
    funds_df["Date"] = pd.to_datetime(funds_df["Date"])

    dates = sorted(nav_df["Date"].unique())

    summary = []

    for d in dates:
        day_nav = nav_df[nav_df["Date"] == d]

        total_invested = 0.0
        total_current = 0.0

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

        # ✅ FORMAT DATE AS dd-mm-yyyy
        formatted_date = d.strftime("%d-%m-%Y")

        summary.append([
            formatted_date,
            round(total_invested, 2),
            round(total_current, 2),
            round(total_gain, 2)
        ])

    df = pd.DataFrame(
        summary,
        columns=["date", "total_invested", "total_current", "total_gain"]
    )

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Daily summary written to {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_daily_summary()
