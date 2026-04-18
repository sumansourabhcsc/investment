import pandas as pd
import os

NAV_FILE = "data/nav_all_latest.csv"
MF_FOLDER = "mutualfund"

def load_nav():
    df = pd.read_csv(NAV_FILE)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

def load_fund(fund_name):
    path = os.path.join(MF_FOLDER, fund_name, "fund.csv")
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df

def get_all_funds():
    return os.listdir(MF_FOLDER)
