import streamlit as st
import pandas as pd
import json
import os
import requests
from api_client.client import AUTH_TOKEN, API_URL, TIMEOUT

# Configuración de la página
st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")

# Hacer la tabla desplazable horizontalmente en móviles
st.markdown(
    """
    <style>
      div[data-testid="stDataFrame"] {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
      }
    </style>
    """, unsafe_allow_html=True
)

# Ocultar menú, footer y header de Streamlit
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Diccionario de slugs a (nombre, logo local)
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
    "real-valladolid-club-de-futbol": ("Real Valladolid","logos/real_valladolid.png"),
    "futbol-club-barcelona":         ("Barcelona",        "logos/barcelona.png"),
    "real-madrid-club-de-futbol":    ("Real Madrid CF",   "logos/real_madrid.png"),
    "real-club-celta-de-vigo":       ("Celta",            "logos/celta.png"),
    "sevilla-futbol-club":           ("Sevilla FC",       "logos/sevilla.png"),
    "club-deportivo-leganes-sad":    ("Leganés",          "logos/leganes.png"),
    "reial-club-deportiu-espanyol":  ("Espanyol",         "logos/espanyol.png"),
    "real-betis":                    ("Real Betis",       "logos/betis.png"),
    "real-sociedad-de-futbol":       ("Real Sociedad",    "logos/sociedad.png"),
    "athletic-club":                 ("Athletic Club",    "logos/athletic.png"),
    "girona-fc":                     ("Girona FC",        "logos/girona.png"),
    "real-club-deportivo-mallorca":  ("Mallorca",         "logos/mallorca.png"),
    # Primera RFEF
    "sociedad-deportiva-ponferradina": ("Ponferradina",   "logos/ponferradina.png"),
    "cultural-y-deportiva-leonesa":    ("Cultural Leonesa","logos/cultural.png"),
}

# Función para convertir slug a nombre legible
def slug_to_name(slug: str) -> str:
    return slug.replace('-', ' ').title()

# Intentar cargar logos vía API de Football-Data
try:
    teams_url = API_URL.rsplit("/", 1)[0] + "/teams"
    resp = requests.get(teams_url, headers={"X-Auth-Token": AUTH_TOKEN}, timeout=TIMEOUT)
    resp.raise_for_status()
    data_teams = resp.json().get("teams", [])
    crest_map = {team["name"]: team.get("crestUrl") for team in data_teams}
except:
    crest_map = {}

# Carga de datos y renderizado
def main():
    st.subheader("📋 Partidos de la jornada")
    try:
        with open("data/resultados.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
    except FileNotFoundError:
        st.error("❌ data/resultados.json no encontrado.")
        return
    except json.JSONDecodeError:
        st.error("❌ El JSON de resultados está corrupto.")
        return

    partidos = datos.get("partidos", {})
    resultados = datos.get("resultados", {})

    if partidos:
        for key, partido_str in partidos.items():
            if "vs" in partido_str:
                local_slug, visit_slug = [s.strip() for s in partido_str.split("vs")]
            else:
                local_slug, visit_slug = partido_str.strip(), None

            local_name, local_logo = custom_teams.get(local_slug, (slug_to_name(local_slug), None))
            visit_name, visit_logo = (None, None)
            if visit_slug:
                visit_name, visit_logo = custom_teams.get(visit_slug, (slug_to_name(visit_slug), None))

            # Sustituir por crestUrl si coincide el nombre exacto
            if local_name in crest_map:
                local_logo = crest_map[local_name]
            if visit_name in crest_map:
                visit_logo = crest_map[visit_name]

            score = resultados.get(key, "--")
            cols = st.columns([1, 6])
            with cols[0]:
                if local_logo:
                    st.image(local_logo, width=30)
                if visit_logo:
                    st.image(visit_logo, width=30)
            with cols[1]:
                display = f"{local_name} vs {visit_name}" if visit_name else local_name
                st.markdown(f"**⚽ {display}** → <span style='font-size:2em; color:green;'>{score}</span>", unsafe_allow_html=True)
            st.write("---")
    else:
        st.info("No hay partidos programados.")

    # Sección participantes
    csv_path = "data/supervivientes.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Eliminar columna índice de Streamlit
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])
        # Resetear índice para que no muestre numeración
        df = df.reset_index(drop=True)

        st.subheader("🟢 Participantes que siguen vivos")
        if df.empty:
            st.error("😢 Ningún participante acertó los tres partidos.")
        else:
            st.success(f"🎉 ¡Quedan {len(df)} participantes en juego!")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no se han publicado resultados.")

if __name__ == '__main__':
    main()
