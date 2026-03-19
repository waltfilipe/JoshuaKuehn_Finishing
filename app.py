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
st.caption("Markers with a **thick black border** contain video footage. Click them to play.")

# ==========================
# 1. DATA SETUP
# ==========================
@st.cache_data
def get_data():
    data = {
        "x": [93.08, 101.06, 97.24, 105.38, 111.70, 95.24, 109.37],
        "y": [43.99, 37.84, 54.46, 49.64, 41.83, 49.64, 45.15],
        "outcome": ["On Target", "Goal", "Off Target", "Off Target", "Off Target", "On Target", "On Target"],
        # Lista de vídeos (alguns como None para testar a transparência)
        "video": ["videos/Fin 1.mp4", "videos/Fin 2.mp4", None, "videos/Fin 4.mp4", None, "videos/Fin 6.mp4", "videos/Fin 7.mp4"]
    }
    return pd.DataFrame(data)

df_shots = get_data()

# Helper para estatísticas por zona
# No VerticalPitch (Statsbomb), o Y lateral vai de 0-80. Central é ~20-60.
df_shots["zone"] = df_shots["y"].apply(lambda y: "CENTRAL" if 20 < y <= 60 else "SIDE")

# ==========================
# 2. MAIN LAYOUT
# ==========================
col_map, col_vid = st.columns([1.2, 1])

with col_map:
    # Setup the Pitch
    pitch = VerticalPitch(
        half=True,
        pitch_type='statsbomb',
        pitch_color='#f8f8f8',
        line_color='#4a4a4a'
    )
    fig, ax = pitch.draw(figsize=(10, 8))

    # Plot each shot
    for _, row in df_shots.iterrows():
        # Definir estilo baseado no outcome
        if row["outcome"] == "Goal":
            marker, base_color, base_size = '*', '#EF476F', 500
        elif row["outcome"] == "On Target":
            marker, base_color, base_size = 'h', '#06D6A0', 380
        else:
            marker, base_color, base_size = 'o', '#FFD166', 320
        
        has_vid = row["video"] is not None
        
        # Lógica de transparência e borda (Igual ao mapa de duelos)
        if has_vid:
            alpha, lw, ec = 1.0, 3.0, 'black'
            z = 4
        else:
            alpha, lw, ec = 0.2, 1.0, base_color # Fica "fantasmagórico"
            z = 2

        pitch.scatter(
            row.x, row.y,
            s=base_size,
            marker=marker,
            facecolors=base_color,
            alpha=alpha,
            edgecolors=ec,
            linewidths=lw,
            ax=ax,
            zorder=z
        )

    # Legenda Customizada
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='#EF476F', markersize=12),
        Line2D([0], [0], marker='h', color='w', label='On Target', markerfacecolor='#06D6A0', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Off Target', markerfacecolor='#FFD166', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='With Video', markerfacecolor='none', markeredgecolor='black', markeredgewidth=2, markersize=12),
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.05), frameon=False)

    # Converter para imagem para o clique funcionar
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=120, bbox_inches='tight')
    buf.seek(0)
    img_obj = Image.open(buf)
    
    # Renderizar imagem interativa com largura fixa
    click = streamlit_image_coordinates(img_obj, width=700)

# ==========================
# 3. INTERACTION LOGIC
# ==========================
selected_shot = None

if click is not None:
    real_w, real_h = img_obj.size
    disp_w, disp_h = click["width"], click["height"]
    
    pixel_x = click["x"] * (real_w / disp_w)
    pixel_y = click["y"] * (real_h / disp_h)
    
    # Inverter Y para lógica do Matplotlib e transformar em coordenadas de campo
    mpl_pixel_y = real_h - pixel_y
    coords = ax.transData.inverted().transform((pixel_x, mpl_pixel_y))
    field_x, field_y = coords[0], coords[1]

    # Calcular distância (Euclidiana)
    df_shots["dist"] = np.sqrt((df_shots["x"] - field_x)**2 + (df_shots["y"] - field_y)**2)
    
    # Raio de tolerância para o clique
    RADIUS = 4 
    candidates = df_shots[df_shots["dist"] < RADIUS]

    if not candidates.empty:
        # Priorizar finalizações que têm vídeo no clique
        with_vid = candidates[candidates["video"].notnull()]
        if not with_vid.empty:
            selected_shot = with_vid.loc[with_vid["dist"].idxmin()]
        else:
            selected_shot = candidates.loc[candidates["dist"].idxmin()]

# ==========================
# 4. VIDEO & STATS (LATERAL)
# ==========================
with col_vid:
    st.subheader("Shot Analysis")
    
    if selected_shot is not None:
        outcome = selected_shot['outcome']
        st.success(f"**Shot Result:** {outcome}")
        
        if selected_shot["video"]:
            try:
                st.video(selected_shot["video"])
            except:
                st.error("Video file not found.")
        else:
            st.warning("No video available for this shot.")
            
        dist_to_goal = np.sqrt((120 - selected_shot['x'])**2 + (40 - selected_shot['y'])**2)
        st.metric("Distance to Goal", f"{dist_to_goal:.1f} m")
    else:
        st.info("Click a marker with a **black border** to watch the clip.")

    st.write("---")
    st.subheader("Efficiency by Zone")
    
    s1, s2 = st.columns(2)
    for zone, col in zip(["CENTRAL", "SIDE"], [s1, s2]):
        subset = df_shots[df_shots["zone"] == zone]
        total = len(subset)
        goals = len(subset[subset["outcome"] == "Goal"])
        acc = (len(subset[subset["outcome"] != "Off Target"]) / total * 100) if total > 0 else 0
        
        col.metric(
            label=f"{zone} SHOTS", 
            value=f"{goals} Goals / {total}", 
            delta=f"{acc:.1f}% Accuracy"
        )

# ==========================
# 5. GENERAL SUMMARY
# ==========================
st.write("---")
st.subheader("Game Summary")
total_shots = len(df_shots)
goals = len(df_shots[df_shots["outcome"] == "Goal"])
accuracy = (len(df_shots[df_shots["outcome"] != "Off Target"]) / total_shots * 100)

m1, m2, m3 = st.columns(3)
m1.metric("Total Shots", total_shots)
m2.metric("Total Goals", goals)
m3.metric("Overall Accuracy", f"{accuracy:.1f}%")
