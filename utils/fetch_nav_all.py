import requests
import os
from datetime import datetime
import pandas as pd

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = f"{OUTPUT_DIR}/nav_all_latest.csv"

def fetch_and_clean_navall():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    r = requests.get(AMFI_URL)
    r.raise_for_status()

    rows = []

    for line in r.text.splitlines():
        line = line.strip()

        if not line or "Scheme Code" in line or "Mutual Fund" in line:
            continue

        parts = line.split(";")

        if len(parts) != 6:
            continue

        scheme_code, isin_g, isin_r, name, nav, date = parts

        try:
            nav = float(nav)
        except:
            continue

        try:
            date_obj = datetime.strptime(date, "%d-%b-%Y")
            date = date_obj.strftime("%d-%m-%Y")
        except:
            continue

        rows.append([
            scheme_code.strip(),
            isin_g.strip(),
            isin_r.strip(),
            name.strip(),
            nav,
            date
        ])

    df = pd.DataFrame(rows, columns=[
        "SchemeCode",
        "ISIN_Growth",
        "ISIN_Reinvestment",
        "SchemeName",
        "NAV",
        "Date"
    ])

    df.to_csv(OUTPUT_FILE, index=False)

    print("✅ NAV updated:", OUTPUT_FILE)

if __name__ == "__main__":
    fetch_and_clean_navall()
