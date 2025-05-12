#!/usr/bin/env python3
import os
import json
import subprocess
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# Parámetros generales
timeout = 5      # segundos de espera por petición
retries = 3      # reintentos en caso de fallo
data_file = 'resultados.json'
predictions_xlsx = 'predicciones.xlsx'
survivors_csv = 'supervivientes.csv'

# Encabezados HTTP genéricos para scraping
headers_scrap = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/XX Safari/537.36'
    )
}

# Lista de partidos y URLs exactas
# Rellena aquí con la URL absoluta de cada enfrentamiento en Soccerway
partidos = [
    {
        'name': 'Real Madrid',
        'url_override': 'https://int.soccerway.com/matches/2025/05/11/spain/primera/futbol-club-barcelona/real-madrid-club-de-futbol/4367683/'
    },
    {
        'name': 'Barcelona',
        'url_override': 'https://int.soccerway.com/matches/2025/05/10/spain/primera/club-atletico-de-madrid/real-sociedad-de-futbol/4367682/'
    },
    {
        'name': 'Ponferradina',
        'url_override': 'https://int.soccerway.com/matches/2025/05/11/spain/segunda-b/real-sociedad-de-futbol-ii/sociedad-deportiva-ponferradina/4453956/'
    }
]


def obtener_resultado(url):
    """
    Realiza scraping en la URL completa proporcionada
y devuelve una tupla (goles_local, goles_visitante).
    """
    for intento in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers_scrap, timeout=timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 1) Intento con selectores específicos
            span_home = soup.select_one('div.score span.home')
            span_away = soup.select_one('div.score span.away')
            if span_home and span_away:
                return int(span_home.text.strip()), int(span_away.text.strip())

            # 2) Fallback con regex sobre el texto completo
            text = soup.get_text()
            m = re.search(r"(\d+)[-–](\d+)", text)
            if m:
                return int(m.group(1)), int(m.group(2))

            raise ValueError('Marcador no encontrado en la página')

        except Exception as e:
            print(f"[WARN] Intento {intento}/{retries} FALLIDO para {url}: {e}")
            time.sleep(1)

    print(f"[ERROR] No se pudo obtener resultado de {url}")
    return None


def convert_to_1X2(local, visitante):
    """
    Convierte un resultado de goles en 1/X/2.
    """
    if local > visitante:
        return '1'
    if local < visitante:
        return '2'
    return 'X'


def main():
    # Carga de resultados previos o creación de estructura
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            resultados = json.load(f)
    else:
        resultados = {}

    cambios = False

    # Procesar cada partido
    for p in partidos:
        name = p['name']
        url = p['url_override']
        res = obtener_resultado(url)
        if not res:
            continue
        local, visit = res
        # Uso de 1X2 para Ponferradina, goles para el resto
        if name.lower() == 'ponferradina':
            valor = convert_to_1X2(local, visit)
        else:
            valor = f"{local}-{visit}"

        if resultados.get(name) != valor:
            resultados[name] = valor
            cambios = True
            print(f"[UPDATE] {name}: {valor}")

    # Si hay cambios, volcar JSON, recalcular Excel y git push
    if cambios:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print("[OK] resultados.json actualizado.")

        # Recalcular supervivientes si existe predicciones.xlsx
        if os.path.exists(predictions_xlsx):
            df = pd.read_excel(predictions_xlsx)
            df_surv = df
            for name, val in resultados.items():
                df_surv = df_surv[df_surv[name] == val]
            df_surv.to_csv(survivors_csv, index=False, encoding='utf-8')
            print("[OK] supervivientes.csv generado.")

        # Versionado en Git
        subprocess.run(['git', 'add', data_file], check=False)
        subprocess.run(['git', 'commit', '-m', 'Actualización automática de resultados'], check=False)
        subprocess.run(['git', 'push'], check=False)
        print("[OK] cambios empujados.")
    else:
        print("[INFO] Sin cambios en resultados.")


if __name__ == '__main__':
    main()
