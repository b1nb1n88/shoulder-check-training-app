import streamlit as st
import json

st.set_page_config(page_title="Reaction Time Trainer", layout="centered")

st.markdown("""
<style>
    .block-container { max-width: 600px; padding-top: 2rem; }
    h1 { text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("Reaction Time Trainer")
st.caption("Select colors and timing, then go fullscreen!")

# ── Color Selection ──
COLORS = {
    "Red": "#e80000",
    "Blue": "#0055ff",
    "Green": "#00c853",
    "Yellow": "#ffd600",
    "Orange": "#ff6d00",
    "Purple": "#aa00ff",
    "Cyan": "#00e5ff",
    "White": "#ffffff",
    "Black": "#000000",
}

st.subheader("Colors")
cols = st.columns(3)
selected_colors = []
for i, (name, hex_val) in enumerate(COLORS.items()):
    with cols[i % 3]:
        if st.checkbox(name, value=name in ("Red", "Blue", "Green"), key=name):
            selected_colors.append(hex_val)

# ── Timing ──
st.subheader("Timing")
col1, col2 = st.columns(2)
with col1:
    min_dur = st.slider("Min duration (ms)", 50, 2000, 200, step=50)
with col2:
    max_dur = st.slider("Max duration (ms)", 100, 5000, 1500, step=50)

if max_dur < min_dur:
    max_dur = min_dur

# ── Start ──
st.divider()

if not selected_colors:
    st.warning("Please select at least one color.")
else:
    if st.button("Start Fullscreen", type="primary", use_container_width=True):
        colors_json = json.dumps(selected_colors)

        flash_html = f"""
        <html>
        <head>
        <style>
            html, body {{
                margin: 0; padding: 0;
                width: 100%; height: 100%;
                overflow: hidden;
            }}
            #flashBox {{
                width: 100vw; height: 100vh;
                display: flex; align-items: center; justify-content: center;
                cursor: none;
            }}
            #hint {{
                position: fixed; bottom: 30px; left: 50%;
                transform: translateX(-50%);
                font-family: 'Segoe UI', sans-serif; font-size: 18px;
                color: rgba(255,255,255,0.5);
                pointer-events: none;
                transition: opacity 2s;
            }}
        </style>
        </head>
        <body>
        <div id="flashBox">
            <div id="hint">Press ESC or click to exit</div>
        </div>
        <script>
        (function() {{
            const box = document.getElementById('flashBox');
            const hint = document.getElementById('hint');
            const colors = {colors_json};
            const minDur = {min_dur};
            const maxDur = {max_dur};
            let running = true;
            let timer = null;

            // Go fullscreen on the iframe itself
            try {{
                const iframe = window.frameElement;
                if (iframe) {{
                    iframe.style.position = 'fixed';
                    iframe.style.top = '0';
                    iframe.style.left = '0';
                    iframe.style.width = '100vw';
                    iframe.style.height = '100vh';
                    iframe.style.zIndex = '999999';
                    iframe.style.border = 'none';
                    iframe.requestFullscreen?.().catch(() => {{}});
                }}
            }} catch(e) {{}}

            setTimeout(() => {{ hint.style.opacity = '0'; }}, 2000);

            function flash() {{
                if (!running) return;
                const c = colors[Math.floor(Math.random() * colors.length)];
                box.style.background = c;
                document.body.style.background = c;
                const dur = minDur + Math.random() * (maxDur - minDur);
                timer = setTimeout(flash, dur);
            }}
            flash();

            function stop() {{
                running = false;
                clearTimeout(timer);
                if (document.fullscreenElement) {{
                    document.exitFullscreen?.().catch(() => {{}});
                }}
                try {{
                    const iframe = window.frameElement;
                    if (iframe) {{
                        iframe.style.position = '';
                        iframe.style.top = '';
                        iframe.style.left = '';
                        iframe.style.width = '';
                        iframe.style.height = '';
                        iframe.style.zIndex = '';
                    }}
                }} catch(e) {{}}
                box.style.background = '#222';
                document.body.style.background = '#222';
                hint.style.opacity = '1';
                hint.textContent = 'Done! Scroll up to restart.';
                hint.style.color = '#aaa';
            }}

            document.addEventListener('keydown', function handler(e) {{
                if (running) {{ stop(); document.removeEventListener('keydown', handler); }}
            }});
            box.addEventListener('click', function handler() {{
                if (running) {{ stop(); box.removeEventListener('click', handler); }}
            }});
        }})();
        </script>
        </body>
        </html>
        """

        st.components.v1.html(flash_html, height=600, scrolling=False)
