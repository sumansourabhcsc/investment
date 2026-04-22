import streamlit as st

st.set_page_config(page_title="MF Tracker", layout="wide")

st.title("📊 Mutual Fund Portfolio Tracker")

st.write("Use sidebar to navigate")

#########################

import streamlit as st
import streamlit.components.v1 as components

def pulser(
    size: int = 80,
    color: str = "#00f5d4",
    pulse_count: int = 3,
    speed: float = 1.8,
    label: str = "",
    height: int = 200,
):
    """
    Render an animated pulser component inside a Streamlit app.

    Parameters
    ----------
    size        : diameter of the core circle in px
    color       : primary color (hex or CSS value)
    pulse_count : number of ripple rings
    speed       : animation cycle duration in seconds
    label       : optional text displayed below the pulser
    height      : height of the iframe container in px
    """

    delays = " ".join(
        f".ring:nth-child({i + 1}) {{ animation-delay: {i * (speed / pulse_count):.2f}s; }}"
        for i in range(pulse_count)
    )

    rings_html = "\n".join(f'<div class="ring"></div>' for _ in range(pulse_count))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8"/>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

      *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

      body {{
        background: transparent;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: {height}px;
        font-family: 'Space Mono', monospace;
        overflow: hidden;
      }}

      .pulser-wrapper {{
        position: relative;
        width: {size * 4}px;
        height: {size * 4}px;
        display: flex;
        align-items: center;
        justify-content: center;
      }}

      /* ripple rings */
      .ring {{
        position: absolute;
        width: {size}px;
        height: {size}px;
        border-radius: 50%;
        border: 2px solid {color};
        opacity: 0;
        animation: ripple {speed}s ease-out infinite;
      }}

      {delays}

      @keyframes ripple {{
        0%   {{ transform: scale(1);   opacity: 0.8; }}
        100% {{ transform: scale({pulse_count + 1}.5); opacity: 0; }}
      }}

      /* core dot */
      .core {{
        position: relative;
        width: {size}px;
        height: {size}px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, {color}cc, {color}44);
        box-shadow:
          0 0 {size // 4}px {color}99,
          0 0 {size // 2}px {color}44,
          inset 0 0 {size // 6}px {color}66;
        animation: throb {speed * 0.6:.2f}s ease-in-out infinite alternate;
        z-index: 10;
      }}

      @keyframes throb {{
        from {{ box-shadow: 0 0 {size // 4}px {color}99, 0 0 {size // 2}px {color}44, inset 0 0 {size // 6}px {color}66; }}
        to   {{ box-shadow: 0 0 {size // 2}px {color}dd, 0 0 {size}px     {color}66, inset 0 0 {size // 4}px {color}aa; }}
      }}

      /* inner crosshair lines */
      .core::before, .core::after {{
        content: '';
        position: absolute;
        background: {color}55;
        border-radius: 1px;
      }}
      .core::before {{
        width: 1px; height: 60%;
        top: 20%; left: 50%;
        transform: translateX(-50%);
      }}
      .core::after {{
        height: 1px; width: 60%;
        left: 20%; top: 50%;
        transform: translateY(-50%);
      }}

      /* label */
      .label {{
        margin-top: 12px;
        color: {color}cc;
        font-size: 11px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        animation: blink 1.4s step-start infinite;
      }}

      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50%       {{ opacity: 0.2; }}
      }}
    </style>
    </head>
    <body>
      <div class="pulser-wrapper">
        {rings_html}
        <div class="core"></div>
      </div>
      {"<div class='label'>" + label + "</div>" if label else ""}
    </body>
    </html>
    """

    components.html(html, height=height, scrolling=False)


# ── Demo / standalone run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(page_title="Pulser Demo", layout="centered")

    st.markdown(
        """
        <style>
        body { background: #0d0d0d; }
        .block-container { padding-top: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

   # st.title("🔴 Pulser Component")
  #  st.markdown("A reusable animated radar / sonar pulser for Streamlit apps.")

    st.divider()

    # ── Sidebar controls ──────────────────────────────────────────────────────
  #  with st.sidebar:
   #     st.header("Customize")
    #    color   = st.color_picker("Color",        "#00f5d4")
     #   size    = st.slider("Core size (px)",      40, 160, 80, step=10)
      #  rings   = st.slider("Ripple rings",        1, 6, 3)
       # speed   = st.slider("Speed (seconds)",     0.5, 4.0, 1.8, step=0.1)
        #label   = st.text_input("Label text",      "SCANNING")
       # height  = st.slider("Container height",    120, 400, 220, step=20)

    # ── Render ────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pulser(
            size=80,
            color="#00f5d4",
            pulse_count=6,
            speed=1.8,
            label="PULSER",
            height=220,
        )

    st.divider()
    st.subheader("Usage in your own app")
    st.code(
        """
from pulser import pulser

# Minimal — just drop it anywhere in your Streamlit page
pulser()

# Customised
pulser(
    size=80,
    color="#ff6b6b",
    pulse_count=3,
    speed=1.8,
    label="LIVE",
    height=220,
)
""",
        language="python",
    )
