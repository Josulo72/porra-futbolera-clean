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
retries = 3      # número de reintentos en caso de fallo
data_file     = 'data/resultados.json'
predictions_xlsx = 'data/predicciones.xlsx'
survivors_csv    = 'data/supervivientes.csv'

# Encabezados HTTP genéricos para scraping
headers_scrap = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/XX Safari/537.36'
    )
}


def obtener_resultado(url_override, name_equipo):
    """
    Realiza scraping directo usando la URL absoluta en url_override
    y devuelve una tupla (goles_local, goles_visitante), o None si falla.
    """
    url = url_override  # usamos la URL completa que proporcionas
    for intento in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers_scrap, timeout=timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Intento con selectores específicos
            span_home = soup.select_one('div.score span.home')
            span_away = soup.select_one('div.score span.away')
            if span_home and span_away:
                return int(span_home.text.strip()), int(span_away.text.strip())
            # Fallback con regex en el texto completo
            texto = soup.get_text()
            m = re.search(r"(\d+)[-–](\d+)", texto)
            if m:
                return int(m.group(1)), int(m.group(2))
            # Si llegamos aquí, no encontramos marcador
            raise ValueError("Marcador no localizado en la página")
        except Exception as e:
            print(f"[WARN] {name_equipo} intento {intento}/{retries} FALLIDO en {url}: {e}")
            time.sleep(1)
    print(f"[ERROR] No se pudo obtener resultado de {name_equipo} en {url}")
    return None


def convert_to_1X2(local, visitante):
    """
    Convierte un marcador de goles en 1/X/2.
    """
    if local > visitante:
        return '1'
    if local < visitante:
        return '2'
    return 'X'


def main():
    # Cargar JSON de configuración y overrides
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    else:
        print(f"[ERROR] No existe '{data_file}'. Ejecuta primero la interfaz de control.")
        return

    cambios = False
    resultados = datos.get('resultados', {})
    overrides  = datos.get('overrides', {})

    # Iterar cada partido según claves en overrides
    for name, url in overrides.items():
        if not url:
            print(f"[WARN] No hay URL override para '{name}', se omite.")
            continue
        res = obtener_resultado(url, name)
        if not res:
            continue
        local, visit = res
        if name.lower() == 'ponferradina':
            valor = convert_to_1X2(local, visit)
        else:
            valor = f"{local}-{visit}"
        if resultados.get(name) != valor:
            resultados[name] = valor
            datos['resultados'][name] = valor
            cambios = True
            print(f"[UPDATE] {name}: {valor}")

    # Si hubo cambios, actualizar JSON, CSV de supervivientes y versionar en Git
    if cambios:
        # Guardar JSON actualizado
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        print("[OK] data/resultados.json actualizado.")

        # Recalcular supervivientes desde predicciones.xlsx
        if os.path.exists(predictions_xlsx):
            df = pd.read_excel(predictions_xlsx)
            df_surv = df.copy()
            for name, val in datos['resultados'].items():
                df_surv = df_surv[df_surv[name] == val]
            os.makedirs(os.path.dirname(survivors_csv), exist_ok=True)
            df_surv.to_csv(survivors_csv, index=False, encoding='utf-8')
            print("[OK] data/supervivientes.csv generado.")

        # Commit y push de todos los cambios
        subprocess.run(['git', 'add', '-A'], check=False)
        subprocess.run(['git', 'commit', '-m', 'Actualización automática de resultados'], check=False)
        subprocess.run(['git', 'push'], check=False)
        print("[OK] Cambios empujados a GitHub.")
    else:
        print("[INFO] Sin cambios en resultados.")

if __name__ == '__main__':
    main()
