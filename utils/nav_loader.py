import pandas as pd

# this will load the daily NAV file to dataframe- df
def load_nav_file(nav_path="data/nav_all_latest.txt"):
    df = pd.read_csv(
        nav_path,
        sep=";",
        skiprows=1,
        header=0
    )

    # Normalize column names
    df.columns = df.columns.str.strip().str.replace("\r", "", regex=False)

    # Ensure correct types
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y", errors="coerce")
    df["SchemeCode"] = df["SchemeCode"].astype(str).str.strip()

    return df
