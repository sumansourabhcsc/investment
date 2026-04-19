import pandas as pd
import os
import sys

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from utils.data_loader import load_nav, load_fund
from utils.calculations import calculate_invested_amount, calculate_current_value
from config import mutual_funds


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)


def compute_portfolio_snapshot():
    nav_df = load_nav()
    nav_df["Date"] = pd.to_datetime(nav_df["Date"])

    # Latest NAV date across all funds
    latest_nav_date = nav_df["Date"].max().date()

    total_invested = 0
    total_current = 0

    # ---------------------------------------------------------
    # CALCULATE TOTAL INVESTED + TOTAL CURRENT VALUE
    # ---------------------------------------------------------
    for fund_name, meta in mutual_funds.items():
        code = str(meta["code"])
        folder = meta["folder"]

        fund_df = load_fund(folder)

        # Latest NAV for this fund
        match = nav_df[nav_df["SchemeCode"] == code]
        if match.empty:
            continue

        latest_row = match.sort_values("Date", ascending=False).iloc[0]
        latest_nav = float(latest_row["NAV"])

        invested = calculate_invested_amount(fund_df)
        current = calculate_current_value(fund_df, latest_nav)

        total_invested += invested
        total_current += current

    # ---------------------------------------------------------
    # COMPUTE CURRENT RETURN
    # ---------------------------------------------------------
    current_return = total_current - total_invested

    # ---------------------------------------------------------
    # LOAD PREVIOUS SNAPSHOT (if exists)
    # ---------------------------------------------------------
    file_path = "portfolio_daily.csv"
    prev_change = 0
    prev_change_pct = 0
    indicator = "🟢 ↑"

    if os.path.exists(file_path):
        df_prev = pd.read_csv(file_path)
        df_prev["Date"] = pd.to_datetime(df_prev["Date"], format="%d-%m-%Y")

        prev_rows = df_prev[df_prev["Date"] < pd.to_datetime(latest_nav_date)]
        if not prev_rows.empty:
            last_prev = prev_rows.iloc[-1]

            prev_value = float(last_prev["TotalValue"])
            prev_change = total_current - prev_value
            prev_change_pct = (prev_change / prev_value * 100) if prev_value != 0 else 0
            indicator = "🟢 ↑" if prev_change > 0 else "🔴 ↓"

    # ---------------------------------------------------------
    # BUILD NEW ROW
    # ---------------------------------------------------------
    new_row = {
        "Date": latest_nav_date.strftime("%d-%m-%Y"),
        "TotalInvested": round(total_invested, 2),
        "TotalValue": round(total_current, 2),
        "CurrentReturn": round(current_return, 2),
        "OneDayChange": round(prev_change, 2),
        "OneDayChangePct": f"{prev_change_pct:.2f}%",
        "Indicator": indicator
    }

    # ---------------------------------------------------------
    # APPEND TO FILE
    # ---------------------------------------------------------
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)

        # Avoid duplicate entries
        if new_row["Date"] in df_existing["Date"].astype(str).values:
            print("Already updated for today.")
            return

        df_updated = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df_updated = pd.DataFrame([new_row])

    df_updated.to_csv(file_path, index=False)
    print("Portfolio snapshot updated.")


if __name__ == "__main__":
    compute_portfolio_snapshot()
