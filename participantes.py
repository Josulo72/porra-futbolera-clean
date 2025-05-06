import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        button[kind="header"] {display: none !important;}
        .st-emotion-cache-zq5wmm, .st-emotion-cache-1avcm0n, .css-1lsmgbg, .css-eczf16 {display: none !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Función para convertir “slugs” con guiones en nombres con espacios y mayúsculas
def format_team_name(slug: str) -> str:
    return slug.replace('-', ' ').title()

# Leer resultados y supervivientes
try:
    with open("data/resultados.json", "r") as f:
        datos = json.load(f)
    partidos = datos["partidos"]
    resultados = datos["resultados"]

    st.subheader("📋 Partidos de la jornada")
    # Recorremos todos los partidos para mostrar nombre formateado y marcador más grande
    for key, slug in partidos.items():
        nombre = format_team_name(slug)
        marcador = resultados.get(key, "")
        st.markdown(
            f"**⚽ {nombre}** → Resultado: "
            f"<span style='font-size:1.5em; color:green;'>{marcador}</span>",
            unsafe_allow_html=True
        )

    if os.path.exists("data/supervivientes.csv"):
        df = pd.read_csv("data/supervivientes.csv")

        st.subheader("🟢 Participantes que siguen vivos")

        if df.empty:
            st.error("😢 Ningún participante acertó los tres partidos.")
        else:
            st.success(f"🎉 ¡Quedan {len(df)} participantes en juego!")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no se han publicado resultados.")

except Exception as e:
    st.error("❌ No se pudieron cargar los datos. Asegúrate de que el encargado haya publicado los resultados.")
