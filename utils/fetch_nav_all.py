import requests
import os
from datetime import datetime

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
OUTPUT_DIR = "data"
OUTPUT_FILE = f"{OUTPUT_DIR}/nav_all_latest.txt"

def fetch_and_clean_navall():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    response = requests.get(AMFI_URL)
    response.raise_for_status()
    raw_text = response.text

    cleaned_rows = []
    for line in raw_text.splitlines():
        line = line.strip()

        # Skip empty lines, comments, headings, category names
        if not line or line.startswith("#") or "Scheme Code" in line:
            continue
        if "Mutual Fund" in line or "Schemes" in line:
            continue

        parts = line.split(";")

        # Valid NAV rows always have 6 fields
        if len(parts) != 6:
            continue

        scheme_code, isin_growth, isin_reinv, scheme_name, nav, date = parts

        # Validate NAV
        try:
            nav = float(nav)
        except:
            continue

        cleaned_rows.append(
            f"{scheme_code};{isin_growth};{isin_reinv};{scheme_name};{nav};{date}"
        )

    # Save cleaned file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        #f.write(f"# Cleaned NAV file — Downloaded on {datetime.now()}\n")
        f.write("SchemeCode;ISIN_Growth;ISIN_Reinvestment;SchemeName;NAV;Date\n")
        for row in cleaned_rows:
            f.write(row + "\n")

    print("Cleaned NAVAll.txt saved successfully.")

if __name__ == "__main__":
    fetch_and_clean_navall()
