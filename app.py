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

st.title("Interactive Shot Map Analysis")
st.caption("Click on the icons on the pitch to play the corresponding shot video.")

# ==========================
# Data Setup - Updated with New Coordinates
# ==========================
shots_raw = [
    ("ON TARGET", 93.08, 43.99, "videos/Fin 1.mp4"),  # 13:51 – Shot on Goal
    ("GOAL", 101.06, 37.84, "videos/Fin 2.mp4"),       # 30:11 – Goal
    ("OFF TARGET", 97.24, 54.46, "videos/Fin 3.mp4"),  # 34:01 – Shot Off
    ("OFF TARGET", 105.38, 49.64, "videos/Fin 4.mp4"), # 35:28 – Shot Off
    ("OFF TARGET", 111.70, 41.83, "videos/Fin 5.mp4"), # 48:13 – Shot Off
    ("ON TARGET", 95.24, 49.64, "videos/Fin 6.mp4"),   # 57:46 – Shot
    ("ON TARGET", 109.37, 45.15, "videos/Fin 7.mp4"),  # 58:38 – Shot
]

df = pd.DataFrame(shots_raw, columns=["type", "x", "y", "video"])

def get_style(outcome):
    if outcome == "GOAL":
        return '*', '#EF476F', 350  # Pink Star (Enlarged)
    if outcome == "ON TARGET":
        return 'h', '#06D6A0', 250  # Green Hexagon (Enlarged)
    return 'o', '#FFD166', 200      # Yellow Circle (Enlarged)

# ==========================
# Main Layout (Enlarged Pitch)
# ==========================
# Proportions set to 2:1 so the map dominates the screen
col_map, col_vid = st.columns([2, 1])

with col_map:
    st.subheader("Interactive Pitch Map")
    
    # Pitch Setup: Dark Mode
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#c2c2c2')
    
    # Increased figsize to (12, 9) for a larger workspace
    fig, ax = pitch.draw(figsize=(12, 9))
    
    for _, row in df.iterrows():
        marker, color, size = get_style(row["type"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors='white', linewidths=1.2, ax=ax, zorder=3)

    # Custom Legend
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='#EF476F', markersize=15, linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='On Target', markerfacecolor='#06D6A0', markersize=12, linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Off Target', markerfacecolor='#FFD166', markersize=12, linestyle='None'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, fontsize='medium')

    # Convert plot to image with higher DPI for sharpness
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Rendering with 950px width for a large display
    click = streamlit_image_coordinates(img_obj, width=950)

# ==========================
# Interaction Logic
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

    # Calculate Euclidean distance to find the nearest shot
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Click tolerance radius
    RADIUS = 4 
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
        st.write(f"Coordinates: ({selected_event['x']}, {selected_event['y']})")
        
        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except Exception:
                st.error(f"Video file not found: {selected_event['video']}")
    else:
        st.info("Select a marker on the pitch to play the analysis video.")
