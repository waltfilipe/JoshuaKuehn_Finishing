import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from streamlit_image_coordinates import streamlit_image_coordinates
from io import BytesIO
from PIL import Image
import numpy as np
from matplotlib.lines import Line2D

# ==========================
# Page Configuration
# ==========================
st.set_page_config(layout="wide", page_title="Interactive Shot Map")

st.title("⚽ Interactive Shot Map")
st.caption("Click on any marker on the pitch to analyze the shot details and view footage.")

# ==========================
# 1. DATA SETUP
# ==========================
@st.cache_data
def get_data():
    # Dados de finalização (Todas com vídeo)
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"],
        "video": [
            "videos/Fin 1.mp4", "videos/Fin 2.mp4", "videos/Fin 3.mp4", 
            "videos/Fin 4.mp4", "videos/Fin 5.mp4", "videos/Fin 6.mp4", "videos/Fin 7.mp4"
        ]
    }
    return pd.DataFrame(data)

df_shots = get_data()

# Lógica de Zonas para Estatísticas (Statsbomb Vertical: Central entre Y 26.6 e 53.3)
df_shots["zone"] = df_shots["y"].apply(lambda y: "CENTRAL" if 26.6 < y <= 53.3 else "LATERAL")

# ==========================
# 2. MAIN LAYOUT
# ==========================
col_map, col_vid = st.columns([1.2, 1])

with col_map:
    st.subheader("Interactive Pitch Map")
    
    # Setup do Campo (Cor Preta)
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#1a1a1a', 
        line_color='#c2c2c2'
    )
    fig, ax = pitch.draw(figsize=(10, 8))

    # Plotagem das finalizações
    for _, row in df_shots.iterrows():
        # Estilo por resultado
        if row["outcome"] == "Goal":
            marker, color, size = '*', '#EF476F', 500  # Estrela Rosa
        elif row["outcome"] == "On Target":
            marker, color, size = 'h', '#06D6A0', 380  # Hexágono Verde
        else:
            marker, color, size = 'o', '#FFD166', 320  # Círculo Amarelo

        pitch.scatter(
            row.x, row.y,
            s=size,
            marker=marker,
            c=color,
            edgecolors='white',
            linewidths=1.2,
            ax=ax,
            zorder=3
        )

    # Legenda
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='#EF476F', markersize=12, linestyle='None'),
        Line2D([0], [0], marker='h', color='w', label='On Target', markerfacecolor='#06D6A0', markersize=10, linestyle='None'),
        Line2D([0], [0], marker='o', color='w', label='Off Target', markerfacecolor='#FFD166', markersize=10, linestyle='None'),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.05), frameon=False, labelcolor='white')

    # Convert plot to image para capturar coordenadas
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches='tight', facecolor='#1a1a1a')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Widget de captura de clique
    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# 3. INTERACTION LOGIC (Mesma do Duel App)
# ==========================
selected_shot = None

if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]
    
    # Mapeia o clique do pixel para o tamanho real da imagem
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Inverte o Y para lógica do Matplotlib e transforma em coordenadas do Pitch
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Calcula distância euclidiana para encontrar a finalização mais próxima
    df_shots["dist"] = np.sqrt((df_shots["x"] - field_x)**2 + (df_shots["y"] - field_y)**2)
    
    # Raio de tolerância (ajustável)
    RADIUS = 4 
    candidates = df_shots[df_shots["dist"] < RADIUS]

    if not candidates.empty:
        selected_shot = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# 4. VIDEO & STATS
# ==========================
with col_vid:
    st.subheader("Shot Analysis")
    
    if selected_shot is not None:
        outcome = selected_shot['outcome']
        st.success(f"**Outcome:** {outcome} | X: {selected_shot['x']:.1f}, Y: {selected_shot['y']:.1f}")
        
        # Exibição do Vídeo
        try:
            st.video(selected_shot["video"])
        except:
            st.error(f"Video file not found: {selected_shot['video']}")
            
        # Métrica de distância
        dist_to_goal = np.sqrt((120 - selected_shot['x'])**2 + (40 - selected_shot['y'])**2)
        st.metric("Estimated Distance to Goal", f"{dist_to_goal:.1f} m")
    else:
        st.info("Select a marker on the pitch to load the video analysis.")

    st.divider()
    st.subheader("Performance by Zone")
    
    # Cálculos de estatísticas por zona
    s_col1, s_col2 = st.columns(2)
    for zone, col in zip(["CENTRAL", "LATERAL"], [s_col1, s_col2]):
        subset = df_shots[df_shots["zone"] == zone]
        total = len(subset)
        gols = len(subset[subset["outcome"] == "Goal"])
        no_alvo = len(subset[subset["outcome"].isin(["Goal", "On Target"])])
        taxa_alvo = (no_alvo / total * 100) if total > 0 else 0
        
        col.metric(f"{zone} Zone", f"{gols} Goals / {total} Shots", f"{taxa_alvo:.1f}% on target")

# ==========================
# 5. FOOTER SUMMARY
# ==========================
st.divider()
m1, m2, m3 = st.columns(3)
total_shots = len(df_shots)
total_goals = len(df_shots[df_shots["outcome"] == "Goal"])
m1.metric("Total Shots", total_shots)
m2.metric("Total Goals", total_goals)
m3.metric("Shot Conversion", f"{(total_goals/total_shots*100):.1f}%")
