import streamlit as st
import pandas as pd
import json
import os

# Configuración de la página
st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")

# Ocultar menú, footer y header de Streamlit
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Diccionario completo de slugs a (nombre legible, ruta del logo)
custom_teams = {
    # LaLiga
    "rayo-vallecano":                ("Rayo",             "logos/rayo.png"),
    "getafe-club-de-futbol":         ("Getafe",           "logos/getafe.png"),
    "deportivo-alaves":              ("Alavés",           "logos/alaves.png"),
    "club-atletico-de-madrid":       ("Atlético",         "logos/atletico.png"),
    "villarreal-club-de-futbol":     ("Villarreal",       "logos/villarreal.png"),
    "club-atletico-osasuna":         ("Osasuna",          "logos/osasuna.png"),
    "union-deportiva-las-palmas":    ("Las Palmas",       "logos/las_palmas.png"),
    "valencia-club-de-futbol":       ("Valencia",         "logos/valencia.png"),
    "real-valladolid-club-de-futbol": ("Real Valladolid", "logos/real_valladolid.png"),
    "futbol-club-barcelona":         ("Barcelona",        "logos/barcelona.png"),
    "real-madrid-club-de-futbol":    ("Real Madrid",      "logos/real_madrid.png"),
    "real-club-celta-de-vigo":       ("Celta",            "logos/celta.png"),
    "sevilla-futbol-club":           ("Sevilla",          "logos/sevilla.png"),
    "club-deportivo-leganes-sad":    ("Leganés",          "logos/leganes.png"),
    "reial-club-deportiu-espanyol":  ("Espanyol",         "logos/espanyol.png"),
    "real-betis":                    ("Betis",            "logos/betis.png"),
    "real-sociedad-de-futbol":       ("R. Sociedad",      "logos/real_sociedad.png"),
    "athletic-club":                 ("Athletic",         "logos/athletic.png"),
    "girona-fc":                     ("Girona",           "logos/girona.png"),
    "real-club-deportivo-mallorca":  ("Mallorca",         "logos/mallorca.png"),
    # Primera Federación
    "gimnastica-segoviana-club-de-futbol": ("G. Segoviana",     "logos/segoviana.png"),
    "real-sociedad-de-futbol-ii":          ("R. Sociedad B",    "logos/real_sociedad_b.png"),
    "sociedad-deportiva-ponferradina":     ("Ponferradina",     "logos/ponferradina.png"),
    "athletic-club-bilbao-ii":             ("Bilbao Athletic",  "logos/bilbao_athletic.png"),
    "arenteiro":                           ("CD Arenteiro",     "logos/arenteiro.png"),
    "zamora-cf":                           ("Zamora",           "logos/zamora.png"),
    "real-union-club-de-irun":             ("Real Unión",       "logos/real_union.png"),
    "sd-tarazona":                         ("Tarazona",         "logos/tarazona.png"),
    "ourense-cf":                          ("Ourense CF",       "logos/ourense.png"),
    "cultural-y-deportiva-leonesa":        ("Cultural",         "logos/cultural.png"),
    "barakaldo-club-de-futbol":            ("Barakaldo",        "logos/barakaldo.png"),
    "sd-amorebieta":                       ("SD Amorebieta",    "logos/amorebieta.png"),
    "unionistas-de-salamanca":             ("Unionistas CF",    "logos/unionistas.png"),
    "sestao-river-club":                   ("Sestao",           "logos/sestao.png"),
    "club-deportivo-lugo":                 ("Lugo",             "logos/lugo.png"),
    "futbol-club-barcelona-ii":            ("Barcelona B",      "logos/barcelona_b.png"),
    "fc-andorra":                          ("Andorra",          "logos/andorra.png"),
    "club-gimnastic-de-tarragona":         ("Gimnàstic",        "logos/gimnastic.png"),
    "real-club-celta-de-vigo-ii":          ("Celta B",          "logos/celta_b.png"),
    "ca-osasuna-ii":                       ("Osasuna B",        "logos/osasuna_b.png")
}
custom_teams.update({
    "Real Sociedad de Fútbol":    ("Real Sociedad de Fútbol",  "logos/sociedad.png"),
    "Villarreal CF":              ("Villarreal CF",            "logos/villarreal.png"),
    "Valencia CF":                ("Valencia CF",              "logos/valencia.png"),
    "Real Valladolid CF":         ("Real Valladolid CF",       "logos/real_valladolid.png"),
    "Deportivo Alavés":           ("Deportivo Alavés",         "logos/alaves.png"),
    "UD Las Palmas":              ("UD Las Palmas",            "logos/las_palmas.png"),
    "Girona FC":                  ("Girona FC",                "logos/girona.png"),
    "RC Celta de Vigo":           ("RC Celta de Vigo",         "logos/celta.png"),
    "Sevilla FC":                 ("Sevilla FC",               "logos/sevilla.png"),
    "CD Leganés":                 ("CD Leganés",               "logos/leganes.png"),
    "Athletic Club":              ("Athletic Club",            "logos/athletic.png"),
    "Club Atlético de Madrid":    ("Club Atlético de Madrid",  "logos/atletico.png"),
    "CA Osasuna":                 ("CA Osasuna",               "logos/osasuna.png"),
    "RCD Espanyol de Barcelona":  ("RCD Espanyol de Barcelona","logos/espanyol.png"),
    "FC Barcelona":               ("FC Barcelona",             "logos/barcelona.png"),
    "Getafe CF":                  ("Getafe CF",                "logos/getafe.png"),
    "Real Madrid CF":             ("Real Madrid CF",           "logos/real_madrid.png"),
    "Rayo Vallecano de Madrid":   ("Rayo Vallecano de Madrid", "logos/rayo.png"),
    "RCD Mallorca":               ("RCD Mallorca",             "logos/mallorca.png"),
    "Real Betis Balompié":        ("Real Betis Balompié",      "logos/betis.png"),
})

# Función para convertir un slug genérico en nombre legible

def slug_to_name(slug: str) -> str:
    return slug.replace('-', ' ').title()

# Carga de datos y renderizado de la app
try:
    with open("data/resultados.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    partidos = datos.get("partidos", {})      # Dict: clave -> "slug1 vs slug2"
    resultados = datos.get("resultados", {})  # Dict: clave -> marcador

    st.subheader("📋 Partidos de la jornada")
    if partidos:
        for team_key, partido_str in partidos.items():
            # Extraer slugs del string
            if "vs" in partido_str:
                local_slug, visit_slug = [s.strip() for s in partido_str.split("vs")]
                local_name, local_logo = custom_teams.get(local_slug, (slug_to_name(local_slug), None))
                visit_name, visit_logo = custom_teams.get(visit_slug, (slug_to_name(visit_slug), None))
            else:
                local_slug = partido_str.strip()
                local_name, local_logo = custom_teams.get(local_slug, (slug_to_name(local_slug), None))
                visit_name = visit_logo = None

            display = f"{local_name} vs {visit_name}" if visit_name else local_name
            score = resultados.get(team_key, "--")

            # Layout en dos columnas: escudos y texto/marcador
            cols = st.columns([1, 6])
            with cols[0]:
                if local_logo and os.path.exists(local_logo):
                    st.image(local_logo, width=30)
                if visit_logo and os.path.exists(visit_logo):
                    st.image(visit_logo, width=30)
            with cols[1]:
                st.markdown(
                    f"**⚽ {display}** → "
                    f"<span style='font-size:2em; color:green;'>{score}</span>",
                    unsafe_allow_html=True
                )
            st.write("---")
    else:
        st.info("No hay partidos programados.")

    # Sección de participantes vivos
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
    st.error("❌ data/resultados.json no encontrado.")
except json.JSONDecodeError:
    st.error("❌ El JSON de resultados está corrupto.")
except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
