
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
            df["FundName"] = fund_name
            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
