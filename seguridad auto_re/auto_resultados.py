import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
import subprocess
import re

# ========================
# Headers para scraping
# ========================
HEADERS_SCRAP = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

SLUG_OVERRIDES = {
    "Gimnástica Segoviana":     "gimnastica-segoviana",
    "Real Sociedad B":           "real-sociedad-b",
    "Ponferradina":              "sociedad-deportiva-ponferradina",
    "Athletic Club II":          "athletic-club-bilbao-ii",
    "Arenteiro":                 "cd-arenteiro",
    "Zamora":                    "zamora",
    "Real Unión":                "real-union",
    "Tarazona":                  "tarazona",
    "Ourense CF":                "ourense-cf",
    "Cultural Leonesa":          "cultural-leonesa",
    "Barakaldo":                 "barakaldo",
    "Amorebieta":                "sd-amorebieta",
    "Unionistas de Salamanca":   "unionistas-de-salamanca",
    "Sestao River":              "sestao-river",
    "Lugo":                      "lugo",
    "Barcelona II":              "barcelona-b",
    "FC Andorra":                "fc-andorra",
    "Gimnàstic Tarragona":       "gimnastic-tarragona",
    "Celta de Vigo II":          "celta-vigo-b",
    "Osasuna II":                "osasuna-b"
}

# ========================
# Función de logging de estado
# ========================
def escribir_estado(texto):
    try:
        with open("data/estado.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} - {texto}\n")
    except Exception as e:
        print("Error escribiendo en estado.txt:", e)

# ========================
# Cargar datos iniciales
# ========================
with open("data/resultados.json", "r", encoding="utf-8") as f:
    datos = json.load(f)
partidos = datos.get("partidos", {})
horarios = datos.get("horarios", {})

# ========================
# Configuración API-Football
# ========================
APIFOOTBALL_HOST = "v3.football.api-sport.io"
APIFOOTBALL_KEY  = "c7b81f5f238635a30b5526d452332393"

# ========================
# Helper: convertir goles a 1/X/2
# ========================
import re

def formato_1X2(g_local, g_visit):
    """
    Convierte un marcador en formato goles a '1' si gana local,
    '2' si gana visitante o 'X' si empata.
    """
    if g_local > g_visit:
        return "1"
    if g_local < g_visit:
        return "2"
    return "X"

def slugify(name):
    """
    Genera un 'slug' a partir de un nombre, para encajar en las URLs de Soccerway.
    - Minusculas, quita tildes y eñes.
    - Reemplaza espacios y puntos por guiones.
    - Elimina caracteres no alfanuméricos ni guiones.
    """
    s = name.lower()
    # sustituye acentos y eñes
    acc = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ñ':'n'}
    for k, v in acc.items():
        s = s.replace(k, v)
    # reemplaza espacios y '.' por guiones
    s = re.sub(r"[.\s]+", "-", s)
    # elimina cualquier caracter que no sea letra, número o guión
    s = re.sub(r"[^a-z0-9\-]", "", s)
    return s


# ========================
# Scraping dinámico para Ponferradina
# ========================
def obtener_resultado_scraping():
    clave = "Ponferradina"
    partido_str = partidos.get(clave, "")
    fecha = horarios.get(clave, {}).get("fecha", "")
    try:
        local, visitante = [p.strip() for p in partido_str.split("vs")]
    except:
        escribir_estado(f"⚠️ Formato partido inválido: {partido_str}")
        return None

    slug_local = SLUG_OVERRIDES.get(local, slugify(local))
    slug_vis   = SLUG_OVERRIDES.get(visitante, slugify(visitante))
    fecha_url  = fecha.replace('-', '/')
    base = (
        f"https://es.soccerway.com/matches/{fecha_url}/"
        f"spain/segunda-b/{slug_local}/{slug_vis}/"
    )
    escribir_estado(f"🔍 Buscando URL partido: {base}")

    try:
        # Primera petición a la página base
        resp = requests.get(base, headers=HEADERS_SCRAP, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Encontrar el enlace al partido con ID
        link = soup.find(
            'a',
            href=re.compile(
                rf"/matches/{re.escape(fecha_url)}/spain/segunda-b/"
                rf"{slug_local}/{slug_vis}/\d+/"
            )
        )
        if not link:
            escribir_estado("❌ No se encontró enlace de partido en la página")
            return None

        full_url = "https://es.soccerway.com" + link['href']
        escribir_estado(f"🔗 URL final de scraping: {full_url}")

        # Segunda petición a la página del partido concreto
        r2 = requests.get(full_url, headers=HEADERS_SCRAP, timeout=10)
        r2.raise_for_status()
        s2 = BeautifulSoup(r2.text, "html.parser")

        home = s2.find("span", class_="score-home")
        away = s2.find("span", class_="score-away")
        if home and away:
            g_local = int(home.text.strip())
            g_visit = int(away.text.strip())
            escribir_estado(f"✅ Scraping: {g_local}-{g_visit}")
            return {"goles_local": g_local, "goles_visitante": g_visit}

    except Exception as e:
        escribir_estado(f"❌ Error scraping: {e}")

    return None

# ========================
# Polling de resultados
# ========================
# Usamos scraping vía override para Real Madrid, Barcelona y Ponferradina
override_map = datos.get("overrides", {})
any_updated = False

for clave in ["Real Madrid", "Barcelona", "Ponferradina"]:
    url = override_map.get(clave, "").strip()
    if not url:
        escribir_estado(f"❌ No hay URL de override para {clave}")
        continue

    escribir_estado(f"🔄 Override manual detectado para {clave}, ignorando fecha/hora")
    try:
        r2 = requests.get(url, headers=HEADERS_SCRAP, timeout=10)
        r2.raise_for_status()
        s2 = BeautifulSoup(r2.text, "html.parser")

        # 1) Intento con div.score > span.home/.away
        g_local = g_visit = None
        score_div = s2.find("div", class_="score")
        if score_div:
            home = score_div.find("span", class_="home")
            away = score_div.find("span", class_="away")
            if home and away:
                g_local = int(home.text.strip())
                g_visit = int(away.text.strip())

        # 2) Fallback regex si no se obtuvo con el div
        if g_local is None or g_visit is None:
            for text in s2.stripped_strings:
                if '-' in text:
                    m = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', text)
                    if m:
                        g_local, g_visit = map(int, m.groups())
                        break

        # 3) Si sigue sin datos, lo reportamos
        if g_local is None or g_visit is None:
            escribir_estado(f"❌ No se pudo parsear el marcador de {clave}")
            continue

        escribir_estado(f"✅ Scraping fijo {clave}: {g_local}-{g_visit}")

        # 4) Guardamos distinto según el partido
        if clave == "Ponferradina":
            resultado = formato_1X2(g_local, g_visit)
        else:
            resultado = f"{g_local}-{g_visit}"

        datos["resultados"][clave] = resultado
        escribir_estado(f"💾 Guardado: {clave} = {resultado}")
        any_updated = True

    except Exception as e:
        escribir_estado(f"❌ Error scraping {clave}: {e}")

# Si al menos un partido actualizó resultado, volcamos JSON y reevaluamos
if any_updated:
    os.makedirs("data", exist_ok=True)
    with open("data/resultados.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)
    escribir_estado("🔄 JSON resultados actualizado")

    # Reevaluar porra y volver a escribir CSV
    if os.path.exists("data/predicciones.xlsx"):
        df = pd.read_excel("data/predicciones.xlsx")
        df_fil = df.copy()
        for partido, res in datos["resultados"].items():
            if res:
                df_fil = df_fil[df_fil[partido].astype(str) == res]
        df_fil.to_csv("data/supervivientes.csv", index=False)
        escribir_estado(f"🎯 Supervivientes: {len(df_fil)}")

    # Subir a GitHub
    try:
        subprocess.run(
            ["git", "add", "data/resultados.json", "data/supervivientes.csv"],
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Actualización automática resultados"],
            check=True
        )
        subprocess.run(["git", "push"], check=True)
        escribir_estado("🚀 Cambios subidos a GitHub")
    except subprocess.CalledProcessError as e:
        escribir_estado(f"❌ Error Git: {e}")
else:
    escribir_estado("❌ Ningún resultado se pudo actualizar")
