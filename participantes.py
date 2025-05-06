import streamlit as st
import pandas as pd
import json
import os

# Configuración de página
st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")

# Ocultar elementos por defecto
hide = """
<style>
  #MainMenu, footer, header {visibility: hidden;}
</style>
"""
st.markdown(hide, unsafe_allow_html=True)

# Mapeo de slugs a (nombre limpio, ruta logo)
custom_teams = {
    "futbol-club-barcelona":       ("Barcelona",      "logos/barcelona.png"),
    "real-madrid-club-de-futbol":  ("Real Madrid",    "logos/real_madrid.png"),
    "club-atletico-de-madrid":     ("Atlético",       "logos/atletico.png"),
    "athletic-club":               ("Athletic",       "logos/athletic.png"),
    "villarreal-cf":               ("Villarreal",     "logos/villarreal.png"),
    "real-betis-balompie":         ("Betis",          "logos/betis.png"),
    "real-club-deportivo-celta-de-vigo": ("Celta",    "logos/celta.png"),
    "rayo-vallecano-de-madrid":    ("Rayo",           "logos/rayo.png"),
    "club-atletico-osasuna":       ("Osasuna",        "logos/osasuna.png"),
    "real-club-deportivo-mallorca": ("Mallorca",      "logos/mallorca.png"),
    "real-sociedad-de-futbol":     ("R. Sociedad",    "logos/real_sociedad.png"),
    "valencia-cf":                 ("Valencia",       "logos/valencia.png"),
    "getafe-cf":                   ("Getafe",         "logos/getafe.png"),
    "reial-club-deportiu-espanyol": ("Espanyol",      "logos/espanyol.png"),
    "girona-fc":                   ("Girona",         "logos/girona.png"),
    "sevilla-fc":                  ("Sevilla",        "logos/sevilla.png"),
    "deportivo-alaves":            ("Alavés",         "logos/alaves.png"),
    "union-deportiva-las-palmas":  ("Las Palmas",     "logos/las_palmas.png"),
    "club-deportivo-leganes":      ("Leganés",        "logos/leganes.png"),
    "real-valladolid-cf":          ("Real Valladolid","logos/real_valladolid.png"),
    # Primera Federación
    "cultural-y-deportiva-leonesa": ("Cultural",      "logos/cultural.png"),
    "ponferradina":                ("Ponferradina",   "logos/ponferradina.png"),
    "fc-andorra":                  ("Andorra",        "logos/andorra.png"),
    "real-sociedad-b":             ("R. Sociedad B",  "logos/real_sociedad_b.png"),
    "gimnastic-de-tarragona":      ("Gimnàstic",      "logos/gimnastic.png"),
    "bilbao-athletic":             ("Bilbao Athletic","logos/bilbao_athletic.png"),
    "celta-de-vigo-b":             ("Celta B",        "logos/celta_b.png"),
    "ourense-cf":                  ("Ourense CF",     "logos/ourense.png"),
    "zamora-cf":                   ("Zamora",         "logos/zamora.png"),
    "barakaldo-cf":                ("Barakaldo",      "logos/barakaldo.png"),
    "club-deportivo-arenteiro":    ("CD Arenteiro",   "logos/arenteiro.png"),
    "cd-tarazona":                 ("Tarazona",       "logos/tarazona.png"),
    "real-union":                  ("Real Unión",     "logos/real_union.png"),
    "cd-lugo":                     ("Lugo",           "logos/lugo.png"),
    "unionistas-cf":               ("Unionistas CF",  "logos/unionistas.png"),
    "sestao-river":                ("Sestao",         "logos/sestao.png"),
    "osasuna-b":                   ("Osasuna B",      "logos/osasuna_b.png"),
    "fc-barcelona-b":              ("Barcelona B",    "logos/barcelona_b.png"),
    "gimnastic-segoviana":         ("G. Segoviana",   "logos/segoviana.png"),
    "sd-amorebieta":               ("SD Amorebieta",  "logos/amorebieta.png")
}

# Función auxiliar para formatear slugs perdidos
def slug_to_name(slug: str) -> str:
    return slug.replace('-', ' ').title()

# Carga de datos
try:
    with open("data/resultados.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    partidos = datos.get("partidos", {})      # Dict: nombre_equipo -> "slug1 vs slug2"
    resultados = datos.get("resultados", {})  # Dict: nombre_equipo -> marcador

    st.subheader("📋 Partidos de la jornada")
    if partidos:
        for team_key, partido_str in partidos.items():
            # Partido_str: "slug_local vs slug_visit"
            if 'vs' in partido_str:
                local_slug, visit_slug = [s.strip() for s in partido_str.split('vs')]
                local_name, local_logo = custom_teams.get(local_slug, (slug_to_name(local_slug), None))
                visit_name, visit_logo = custom_teams.get(visit_slug, (slug_to_name(visit_slug), None))
                display = f"{local_name} vs {visit_name}"
            else:
                # Fallback si no contiene 'vs'
                display = slug_to_name(partido_str)
                local_logo = visit_logo = None
            # Marcador (o placeholder)
            score = resultados.get(team_key, "--")
            # Mostrar con escudos si existen
            cols = st.columns([1, 5])
            # Columna de logos
            with cols[0]:
                if local_logo and os.path.exists(local_logo):
                    st.image(local_logo, width=30)
                if visit_logo and os.path.exists(visit_logo):
                    st.image(visit_logo, width=30)
            # Columna de texto y marcador
            with cols[1]:
                st.markdown(
                    f"**⚽ {display}** → "
                    f"<span style='font-size:2em; color:green;'>{score}</span>",
                    unsafe_allow_html=True
                )
            st.write("---") (o placeholder)
            score = resultados.get(team_key, "--")
            # Mostrar
            st.markdown(
                f"**⚽ {display}** → "
                f"<span style='font-size:2em; color:green;'>{score}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("No hay partidos programados.")

    # Supervivientes
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

except FileNotFoundError:
    st.error("❌ data/resultados.json no encontrado. Ejecuta primero el control de resultados.")
except json.JSONDecodeError:
    st.error("❌ El JSON de resultados está corrupto.")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
