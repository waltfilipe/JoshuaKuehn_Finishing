import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# ==========================
# Page Configuration
# ==========================
st.set_page_config(layout="wide", page_title="Shot Map Analysis")

st.title("Shot Map Analysis")
st.caption("Click on the icons on the pitch to play the corresponding shot video.")

# ==========================
# Data Setup (Identical structure to your working code)
# ==========================
shots_raw = [
    ("GOAL", 115.0, 40.0, "videos/Fin 1.mp4"),
    ("ON TARGET", 105.0, 35.0, "videos/Fin 2.mp4"),
    ("OFF TARGET", 98.0, 50.0, "videos/Fin 3.mp4"),
    ("ON TARGET", 110.0, 45.0, "videos/Fin 4.mp4"),
    ("GOAL", 112.0, 38.0, "videos/Fin 5.mp4"),
    ("OFF TARGET", 102.0, 25.0, "videos/Fin 6.mp4"),
    ("ON TARGET", 108.0, 42.0, "videos/Fin 7.mp4"),
]

df = pd.DataFrame(shots_raw, columns=["type", "x", "y", "video"])

def get_style(outcome):
    if outcome == "GOAL":
        return '*', '#EF476F', 150  # Pink Star
    if outcome == "ON TARGET":
        return 'h', '#06D6A0', 120  # Green Hexagon
    return 'o', '#FFD166', 100      # Yellow Circle

# ==========================
# Main Layout
# ==========================
col_map, col_vid = st.columns([1, 1])

with col_map:
    st.subheader("Interactive Pitch Map")
    # Pitch Setup: Black background to match your request
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#c2c2c2')
    fig, ax = pitch.draw(figsize=(8, 6))
    
    for _, row in df.iterrows():
        marker, color, size = get_style(row["type"])
        # Using white edge to make markers pop on black background
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors='white', linewidths=0.8, ax=ax, zorder=3)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='#EF476F', markersize=10, linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='On Target', markerfacecolor='#06D6A0', markersize=8, linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Off Target', markerfacecolor='#FFD166', markersize=8, linestyle='None'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, fontsize='small')

    # Convert plot to image for coordinate tracking
    buf = BytesIO()
    # Ensure the savefig also uses the dark background
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight', facecolor='#1a1a1a')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Use fixed width (700) exactly like your working code
    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# Interaction Logic (Exact same as Duel Map)
# ==========================
selected_event = None

if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]
    
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    RADIUS = 5 
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Video Display
# ==========================
with col_vid:
    st.subheader("Video Analysis")
    if selected_event is not None:
        st.success(f"**Outcome:** {selected_event['type']}")
        
        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except:
                st.error(f"Video file not found: {selected_event['video']}")
    else:
        st.info("Select a marker on the pitch to load the video analysis.")
