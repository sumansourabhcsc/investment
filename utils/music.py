import streamlit.components.v1 as components

def play_background_music(music_url: str, volume: float = 0.3, loop: bool = True):
    loop_attr = "loop" if loop else ""
    components.html(f"""
        <audio id="bg-music" {loop_attr} autoplay>
            <source src="{music_url}" type="audio/mpeg">
        </audio>
        <script>
            const audio = document.getElementById('bg-music');
            audio.volume = {volume};

            // Browsers block autoplay until user interaction — this handles that
            const unlock = () => {{
                audio.play().catch(() => {{}});
                document.removeEventListener('click', unlock);
            }};
            audio.play().catch(() => {{
                document.addEventListener('click', unlock);
            }});
        </script>
    """, height=0)
