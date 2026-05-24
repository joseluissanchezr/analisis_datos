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

# Rutas absolutas basadas en la ubicación del script
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_RAIZ   = os.path.dirname(os.path.dirname(DIR_SCRIPT))   # sube hasta group4-2026/

CARPETA_RESULTADOS = os.path.join(DIR_RAIZ, "data", "processed", "resultados")
CARPETA_PROCESSED  = os.path.join(DIR_RAIZ, "data", "processed")
CARPETA_FIGURAS    = os.path.join(DIR_RAIZ, "figures")

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
    # Usamos número del mes (1-12) para evitar problemas con el locale del sistema.
    df_local = df[["uso_ES_FR_pct"]].copy()
    df_local["hora"]    = df_local.index.hour
    df_local["mes_num"] = df_local.index.month

    # Etiquetas en español, en orden natural Ene → Dic
    meses_es = ["Ene","Feb","Mar","Abr","May","Jun",
                "Jul","Ago","Sep","Oct","Nov","Dic"]

    # Tabla pivote: filas = hora del día, columnas = número de mes
    tabla = df_local.pivot_table(
        index="hora",
        columns="mes_num",
        values="uso_ES_FR_pct",
        aggfunc="mean"
    )

    # Renombramos las columnas (1-12) a etiquetas en español ("Ene"-"Dic")
    tabla.columns = [meses_es[m - 1] for m in tabla.columns]

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
# GRÁFICA 4 — SPREAD DE PRECIOS vs FLUJO NETO (ES↔FR)
# -------------------------------------------------------------

def grafica_spread_vs_flujo():
    """
    Scatter plot que muestra la relación entre el spread de precios
    (precio_ES - precio_FR) y el flujo neto entre ambos países.

    Hipótesis económica:
        En un mercado bien integrado, la electricidad debe fluir
        del mercado barato hacia el mercado caro. Es decir:
            - Spread positivo (ES más caro) → flujo negativo (FR→ES)
            - Spread negativo (FR más caro) → flujo positivo (ES→FR)

    Se espera una correlación negativa fuerte entre las dos variables.
    Una correlación cercana a 0 indicaría que las interconexiones
    no están permitiendo el arbitraje natural del mercado (por ejemplo,
    por congestión persistente).
    """
    print("\nGenerando spread_vs_flujo.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    # Calculamos spread y juntamos con el flujo neto
    spread = df["precio_ES_EUR_MWh"] - df["precio_FR_EUR_MWh"]
    flujo  = df["neto_ES_FR_MWh"]

    # Quitamos filas con NaN para regresión y correlación
    datos = pd.DataFrame({"spread": spread, "flujo": flujo}).dropna()
    correlacion = datos["spread"].corr(datos["flujo"])

    # Ajuste lineal: y = pendiente·x + intercepto
    pendiente, intercepto = np.polyfit(datos["spread"], datos["flujo"], 1)
    x_linea = np.linspace(datos["spread"].min(), datos["spread"].max(), 100)
    y_linea = pendiente * x_linea + intercepto

    # Figura
    fig, ax = plt.subplots(figsize=(11, 7))

    # Scatter — alpha bajo porque hay miles de puntos solapados
    ax.scatter(datos["spread"], datos["flujo"],
               alpha=0.15, s=10, color=COLOR_ES,
               edgecolors="none", label="Horas")

    # Línea de tendencia
    ax.plot(x_linea, y_linea,
            color="black", linestyle="--", linewidth=2,
            label=f"Tendencia lineal (pendiente = {pendiente:.1f})")

    # Líneas de referencia en cero
    ax.axhline(0, color="gray", linewidth=0.7, alpha=0.6)
    ax.axvline(0, color="gray", linewidth=0.7, alpha=0.6)

    # Anotaciones en los cuadrantes para facilitar la interpretación
    ax.text(0.97, 0.97, "ES caro\nES exporta\n(esperado vacío)",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color="gray", alpha=0.7, style="italic")
    ax.text(0.03, 0.03, "FR caro\nES importa\n(esperado vacío)",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=9, color="gray", alpha=0.7, style="italic")
    ax.text(0.97, 0.03, "ES caro → FR exporta\n(lógico)",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=9, color="green", alpha=0.8, style="italic")
    ax.text(0.03, 0.97, "FR caro → ES exporta\n(lógico)",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=9, color="green", alpha=0.8, style="italic")

    ax.set_title(
        f"Relación entre spread de precios y flujo neto ES↔FR\n"
        f"Correlación de Pearson: {correlacion:.3f}",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("Spread precio (ES − FR) en EUR/MWh")
    ax.set_ylabel("Flujo neto ES → FR en MWh/h")
    ax.legend(loc="lower left")

    plt.tight_layout()
    guardar_figura("spread_vs_flujo.png")

    # -------------------------------------------------------------
# GRÁFICA 5 — CONVERGENCIA DE PRECIOS (SPREAD)
# -------------------------------------------------------------

def grafica_convergencia_precios():
    """
    Gráfica de línea con la evolución diaria del spread absoluto
entre los tres pares de países (ES-FR, FR-DE, ES-DE).

    Spread pequeño (<5 EUR/MWh) → mercados bien integrados,
    los precios convergen entre países.
    Spread grande → mercados poco conectados o con congestión
    en las interconexiones.

La franja verde indica la zona de convergencia. Cuanto más
tiempo pasen las líneas dentro de esa franja, mejor integrado
está el mercado europeo.
    """
    print("\nGenerando convergencia_precios.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    spreads = pd.DataFrame({
        "ES–FR": (df["precio_ES_EUR_MWh"] - df["precio_FR_EUR_MWh"]).abs(),
        "FR–DE": (df["precio_FR_EUR_MWh"] - df["precio_DE_EUR_MWh"]).abs(),
        "ES–DE": (df["precio_ES_EUR_MWh"] - df["precio_DE_EUR_MWh"]).abs(),
    }).resample("D").mean()

    UMBRAL = 5

    fig, ax = plt.subplots(figsize=(13, 6))

    ax.axhspan(0, UMBRAL, color="#2EC27E", alpha=0.12,
               label=f"Zona convergencia (<{UMBRAL} EUR/MWh)")
    ax.axhline(UMBRAL, color="#2EC27E", linewidth=1.2, linestyle="--", alpha=0.7)

    for col, color in zip(spreads.columns, [COLOR_ES, COLOR_FR, COLOR_DE]):
        ax.plot(spreads.index, spreads[col], label=col, color=color, linewidth=1.4)

    ax.set_title("Convergencia de precios — Spread diario absoluto entre países (2024)",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Spread absoluto (EUR/MWh)")
    ax.set_xlabel("Fecha")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=30, ha="right")
    ax.legend(loc="upper right")
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    guardar_figura("convergencia_precios.png")

# -------------------------------------------------------------
# GRÁFICA 6 — COMPARATIVA DE PRECIOS POR PAÍS
# -------------------------------------------------------------

def grafica_precios_comparativo():
    """
    Dos subgráficas en una sola figura:

        Superior: evolución mensual del precio medio por país.
        Inferior: boxplot con la distribución completa del periodo.

    Permite comparar tanto la tendencia temporal como la
    dispersión y los outliers de cada mercado.
    """
    print("\nGenerando precios_comparativo.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    precios = df[["precio_ES_EUR_MWh", "precio_FR_EUR_MWh", "precio_DE_EUR_MWh"]].copy()
    mensual = precios.resample("ME").mean()
    etiquetas = {
        "precio_ES_EUR_MWh": "España (ES)",
        "precio_FR_EUR_MWh": "Francia (FR)",
        "precio_DE_EUR_MWh": "Alemania (DE)",
    }
    mensual = mensual.rename(columns=etiquetas)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10))
    fig.suptitle("Comparativa de precios day-ahead — ES / FR / DE (2024)",
                 fontsize=14, fontweight="bold")

    for col, color in zip(mensual.columns, [COLOR_ES, COLOR_FR, COLOR_DE]):
        ax1.plot(mensual.index, mensual[col], marker="o", markersize=5,
                 linewidth=2, color=color, label=col)

    ax1.set_title("Evolución mensual del precio medio")
    ax1.set_ylabel("Precio (EUR/MWh)")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.tick_params(axis="x", rotation=30)
    ax1.legend()

    datos_boxplot = [
        precios["precio_ES_EUR_MWh"].dropna().values,
        precios["precio_FR_EUR_MWh"].dropna().values,
        precios["precio_DE_EUR_MWh"].dropna().values,
    ]
    nombres = ["España (ES)", "Francia (FR)", "Alemania (DE)"]
    colores  = [COLOR_ES, COLOR_FR, COLOR_DE]

    bp = ax2.boxplot(
        datos_boxplot,
        labels=nombres,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=2),
        flierprops=dict(marker="o", markersize=2.5, alpha=0.3, linestyle="none"),
    )

    for patch, color in zip(bp["boxes"], colores):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)

    ax2.set_title("Distribución completa del periodo")
    ax2.set_ylabel("Precio (EUR/MWh)")

    plt.tight_layout()
    guardar_figura("precios_comparativo.png")

# -------------------------------------------------------------
# GRÁFICA 7 — HEATMAP DE CONGESTIONES FR-DE
# -------------------------------------------------------------

def grafica_heatmap_congestiones_fr_de():
    """
    Heatmap que muestra el porcentaje de uso de la interconexión
    FR-DE por hora del día (eje Y) y por mes (eje X).

    Complementa el heatmap ES-FR ya existente, completando
    el análisis del corredor eléctrico europeo ES-FR-DE.

        Verde implica uso bajo, línea con capacidad disponible.
        Rojo implica uso cercano al 90%, riesgo de congestión.
    """
    print("\nGenerando heatmap_congestiones_fr_de.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    df["uso_FR_DE_pct"] = (
        df["flujo_FR_DE_MWh"].abs() / df["ntc_FR_DE_MW"] * 100
    ).clip(upper=120)

    df_local = df[["uso_FR_DE_pct"]].copy()
    df_local["hora"]    = df_local.index.hour
    df_local["mes_num"] = df_local.index.month

    meses_es = ["Ene","Feb","Mar","Abr","May","Jun",
                "Jul","Ago","Sep","Oct","Nov","Dic"]

    tabla = df_local.pivot_table(
        index="hora",
        columns="mes_num",
        values="uso_FR_DE_pct",
        aggfunc="mean"
    )
    tabla.columns = [meses_es[m - 1] for m in tabla.columns]
    fig, ax = plt.subplots(figsize=(13, 7))

    sns.heatmap(
        tabla,
        ax=ax,
        cmap="RdYlGn_r",
        vmin=0, vmax=100,
        linewidths=0.4,
        linecolor="white",
        cbar_kws={"label": "Uso de la interconexión (%)", "shrink": 0.85},
        annot=False,
    )

    ax.set_title(
        "Heatmap de uso de la interconexión FR–DE\n"
        "(% de la capacidad NTC, media por hora y mes — 2024)",
        fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("Mes")
    ax.set_ylabel("Hora del día (UTC)")
    ax.set_yticklabels([f"{h:02d}:00" for h in range(24)], rotation=0, fontsize=9)

    plt.tight_layout()
    guardar_figura("heatmap_congestiones_fr_de.png")

    # -------------------------------------------------------------
# GRÁFICA 8 — BALANCE IMPORT/EXPORT ANUAL POR PAÍS
# -------------------------------------------------------------

def grafica_balance_importexport():
    """
    Gráfico de barras horizontales con el balance neto anual
    de cada país en sus interconexiones.

        Barra positiva -> el país exporta más de lo que importa
        Barra negativa -> el país importa más de lo que exporta

    Permite identificar de un vistazo qué países actúan como
    exportadores netos y cuáles como importadores netos en 2024.
    """
    print("\nGenerando balance_importexport.png...")

    df = cargar_datos_limpios()
    if df is None:
        return

    # Balance anual: suma de todos los flujos netos del año
    balance_ES = df["neto_ES_FR_MWh"].sum() / 1e6   # convertimos a TWh
    balance_FR = -df["neto_ES_FR_MWh"].sum() / 1e6 + df["neto_FR_DE_MWh"].sum() / 1e6
    balance_DE = -df["neto_FR_DE_MWh"].sum() / 1e6

    paises  = ["España (ES)", "Francia (FR)", "Alemania (DE)"]
    valores = [balance_ES, balance_FR, balance_DE]
    colores = [COLOR_ES if v >= 0 else "#AAAAAA" for v in valores]

    fig, ax = plt.subplots(figsize=(10, 5))

    bars = ax.barh(paises, valores, color=colores, edgecolor="white", height=0.5)

    # Etiquetas con el valor dentro de cada barra
    for bar, val in zip(bars, valores):
        ax.text(
            val + (0.02 if val >= 0 else -0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f} TWh",
            va="center",
            ha="left" if val >= 0 else "right",
            fontsize=11, fontweight="bold"
        )

    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Balance neto anual de intercambios eléctricos por país (2024)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Balance neto (TWh)")

    plt.tight_layout()
    guardar_figura("balance_importexport.png")
# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------

def visualizar_todo():
    print("=" * 50)
    print("VISUALIZACIÓN — GRUPO 4")
    print("=" * 50)

    grafica_flujos_netos()
    grafica_heatmap_congestiones()
    grafica_correlacion_precios()
    grafica_spread_vs_flujo()
    grafica_convergencia_precios()
    grafica_precios_comparativo()
    grafica_heatmap_congestiones_fr_de()
    grafica_balance_importexport()

    print("\n" + "=" * 50)
    print("Gráficas completadas")
    print(f"Archivos guardados en: {CARPETA_FIGURAS}/")
    print("=" * 50)


if __name__ == "__main__":
    visualizar_todo()