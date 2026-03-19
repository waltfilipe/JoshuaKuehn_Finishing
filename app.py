import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ==========================
# 1. DATA
# ==========================

shots_raw = [
    ("ON TARGET", 93.08, 43.99, "videos/Fin 1.mp4"),
    ("GOAL", 101.06, 37.84, "videos/Fin 2.mp4"),
    ("OFF TARGET", 97.24, 54.46, "videos/Fin 3.mp4"),
    ("OFF TARGET", 105.38, 49.64, "videos/Fin 4.mp4"),
    ("OFF TARGET", 111.70, 41.83, "videos/Fin 5.mp4"),
    ("ON TARGET", 95.24, 49.64, "videos/Fin 6.mp4"),
    ("ON TARGET", 109.37, 45.15, "videos/Fin 7.mp4"),
]

df = pd.DataFrame(shots_raw, columns=["result", "x", "y", "video"])

# ==========================
# 2. STYLE MAP
# ==========================

color_map = {
    "GOAL": "#EF476F",
    "ON TARGET": "#06D6A0",
    "OFF TARGET": "#FFD166"
}

symbol_map = {
    "GOAL": "star",
    "ON TARGET": "hexagon",
    "OFF TARGET": "circle"
}

# ==========================
# 3. SESSION STATE
# ==========================

if "selected_shot" not in st.session_state:
    st.session_state.selected_shot = None

# ==========================
# 4. CREATE PLOTLY PITCH
# ==========================

fig = go.Figure()

for result in df["result"].unique():
    subset = df[df["result"] == result]

    fig.add_trace(go.Scatter(
        x=subset["x"],
        y=subset["y"],
        mode="markers",
        marker=dict(
            size=18,
            color=color_map[result],
            symbol=symbol_map[result],
            line=dict(width=2, color="#1f1f1f")
        ),
        name=result,
        customdata=subset.index,
        hovertemplate=f"{result}<extra></extra>"
    ))

# Pitch layout (StatsBomb style half pitch)
fig.update_layout(
    height=700,
    plot_bgcolor="#6DAA2C",
    paper_bgcolor="#6DAA2C",
    xaxis=dict(range=[80, 120], showgrid=False, visible=False),
    yaxis=dict(range=[0, 80], showgrid=False, visible=False),
    margin=dict(l=10, r=10, t=10, b=10)
)

# ==========================
# 5. CLICK HANDLING
# ==========================

clicked = st.plotly_chart(
    fig,
    use_container_width=True,
    key="pitch",
    on_select="rerun"
)

# Detect click
if clicked and "selection" in clicked:
    points = clicked["selection"]["points"]
    if points:
        idx = points[0]["customdata"]
        st.session_state.selected_shot = idx

# ==========================
# 6. LAYOUT (PITCH + VIDEO)
# ==========================

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Finalizações")

with col2:
    st.subheader("Vídeo da Jogada")

    if st.session_state.selected_shot is not None:
        video_path = df.loc[st.session_state.selected_shot, "video"]
        st.video(video_path)
    else:
        st.info("Clique em uma finalização para ver o vídeo 🎥")
