import pandas as pd

def load_nav_file(nav_path="data/nav_all_latest.csv"):
    df = pd.read_csv(nav_path)

    df.columns = df.columns.str.strip()

    df["SchemeCode"] = df["SchemeCode"].astype(str).str.strip()
    df["NAV"] = pd.to_numeric(df["NAV"], errors="coerce")

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")

    # keep latest NAV per scheme
    df = df.sort_values("Date").drop_duplicates("SchemeCode", keep="last")

    return df
