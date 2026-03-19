import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import os

# Streamlit Page Configuration
st.set_page_config(page_title="Shot Map & Video Analysis", layout="centered")

def main():
    st.title("⚽ Shot Analysis Dashboard")

    # ==========================
    # 1. DATA
    # ==========================
    data = {
        "id": ["Fin 1", "Fin 2", "Fin 3", "Fin 4", "Fin 5", "Fin 6", "Fin 7"],
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"]
    }
    df_shots = pd.DataFrame(data)

    # ==========================
    # 2. PITCH VISUALIZATION
    # ==========================
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#000000', # Pure black
        line_color='#555555', # Dimmed lines for focus on markers
        linewidth=2
    )
    fig, ax = pitch.draw(figsize=(10, 8))
    fig.patch.set_facecolor('#000000')
    
    SIZE = 800 # Large markers as requested

    # Plotting logic with smaller legend settings
    outcomes = [("Goal", "#EF476F", "*"), ("On Target", "#06D6A0", "h"), ("Off Target", "#FFD166", "o")]
    
    for label, color, marker in outcomes:
        subset = df_shots[df_shots["outcome"] == label]
        if not subset.empty:
            pitch.scatter(subset.x, subset.y, s=SIZE if marker != "*" else SIZE+400, 
                          marker=marker, c=color, edgecolors='#ffffff', 
                          linewidth=1.5, ax=ax, label=label)

    # LEGEND: Small and discreet
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(0.02, 0.98),
        frameon=False,
        fontsize=9,      # Smaller font
        labelcolor='white',
        handletextpad=0.2
    )

    st.pyplot(fig)

    # ==========================
    # 3. VIDEO SELECTOR
    # ==========================
    st.markdown("---")
    st.subheader("Video Replay")

    # List of available shot IDs from the dataframe
    shot_options = df_shots["id"].tolist()
    
    selected_shot = st.selectbox("Select a shot to watch:", shot_options)

    # Path logic: videos/Fin 1.mp4, etc.
    # Adjust the extension (.mp4, .mov) if needed
    video_filename = f"{selected_shot}.mp4"
    video_path = os.path.join("videos", video_filename)

    if os.path.exists(video_path):
        st.video(
            video_path, 
            format="video/mp4", 
            loop=True, 
            autoplay=True, 
            muted=True
        )
        st.caption(f"Currently playing: {video_filename}")
    else:
        st.warning(f"Video not found: {video_path}")
        st.info("Check if your files in GitHub are named exactly like 'Fin 1.mp4' inside the 'videos' folder.")

if __name__ == "__main__":
    main()
