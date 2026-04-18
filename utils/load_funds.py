# utils/load_funds.py
import pandas as pd
import glob

def load_all_funds():
    files = glob.glob("mutualfund/*/fund.csv")
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        df["FundName"] = f.split("/")[-2]  # folder name as fund name
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)
