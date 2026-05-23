# =============================================================
# visualize.py
# Módulo de visualización de resultados
# Grupo 4 — Intercambios Internacionales
# =============================================================
# Genera 5 gráficas PNG a partir de los CSVs producidos por
# analysis.py. Los archivos se guardan en figures/.
#)
#
# Orden de ejecución:
#   1. extract.py
#   2. clean.py
#   3. analysis.py
#   4. visualize.py
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

# -------------------------------------------------------------
# GRÁFICA 1 — FLUJOS NETOS ES ↔ FR / FR ↔ DE
# -------------------------------------------------------------

def grafica_flujos_netos():
    """
    Gráfica de línea con la evolución diaria del flujo neto entre
    España↔Francia y Francia↔Alemania.

    Zonas rellenas:
        Rojo  → España exporta a Francia (flujo positivo)
        Azul  → España importa de Francia (flujo negativo)

    Los datos horarios se agregan a media diaria para mayor claridad.
    """
    print("\nGenerando flujos_netos.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    # Calculamos la media diaria del flujo neto
    flujo_diario = df[["neto_ES_FR_MWh", "neto_FR_DE_MWh"]].resample("D").mean()

    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    fig.suptitle("Flujos netos de electricidad — Media diaria (2024)",
                 fontsize=14, fontweight="bold", y=1.01)

    pares = [
        (axes[0], "neto_ES_FR_MWh", "ES → FR", COLOR_ES, COLOR_FR),
        (axes[1], "neto_FR_DE_MWh", "FR → DE", COLOR_FR, COLOR_DE),
    ]

    for ax, col, label, color_pos, color_neg in pares:
        serie = flujo_diario[col]

        # Línea principal
        ax.plot(serie.index, serie.values, color="dimgray", linewidth=0.8, zorder=3)

        # Zona rellena: exportación (positivo)
        ax.fill_between(serie.index, serie.values, 0,
                        where=(serie.values >= 0),
                        color=color_pos, alpha=0.45, label="Exportación")

        # Zona rellena: importación (negativo)
        ax.fill_between(serie.index, serie.values, 0,
                        where=(serie.values < 0),
                        color=color_neg, alpha=0.45, label="Importación")

        # Línea de cero
        ax.axhline(0, color="black", linewidth=0.9)

        ax.set_ylabel("Flujo neto (MWh/h)")
        ax.set_title(f"Interconexión {label}", fontsize=12)
        ax.legend(loc="upper right")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    axes[1].set_xlabel("Fecha")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    guardar_figura("flujos_netos.png")


# -------------------------------------------------------------
# GRÁFICA 2 — HEATMAP DE CONGESTIONES
# -------------------------------------------------------------

def grafica_heatmap_congestiones():
    """
    Heatmap que muestra el porcentaje de uso de la interconexión
    ES-FR por hora del día (eje Y) y por mes (eje X).

    Cuanto más rojo, más cerca del 90% de congestión.
    Ayuda a detectar qué horas y meses tienen mayor presión en la red.
    """
    print("\nGenerando heatmap_congestiones.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    # Calculamos el porcentaje de uso para ES-FR
    # Limitamos a 120% para no distorsionar la escala de color con picos extremos
    df["uso_ES_FR_pct"] = (
        df["flujo_ES_FR_MWh"].abs() / df["ntc_ES_FR_MW"] * 100
    ).clip(upper=120)

    # Columnas auxiliares para pivotar
    df_local = df[["uso_ES_FR_pct"]].copy()
    df_local["hora"] = df_local.index.hour
    df_local["mes"]  = df_local.index.strftime("%b")

    # Respetamos el orden natural de los meses
    meses_orden    = ["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"]
    meses_presentes = [m for m in meses_orden if m in df_local["mes"].unique()]

    # Tabla pivote: filas = hora del día, columnas = mes
    tabla = df_local.pivot_table(
        index="hora",
        columns="mes",
        values="uso_ES_FR_pct",
        aggfunc="mean"
    )[meses_presentes]

    fig, ax = plt.subplots(figsize=(13, 7))

    sns.heatmap(
        tabla,
        ax=ax,
        cmap="RdYlGn_r",       # verde = poco uso, rojo = congestión
        vmin=0, vmax=100,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "Uso de la interconexión (%)", "shrink": 0.85},
        annot=False,
    )

    ax.set_title(
        "Heatmap de uso de la interconexión ES–FR\n"
        "(% de la capacidad NTC, media por hora y mes — 2024)",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("Mes")
    ax.set_ylabel("Hora del día (UTC)")
    ax.set_yticklabels([f"{h:02d}:00" for h in range(24)], rotation=0, fontsize=9)

    plt.tight_layout()
    guardar_figura("heatmap_congestiones.png")


# -------------------------------------------------------------
# GRÁFICA 3 — MATRIZ DE CORRELACIÓN DE PRECIOS
# -------------------------------------------------------------

def grafica_correlacion_precios():
    """
    Muestra la matriz de correlación 3×3 de precios entre
    España, Francia y Alemania como un heatmap de seaborn.

    Interpretación:
        1.0  → precios perfectamente sincronizados
        0.0  → sin relación
       -1.0  → relación inversa

    Una correlación alta indica mercados bien integrados.
    """
    print("\nGenerando correlacion_precios.png...")

    df = cargar_csv("correlacion_global.csv")
    if df is None:
        return

    # Renombramos para la leyenda visual
    etiquetas = {
        "precio_ES_EUR_MWh": "España (ES)",
        "precio_FR_EUR_MWh": "Francia (FR)",
        "precio_DE_EUR_MWh": "Alemania (DE)",
    }
    df = df.rename(index=etiquetas, columns=etiquetas)

    fig, ax = plt.subplots(figsize=(7, 6))

    sns.heatmap(
        df,
        ax=ax,
        annot=True,
        fmt=".3f",
        cmap="RdYlGn",
        vmin=-1, vmax=1,
        linewidths=1.5,
        linecolor="white",
        square=True,
        cbar_kws={"label": "Correlación de Pearson", "shrink": 0.8},
        annot_kws={"size": 14, "weight": "bold"},
    )

    ax.set_title("Correlación de precios day-ahead entre países\n(Pearson — 2024)",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plt.tight_layout()
    guardar_figura("correlacion_precios.png")


# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------

def visualizar_todo():
    print("=" * 50)
    print("VISUALIZACIÓN — GRUPO 4 (parte 1/2)")
    print("=" * 50)

    grafica_flujos_netos()
    grafica_heatmap_congestiones()
    grafica_correlacion_precios()

    print("\n" + "=" * 50)
    print("Gráficas 1–3 completadas")
    print(f"Archivos guardados en: {CARPETA_FIGURAS}/")
    print("Ejecuta visualize_parte2.py para las gráficas 4 y 5")
    print("=" * 50)


if __name__ == "__main__":
    visualizar_todo()