import pandas as pd

# this will load the daily NAV file to dataframe- df
def load_nav_file(nav_path="data/nav_all_latest.txt"):
    df = pd.read_csv(nav_path, sep=";")
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y")
    df["SchemeCode"] = df["SchemeCode"].astype(str)
    return df
