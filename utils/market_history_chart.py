# utils/market_history_chart.py

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import date, datetime, timedelta

from utils.sidebar_style import scale_component_html

def show_market_history_chart():
    base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "data", "market_index_history.json")

    if not os.path.exists(data_path):
        st.info("No market history yet — data will appear after the first capture.")
        return

    with open(data_path, "r") as f:
        history = json.load(f)

    if len(history) < 2:
        st.info("Collecting data — chart will appear once 2+ days are recorded.")
        return

    range_choice = st.radio(
        "Quick Range", options=["1M", "6M", "1Y", "All", "Custom"],
        index=3, horizontal=True, label_visibility="collapsed", key="market_history_range"
    )

    range_map = {"1M": 30, "6M": 180, "1Y": 365, "All": 9999}

    if range_choice != "Custom":
        days          = range_map[range_choice]
        default_start = date.today() - timedelta(days=days)
        default_end   = date.today()
        col_d1, col_d2, col_spacer = st.columns([1, 1, 3])
        with col_d1:
            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:8px;
                background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.07);
                border-radius:6px;padding:5px 12px;font-family:'DM Mono',monospace;
                font-size:0.8125rem;color:rgba(255,255,255,0.5);">
                <span style="color:rgba(255,255,255,0.3);font-size:0.6875rem;">FROM</span>
                <span style="color:rgba(255,255,255,0.85);">{default_start.strftime("%d %b %Y")}</span>
            </div>""", unsafe_allow_html=True)
        with col_d2:
            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:8px;
                background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.07);
                border-radius:6px;padding:5px 12px;font-family:'DM Mono',monospace;
                font-size:0.8125rem;color:rgba(255,255,255,0.5);">
                <span style="color:rgba(255,255,255,0.3);font-size:0.6875rem;">TO</span>
                <span style="color:rgba(255,255,255,0.85);">{default_end.strftime("%d %b %Y")}</span>
            </div>""", unsafe_allow_html=True)
        start_date, end_date = default_start, default_end
    else:
        default_start = date.today() - timedelta(days=365)
        default_end   = date.today()
        col_d1, col_d2, col_spacer = st.columns([1, 1, 3])
        with col_d1:
            start_date = st.date_input("Start Date", value=default_start, max_value=date.today(), key="market_start_date")
        with col_d2:
            end_date = st.date_input("End Date", value=default_end, min_value=start_date, max_value=date.today(), key="market_end_date")

    history = [
        e for e in history
        if start_date <= datetime.strptime(e["date"], "%Y-%m-%d").date() <= end_date
    ]

    if len(history) < 2:
        st.info("Not enough data in the selected range — try a wider range.")
        return

    dates_js  = json.dumps([e["date"]   for e in history])
    nifty_js  = json.dumps([e["nifty"]  for e in history])
    sensex_js = json.dumps([e["sensex"] for e in history])

    data_script = f"<script>const dates={dates_js};const nifty={nifty_js};const sensex={sensex_js};</script>"

    html = """
<!DOCTYPE html><html><head>
<meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@300;400&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: transparent; font-family: 'DM Mono', monospace; padding: 0.4rem 0; }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }
  .chart-shell {
    background: rgba(8,14,20,0.82);
    border: 1px solid rgba(0,245,212,0.15);
    border-radius: 14px;
    padding: 1rem 1.2rem 0.9rem;
    position: relative;
    overflow: hidden;
  }
  .chart-shell.sensex {
    border-color: rgba(167,139,250,0.2);
  }
  .chart-shell::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    opacity: 0.6;
  }
  .chart-shell.nifty::before  { background: linear-gradient(90deg, #00f5d4, #00c9ff); }
  .chart-shell.sensex::before { background: linear-gradient(90deg, #a78bfa, #c084fc); }
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.7rem;
  }
  .chart-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }
  .nifty  .chart-label { color: rgba(0,245,212,0.6); }
  .sensex .chart-label { color: rgba(167,139,250,0.7); }
  .chart-index {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.06em;
  }
  .nifty  .chart-index { color: rgba(0,245,212,0.35); }
  .sensex .chart-index { color: rgba(167,139,250,0.35); }
  .latest-price {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 0.2rem;
  }
  .nifty  .latest-price { color: #00f5d4; }
  .sensex .latest-price { color: #a78bfa; }
  .change-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.62rem;
    margin-bottom: 0.8rem;
  }
  canvas { width: 100% !important; }
</style>
</head><body>
""" + data_script + """
<div class="grid">

  <!-- Nifty 50 -->
  <div class="chart-shell nifty">
    <div class="chart-header">
      <div>
        <div class="chart-label">&#11043; NSE</div>
        <div class="latest-price" id="nifty-price">--</div>
        <div class="change-row" id="nifty-change"></div>
      </div>
      <div class="chart-index">NIFTY 50</div>
    </div>
    <canvas id="niftyChart" height="160"></canvas>
  </div>

  <!-- Sensex -->
  <div class="chart-shell sensex">
    <div class="chart-header">
      <div>
        <div class="chart-label">&#11043; BSE</div>
        <div class="latest-price" id="sensex-price">--</div>
        <div class="change-row" id="sensex-change"></div>
      </div>
      <div class="chart-index">SENSEX</div>
    </div>
    <canvas id="sensexChart" height="160"></canvas>
  </div>

</div>

<script>
function makeGradient(ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 160);
  g.addColorStop(0, color.replace("1)", "0.22)"));
  g.addColorStop(1, color.replace("1)", "0)"));
  return g;
}

function changeHTML(arr, color) {
  const first = arr[0], last = arr[arr.length - 1];
  const diff = (last - first).toFixed(2);
  const pct  = ((last - first) / first * 100).toFixed(2);
  const up   = diff >= 0;
  const arrow = up ? "▲" : "▼";
  const c     = up ? (color === "teal" ? "#00f5d4" : "#a78bfa") : "#ff4d6d";
  return `<span style="color:${c};font-weight:500;">${arrow} ${Math.abs(diff).toLocaleString("en-IN")}</span>
          <span style="color:${c};opacity:0.8;">(${arrow}${Math.abs(pct)}%)</span>
          <span style="color:rgba(200,230,225,0.35);">vs first</span>`;
}

// ── Nifty Chart ──
const niftyCtx = document.getElementById("niftyChart").getContext("2d");
document.getElementById("nifty-price").textContent = nifty[nifty.length - 1].toLocaleString("en-IN");
document.getElementById("nifty-change").innerHTML  = changeHTML(nifty, "teal");

new Chart(niftyCtx, {
  type: "line",
  data: {
    labels: dates,
    datasets: [{
      data: nifty,
      borderColor: "#00f5d4",
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: "#00f5d4",
      pointHoverRadius: 5,
      fill: true,
      backgroundColor: makeGradient(niftyCtx, "rgba(0,245,212,1)"),
      tension: 0.35,
    }]
  },
  options: {
    responsive: true,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(8,14,24,0.92)",
        borderColor: "rgba(0,245,212,0.25)",
        borderWidth: 1,
        titleFont: { family: "'Syne', sans-serif", size: 11 },
        bodyFont:  { family: "'DM Mono', monospace", size: 11 },
        titleColor: "rgba(0,245,212,0.8)",
        bodyColor: "#e8f5f2",
        padding: 10,
        callbacks: {
          label: (c) => ` Nifty 50: ${c.parsed.y.toLocaleString("en-IN")}`
        }
      }
    },
    scales: {
      x: {
        ticks: { font: { family: "'DM Mono', monospace", size: 8 }, color: "rgba(200,230,225,0.35)", maxTicksLimit: 8, maxRotation: 35 },
        grid:   { color: "rgba(0,245,212,0.05)" },
        border: { color: "rgba(0,245,212,0.1)" }
      },
      y: {
        ticks: { font: { family: "'DM Mono', monospace", size: 8 }, color: "rgba(200,230,225,0.35)", callback: (v) => v.toLocaleString("en-IN") },
        grid:   { color: "rgba(0,245,212,0.05)" },
        border: { color: "rgba(0,245,212,0.1)" }
      }
    }
  }
});

// ── Sensex Chart ──
const sensexCtx = document.getElementById("sensexChart").getContext("2d");
document.getElementById("sensex-price").textContent = sensex[sensex.length - 1].toLocaleString("en-IN");
document.getElementById("sensex-change").innerHTML  = changeHTML(sensex, "purple");

new Chart(sensexCtx, {
  type: "line",
  data: {
    labels: dates,
    datasets: [{
      data: sensex,
      borderColor: "#a78bfa",
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: "#a78bfa",
      pointHoverRadius: 5,
      fill: true,
      backgroundColor: makeGradient(sensexCtx, "rgba(167,139,250,1)"),
      tension: 0.35,
    }]
  },
  options: {
    responsive: true,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(8,14,24,0.92)",
        borderColor: "rgba(167,139,250,0.25)",
        borderWidth: 1,
        titleFont: { family: "'Syne', sans-serif", size: 11 },
        bodyFont:  { family: "'DM Mono', monospace", size: 11 },
        titleColor: "rgba(167,139,250,0.8)",
        bodyColor: "#e8f5f2",
        padding: 10,
        callbacks: {
          label: (c) => ` Sensex: ${c.parsed.y.toLocaleString("en-IN")}`
        }
      }
    },
    scales: {
      x: {
        ticks: { font: { family: "'DM Mono', monospace", size: 8 }, color: "rgba(200,230,225,0.35)", maxTicksLimit: 8, maxRotation: 35 },
        grid:   { color: "rgba(167,139,250,0.05)" },
        border: { color: "rgba(167,139,250,0.1)" }
      },
      y: {
        ticks: { font: { family: "'DM Mono', monospace", size: 8 }, color: "rgba(200,230,225,0.35)", callback: (v) => v.toLocaleString("en-IN") },
        grid:   { color: "rgba(167,139,250,0.05)" },
        border: { color: "rgba(167,139,250,0.1)" }
      }
    }
  }
});
</script>
</body></html>
"""

    components.html(scale_component_html(html), height=380, scrolling=False)
