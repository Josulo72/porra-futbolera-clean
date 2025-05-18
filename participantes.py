import streamlit as st
import pandas as pd
import json
import os
import requests
import pathlib  

# Directorio base del proyecto
BASE_DIR = pathlib.Path(__file__).parent

# Configuración general
st.set_page_config(page_title="Porra Futbolera", page_icon="⚽", layout="centered")

# Estilos: ocultar menú y detectar móvil
st.markdown(
    """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        @media only screen and (max-width: 600px) {
            html body { --is-mobile: 1; }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Para adaptar diseño si es móvil (estimación básica)
is_mobile = st.runtime.scriptrunner.is_running_with_streamlit and st._get_report_ctx().session_id
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

# Utilidad
slug_to_name = lambda slug: slug.replace('-', ' ').title()

try:
    with open(BASE_DIR / "data" / "resultados.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    partidos = datos.get("partidos", {})
    resultados = datos.get("resultados", {})

    st.subheader("📋 Partidos de la jornada")

    if partidos:
        for key, vs in partidos.items():
            if "vs" not in vs:
                continue
            local_slug, visit_slug = [s.strip() for s in vs.split("vs")]
            local_disp, local_logo = custom_teams.get(local_slug, (slug_to_name(local_slug), None))
            visit_disp, visit_logo = custom_teams.get(visit_slug, (slug_to_name(visit_slug), None))

            score_logic = resultados.get(key, '--')
            score_map = {'1': '2-1', 'X': '1-1', '2': '0-3'}
            score_vis = score_map.get(score_logic, '--')
            date_str = "17.05.2025 19:00"

            cols = st.columns([2, 4, 2])

            with cols[0]:
                if local_logo:
                    path_a = BASE_DIR / local_logo
                    if path_a.exists():
                        st.image(str(path_a), width=40 if is_mobile else 60)
                st.caption(local_disp)

            with cols[1]:
                st.markdown(f"<div style='text-align: center; font-size: 13px'>{date_str}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 36px'><strong>{score_vis}</strong></div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center;'>FINALIZADO</div>", unsafe_allow_html=True)

            with cols[2]:
                if visit_logo:
                    path_b = BASE_DIR / visit_logo
                    if path_b.exists():
                        st.image(str(path_b), width=40 if is_mobile else 60)
                st.caption(visit_disp)

            st.markdown("---")
    else:
        st.info("No hay partidos programados.")

    # Participantes vivos
    path_csv = BASE_DIR / "data" / "supervivientes.csv"
    if path_csv.exists():
        df = pd.read_csv(path_csv)
        st.subheader("🟢 Participantes que siguen vivos")
        if df.empty:
            st.error("😢 Ningún participante acertó los tres partidos.")
        else:
            st.success(f"🎉 ¡Quedan {len(df)} participantes en juego!")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no se han publicado resultados.")

except Exception as e:
    st.error(f"❌ Error al cargar datos: {e}")
