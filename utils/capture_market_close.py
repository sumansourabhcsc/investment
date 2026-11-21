# utils/capture_market_close.py
import json
import os
import shutil
import sys
import time
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

import requests
import yfinance as yf

IST = ZoneInfo("Asia/Kolkata")
DATA_PATH = "data/market_index_history.json"
CLOSE_READY = dtime(15, 45)      # bars for today are final after this
MAX_MOVE = 0.15                  # reject >15% day-over-day jump as bad data
MAX_STALE_DAYS = 4               # fail the run if history is older than this
SYMBOLS = {"nifty": "^NSEI", "sensex": "^BSESN"}

# Higher rank wins when two sources give the same date
RANK = {"yf_5m": 2, "nse": 3, "yf_1d": 1}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


def retry(fn, tries=3, delay=3):
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            last = e
            print(f"[WARN] attempt {i + 1}/{tries} failed: {e}")
            time.sleep(delay * (i + 1))
    print(f"[WARN] giving up: {last}")
    return {}


def _to_ist(index):
    return index.tz_localize(IST) if index.tz is None else index.tz_convert(IST)


# ---------- sources: each returns {iso_date: close} ----------
def yf_daily(symbol):
    def go():
        h = yf.Ticker(symbol).history(period="10d", interval="1d").dropna(subset=["Close"])
        h.index = _to_ist(h.index)
        return {ts.date().isoformat(): round(float(c), 2) for ts, c in h["Close"].items()}
    return retry(go)


def yf_5m(symbol):
    def go():
        h = yf.Ticker(symbol).history(period="10d", interval="5m").dropna(subset=["Close"])
        h.index = _to_ist(h.index)
        out = {}
        for ts, c in h["Close"].items():          # chronological: last bar per date wins
            if ts.time() >= dtime(15, 15):         # ignore days whose feed stopped early
                out[ts.date().isoformat()] = round(float(c), 2)
        return out
    return retry(go)


def nse_nifty():
    def go():
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=HEADERS, timeout=10)
        r = s.get("https://www.nseindia.com/api/allIndices", headers=HEADERS, timeout=10)
        r.raise_for_status()
        j = r.json()
        stamp = (j.get("timestamp") or "").split(" ")[0]
        d = datetime.strptime(stamp, "%d-%b-%Y").date().isoformat()
        for item in j.get("data", []):
            if item.get("index") == "NIFTY 50":
                return {d: round(float(item["last"]), 2)}
        return {}
    return retry(go, tries=2)


# ---------- merge + validate ----------
def collect(name, symbol):
    """Return {date: (value, source)} using the highest-ranked source per date."""
    sources = [("yf_1d", yf_daily(symbol)), ("yf_5m", yf_5m(symbol))]
    if name == "nifty":
        sources.append(("nse", nse_nifty()))
    merged = {}
    for src, data in sources:
        for d, v in data.items():
            if v > 0 and (d not in merged or RANK[src] > RANK[merged[d][1]]):
                merged[d] = (v, src)
    return merged


def load_history():
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        return []
    with open(DATA_PATH) as f:
        txt = f.read().strip()
    if not txt:
        return []
    try:
        data = json.loads(txt)
        assert isinstance(data, list)
        return data
    except Exception:
        backup = DATA_PATH + f".corrupt-{int(time.time())}"
        shutil.copy(DATA_PATH, backup)
        print(f"[ERROR] history unreadable, backed up to {backup}. Aborting, nothing overwritten.")
        sys.exit(2)


def capture_and_save():
    now = datetime.now(IST)
    today = now.strftime("%Y-%m-%d")

    series = {n: collect(n, s) for n, s in SYMBOLS.items()}
    dates = sorted(set(series["nifty"]) & set(series["sensex"]))

    mismatch = (set(series["nifty"]) ^ set(series["sensex"]))
    if mismatch:
        print(f"[WARN] dates present for only one index, skipped: {sorted(mismatch)}")

    # today's bar is partial before the close, and meaningless on weekends
    if today in dates and (now.time() < CLOSE_READY or now.weekday() >= 5):
        dates.remove(today)

    history = load_history()
    hmap = {e["date"]: e for e in history}

    def prev_value(d, key):
        earlier = [x for x in hmap if x < d]
        return hmap[max(earlier)][key] if earlier else None

    written = 0
    for d in dates:
        ok = True
        for key in SYMBOLS:
            p = prev_value(d, key)
            v = series[key][d][0]
            if p and abs(v / p - 1) > MAX_MOVE:
                print(f"[WARN] {d} {key}={v} moves >{MAX_MOVE:.0%} vs {p}, rejected")
                ok = False
        if not ok:
            continue
        new_rank = min(RANK[series[k][d][1]] for k in SYMBOLS)
        old = hmap.get(d)
        # Never replace a better-sourced stored bar with a worse one
        if old and RANK.get(old.get("source", "yf_1d"), 3) > new_rank:
            continue
        hmap[d] = {
            "date": d,
            "nifty": series["nifty"][d][0],
            "sensex": series["sensex"][d][0],
            "source": "/".join(sorted({series[k][d][1] for k in SYMBOLS})),
        }
        written += 1

    updated = sorted(hmap.values(), key=lambda e: e["date"])
    if not updated:
        print("[ERROR] no data at all")
        sys.exit(1)

    tmp = DATA_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(updated, f, indent=2)
    os.replace(tmp, DATA_PATH)             # atomic

    last = updated[-1]
    print(f"[OK] {written} bars written, {len(updated)} total. "
          f"Latest {last['date']}: NIFTY={last['nifty']}, SENSEX={last['sensex']}")

    age = (now.date() - datetime.strptime(last["date"], "%Y-%m-%d").date()).days
    if age > MAX_STALE_DAYS:
        print(f"[ERROR] history is {age} days stale, failing run so you get alerted")
        sys.exit(1)


if __name__ == "__main__":
    capture_and_save()
