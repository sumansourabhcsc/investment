import streamlit.components.v1 as components


def play_background_music(music_url: str, volume: float = 0.3, loop: bool = True):
    loop_attr = "loop" if loop else ""
    components.html(f"""
        <style>
            body {{ margin: 0; padding: 0; background: transparent; }}
            #music-btn {{
                position: fixed;
                bottom: 12px;
                right: 12px;
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background: rgba(0, 245, 212, 0.12);
                border: 1px solid rgba(0, 245, 212, 0.4);
                color: #00f5d4;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
                z-index: 9999;
            }}
            #music-btn:hover {{
                background: rgba(0, 245, 212, 0.25);
            }}
        </style>

        <audio id="bg-music" {loop_attr}>
            <source src="{music_url}" type="audio/mpeg">
        </audio>

        <button id="music-btn" title="Toggle music">🔇</button>

        <script>
            const audio = document.getElementById('bg-music');
            const btn   = document.getElementById('music-btn');
            audio.volume = {volume};

            let playing = false;

            function startMusic() {{
                audio.play().then(() => {{
                    playing = true;
                    btn.textContent = '🔊';
                }}).catch(() => {{}});
            }}

            function toggleMusic() {{
                if (playing) {{
                    audio.pause();
                    playing = false;
                    btn.textContent = '🔇';
                }} else {{
                    startMusic();
                }}
            }}

            btn.addEventListener('click', toggleMusic);

            // Try autoplay immediately; if blocked, wait for first click on the button
            audio.play().then(() => {{
                playing = true;
                btn.textContent = '🔊';
            }}).catch(() => {{
                // Autoplay blocked — user must click the button
                btn.textContent = '🔇';
            }});
        </script>
    """, height=60, scrolling=False)
