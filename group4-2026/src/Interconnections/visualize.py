# =============================================================
# visualize.py
# Módulo de visualización de resultados
# Grupo 4 — Intercambios Internacionales
# =============================================================
# Genera 5 gráficas PNG a partir de los CSVs producidos por
# analysis.py. Los archivos se guardan en figures/.
#
# Gráficas 1–3: este archivo
# Gráficas 4–5: visualize_parte2.py (rama del compañero)
#
# Orden de ejecución:
#   1. extract.py
#   2. clean.py
#   3. analysis.py
#   4. visualize.py  ← este archivo
#      visualize_parte2.py (complementario)
# =============================================================

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# -------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -------------------------------------------------------------

CARPETA_RESULTADOS = os.path.join("data", "processed", "resultados")
CARPETA_PROCESSED  = os.path.join("data", "processed")
CARPETA_FIGURAS    = "figures"

os.makedirs(CARPETA_FIGURAS, exist_ok=True)

# Colores del proyecto (uno por país)
COLOR_ES = "#E63946"   # rojo  — España
COLOR_FR = "#4F8EF7"   # azul  — Francia
COLOR_DE = "#2EC27E"   # verde — Alemania

# Estilo global de matplotlib
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.grid":        True,
    "grid.alpha":       0.35,
    "grid.linestyle":   "--",
    "font.size":        11,
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.labelsize":   11,
    "legend.fontsize":  10,
    "xtick.labelsize":  10,
    "ytick.labelsize":  10,
})


# -------------------------------------------------------------
# FUNCIONES DE AYUDA
# (exportadas para que visualize_parte2.py las reutilice)
# -------------------------------------------------------------

def cargar_csv(nombre_archivo):
    """
    Carga un CSV de la carpeta de resultados y prepara el índice
    como fechas.

    Parámetros:
        nombre_archivo: nombre del archivo (ej: "importexport_mensual.csv")

    Retorna:
        Un DataFrame listo para graficar, o None si hay error
    """
    ruta = os.path.join(CARPETA_RESULTADOS, nombre_archivo)

    if not os.path.exists(ruta):
        print(f"  ✗ Archivo no encontrado: {ruta}")
        print("    Asegúrate de haber ejecutado analysis.py primero")
        return None

    try:
        df = pd.read_csv(ruta, index_col=0, parse_dates=True)
        return df
    except Exception as error:
        print(f"  ✗ Error cargando {nombre_archivo}: {error}")
        return None


def cargar_datos_limpios():
    """
    Carga el archivo maestro con todos los datos horarios limpios.

    Retorna:
        El DataFrame con todos los datos, o None si hay error
    """
    ruta = os.path.join(CARPETA_PROCESSED, "datos_limpios.csv")

    if not os.path.exists(ruta):
        print(f"  ✗ No se encontró datos_limpios.csv")
        return None

    try:
        df = pd.read_csv(ruta, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index, utc=True)
        return df
    except Exception as error:
        print(f"  ✗ Error cargando datos_limpios.csv: {error}")
        return None


def guardar_figura(nombre_archivo):
    """
    Guarda la figura actual en figures/ y cierra el plot para
    liberar memoria.

    Parámetros:
        nombre_archivo: nombre del PNG (ej: "flujos_netos.png")
    """
    ruta = os.path.join(CARPETA_FIGURAS, nombre_archivo)
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Guardado en {ruta}")

