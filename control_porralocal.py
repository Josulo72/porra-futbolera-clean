import tkinter as tk
from tkinter import filedialog, messagebox, LabelFrame, Label, Frame
from tkinter.ttk import Combobox, Entry
from tkcalendar import DateEntry
import json, os, shutil, pandas as pd, subprocess, threading
from datetime import datetime
import time
import re
import requests
from bs4 import BeautifulSoup
from api_client.client import fetch_jornada, fetch_teams 

# Función para convertir goles en 1/X/2
def formato_1X2(g_local: int, g_visit: int) -> str:
    if g_local > g_visit:
        return "1"
    if g_local < g_visit:
        return "2"
    return "X"

# ========================
# LIMPIEZA DE DATOS AL INICIO Y AL CIERRE
# ========================
def limpiar_data():
    if os.path.isdir("data"):
        shutil.rmtree("data")
    os.makedirs("data", exist_ok=True)

def on_closing():
    limpiar_data()
    root.destroy()

# -----------------------
# Equipos de LaLiga (dinámico con fallback)
# -----------------------
equipos_laliga = fetch_teams()
if not equipos_laliga:
    equipos_laliga = [
        'rayo-vallecano', 'getafe-club-de-futbol', 'deportivo-alaves',
        'club-atletico-de-madrid', 'villarreal-club-de-futbol', 'club-atletico-osasuna',
        'union-deportiva-las-palmas', 'valencia-club-de-futbol',
        'real-valladolid-club-de-futbol', 'futbol-club-barcelona',
        'real-madrid-club-de-futbol', 'real-club-celta-de-vigo',
        'sevilla-futbol-club', 'club-deportivo-leganes-sad',
        'reial-club-deportiu-espanyol', 'real-betis',
        'real-sociedad-de-futbol', 'athletic-club', 'girona-fc',
        'real-club-deportivo-mallorca'
    ]

equipos_primera_fed = [
    'gimnastica-segoviana-club-de-futbol', 'real-sociedad-de-futbol-ii',
    'sociedad-deportiva-ponferradina', 'athletic-club-bilbao-ii',
    'arenteiro', 'zamora-cf', 'real-union-club-de-irun',
    'sd-tarazona', 'ourense-cf', 'cultural-y-deportiva-leonesa',
    'barakaldo-club-de-futbol', 'sd-amorebieta',
    'unionistas-de-salamanca', 'sestao-river-club',
    'club-deportivo-lugo', 'futbol-club-barcelona-ii',
    'fc-andorra', 'club-gimnastic-de-tarragona',
    'real-club-celta-de-vigo-ii', 'ca-osasuna-ii'
]

# ========================
# FUNCIONES PRINCIPALES
# ========================
def guardar_partidos():
    override_rm = url_rm.get().strip()
    override_bar = url_bar.get().strip()
    override_ponf = url_ponf.get().strip()
    try:
        datos = {
            "partidos": {
                "Real Madrid": f"{tk_vars['rm_local'].get()} vs {tk_vars['rm_visit'].get()}",
                "Barcelona":   f"{tk_vars['bar_local'].get()} vs {tk_vars['bar_visit'].get()}",
                "Ponferradina":f"{tk_vars['ponf_local'].get()} vs {tk_vars['ponf_visit'].get()}"
            },
            "horarios": {
                "Real Madrid": {"fecha": fecha_rm.get(),  "hora": hora_rm.get()},
                "Barcelona":   {"fecha": fecha_bar.get(), "hora": hora_bar.get()},
                "Ponferradina":{"fecha": fecha_ponf.get(),"hora": hora_ponf.get()}
            },
            "resultados": {
                "Real Madrid": resultado_rm.get(),
                "Barcelona":   resultado_bar.get(),
                "Ponferradina":resultado_ponf.get()
            }
        }
        overrides = {}
        if override_rm:
            overrides["Real Madrid"] = override_rm
        if override_bar:
            overrides["Barcelona"]   = override_bar
        if override_ponf:
            overrides["Ponferradina"] = override_ponf
        if overrides:
            datos["overrides"] = overrides

        os.makedirs("data", exist_ok=True)
        with open("data/resultados.json","w",encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
        messagebox.showinfo("✅ Éxito","Datos guardados correctamente.")
    except Exception as e:
        messagebox.showerror("❌ Error al guardar", str(e))


def subir_excel():
    archivo = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx")])
    if archivo:
        try:
            os.makedirs("data", exist_ok=True)
            shutil.copy(archivo, "data/predicciones.xlsx")
            df = pd.read_excel("data/predicciones.xlsx")
            messagebox.showinfo("✅ Excel cargado", f"Archivo con {len(df)} registros.")
        except Exception as e:
            messagebox.showerror("❌ Error al cargar Excel", str(e))


def evaluar_porra():
    try:
        df = pd.read_excel("data/predicciones.xlsx")
        with open("data/resultados.json","r",encoding="utf-8") as f:
            datos = json.load(f)
        df_filtrado = df.copy()
        for partido, res in datos['resultados'].items():
            if res:
                df_filtrado = df_filtrado[df_filtrado[partido].astype(str) == res]
        df_filtrado.to_csv("data/supervivientes.csv", index=False)
        messagebox.showinfo("🎯 Evaluación", f"Supervivientes: {len(df_filtrado)}")
    except Exception as e:
        messagebox.showerror("❌ Error al evaluar porra", str(e))


def subir_a_github():
    """
    Añade al repositorio los archivos de datos que existan y los sube a GitHub.
    No intentará añadir archivos ignorados ni inexistentes.
    """
    try:
        # 1) Construir lista de archivos de datos válidos
        files_to_add = []
        if os.path.exists("data/resultados.json"):
            files_to_add.append("data/resultados.json")
        if os.path.exists("data/supervivientes.csv"):
            files_to_add.append("data/supervivientes.csv")

        # 2) Si no hay nada, informamos y salimos
        if not files_to_add:
            messagebox.showinfo("🚀 GitHub", "No hay archivos nuevos para subir.")
            return

        # 3) Hacemos git add
        subprocess.run(["git", "add"] + files_to_add, check=True)

        # 4) Comprobamos si hay staged changes
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
        if diff.returncode == 0:
            messagebox.showinfo("🚀 GitHub", "No hay cambios para commitear.")
            return

        # 5) Commit y push
        subprocess.run(["git", "commit", "-m", "Actualización automática desde GUI"], check=True)
        subprocess.run(["git", "push"], check=True)
        messagebox.showinfo("🚀 GitHub", "Archivos subidos correctamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("❌ Error en Git", str(e))

def scraping_result(url):
    try:
        resp = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        score = soup.find('div', class_='score')
        if score:
            h = score.find('span', class_='home')
            a = score.find('span', class_='away')
            if h and a:
                return int(h.text.strip()), int(a.text.strip())
        for text in soup.stripped_strings:
            m = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', text)
            if m:
                return int(m.group(1)), int(m.group(2))
    except:
        pass
    return None, None


def ejecutar_auto_resultados():
    status_var.set("📡 Iniciando monitor de resultados…")

    def poll_match(nombre, fecha_var, hora_var, url_var, lbl, convierte_1X2):
        # 1) API para LaLiga si no hay override
        url = url_var.get().strip()
        if not url and nombre in ("Real Madrid","Barcelona"):
            try:
                matches = fetch_jornada(1)
                for m in matches:
                    if m['local'] == nombre or m['visitante'] == nombre:
                        g_loc, g_vis = m['goles_local'], m['goles_visitante']
                        res = f"{g_loc}-{g_vis}"
                        break
                else:
                    raise ValueError("Partido no encontrado en API")
                with open("data/resultados.json","r+",encoding="utf-8") as f:
                    data = json.load(f)
                    data["resultados"][nombre] = res
                    f.seek(0); f.truncate(); json.dump(data, f, indent=4)
                evaluar_porra()
                subir_a_github()
                lbl.config(text=f"✅ {nombre} = {res}")
            except Exception:
                lbl.config(text=f"❌ {nombre}: fallo API")
            return
        # 2) override vacío para scraping Ponferradina
        if not url:
            lbl.config(text=f"⚠️ {nombre}: sin URL override, omito monitoreo")
            return

        # Esperar fin de partido
        try:
            dt = datetime.strptime(f"{fecha_var.get()} {hora_var.get()}", "%Y-%m-%d %H:%M")
            espera = (dt - datetime.now()).total_seconds()
            if espera > 0:
                lbl.config(text=f"⏳ {nombre} hasta {dt}")
                time.sleep(espera)
        except:
            pass

        # Hasta 4 intentos de scraping cada 15 min
        for intento in range(1, 5):
            g_loc, g_vis = scraping_result(url)
            if g_loc is not None:
                res = formato_1X2(g_loc, g_vis) if convierte_1X2 else f"{g_loc}-{g_vis}"
                with open("data/resultados.json","r+",encoding="utf-8") as f:
                    data = json.load(f)
                    data["resultados"][nombre] = res
                    f.seek(0); f.truncate(); json.dump(data, f, indent=4)
                evaluar_porra()
                try:
                    subir_a_github()
                except:
                    pass
                lbl.config(text=f"✅ {nombre} = {res}")
                return
            else:
                lbl.config(text=f"🔁 {nombre} intento {intento}/4")
                time.sleep(15 * 60)
        lbl.config(text=f"❌ {nombre} sin resultado tras 4 intentos")

    # Lanzar los hilos al pulsar el botón
    threading.Thread(target=poll_match, args=("Real Madrid", fecha_rm, hora_rm, url_rm, status_labels['rm'], False), daemon=True).start()
    threading.Thread(target=poll_match, args=("Barcelona",   fecha_bar, hora_bar, url_bar, status_labels['bar'], False), daemon=True).start()
    threading.Thread(target=poll_match, args=("Ponferradina",fecha_ponf, hora_ponf, url_ponf, status_labels['ponf'], True), daemon=True).start()

# ========================
# INTERFAZ GRÁFICA
# ========================
limpiar_data()
root = tk.Tk()
root.title("🎮 Porra Futbolera")
root.geometry("900x700")
root.protocol("WM_DELETE_WINDOW", on_closing)

font_label = ('Segoe UI', 14)
font_entry = ('Segoe UI', 12)
font_button = ('Segoe UI', 12, 'bold')

# Variables Tk
tk_vars = {key: tk.StringVar() for key in [
    'rm_local','rm_visit','fecha_rm','hora_rm','resultado_rm','url_rm',
    'bar_local','bar_visit','fecha_bar','hora_bar','resultado_bar','url_bar',
    'ponf_local','ponf_visit','fecha_ponf','hora_ponf','resultado_ponf','url_ponf'
]}

fecha_rm, hora_rm, resultado_rm, url_rm       = (tk_vars['fecha_rm'],    tk_vars['hora_rm'],    tk_vars['resultado_rm'],   tk_vars['url_rm'])
fecha_bar, hora_bar, resultado_bar, url_bar  = (tk_vars['fecha_bar'],    tk_vars['hora_bar'],  tk_vars['resultado_bar'],  tk_vars['url_bar'])
fecha_ponf, hora_ponf, resultado_ponf, url_ponf = (tk_vars['fecha_ponf'], tk_vars['hora_ponf'], tk_vars['resultado_ponf'], tk_vars['url_ponf'])

status_var = tk.StringVar()
Label(root, textvariable=status_var, font=('Segoe UI', 12), anchor='w').pack(fill='x', padx=30, pady=(10,0))

status_labels = {}

def crear_partido(parent, title, equipos, keys, suffix, bg_color):
    lf = LabelFrame(parent, text=title, font=('Segoe UI',16,'bold'), bg=bg_color, padx=10, pady=10)
    lf.pack(fill='x', padx=30, pady=15)
    frame_top = Frame(lf, bg=bg_color)
    frame_top.pack(fill='x', pady=5)
    Label(frame_top, text='Local', bg=bg_color, font=font_label).pack(side='left', padx=10)
    Combobox(frame_top, values=equipos, textvariable=tk_vars[keys[0]], width=30, font=font_entry).pack(side='left', padx=5, expand=True)
    Label(frame_top, text='Visitante', bg=bg_color, font=font_label).pack(side='left', padx=10)
    Combobox(frame_top, values=equipos, textvariable=tk_vars[keys[1]], width=30, font=font_entry).pack(side='left', padx=5, expand=True)
    frame_mid = Frame(lf, bg=bg_color)
    frame_mid.pack(fill='x', pady=5)
    Label(frame_mid, text='Fecha', bg=bg_color, font=font_label).pack(side='left', padx=10)
    DateEntry(frame_mid, textvariable=tk_vars[keys[2]], date_pattern='yyyy-mm-dd', font=font_entry, width=12).pack(side='left', padx=5)
    Label(frame_mid, text='Hora fin', bg=bg_color, font=font_label).pack(side='left', padx=10)
    Entry(frame_mid, textvariable=tk_vars[keys[3]], font=font_entry, width=12).pack(side='left', padx=5)
    frame_bot = Frame(lf, bg=bg_color)
    frame_bot.pack(fill='x', pady=5)
    Label(frame_bot, text='Resultado', bg=bg_color, font=font_label).pack(side='left', padx=10)
    Entry(frame_bot, textvariable=tk_vars[keys[4]], font=font_entry, width=12).pack(side='left', padx=5)
    Label(frame_bot, text='URL override', bg=bg_color, font=font_label).pack(side='left', padx=10)
    Entry(frame_bot, textvariable=tk_vars[f'url_{suffix}'], font=font_entry, width=40).pack(side='left', padx=5)
    lbl = Label(frame_bot, text='●', fg='orange', bg=bg_color, font=('Segoe UI',16))
    lbl.pack(side='right', padx=10)
    status_labels[suffix] = lbl

crear_partido(root, 'Partido 1', equipos_laliga, ['rm_local','rm_visit','fecha_rm','hora_rm','resultado_rm'], 'rm', '#FFFBF0')
crear_partido(root, 'Partido 2', equipos_laliga, ['bar_local','bar_visit','fecha_bar','hora_bar','resultado_bar'], 'bar', '#F0FFFB')
crear_partido(root, 'Partido 3', equipos_primera_fed, ['ponf_local','ponf_visit','fecha_ponf','hora_ponf','resultado_ponf'], 'ponf', '#F0F7FF')

def actualizar_semaforos():
    now = datetime.now()
    for suf, lbl in status_labels.items():
        try:
            dt = datetime.strptime(f"{tk_vars[f'fecha_{suf}'].get()} {tk_vars[f'hora_{suf}'].get()}", "%Y-%m-%d %H:%M")
            delta = (now - dt).total_seconds()
            color = 'orange' if delta < -600 else 'green' if delta <= 600 else 'red'
            lbl.config(fg=color)
        except:
            lbl.config(fg='gray')
    root.after(60000, actualizar_semaforos)

actualizar_semaforos()

# Botones finales
dialog_frame = Frame(root)
dialog_frame.pack(fill='x', padx=30, pady=20)
buttons = [
    ('💾 Guardar todo', guardar_partidos, '#e74c3c'),
    ('📥 Subir Excel', subir_excel, '#27ae60'),
    ('🎯 Evaluar porra', evaluar_porra, '#3498db'),
    ('🚀 Subir a GitHub', subir_a_github, '#f39c12'),
    ('📡 Consultar resultados', ejecutar_auto_resultados, '#9b59b6')
]
for text, cmd, color in buttons:
    btn = tk.Button(dialog_frame, text=text, command=cmd,
                    bg='white', fg=color,
                    highlightbackground=color, highlightthickness=2,
                    bd=0, font=font_button, padx=15, pady=8)
    btn.pack(side='left', expand=True, fill='x', padx=10)

root.mainloop()
