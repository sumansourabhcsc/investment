# utils/capture_market_close.py
import yfinance as yf
import json
import os
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
DATA_PATH = "data/market_index_history.json"

def _closes(symbol: str) -> dict:
    h = yf.Ticker(symbol).history(period="10d", interval="1d").dropna(subset=["Close"])
    return {ts.date().isoformat(): round(float(c), 2) for ts, c in h["Close"].items()}

def capture_and_save():
    now = datetime.now(IST)
    today = now.strftime("%Y-%m-%d")

    nifty, sensex = _closes("^NSEI"), _closes("^BSESN")
    dates = sorted(set(nifty) & set(sensex))

    # today's bar is partial until the session has finished
    if dates and dates[-1] == today and now.time() < dtime(15, 45):
        dates.pop()
    if not dates:
        raise RuntimeError("No completed daily bars returned")

    history = []
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH) as f:
                txt = f.read().strip()
                history = json.loads(txt) if txt else []
        except json.JSONDecodeError:
            print("[WARN] Invalid JSON, starting fresh.")
    else:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    # replace everything from the first fetched date onward with real bars
    history = [e for e in history if e["date"] < dates[0]]
    history += [{"date": d, "nifty": nifty[d], "sensex": sensex[d]} for d in dates]
    history.sort(key=lambda e: e["date"])

    with open(DATA_PATH, "w") as f:
        json.dump(history, f, indent=2)
    print(f"[OK] Wrote {len(dates)} bars, latest {dates[-1]}: "
          f"NIFTY={nifty[dates[-1]]}, SENSEX={sensex[dates[-1]]}")

if __name__ == "__main__":
    capture_and_save()
