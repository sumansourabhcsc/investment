import os
import pandas as pd

def load_all_funds(base_path="mutualfund"):
    all_data = []

    for fund_name in os.listdir(base_path):
        fund_folder = os.path.join(base_path, fund_name)
        fund_file = os.path.join(fund_folder, "fund.csv")

        if os.path.isfile(fund_file):
            df = pd.read_csv(fund_file)

            df["FundName"] = fund_name

            # FIX: ensure correct types
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            df["Units"] = pd.to_numeric(df["Units"], errors="coerce")
            df["Date_Purchase"] = pd.to_datetime(df["Date_Purchase"], errors="coerce")

            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
