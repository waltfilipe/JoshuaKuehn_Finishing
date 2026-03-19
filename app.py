import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np

st.set_page_config(layout="wide")
st.title("Shot Map with Video")

# ==========================
# 1. RAW DATA
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
# 2. SPLIT TYPES
# ==========================

goal = df[df["result"] == "GOAL"]
on_target = df[df["result"] == "ON TARGET"]
off_target = df[df["result"] == "OFF TARGET"]

# ==========================
# 3. CREATE PITCH
# ==========================

pitch = VerticalPitch(
    half=True,
    pitch_type='statsbomb',
    pitch_color='grass',
    line_color='white'
)

fig, ax = pitch.draw(figsize=(6, 8))

SIZE = 320

pitch.scatter(goal.x, goal.y, s=SIZE, marker='*',
              c='#EF476F', edgecolors='#1f1f1f',
              linewidth=1.2, ax=ax, label='Goal')

pitch.scatter(on_target.x, on_target.y, s=SIZE, marker='h',
              c='#06D6A0', edgecolors='#1f1f1f',
              linewidth=1.2, ax=ax, label='On Target')

pitch.scatter(off_target.x, off_target.y, s=SIZE, marker='o',
              c='#FFD166', edgecolors='#1f1f1f',
              linewidth=1.2, ax=ax, label='Off Target')

legend = ax.legend(
    loc='upper left',
    bbox_to_anchor=(0.02, 0.98),
    frameon=True,
    fontsize=10,
    title="Shots"
)

# ==========================
# 4. CONVERT FIG TO IMAGE
# ==========================

buf = BytesIO()
plt.savefig(buf, format="png", dpi=200, bbox_inches="tight")
buf.seek(0)

# ==========================
# 5. LAYOUT
# ==========================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Shot Map")

    value = streamlit_image_coordinates(buf)

# ==========================
# 6. CLICK DETECTION
# ==========================

selected_video = None

if value is not None:
    click_x = value["x"]
    click_y = value["y"]

    # Normalize click (image -> pitch scale)
    img_w, img_h = value["width"], value["height"]

    # Convert to pitch coordinates (approximation)
    pitch_x = (click_x / img_w) * 120
    pitch_y = (click_y / img_h) * 80

    # Find closest shot
    df["distance"] = np.sqrt((df["x"] - pitch_x)**2 + (df["y"] - pitch_y)**2)

    closest = df.loc[df["distance"].idxmin()]

    # Threshold (important to avoid random clicks)
    if closest["distance"] < 8:
        selected_video = closest["video"]

# ==========================
# 7. VIDEO DISPLAY
# ==========================

with col2:
    st.subheader("Video")

    if selected_video:
        st.video(selected_video)
    else:
        st.info("Click on a shot to view the video.")
