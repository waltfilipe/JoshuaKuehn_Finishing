import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Streamlit Page Configuration
st.set_page_config(page_title="Pro Shot Map", layout="centered")

def main():
    st.title("🎯 Precision Shot Map")
    st.markdown("Dark theme visualization with high-visibility markers.")

    # ==========================
    # 1. SHOT DATA
    # ==========================
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"]
    }
    df_shots = pd.DataFrame(data)

    # Sidebar for quick filtering
    st.sidebar.header("Map Settings")
    selected_outcomes = st.sidebar.multiselect(
        "Filter Shot Outcomes:",
        options=["Goal", "On Target", "Off Target"],
        default=["Goal", "On Target", "Off Target"]
    )

    df_filtered = df_shots[df_shots["outcome"].isin(selected_outcomes)]

    # ==========================
    # 2. DARK PITCH SETUP
    # ==========================
    
    # Using 'pitch_color' as black (#000000)
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#0e1117', # Matches Streamlit's dark background or pure black
        line_color='#c7c7c7',
        linewidth=2
    )

    fig, ax = pitch.draw(figsize=(12, 9))
    fig.patch.set_facecolor('#0e1117') # Sets the figure border to match
    
    # INCREASED MARKER SIZE
    # I've bumped this to 600 for a much bolder look
    SIZE = 600 

    # Split and Plot
    shots_goal = df_filtered[df_filtered["outcome"] == "Goal"]
    shots_on_target = df_filtered[df_filtered["outcome"] == "On Target"]
    shots_off_target = df_filtered[df_filtered["outcome"] == "Off Target"]

    # Goals
    if not shots_goal.empty:
        pitch.scatter(shots_goal.x, shots_goal.y, s=SIZE + 200, marker='*', 
                      c='#EF476F', edgecolors='#ffffff', linewidth=1.5, ax=ax, label='Goal')

    # On Target
    if not shots_on_target.empty:
        pitch.scatter(shots_on_target.x, shots_on_target.y, s=SIZE, marker='h', 
                      c='#06D6A0', edgecolors='#ffffff', linewidth=1.5, ax=ax, label='On Target')

    # Off Target
    if not shots_off_target.empty:
        pitch.scatter(shots_off_target.x, shots_off_target.y, s=SIZE, marker='o', 
                      c='#FFD166', edgecolors='#ffffff', linewidth=1.5, ax=ax, label='Off Target')

    # ==========================
    # 3. STYLIZED LEGEND
    # ==========================
    legend = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.02),
        ncol=3, # Horizontal legend for a cleaner look
        frameon=False,
        fontsize=12,
        labelcolor='white',
        handletextpad=0.1
    )

    # Display in Streamlit
    st.pyplot(fig)

if __name__ == "__main__":
    main()
