# api_client/client.py

import os
import yaml
import requests

# Carga la configuración YAML desde config/default.yaml
_here = os.path.dirname(__file__)
_cfg_path = os.path.join(_here, os.pardir, "config", "default.yaml")
with open(_cfg_path, "r", encoding="utf-8") as f:
    _cfg = yaml.safe_load(f)

API_URL    = _cfg["api_base_url"]  # ya incluye /matches
AUTH_TOKEN = _cfg["auth_token"]
TIMEOUT    = _cfg.get("timeout", 10)

def fetch_jornada(num_jornada: int):
    """
    Recupera la lista de partidos de la jornada indicada desde Football-Data.org.
    Devuelve una lista de dicts con: local, visitante, goles_local, goles_visitante, fecha.
    """
    headers = {"X-Auth-Token": AUTH_TOKEN}
    params  = {"matchday": num_jornada}
    try:
        resp = requests.get(API_URL, headers=headers, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] al obtener jornada {num_jornada}: {e}")
        return []

    body = resp.json()
    resultados = []
    for m in body.get("matches", []):
        resultados.append({
            "local": m["homeTeam"]["name"],
            "visitante": m["awayTeam"]["name"],
            "goles_local": m["score"]["fullTime"]["home"],
            "goles_visitante": m["score"]["fullTime"]["away"],
            "fecha": m["utcDate"],
        })
    return resultados
# ========================
# Función: fetch_teams
# ========================
def fetch_teams() -> list[str]:
    """
    Recupera la lista de equipos de LaLiga (competición PD)
    desde Football-Data.org y devuelve una lista de nombres.
    """
    headers = {"X-Auth-Token": AUTH_TOKEN}
    # Reutiliza la misma base de API_URL, cambiando '/matches' por '/teams'
    base = API_URL.rsplit("/", 1)[0]
    url_teams = f"{base}/teams"
    try:
        resp = requests.get(url_teams, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] al obtener equipos de LaLiga: {e}")
        return []
    data = resp.json()
    return [team["name"] for team in data.get("teams", [])]

if __name__ == "__main__":
    print(fetch_jornada(1))
