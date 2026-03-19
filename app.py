import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
from PIL import Image
import numpy as np
from matplotlib.lines import Line2D

# ==========================
# Page Configuration
# ==========================
st.set_page_config(layout="wide", page_title="Shot Map Analysis")

st.title("⚽ Shot Map Analysis")
st.caption("Click on a marker on the pitch to load the corresponding shot video.")

# ==========================
# 1. DATA SETUP
# ==========================
@st.cache_data
def get_data():
    # Shot data (all with assigned video paths)
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"],
        "video": [
            "videos/Fin 1.mp4", "videos/Fin 2.mp4", "videos/Fin 3.mp4", 
            "videos/Fin 4.mp4", "videos/Fin 5.mp4", "videos/Fin 6.mp4", "videos/Fin 7.mp4"
        ]
    }
    return pd.DataFrame(data)

df_shots = get_data()

# ==========================
# 2. MAIN LAYOUT
# ==========================
col_map, col_vid = st.columns([1.2, 1])

with col_map:
    # Pitch Setup (Black Theme)
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#1a1a1a', 
        line_color='#c2c2c2'
    )
    fig, ax = pitch.draw(figsize=(10, 8))

    # Plotting the shots
    for _, row in df_shots.iterrows():
        if row["outcome"] == "Goal":
            marker, color, size = '*', '#EF476F', 550 
        elif row["outcome"] == "On Target":
            marker, color, size = 'h', '#06D6A0', 400 
        else:
            marker, color, size = 'o', '#FFD166', 350

        pitch.scatter(
            row.x, row.y,
            s=size,
            marker=marker,
            c=color,
            edgecolors='white',
            linewidths=1.2,
            ax=ax,
            zorder=3
        )

    # Simple Legend
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='#EF476F', markersize=12, linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='On Target', markerfacecolor='#06D6A0', markersize=10, linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Off Target', markerfacecolor='#FFD166', markersize=10, linestyle='None'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.05), frameon=False, labelcolor='white')

    # Convert plot to image for coordinate tracking
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches='tight', facecolor='#1a1a1a')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Image Widget (Fixed width to maintain coordinate scaling)
    click = streamlit_image_coordinates(img_obj, width=750)

# ==========================
# 3. INTERACTION LOGIC (Mirroring the Duels logic)
# ==========================
selected_shot = None

if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]
    
    # Transform relative click to real image pixels
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Invert Y (Matplotlib starts from bottom) and map to axis coordinates
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Calculate Euclidean distance to find the marker
    df_shots["dist"] = np.sqrt((df_shots["x"] - field_x)**2 + (df_shots["y"] - field_y)**2)
    
    # Tolerance radius (5 Statsbomb units)
    RADIUS = 5 
    candidates = df_shots[df_shots["dist"] < RADIUS]

    if not candidates.empty:
        selected_shot = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# 4. VIDEO DISPLAY
# ==========================
with col_vid:
    st.subheader("Video Player")
    
    if selected_shot is not None:
        st.write(f"**Outcome:** {selected_shot['outcome']}")
        
        # Load Video
        if selected_shot["video"]:
            try:
                st.video(selected_shot["video"])
            except Exception as e:
                st.error(f"Error loading file: {selected_shot['video']}")
    else:
        st.info("Select a shot on the map to load the video footage.")
