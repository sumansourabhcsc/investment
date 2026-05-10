import streamlit.components.v1 as components


def play_background_music(music_url: str, volume: float = 0.3, loop: bool = True):
    components.html(f"""
        <style>
            body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
            #wrap {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 0;
            }}
            #music-btn {{
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
                flex-shrink: 0;
            }}
            #music-btn:hover {{ background: rgba(0, 245, 212, 0.25); }}
            #status {{
                font-family: monospace;
                font-size: 10px;
                color: rgba(0, 245, 212, 0.5);
                letter-spacing: 0.08em;
            }}
        </style>

        <div id="wrap">
            <button id="music-btn" title="Toggle music">🔇</button>
            <span id="status">click to play</span>
        </div>

        <script>
            const btn    = document.getElementById('music-btn');
            const status = document.getElementById('status');

            let audioCtx, gainNode, audioBuffer, sourceNode;
            let playing = false;
            const MUSIC_URL = "{music_url}";
            const VOLUME    = {volume};
            const LOOP      = {'true' if loop else 'false'};

            async function loadAndDecode() {{
                status.textContent = 'loading...';
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                gainNode = audioCtx.createGain();
                gainNode.gain.value = VOLUME;
                gainNode.connect(audioCtx.destination);

                const res = await fetch(MUSIC_URL);
                if (!res.ok) throw new Error('HTTP ' + res.status);
                const buf = await res.arrayBuffer();
                audioBuffer = await audioCtx.decodeAudioData(buf);
                status.textContent = 'ready';
            }}

            function startPlayback() {{
                sourceNode = audioCtx.createBufferSource();
                sourceNode.buffer = audioBuffer;
                sourceNode.loop = LOOP;
                sourceNode.connect(gainNode);
                sourceNode.start(0);
                playing = true;
                btn.textContent = '🔊';
                status.textContent = 'playing';
            }}

            function stopPlayback() {{
                try {{ sourceNode.stop(); sourceNode.disconnect(); }} catch(e) {{}}
                playing = false;
                btn.textContent = '🔇';
                status.textContent = 'paused';
            }}

            btn.addEventListener('click', async () => {{
                try {{
                    if (!audioBuffer) {{
                        await loadAndDecode();
                        await audioCtx.resume();
                        startPlayback();
                    }} else if (playing) {{
                        stopPlayback();
                    }} else {{
                        await audioCtx.resume();
                        startPlayback();
                    }}
                }} catch(e) {{
                    status.textContent = '✗ ' + e.message;
                    console.error(e);
                }}
            }});

            // Attempt autoplay on load
            (async () => {{
                try {{
                    await loadAndDecode();
                    await audioCtx.resume();
                    startPlayback();
                }} catch(e) {{
                    status.textContent = 'click ▶ to start';
                    console.warn('Autoplay blocked or fetch failed:', e);
                }}
            }})();
        </script>
    """, height=60, scrolling=False)
