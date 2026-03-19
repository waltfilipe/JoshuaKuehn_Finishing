import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import os

# Configuração da página
st.set_page_config(page_title="Pro Shot Analysis", layout="centered")

def main():
    # Estilo Dark para o Streamlit
    st.markdown("<h1 style='text-align: center; color: white;'>🎯 Shot Analysis</h1>", unsafe_allow_html=True)

    # ==========================
    # 1. DADOS DAS FINALIZAÇÕES
    # ==========================
    data = {
        "id": ["Fin 1", "Fin 2", "Fin 3", "Fin 4", "Fin 5", "Fin 6", "Fin 7"],
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"]
    }
    df_shots = pd.DataFrame(data)

    # ==========================
    # 2. MAPA BLACK & GOLD/NEON
    # ==========================
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#000000', 
        line_color='#333333', # Linhas sutis para não poluir
        linewidth=1.5
    )
    
    fig, ax = pitch.draw(figsize=(10, 8))
    fig.patch.set_facecolor('#000000')

    # Configurações visuais
    SIZE = 700
    COLORS = {"Goal": "#EF476F", "On Target": "#06D6A0", "Off Target": "#FFD166"}
    MARKERS = {"Goal": "*", "On Target": "h", "Off Target": "o"}

    # Plotar cada chute individualmente para colocar o ID embaixo
    for i, row in df_shots.iterrows():
        # Desenha o ícone
        pitch.scatter(
            row.x, row.y, 
            s=SIZE if row.outcome != "Goal" else SIZE + 400,
            marker=MARKERS[row.outcome],
            c=COLORS[row.outcome],
            edgecolors='#ffffff',
            linewidth=1.2,
            ax=ax,
            zorder=3
        )
        
        # LEGENDA ELEGANTE EMBAIXO DO ÍCONE
        # Ajustamos o 'y' ligeiramente para o texto não sobrepor o ícone
        pitch.annotate(
            row.id, 
            xy=(row.x - 2.5, row.y), # Pequeno offset para ficar logo abaixo no VerticalPitch
            ax=ax, 
            color='white', 
            fontsize=9, 
            fontweight='bold',
            ha='center',
            va='center',
            alpha=0.8
        )

    st.pyplot(fig)

    # ==========================
    # 3. SELETOR DE VÍDEO
    # ==========================
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Criando colunas para o seletor ficar centralizado e elegante
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_shot = st.selectbox("📺 Select Replay:", df_shots["id"].tolist())

    # Caminho do vídeo
    video_path = os.path.join("videos", f"{selected_shot}.mp4")

    if os.path.exists(video_path):
        st.video(video_path, loop=True, autoplay=True, muted=True)
    else:
        st.info(f"🎥 Video for {selected_shot} will appear here when uploaded to '/videos'.")

if __name__ == "__main__":
    main()
