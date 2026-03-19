import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

st.set_page_config(layout="wide")

# ==========================
# DATA
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
df["id"] = df.index + 1

# ==========================
# SESSION STATE
# ==========================

if "selected" not in st.session_state:
    st.session_state.selected = 0

# ==========================
# LAYOUT
# ==========================

col1, col2 = st.columns([2, 1])

# ==========================
# LEFT: PITCH
# ==========================

with col1:
    st.title("Finalizações")

    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white'
    )

    fig, ax = pitch.draw(figsize=(6, 8))

    for i, row in df.iterrows():

        # highlight selected
        if i == st.session_state.selected:
            size = 500
            edge = "black"
            lw = 2.5
        else:
            size = 300
            edge = "#1f1f1f"
            lw = 1.2

        # color
        if row["result"] == "GOAL":
            color = "#EF476F"
            marker = "*"
        elif row["result"] == "ON TARGET":
            color = "#06D6A0"
            marker = "h"
        else:
            color = "#FFD166"
            marker = "o"

        pitch.scatter(
            row["x"], row["y"],
            s=size,
            c=color,
            marker=marker,
            edgecolors=edge,
            linewidth=lw,
            ax=ax
        )

        # label number
        ax.text(row["x"], row["y"], str(row["id"]),
                ha='center', va='center', fontsize=8, color='black')

    st.pyplot(fig)

# ==========================
# RIGHT: VIDEO + SELECTOR
# ==========================

with col2:
    st.title("Vídeo")

    # selector (simulates click)
    selected_id = st.radio(
        "Escolha a finalização:",
        df["id"],
        index=st.session_state.selected
    )

    st.session_state.selected = selected_id - 1

    video_path = df.loc[st.session_state.selected, "video"]

    st.video(video_path)
