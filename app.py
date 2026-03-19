import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import os

# Configuração da página
st.set_page_config(page_title="Pro Shot Map", layout="centered")

def main():
    st.markdown("<h1 style='text-align: center; color: white;'>🎯 Match Analysis: Shots</h1>", unsafe_allow_html=True)

    # ==========================
    # 1. DADOS
    # ==========================
    data = {
        "id": ["Fin 1", "Fin 2", "Fin 3", "Fin 4", "Fin 5", "Fin 6", "Fin 7"],
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"]
    }
    df_shots = pd.DataFrame(data)

    # ==========================
    # 2. PITCH & PLOT
    # ==========================
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#000000', 
        line_color='#444444',
        linewidth=1.5
    )
    
    fig, ax = pitch.draw(figsize=(10, 8))
    fig.patch.set_facecolor('#000000')

    # Configurações de Estilo
    SIZE = 700
    SETTINGS = {
        "Goal": {"color": "#EF476F", "marker": "*", "label": "Goal"},
        "On Target": {"color": "#06D6A0", "marker": "h", "label": "On Target"},
        "Off Target": {"color": "#FFD166", "marker": "o", "label": "Off Target"}
    }

    # Plotar os chutes e IDs
    for i, row in df_shots.iterrows():
        s_info = SETTINGS[row.outcome]
        
        # Desenha o ícone no campo
        pitch.scatter(
            row.x, row.y, 
            s=SIZE if row.outcome != "Goal" else SIZE + 400,
            marker=s_info["marker"],
            c=s_info["color"],
            edgecolors='#ffffff',
            linewidth=1.2,
            ax=ax,
            zorder=3
        )
        
        # ID da Finalização (Fin X)
        pitch.annotate(
            row.id, 
            xy=(row.x - 3, row.y), 
            ax=ax, 
            color='#aaaaaa', 
            fontsize=8, 
            fontweight='bold',
            ha='center',
            va='center'
        )

    # ==========================
    # 3. LEGENDA REFINADA (BOX BRANCO)
    # ==========================
    from matplotlib.lines import Line2D

    # Criando os elementos customizados para a legenda
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal',
               markerfacecolor='#EF476F', markersize=12, markeredgecolor='black', linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='On Target',
               markerfacecolor='#06D6A0', markersize=10, markeredgecolor='black', linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Off Target',
               markerfacecolor='#FFD166', markersize=10, markeredgecolor='black', linestyle='None')
    ]

    legend = ax.legend(
        handles=legend_elements,
        loc='upper left',
        bbox_to_anchor=(0.02, 0.98),
        frameon=True,
        facecolor='white',
        edgecolor='black',
        fontsize=10,
        title="Shot Outcome",
        title_fontsize=11,
        borderpad=1,
        labelspacing=1.2
    )
    legend.get_title().set_fontweight('bold')

    st.pyplot(fig)

    # ==========================
    # 4. VIDEO SELECTOR
    # ==========================
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_shot = st.selectbox("🎞️ Choose Replay:", df_shots["id"].tolist())

    video_path = os.path.join("videos", f"{selected_shot}.mp4")

    if os.path.exists(video_path):
        st.video(video_path, loop=True, autoplay=True, muted=True)
    else:
        st.info(f"Video `{selected_shot}.mp4` not found in /videos.")

if __name__ == "__main__":
    main()
