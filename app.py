import streamlit as st
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import pandas as pd
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
import numpy as np
from PIL import Image
from matplotlib.lines import Line2D

# Configuração da página
st.set_page_config(layout="wide", page_title="Shot Map Analysis")

# Inicializa selected_event no topo para evitar o erro que você recebeu
selected_event = None

# ==========================
# Data Setup
# ==========================
shots_raw = [
    ("ON TARGET", 93.08, 43.99, "videos/Fin 1.mp4"),
    ("GOAL", 101.06, 37.84, "videos/Fin 2.mp4"),
    ("OFF TARGET", 97.24, 54.46, "videos/Fin 3.mp4"),
    ("OFF TARGET", 105.38, 49.64, "videos/Fin 4.mp4"),
    ("OFF TARGET", 111.70, 41.83, "videos/Fin 5.mp4"),
    ("ON TARGET", 95.24, 49.64, "videos/Fin 6.mp4"),
    ("ON TARGET", 109.37, 45.15, "videos/Fin 7.mp4"),
]
df = pd.DataFrame(shots_raw, columns=["type", "x", "y", "video"])

def get_style(outcome):
    if outcome == "GOAL": return '*', '#EF476F', 250
    if outcome == "ON TARGET": return 'h', '#06D6A0', 200
    return 'o', '#FFD166', 180

# ==========================
# Layout
# ==========================
col_map, col_vid = st.columns([1, 1])

with col_map:
    st.subheader("Interactive Pitch Map")
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#1a1a1a', line_color='#c2c2c2')
    fig, ax = pitch.draw(figsize=(8, 6))

    # Plotar os pontos
    for _, row in df.iterrows():
        marker, color, size = get_style(row["type"])
        pitch.scatter(row.x, row.y, marker=marker, s=size, color=color, 
                      edgecolors='white', linewidths=1, ax=ax, zorder=3)

    # Ajuste CRÍTICO: remove as margens para o clique bater com a imagem
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)

    # Salvar a imagem sem o 'tight' (que distorce as coordenadas)
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, facecolor='#1a1a1a')
    buf.seek(0)
    img_obj = Image.open(buf)

    # Exibir mapa e capturar clique
    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# Lógica do Clique (Corrigida)
# ==========================
if click is not None:
    # Transformação Linear Simples (Normalizada)
    # No Statsbomb: X=0-120, Y=0-80. 
    # Imagem: x=0 a width, y=0 a height
    
    field_x = (click["x"] / click["width"]) * 120
    field_y = (click["y"] / click["height"]) * 80

    # Calcular distância (Euclidiana direta nas unidades do campo)
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)

    # Raio de tolerância (3 a 5 unidades costuma ser o ideal para clique)
    RADIUS = 3.5
    candidates = df[df["dist"] < RADIUS]

    if not candidates.empty:
        selected_event = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# Video Display
# ==========================
with col_vid:
    st.subheader("Video Analysis")
    if selected_event is not None:
        st.success(f"Outcome: {selected_event['type']}")
        try:
            st.video(selected_event["video"])
        except:
            st.error(f"Video not found: {selected_event['video']}")
    else:
        st.info("Select a marker on the pitch to load the video.")
