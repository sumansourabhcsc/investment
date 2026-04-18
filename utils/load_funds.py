# utils/load_funds.py
import pandas as pd
import glob
from config import mutual_funds

def load_all_funds():
    files = glob.glob("mutualfund/*/fund.csv")
    dfs = []

    # Create reverse lookup: folder → scheme code
    folder_to_code = {v["folder"]: v["code"] for v in mutual_funds.values()}

    for f in files:
        df = pd.read_csv(f)

        # Parse date
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

        # Extract folder name
        folder = f.split("/")[-2]

        df["FundName"] = folder
        df["SchemeCode"] = str(folder_to_code.get(folder, ""))

        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)
