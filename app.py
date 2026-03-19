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
st.caption("Click on the icons on the pitch to play the corresponding shot video.")

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
    if outcome == "GOAL":
        return '*', '#EF476F', 250
    if outcome == "ON TARGET":
        return 'h', '#06D6A0', 200
    return 'o', '#FFD166', 180

# ==========================
# Layout
# ==========================
col_map, col_vid = st.columns([1, 1])

# ==========================
# Pitch + Plot
# ==========================
with col_map:
    st.subheader("Interactive Pitch Map")

    pitch = Pitch(
        pitch_type='statsbomb',
        pitch_color='#1a1a1a',
        line_color='#c2c2c2'
    )

    # CORREÇÃO 1: Ajuste fino do layout da figura para evitar margens fantasmas
    fig, ax = pitch.draw(figsize=(8, 6))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1) # Remove bordas brancas

    for _, row in df.iterrows():
        marker, color, size = get_style(row["type"])
        pitch.scatter(
            row.x,
            row.y,
            marker=marker,
            s=size,
            color=color,
            edgecolors='white',
            linewidths=1,
            ax=ax,
            zorder=3
        )

    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal',
               markerfacecolor='#EF476F', markersize=12, linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='On Target',
               markerfacecolor='#06D6A0', markersize=10, linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Off Target',
               markerfacecolor='#FFD166', markersize=10, linestyle='None'),
    ]

    ax.legend(
        handles=legend_elements,
        loc='upper left',
        frameon=True,
        fontsize=10,
        facecolor='white',
        edgecolor='black'
    )

    # Converter imagem para clique
    buf = BytesIO()
    # CORREÇÃO 2: Salvar sem bbox_inches='tight' para manter a proporção dos eixos fixa
    plt.savefig(
        buf,
        format="png",
        dpi=100,
        facecolor='#1a1a1a'
    )
    buf.seek(0)

    img_obj = Image.open(buf)
    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# Click Logic
# ==========================
selected_event = None

if click is not None:
    # CORREÇÃO 3: Lógica de mapeamento simplificada e precisa
    # Calculamos a posição relativa (0 a 1) do clique e multiplicamos pelas dimensões do Statsbomb (120x80)
    
    # O componente 'click' já retorna as coordenadas baseadas no 'width' passado (700px)
    # Precisamos saber a altura proporcional que o Streamlit exibiu:
    img_display_ratio = 700 / img_obj.width
    display_height = img_obj.height * img_display_ratio

    # Converter clique para escala 0-1
    rel_x = click["x"] / 700
    rel_y = click["y"] / display_height

    # Converter para coordenadas Statsbomb (X: 0-120, Y: 0-80)
    # Nota: No Matplotlib o Y 0 é embaixo, mas na imagem o clique Y 0 é no topo.
    field_x = rel_x * 120
    field_y = rel_y * 80

    # Cálculo de distância euclidiana simples (sem ajustes arbitrários)
    df["dist"] = np.sqrt((df["x"] - field_x)**2 + (df["y"] - field_y)**2)

    # Raio de tolerância (ajuste conforme necessário, 3 a 5 costuma ser ideal)
    RADIUS = 3 
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
