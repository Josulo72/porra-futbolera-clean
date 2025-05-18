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

# Diccionario de slugs a (nombre legible, logo local)
custom_teams = {
    # LaLiga
    "rayo-vallecano":                ("Rayo Vallecano",    "logos/rayo.png"),
    "getafe-club-de-futbol":         ("Getafe CF",         "logos/getafe.png"),
    "deportivo-alaves":              ("Deportivo Alavés",  "logos/alaves.png"),
    "club-atletico-de-madrid":       ("Atlético de Madrid","logos/atletico.png"),
    "villarreal-club-de-futbol":     ("Villarreal CF",     "logos/villarreal.png"),
    "club-atletico-osasuna":         ("Osasuna",           "logos/osasuna.png"),
    "union-deportiva-las-palmas":    ("UD Las Palmas",     "logos/las_palmas.png"),
    "valencia-club-de-futbol":       ("Valencia CF",       "logos/valencia.png"),
    "real-valladolid-club-de-futbol": ("Real Valladolid",  "logos/real_valladolid.png"),
    "futbol-club-barcelona":         ("FC Barcelona",      "logos/barcelona.png"),
    "real-madrid-club-de-futbol":    ("Real Madrid CF",    "logos/real_madrid.png"),
    "real-club-celta-de-vigo":       ("RC Celta de Vigo",  "logos/celta.png"),
    "sevilla-futbol-club":           ("Sevilla FC",        "logos/sevilla.png"),
    "club-deportivo-leganes-sad":    ("CD Leganés",        "logos/leganes.png"),
    "reial-club-deportiu-espanyol":  ("RCD Espanyol",      "logos/espanyol.png"),
    "real-betis":                    ("Real Betis",        "logos/betis.png"),
    "real-sociedad-de-futbol":       ("Real Sociedad",     "logos/sociedad.png"),
    "athletic-club":                 ("Athletic Club",     "logos/athletic.png"),
    "girona-fc":                     ("Girona FC",         "logos/girona.png"),
    "real-club-deportivo-mallorca":  ("RCD Mallorca",      "logos/mallorca.png"),
    # Primera RFEF
    "sociedad-deportiva-ponferradina": ("SD Ponferradina",  "logos/ponferradina.png"),
    "cultural-y-deportiva-leonesa":    ("Cultural Leonesa", "logos/cultural.png"),
}

# Función para pasador slug a nombre legible
def slug_to_name(slug: str) -> str:
    return slug.replace('-', ' ').title()

# Función para buscar crestUrl de forma flexible
def find_crest(name: str, crest_map: dict) -> str | None:
    low = name.lower()
    for team_name, url in crest_map.items():
        if team_name.lower() == low:
            return url
    for team_name, url in crest_map.items():
        tn = team_name.lower()
        if low in tn or tn in low:
            return url
    return None

# Cargamos logos desde API (crestUrl)
try:
    teams_url = API_URL.rsplit('/', 1)[0] + '/teams'
    resp = requests.get(teams_url, headers={'X-Auth-Token': AUTH_TOKEN}, timeout=TIMEOUT)
    resp.raise_for_status()
    crest_map = {t['name']: t.get('crestUrl') for t in resp.json().get('teams', [])}
except:
    crest_map = {}

# Renderizado de la app
st.title('📋 Partidos de la jornada')

try:
    with open('data/resultados.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)
except FileNotFoundError:
    st.error('❌ data/resultados.json no encontrado.')
    st.stop()
except json.JSONDecodeError:
    st.error('❌ El JSON de resultados está corrupto.')
    st.stop()

partidos = datos.get('partidos', {})
resultados = datos.get('resultados', {})

if partidos:
    for key, part in partidos.items():
        local_slug, visit_slug = [s.strip() for s in part.split('vs')] if 'vs' in part else (part, None)
        local_name, local_logo = custom_teams.get(local_slug, (slug_to_name(local_slug), None))
        visit_name, visit_logo = (None, None)
        if visit_slug:
            visit_name, visit_logo = custom_teams.get(visit_slug, (slug_to_name(visit_slug), None))

        # Intento con crestUrl
        crest = find_crest(local_name, crest_map)
        if crest:
            local_logo = crest
        crest2 = find_crest(visit_name or '', crest_map)
        if crest2:
            visit_logo = crest2

        score = resultados.get(key, '--')
        cols = st.columns([0.5, 0.5, 8])
        with cols[0]:
            if local_logo:
                st.image(local_logo, width=30)
        with cols[1]:
            if visit_logo:
                st.image(visit_logo, width=30)
        with cols[2]:
            disp = f"{local_name} vs {visit_name}" if visit_name else local_name
            st.markdown(f"**⚽ {disp}** → <span style='font-size:2em; color:green;'>{score}</span>", unsafe_allow_html=True)
        st.write('---')
else:
    st.info('No hay partidos programados.')

st.title('🟢 Participantes que siguen vivos')

csv_path = 'data/supervivientes.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    # Eliminar índice y resetear
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    df = df.reset_index(drop=True)

    if df.empty:
        st.error('😢 Ningún participante acertó los tres resultados.')
    else:
        st.success(f'🎉 ¡Quedan {len(df)} participantes en juego!')
        st.dataframe(df, use_container_width=True)
else:
    st.info('Aún no se han publicado resultados.')
