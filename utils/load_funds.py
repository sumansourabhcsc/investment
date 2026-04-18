# utils/load_funds.py
import pandas as pd
import glob

def load_all_funds():
    files = glob.glob("mutualfund/*/fund.csv")
    dfs = []
    for f in files:
        df = pd.read_csv(f)

        # Parse dates (your format is dd-mm-yyyy)
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")

        df["FundName"] = f.split("/")[-2]
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)
