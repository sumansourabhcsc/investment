import requests
import os
from datetime import datetime
import pandas as pd

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = f"{OUTPUT_DIR}/nav_all_latest.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

mutual_funds = {
    "Mirae Asset FANG+": "148928",
    "SBI Magnum Children's Benefit Fund": "148490",
    "Parag Parikh Flexi Cap Fund": "122639",
    "Bandhan Small Cap Fund": "147946",
    "Edelweiss Flexi Cap Fund": "140353",
    "Motilal Oswal Midcap Fund": "127042",
    "Nippon India Large Cap Fund": "118632",
    "Axis Small Cap Fund": "125354",
    "SBI Small Cap Fund": "125497",
    "quant Small Cap Fund": "120828",
    "HSBC Midcap Fund": "151034",
    "Kotak Midcap Fund": "119775",
    "quant Mid Cap Fund": "120841",
    "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": "150902",
    "Kotak Flexicap Fund": "112090",
    "ICICI Pru BHARAT 22 FOF": "143903"
}

ALLOWED_SCHEME_CODES = set(mutual_funds.values())


def fetch_and_clean_navall():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    r = requests.get(AMFI_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()

    if len(r.text) < 1000:
        raise RuntimeError(f"AMFI response too short ({len(r.text)} chars)")

    rows = []
    for line in r.text.splitlines():
        line = line.strip()
        if not line or "Scheme Code" in line or ";" not in line:
            continue

        parts = line.split(";")

        # AMFI now emits 8 fields: Code;ISIN_G;ISIN_R;Name;Plan;Option;NAV;Date
        if len(parts) != 8:
            continue

        scheme_code, isin_g, isin_r, name, plan, option, nav, date = parts
        scheme_code = scheme_code.strip()

        if scheme_code not in ALLOWED_SCHEME_CODES:
            continue

        # Be explicit about which variant you want — don't take whatever comes first
        if plan.strip() != "Direct Plan" or "Growth" not in option.strip():
            continue

        try:
            nav = float(nav)
        except ValueError:
            continue

        try:
            date_obj = datetime.strptime(date.strip(), "%d-%b-%Y")
            date = date_obj.strftime("%d-%m-%Y")
        except ValueError:
            continue

        rows.append([scheme_code, isin_g.strip(), isin_r.strip(), name.strip(), nav, date])

    if not rows:
        raise RuntimeError("Parsed 0 matching rows — check ALLOWED_SCHEME_CODES and Plan/Option filter")

    df = pd.DataFrame(rows, columns=["SchemeCode", "ISIN_Growth", "ISIN_Reinvestment", "SchemeName", "NAV", "Date"])
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Filtered NAV updated: {OUTPUT_FILE} ({len(rows)} rows)")



if __name__ == "__main__":
    fetch_and_clean_navall()
