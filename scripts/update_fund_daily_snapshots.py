import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_loader import load_nav
from utils.load_funds import load_all_funds
from utils.xirr_helper import compute_fund_xirr
from config import mutual_funds


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)


def update_fund_snapshots():

    nav_df = load_nav()
    funds_df = load_all_funds()

    funds_df.columns = funds_df.columns.str.strip()

    nav_df.columns = nav_df.columns.str.strip()
    funds_df.columns = funds_df.columns.str.strip()

    nav_df["Date"] = pd.to_datetime(nav_df["Date"])
    funds_df["Date"] = pd.to_datetime(funds_df["Date"])

    latest_nav_date = nav_df["Date"].max()
    latest_nav_df = nav_df[nav_df["Date"] == latest_nav_date]

    for fund_name, meta in mutual_funds.items():

        scheme_code = str(meta["code"])
        folder_name = meta["folder"]

        fund_data = funds_df[funds_df["SchemeCode"].astype(str) == scheme_code]

        if fund_data.empty:
            continue

        # NAV row
        nav_row = latest_nav_df[latest_nav_df["SchemeCode"] == scheme_code]

        if nav_row.empty:
            continue

        nav = float(nav_row.iloc[0]["NAV"])

        # file path
        base_path = f"mutualfund/{folder_name}"
        ensure_folder(base_path)

        file_path = f"{base_path}/daily_{scheme_code}.csv"

        # compute metrics
        total_units = float(fund_data["Units"].sum())
        total_invested = float(fund_data["Amount"].sum())

        current_value = total_units * nav
        gain = current_value - total_invested

        return_pct = (gain / total_invested) * 100 if total_invested > 0 else 0

        xirr = compute_fund_xirr(fund_data, nav) * 100

        new_row = {
            "date": latest_nav_date.strftime("%d-%m-%Y"),
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "total_units": round(total_units, 2),
            "absolute_gain_loss": round(gain, 2),
            "total_return_pct": f"{return_pct:.2f}%",
            "xirr_annual": f"{xirr:.2f}%",
            "nav": round(nav, 2)
        }

        # =========================
        # append only if new date
        # =========================
        if os.path.exists(file_path):
            existing = pd.read_csv(file_path)

            if str(new_row["date"]) in existing["date"].astype(str).values:
                print(f"Skipping {fund_name} - already updated")
                continue

            updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
        else:
            updated = pd.DataFrame([new_row])

        updated.to_csv(file_path, index=False)
        print(f"Updated: {fund_name}")


if __name__ == "__main__":
    update_fund_snapshots()
