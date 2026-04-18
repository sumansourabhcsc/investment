import pandas as pd
from datetime import datetime
from utils.data_loader import load_nav
from utils.load_funds import load_all_funds

OUTPUT_FILE = "data/daily_summary.csv"

def generate_daily_summary():

    nav_df = load_nav()
    all_funds = load_all_funds()

    all_funds["Date"] = pd.to_datetime(all_funds["Date"])
    nav_df["Date"] = pd.to_datetime(nav_df["Date"])

    dates = sorted(nav_df["Date"].unique())

    summary = []

    for d in dates:
        day_nav = nav_df[nav_df["Date"] == d]

        total_value = 0
        total_invested = 0

        for _, fund in all_funds.iterrows():
            scheme_code = str(fund["SchemeCode"])

            nav_row = day_nav[day_nav["SchemeCode"] == scheme_code]

            if nav_row.empty:
                continue

            nav = float(nav_row.iloc[0]["NAV"])

            units = fund["Units"]
            amount = fund["Amount"]

            total_value += units * nav
            total_invested += amount

        summary.append([d, total_invested, total_value])

    df = pd.DataFrame(summary, columns=[
        "Date", "Invested", "Total Value"
    ])

    # =========================
    # CALCULATIONS
    # =========================
    df["Current Return"] = df["Total Value"] - df["Invested"]
    df["one_day_change"] = df["Total Value"].diff()
    df["one_day_change_pct"] = df["Total Value"].pct_change() * 100

    df["indicator"] = df["one_day_change"].apply(
        lambda x: "🟢" if x > 0 else ("🔴" if x < 0 else "⚪")
    )

    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    generate_daily_summary()
