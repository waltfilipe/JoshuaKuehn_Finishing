import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Streamlit Page Configuration
st.set_page_config(page_title="Shot Map Dashboard", layout="centered")

def main():
    st.title("⚽ Football Shot Map")
    st.markdown("Visualizing shot data using `mplsoccer` and `Streamlit`.")

    # ==========================
    # 1. SHOT DATA
    # ==========================
    # Creating the initial DataFrame
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"]
    }
    df_shots = pd.DataFrame(data)

    # Sidebar Filters
    st.sidebar.header("Filter Options")
    selected_outcomes = st.sidebar.multiselect(
        "Select outcomes to display:",
        options=["Goal", "On Target", "Off Target"],
        default=["Goal", "On Target", "Off Target"]
    )

    # Filter data based on selection
    df_filtered = df_shots[df_shots["outcome"].isin(selected_outcomes)]

    # ==========================
    # 2. PITCH CALCULATION
    # ==========================
    
    # Split data for plotting
    shots_goal = df_filtered[df_filtered["outcome"] == "Goal"]
    shots_on_target = df_filtered[df_filtered["outcome"] == "On Target"]
    shots_off_target = df_filtered[df_filtered["outcome"] == "Off Target"]

    # Setup the pitch
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white'
    )

    fig, ax = pitch.draw(figsize=(10, 8))
    
    # Marker size
    SIZE = 320 

    # Plot Goals (Stars)
    if not shots_goal.empty:
        pitch.scatter(shots_goal.x, shots_goal.y, s=SIZE, marker='*', c='#EF476F', 
                      edgecolors='#1f1f1f', linewidth=1.2, ax=ax, label='Goal')

    # Plot On Target (Hexagons)
    if not shots_on_target.empty:
        pitch.scatter(shots_on_target.x, shots_on_target.y, s=SIZE, marker='h', c='#06D6A0', 
                      edgecolors='#1f1f1f', linewidth=1.2, ax=ax, label='On Target')

    # Plot Off Target (Circles)
    if not shots_off_target.empty:
        pitch.scatter(shots_off_target.x, shots_off_target.y, s=SIZE, marker='o', c='#FFD166', 
                      edgecolors='#1f1f1f', linewidth=1.2, ax=ax, label='Off Target')

    # Refined Legend
    legend = ax.legend(
        loc='upper left',
        bbox_to_anchor=(0.02, 0.98),
        frameon=True,
        fontsize=11,
        title="Shot Outcomes",
        title_fontsize=12
    )

    # Clean Legend Frame Style
    frame = legend.get_frame()
    frame.set_facecolor("#ffffff")
    frame.set_edgecolor("#d9d9d9")

    # ==========================
    # 3. STREAMLIT DISPLAY
    # ==========================
    st.pyplot(fig)

    # Show raw data option
    with st.expander("View raw data table"):
        st.dataframe(df_filtered, use_container_width=True)

if __name__ == "__main__":
    main()
