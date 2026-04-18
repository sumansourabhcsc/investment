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

            # ---------------------------------------------------
            # NORMALIZE COLUMN NAMES
            # ---------------------------------------------------
            df.columns = df.columns.str.strip().str.title()

            # ---------------------------------------------------
            # FIX DATE COLUMN
            # ---------------------------------------------------
            # Your CSV likely has "Date" column → rename to Date_Purchase
            if "Date" in df.columns:
                df.rename(columns={"Date": "Date_Purchase"}, inplace=True)

            # Convert to datetime
            df["Date_Purchase"] = pd.to_datetime(df["Date_Purchase"], errors="coerce")

            # ---------------------------------------------------
            # FIX NUMERIC COLUMNS
            # ---------------------------------------------------
            for col in ["Units", "Nav", "Amount"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # ---------------------------------------------------
            # ADD FUND NAME
            # ---------------------------------------------------
            df["FundName"] = fund_name

            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
