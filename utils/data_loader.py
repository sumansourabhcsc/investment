import pandas as pd
import os

MF_FOLDER = "mutualfund"

def load_fund(folder_name):
    path = os.path.join(MF_FOLDER, folder_name, "fund.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")

    df = pd.read_csv(path)

    # safe date parsing
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    return df


def load_nav():
    path = "data/nav_all_latest.csv"

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ NAV file missing: {path}")

    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    return df
