import requests
import os
from datetime import datetime
import pandas as pd

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = f"{OUTPUT_DIR}/nav_all_latest.csv"

# -----------------------------
# YOUR FILTER LIST (EASY TO UPDATE)
# -----------------------------
mutual_funds = {
    "Bandhan Small Cap Fund": "147946",
    "Axis Small Cap Fund": "125354",
    "SBI Small Cap Fund": "125497",
    "quant Small Cap Fund": "120828",
    "Motilal Oswal Midcap Fund": "127042",
    "HSBC Midcap Fund": "151034",
    "Kotak Midcap Fund": "119775",
    "quant Mid Cap Fund": "120841",
    "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": "150902",
    "Parag Parikh Flexi Cap Fund": "122639",
    "Kotak Flexicap Fund": "112090",
    "Nippon India Large Cap Fund": "118632",
    "ICICI Pru BHARAT 22 FOF": "143903",
    "Mirae Asset FANG+": "148928",
    "SBI Magnum Children's Benefit Fund": "148490"
}

# Convert to set for fast lookup
ALLOWED_SCHEME_CODES = set(mutual_funds.values())


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

        # -----------------------------
        # FILTER: only selected funds
        # -----------------------------
        if scheme_code.strip() not in ALLOWED_SCHEME_CODES:
            continue

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

    print("✅ Filtered NAV updated:", OUTPUT_FILE)


if __name__ == "__main__":
    fetch_and_clean_navall()
