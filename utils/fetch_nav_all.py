import requests
import os
from datetime import datetime
import pandas as pd

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = f"{OUTPUT_DIR}/nav_all_latest.csv"

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
    "ICICI Pru BHARAT 22 FOF": "143903",
}

ALLOWED_SCHEME_CODES = set(mutual_funds.values())


def fetch_and_clean_navall():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("⏳ Fetching NAV data from AMFI...")
    r = requests.get(AMFI_URL, timeout=30)
    r.raise_for_status()

    # Collect all scheme codes present in the file for diagnostics
    all_codes_in_file = set()
    rows = []

    skipped_parts = 0
    skipped_nav = 0
    skipped_date = 0

    for line in r.text.splitlines():
        line = line.strip()

        # Skip blank lines and header lines
        if not line or "Scheme Code" in line:
            continue

        # Skip section header lines (fund house names, etc.) — they have no semicolons
        if ";" not in line:
            continue

        parts = line.split(";")

        # Collect code for diagnostics regardless of field count
        if parts[0].strip():
            all_codes_in_file.add(parts[0].strip())

        # Require at least 6 fields; tolerate extra trailing fields
        if len(parts) < 6:
            skipped_parts += 1
            continue

        scheme_code = parts[0].strip()
        isin_g      = parts[1].strip()
        isin_r      = parts[2].strip()
        name        = parts[3].strip()
        nav_raw     = parts[4].strip()
        date_raw    = parts[5].strip()

        if scheme_code not in ALLOWED_SCHEME_CODES:
            continue

        # Parse NAV
        try:
            nav = float(nav_raw)
        except ValueError:
            print(f"  ⚠️  Bad NAV for {scheme_code} ({name}): '{nav_raw}'")
            skipped_nav += 1
            continue

        # Parse date — AMFI uses DD-Mon-YYYY (e.g. 26-May-2026)
        date_parsed = None
        for fmt in ("%d-%b-%Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                date_parsed = datetime.strptime(date_raw, fmt)
                break
            except ValueError:
                continue

        if date_parsed is None:
            print(f"  ⚠️  Bad date for {scheme_code} ({name}): '{date_raw}'")
            skipped_date += 1
            continue

        date_str = date_parsed.strftime("%d-%m-%Y")

        rows.append([scheme_code, isin_g, isin_r, name, nav, date_str])

    # ── Diagnostics ──────────────────────────────────────────────────────────
    print(f"\n📊 Parse summary:")
    print(f"   Rows matched:            {len(rows)}")
    print(f"   Skipped (< 6 fields):    {skipped_parts}")
    print(f"   Skipped (bad NAV):       {skipped_nav}")
    print(f"   Skipped (bad date):      {skipped_date}")

    missing = []
    for fund_name, code in mutual_funds.items():
        found = any(r[0] == code for r in rows)
        status = "✅" if found else "❌ MISSING"
        print(f"   {status}  {fund_name} ({code})")
        if not found:
            in_file = code in all_codes_in_file
            missing.append((fund_name, code, in_file))

    if missing:
        print("\n⚠️  Missing funds detail:")
        for fund_name, code, in_file in missing:
            if in_file:
                print(f"   {code} IS in the file but was filtered out (NAV/date parse error)")
            else:
                print(f"   {code} NOT found in AMFI file — scheme code may have changed")

    # ── Save ─────────────────────────────────────────────────────────────────
    df = pd.DataFrame(rows, columns=[
        "SchemeCode", "ISIN_Growth", "ISIN_Reinvestment",
        "SchemeName", "NAV", "Date",
    ])
    df.to_csv(OUTPUT_FILE, index=False)

    if len(rows) == 0:
        print("\n❌ No rows written — check diagnostics above.")
    else:
        print(f"\n✅ Saved {len(rows)} rows → {OUTPUT_FILE}")


if __name__ == "__main__":
    fetch_and_clean_navall()
