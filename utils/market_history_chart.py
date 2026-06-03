# utils/market_history_chart.py

import streamlit as st
import streamlit.components.v1 as components
import json
import os

def show_market_history_chart():
    # Resolve path relative to this file → always finds data/ regardless of CWD
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "market_index_history.json")

    if not os.path.exists(data_path):
        st.info("No market history yet — data will appear after the first capture.")
        return

    with open(data_path, "r") as f:
        history = json.load(f)

    if len(history) < 2:
        st.info("Collecting data — chart will appear once 2+ days are recorded.")
        return

    # ── Prepare series ──
    dates   = [e["date"]   for e in history]
    nifty   = [e["nifty"]  for e in history]
    sensex  = [e["sensex"] for e in history]

    dates_js  = json.dumps(dates)
    nifty_js  = json.dumps(nifty)
    sensex_js = json.dumps(sensex)

    chart_height = 340

    components.html(f"""
<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@300;400&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: transparent;
    font-family: 'DM Mono', monospace;
    padding: 0.6rem 0;
  }}
  .chart-shell {{
    background: rgba(8,14,20,0.82);
    border: 1px solid rgba(0,245,212,0.15);
    border-radius: 14px;
    padding: 1.2rem 1.4rem 1rem;
    position: relative;
    overflow: hidden;
  }}
  .chart-shell::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00f5d4, #00c9ff, #a78bfa);
    opacity: 0.55;
  }}
  .chart-title {{
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    color: rgba(0,245,212,0.6);
    text-transform: uppercase;
    margin-bottom: 0.9rem;
  }}
  .legend-row {{
    display: flex;
    gap: 1.4rem;
    margin-bottom: 0.8rem;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    color: rgba(200,230,225,0.7);
    text-transform: uppercase;
  }}
  .legend-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
  canvas {{ width: 100% !important; }}
</style>
</head><body>
<div class="chart-shell">
  <div class="chart-title">⬡ Market Index History</div>
  <div class="legend-row">
    <div class="legend-item">
      <div class="legend-dot" style="background:#00f5d4;box-shadow:0 0 6px #00f5d488;"></div>
      Nifty 50
    </div>
    <div class="legend-item">
      <div class="legend-dot" style="background:#a78bfa;box-shadow:0 0 6px #a78bfa88;"></div>
      Sensex
    </div>
  </div>
  <canvas id="mktChart" height="220"></canvas>
</div>

<script>
const dates  = {dates_js};
const nifty  = {nifty_js};
const sensex = {sensex_js};

function normalise(arr) {{
  const base = arr[0];
  return arr.map(v => parseFloat(((v / base) * 100).toFixed(3)));
}}

const nNifty  = normalise(nifty);
const nSensex = normalise(sensex);

const ctx = document.getElementById("mktChart").getContext("2d");

const gN = ctx.createLinearGradient(0, 0, 0, 220);
gN.addColorStop(0, "rgba(0,245,212,0.22)");
gN.addColorStop(1, "rgba(0,245,212,0)");

const gS = ctx.createLinearGradient(0, 0, 0, 220);
gS.addColorStop(0, "rgba(
