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
st.caption("Clique nos ícones no campo para carregar o vídeo da finalização.")

# ==========================
# Data Setup - Coordenadas Atualizadas
# ==========================
shots_raw = [
    ("ON TARGET", 93.08, 43.99, "videos/Fin 1.mp4"),  # 13:51
    ("GOAL", 101.06, 37.84, "videos/Fin 2.mp4"),       # 30:11
    ("OFF TARGET", 97.24, 54.46, "videos/Fin 3.mp4"),  # 34:01
    ("OFF TARGET", 105.38, 49.64, "videos/Fin 4.mp4"), # 35:28
    ("OFF TARGET", 111.70, 41.83, "videos/Fin 5.mp4"), # 48:13
    ("ON TARGET", 95.24, 49.64, "videos/Fin 6.mp4"),   # 57:46
    ("ON TARGET", 109.37, 45.15, "videos/Fin 7.mp4"),  # 58:38
]

df = pd.DataFrame(shots_raw, columns=["type", "x", "y", "video"])

def get_style(outcome):
    if outcome == "GOAL":
        return '*', '#EF476F', 300  # Aumentei o tamanho do marcador também
    if outcome == "ON TARGET":
        return 'h', '#06D6A0', 250
    return 'o', '#FFD166', 200

# ==========================
# Main Layout
# ==========================
col_map, col_vid = st.columns([1.5, 1]) # Ajustei a proporção para o mapa ter mais espaço

with col_map:
    st.subheader("Interactive Pitch Map")
    
    # Pitch Setup - Aumentei o figsize de (8, 6) para (12, 9)
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#c2c2c2')
    fig, ax = pitch.draw(figsize=(12, 9)) 
    
    for _, row in df.iterrows():
        marker, color, size = get_style(row["type"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors='white', linewidths=1.2, ax=ax, zorder=3)

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='#EF476F', markersize=12, linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='No Alvo', markerfacecolor='#06D6A0', markersize=10, linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Fora', markerfacecolor='#FFD166', markersize=10, linestyle='None'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', frameon=True, fontsize='medium')

    # Salvando a imagem com DPI maior para manter qualidade no zoom
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Aumentei o width de 700 para 900
    click = streamlit_image_coordinates(img_obj, width=900)

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

    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)
    
    # Mantive o RADIUS em 5, mas pode diminuir para 3 se achar que está selecionando pontos errados
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
        st.success(f"**Resultado:** {selected_event['type']}")
        
        if selected_event["video"]:
            try:
                st.video(selected_event["video"])
            except:
                st.error(f"Arquivo de vídeo não encontrado: {selected_event['video']}")
    else:
        st.info("Selecione um marcador no campo para carregar a análise em vídeo.")
