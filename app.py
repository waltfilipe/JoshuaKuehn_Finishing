import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import os

# Streamlit Page Configuration
st.set_page_config(page_title="Pro Shot Map", layout="centered")

def main():
    st.title("🎯 Precision Shot Map")
    
    # ==========================
    # 1. DATA & PITCH (Same as before)
    # ==========================
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"]
    }
    df_shots = pd.DataFrame(data)

    # Pitch Setup
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#0e1117', 
        line_color='#c7c7c7',
        linewidth=2
    )
    fig, ax = pitch.draw(figsize=(12, 9))
    fig.patch.set_facecolor('#0e1117')
    
    SIZE = 700 

    # Plotting Logic
    for outcome, color, marker in zip(["Goal", "On Target", "Off Target"], 
                                      ["#EF476F", "#06D6A0", "#FFD166"], 
                                      ["*", "h", "o"]):
        subset = df_shots[df_shots["outcome"] == outcome]
        if not subset.empty:
            pitch.scatter(subset.x, subset.y, s=SIZE if marker != "*" else SIZE+300, 
                          marker=marker, c=color, edgecolors='#ffffff', 
                          linewidth=1.5, ax=ax, label=outcome)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=3, 
              frameon=False, fontsize=12, labelcolor='white')

    # Display the Chart
    st.pyplot(fig)

    # ==========================
    # 2. ADDING THE VIDEO BELOW
    # ==========================
    st.markdown("---")
    st.subheader("Match Highlights")

    # Path to your video file
    # Replace 'match_video.mp4' with your actual file name
    video_path = os.path.join("videos", "match_video.mp4")

    if os.path.exists(video_path):
        st.video(
            video_path, 
            format="video/mp4", 
            start_time=0,
            loop=True,      # Keeps the video running
            autoplay=True,  # Starts automatically
            muted=True      # Most browsers require mute for autoplay to work
        )
    else:
        st.error(f"Video file not found at: {video_path}")
        st.info("Make sure the file name is correct and it is inside the 'videos' folder.")

if __name__ == "__main__":
    main()
