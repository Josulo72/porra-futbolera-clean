import os
import base64
import json

import streamlit as st
import pandas as pd
from streamlit.components.v1 import html as st_html

# Configuración de página y estilo
st.set_page_config(
    page_title="Porra Futbolera",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Inyectamos Bootstrap una sola vez
st.markdown("""
<link
  rel="stylesheet"
  href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
/>
""", unsafe_allow_html=True)

# Función para convertir un logo local en data URI base64
def img_to_data_uri(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    # detectamos extensión para la cabecera
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    return f"data:image/{ext};base64,{b64}"
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

# Función auxiliar para nombre legible
def slug_to_name(slug: str) -> str:
    if slug in custom_teams:
        return custom_teams[slug][0]
    parts = slug.replace("-", " ").split()
    return " ".join(p.capitalize() for p in parts)

# Carga de datos de resultados
try:
    with open("data/resultados.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    partidos   = data.get("partidos", {})
    resultados = data.get("resultados", {})
    fechas     = data.get("fechas", {})
except Exception:
    st.error("❌ Error al leer 'data/resultados.json'. Revisa que exista y sea JSON válido.")
    partidos, resultados, fechas = {}, {}, {}

# Renderizado de partidos
if partidos:
    for key, enfrent in partidos.items():
        try:
            local_slug, visitante_slug = enfrent.split(" vs ")
        except ValueError:
            continue

        nombre_local, logo_local_path = custom_teams.get(local_slug, (slug_to_name(local_slug), ""))
        nombre_visitante, logo_visitante_path = custom_teams.get(visitante_slug, (slug_to_name(visitante_slug), ""))

        # Convertimos a data URIs
        logo_local_uri     = img_to_data_uri(logo_local_path)
        logo_visitante_uri = img_to_data_uri(logo_visitante_path)
        marcador           = resultados.get(key, "-")
        fecha              = fechas.get(key, "")

        partido_html = f"""
        <div class="container my-4 p-3 border rounded">
          <div class="row text-center align-items-center">
            <div class="col-4 col-md-3">
              <img src="{logo_local_uri}" class="img-fluid" style="max-height:80px;" alt="{nombre_local}">
              <div class="mt-2">{nombre_local}</div>
            </div>
            <div class="col-4 col-md-6">
              <div class="h1">{marcador}</div>
              <small class="text-muted">{fecha}</small>
              <div>FINALIZADO</div>
            </div>
            <div class="col-4 col-md-3">
              <img src="{logo_visitante_uri}" class="img-fluid" style="max-height:80px;" alt="{nombre_visitante}">
              <div class="mt-2">{nombre_visitante}</div>
            </div>
          </div>
        </div>
        """
        st_html(partido_html, height=200)
else:
    st.info("⚠️ No hay partidos programados.")

# Sección de participantes “vivos”
csv_path = "data/supervivientes.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    if df.empty:
        st.error("😢 Ningún participante acertó en esta jornada.")
    else:
        st.write(f"🎉 {len(df)} participantes siguen vivos:")
        st.dataframe(df)
else:
    st.info("ℹ️ Aún no se han publicado los resultados de supervivientes.")