# utils/capture_market_close.py
import yfinance as yf
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

def capture_and_save():
    ist = ZoneInfo("Asia/Kolkata")
    today = datetime.now(ist).strftime("%Y-%m-%d")
    data_path = "data/market_index_history.json"

    # ── Load existing data ──
    history = []
    if os.path.exists(data_path):
        try:
            with open(data_path, "r") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        except (json.JSONDecodeError, ValueError):
            print("[WARN] Existing JSON file is invalid or empty — starting fresh.")
            history = []
    else:
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

    # ── Skip if today already captured ──
    if any(entry["date"] == today for entry in history):
        print(f"[SKIP] {today} already captured.")
        return

    # ── Fetch latest prices ──
    try:
        ni = yf.Ticker("^NSEI").fast_info
        se = yf.Ticker("^BSESN").fast_info
        entry = {
            "date":   today,
            "nifty":  round(ni.last_price, 2),
            "sensex": round(se.last_price, 2),
        }
        history.append(entry)
        history.sort(key=lambda x: x["date"])
        with open(data_path, "w") as f:
            json.dump(history, f, indent=2)
        print(f"[OK] Captured {today}: NIFTY={entry['nifty']}, SENSEX={entry['sensex']}")
    except Exception as e:
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    capture_and_save()
