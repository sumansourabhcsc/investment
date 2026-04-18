import pandas as pd
import os

MF_FOLDER = "mutualfund"
NAV_FILE = "data/nav_all_latest.csv"


def load_fund(folder_name):
    path = os.path.join(MF_FOLDER, folder_name, "fund.csv")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing fund file: {path}")

    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    return df


def load_nav():
    df = pd.read_csv(NAV_FILE)
    df["SchemeCode"] = df["SchemeCode"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    return df


def get_latest_nav_by_code(nav_df, scheme_code):
    match = nav_df[nav_df["SchemeCode"] == str(scheme_code)]

    if match.empty:
        return None, None

    latest = match.sort_values("Date", ascending=False).iloc[0]

    return latest["NAV"], latest["SchemeName"]
