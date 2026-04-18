import os
import pandas as pd

# utils/portfolio_loader.py — LOAD ALL FUNDS FROM GITHUB FOLDERS
def load_all_funds(base_path="mutualfund"):
    all_data = []

    for fund_name in os.listdir(base_path):
        fund_folder = os.path.join(base_path, fund_name)
        fund_file = os.path.join(fund_folder, "fund.csv")

        if os.path.isfile(fund_file):
            df = pd.read_csv(fund_file)

            # -----------------------------
            # NORMALIZE COLUMN NAMES
            # -----------------------------
            df.columns = df.columns.str.strip().str.title()

            # -----------------------------
            # FIX DATE COLUMN
            # -----------------------------
            if "Date" in df.columns:
                df.rename(columns={"Date": "Date_Purchase"}, inplace=True)

            df["Date_Purchase"] = pd.to_datetime(df["Date_Purchase"], errors="coerce")

            # -----------------------------
            # FIX NUMERIC COLUMNS
            # -----------------------------
            if "Units" in df.columns:
                df["Units"] = pd.to_numeric(df["Units"], errors="coerce")

            if "Nav" in df.columns:
                df["Nav"] = pd.to_numeric(df["Nav"], errors="coerce")

            if "Amount" in df.columns:
                df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

            # -----------------------------
            # ADD FUND NAME
            # -----------------------------
            df["Fundname"] = fund_name

            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
