import streamlit as st
import json

st.set_page_config(page_title="Reaction Time Trainer", layout="centered")

# ── Hide Streamlit UI in flash mode ──
st.markdown("""
<style>
    .block-container { max-width: 600px; padding-top: 2rem; }
    h1 { text-align: center; }
    .stButton > button {
        width: 100%;
        font-size: 18px;
        font-weight: bold;
        padding: 12px;
        background-color: #e94560;
        color: white;
        border: none;
        border-radius: 10px;
    }
    .stButton > button:hover {
        background-color: #c73050;
        color: white;
    }
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
        if st.checkbox(f":{name.lower()}_circle: {name}" if name.lower() in (
            "red", "blue", "green", "orange", "purple"
        ) else f"{name}", value=name in ("Red", "Blue", "Green"), key=name):
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

# ── Start Button ──
st.divider()

if not selected_colors:
    st.warning("Please select at least one color.")
else:
    if st.button("Start Fullscreen", type="primary"):
        colors_json = json.dumps(selected_colors)

        flash_html = f"""
        <div id="flashOverlay" style="
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: 999999; cursor: none; background: #000;
        ">
            <div id="hint" style="
                position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
                font-family: 'Segoe UI', sans-serif; font-size: 16px;
                color: rgba(255,255,255,0.5); z-index: 1000000;
                pointer-events: none; transition: opacity 2s;
            ">Press any key or click to return</div>
        </div>

        <script>
        (function() {{
            const overlay = document.getElementById('flashOverlay');
            const hint = document.getElementById('hint');
            const colors = {colors_json};
            const minDur = {min_dur};
            const maxDur = {max_dur};
            let running = true;
            let timer = null;

            // Fade hint
            setTimeout(() => {{ hint.style.opacity = '0'; }}, 2000);

            // Try real fullscreen
            overlay.requestFullscreen?.().catch(() => {{}});

            function flash() {{
                if (!running) return;
                const color = colors[Math.floor(Math.random() * colors.length)];
                overlay.style.background = color;
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
                overlay.remove();
                hint.remove();
            }}

            document.addEventListener('keydown', function handler(e) {{
                stop();
                document.removeEventListener('keydown', handler);
            }});
            overlay.addEventListener('click', stop);
        }})();
        </script>
        """

        st.components.v1.html(flash_html, height=0)
