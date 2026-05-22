"""
fetch_nav_history.py  (lives in utils/)

Fetches NAV history for each mutual fund defined in config.py
and saves the response as JSON files under NAVHistory/{fund_code}.json
at the repo root.

Directory layout assumed:
    investment/
    ├── config.py
    ├── NAVHistory/
    │   ├── 148928.json
    │   └── ...
    └── utils/
        └── fetch_nav_history.py   ← this file

- On success  : writes/overwrites the file for that fund.
- On any error: leaves the existing file untouched and logs the failure.

Usage (from anywhere):
    python utils/fetch_nav_history.py
    # or from inside utils/
    python fetch_nav_history.py
"""

import json
import os
import sys
import time
import requests

# ---------------------------------------------------------------------------
# Resolve paths relative to this file so the script works regardless of the
# working directory it is launched from.
#
#   __file__  →  .../investment/utils/fetch_nav_history.py
#   REPO_ROOT →  .../investment/
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add repo root to sys.path so `from config import ...` resolves correctly
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ---------------------------------------------------------------------------
# Import fund definitions from config.py (at repo root)
# ---------------------------------------------------------------------------
try:
    from config import mutual_funds
except ImportError:
    print("ERROR: Could not import 'mutual_funds' from config.py. "
          f"Expected it at: {os.path.join(REPO_ROOT, 'config.py')}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL      = "https://api.mfapi.in/mf/{fund_code}"
OUTPUT_DIR    = os.path.join(REPO_ROOT, "NAVHistory")
REQUEST_DELAY = 0.5   # seconds between requests – be polite to the API
TIMEOUT       = 30    # seconds per request


def fetch_nav(fund_name: str, fund_code: str) -> dict | None:
    """
    Fetch NAV history for a single fund.

    Returns the parsed JSON dict on success, or None on any failure.
    """
    url = BASE_URL.format(fund_code=fund_code)
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()          # raises for 4xx / 5xx
        data = response.json()
        return data
    except requests.exceptions.Timeout:
        print(f"  [TIMEOUT]  {fund_name} ({fund_code}) – request timed out after {TIMEOUT}s")
    except requests.exceptions.HTTPError as exc:
        print(f"  [HTTP ERR] {fund_name} ({fund_code}) – {exc}")
    except requests.exceptions.ConnectionError as exc:
        print(f"  [CONN ERR] {fund_name} ({fund_code}) – {exc}")
    except json.JSONDecodeError:
        print(f"  [JSON ERR] {fund_name} ({fund_code}) – response was not valid JSON")
    except Exception as exc:                 # catch-all so one bad fund never kills the run
        print(f"  [ERROR]    {fund_name} ({fund_code}) – unexpected error: {exc}")
    return None


def save_nav(fund_code: str, data: dict) -> None:
    """Write NAV data to /investment/NAVHistory/{fund_code}.json (atomic write)."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{fund_code}.json")

    # Write to a temp file first, then rename – avoids corrupting an existing
    # file if the process is interrupted mid-write.
    tmp_path = output_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp_path, output_path)


def main() -> None:
    total   = len(mutual_funds)
    success = 0
    failed  = []

    print(f"Fetching NAV history for {total} fund(s)…\n")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}\n")
    print("-" * 60)

    for fund_name, fund_info in mutual_funds.items():
        fund_code = fund_info.get("code", "").strip()
        if not fund_code:
            print(f"  [SKIP]     '{fund_name}' – no fund code defined in config.py")
            failed.append(fund_name)
            continue

        print(f"Fetching  {fund_name}  (code: {fund_code})")
        data = fetch_nav(fund_name, fund_code)

        if data is not None:
            save_nav(fund_code, data)
            records = len(data.get("data", []))
            print(f"  [OK]       Saved {records} NAV record(s) → NAVHistory/{fund_code}.json")
            success += 1
        else:
            failed.append(fund_name)

        time.sleep(REQUEST_DELAY)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"Done.  {success}/{total} fund(s) fetched successfully.")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for name in failed:
            print(f"  • {name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
