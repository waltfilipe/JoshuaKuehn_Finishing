import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
from PIL import Image
import numpy as np

# Page Configuration
st.set_page_config(layout="wide", page_title="Interactive Shot Map")

st.title("⚽ Interactive Shot Map")
st.caption("Click on any marker on the pitch to analyze the shot details and view footage.")

# ==========================
# 1. DATA SETUP
# ==========================
@st.cache_data
def get_data():
    # Converted labels to English: "Gol" -> "Goal", "No Alvo" -> "On Target", "Fora" -> "Off Target"
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"],
        # Example video link for the goal
        "video": [None, "https://www.sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4", None, None, None, None, None]
    }
    return pd.DataFrame(data)

df_shots = get_data()

# ==========================
# 2. STYLE LOGIC
# ==========================
def get_shot_style(outcome):
    if outcome == "Goal":
        return '*', '#EF476F', 500  # Star
    elif outcome == "On Target":
        return 'h', '#06D6A0', 380  # Hexagon
    else:
        return 'o', '#FFD166', 320  # Circle

# ==========================
# 3. MAIN LAYOUT
# ==========================
col1, col2 = st.columns([1.3, 1])

with col1:
    # Setup the Pitch
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#1a1a1a', # Dark theme for modern look
        line_color='#c2c2c2'
    )
    fig, ax = pitch.draw(figsize=(10, 8))

    # Plot each shot
    for _, row in df_shots.iterrows():
        marker, color, size = get_shot_style(row["outcome"])
        pitch.scatter(
            row.x, row.y,
            s=size,
            marker=marker,
            c=color,
            edgecolors='white',
            linewidth=1.2,
            ax=ax,
            zorder=3
        )

    # Convert plot to image to enable coordinates tracking
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight', transparent=False)
    buf.seek(0)
    img = Image.open(buf)
    
    # Render interactive image
    click = streamlit_image_coordinates(img, width=700)

# ==========================
# 4. INTERACTION & DETAILS
# ==========================
selected_shot = None

if click is not None:
    # Scaling click coordinates to real image size
    real_w, real_h = img.size
    disp_w, disp_h = click["width"], click["height"]
    
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Reverse transform pixels to field coordinates
    coords = ax.transData.inverted().transform((pixel_x, real_h - pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Find closest shot (Euclidean distance)
    df_shots["dist"] = np.sqrt((df_shots["x"] - field_x)**2 + (df_shots["y"] - field_y)**2)
    
    closest = df_shots.loc[df_shots["dist"].idxmin()]
    if closest["dist"] < 3.5: # Tolerance threshold
        selected_shot = closest

with col2:
    st.subheader("Shot Analysis")
    
    if selected_shot is not None:
        outcome = selected_shot['outcome']
        color = '#EF476F' if outcome == "Goal" else ('#06D6A0' if outcome == "On Target" else '#FFD166')
        
        # English Info Card
        st.markdown(f"""
        <div style="padding:20px; border-radius:10px; border-left: 10px solid {color}; background-color: #262730; color: white;">
            <h3 style="margin:0;">Outcome: {outcome}</h3>
            <p style="margin:5px 0 0 0; opacity: 0.8;"><b>Coordinates:</b> X: {selected_shot['x']:.1f}, Y: {selected_shot['y']:.1f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Video Section
        if pd.notnull(selected_shot["video"]):
            st.video(selected_shot["video"])
        else:
            st.info("No video footage available for this specific shot.")
            
        # Metrics
        dist_to_goal = np.sqrt((120 - selected_shot['x'])**2 + (40 - selected_shot['y'])**2)
        st.metric("Estimated Distance to Goal", f"{dist_to_goal:.1f} m")
        
    else:
        st.info("Please click on a marker on the map to display shot data and video.")

# ==========================
# 5. STATISTICS SUMMARY
# ==========================
st.write("---")
st.subheader("Game Summary")
total_shots = len(df_shots)
goals = len(df_shots[df_shots["outcome"] == "Goal"])
on_target = len(df_shots[df_shots["outcome"] == "On Target"])
accuracy = ((goals + on_target) / total_shots) * 100

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Shots", total_shots)
m2.metric("Goals", goals)
m3.metric("On Target", on_target)
m4.metric("Shooting Accuracy", f"{accuracy:.1f}%")
