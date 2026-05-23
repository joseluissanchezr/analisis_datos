# =============================================================
# extract.py
# Módulo de extracción de datos de ENTSO-E
# Grupo 4 — Intercambios Internacionales
# =============================================================

import os                         # para leer variables del sistema
import pandas as pd                # para trabajar con tablas de datos
from dotenv import load_dotenv     # para leer el archivo .env con el token
from entsoe import EntsoePandasClient  # cliente oficial de ENTSO-E

# -------------------------------------------------------------
# CONFIGURACIÓN INICIAL
# -------------------------------------------------------------

load_dotenv()

TOKEN = os.getenv("ENTSOE_TOKEN")
if not TOKEN:
    raise ValueError("No se encontró el token de ENTSO-E. Revisa tu archivo .env")

cliente = EntsoePandasClient(api_key=TOKEN)

# -------------------------------------------------------------
# PARÁMETROS DEL ANÁLISIS
# -------------------------------------------------------------

# Periodo de análisis: Año 2024 completo para tener datos cerrados
FECHA_INICIO = pd.Timestamp("2024-01-01", tz="UTC")
FECHA_FIN    = pd.Timestamp("2024-12-31", tz="UTC")

# Códigos de país según ENTSO-E
ES = "ES"       # España
FR = "FR"       # Francia
DE = "DE_LU"    # Alemania + Luxemburgo

# RUTA AJUSTADA A TU PROYECTO: group4-2026/data/Raw
CARPETA_RAW = os.path.join("group4-2026", "data", "Raw")

# Creamos la carpeta si no existe todavía
os.makedirs(CARPETA_RAW, exist_ok=True)


# -------------------------------------------------------------
# FUNCIONES
# -------------------------------------------------------------

def descargar_flujo(pais_origen, pais_destino, nombre_archivo):
    print(f"Descargando flujos {pais_origen} → {pais_destino}...")
    try:
        datos = cliente.query_crossborder_flows(
            country_code_from=pais_origen,
            country_code_to=pais_destino,
            start=FECHA_INICIO,
            end=FECHA_FIN
        )
        df = datos.to_frame(name=f"flujo_{pais_origen}_{pais_destino}_MWh")
        ruta = os.path.join(CARPETA_RAW, nombre_archivo)
        df.to_csv(ruta)
        print(f"  ✓ Guardado en {ruta}")
        return df
    except Exception as error:
        print(f"  ✗ Error descargando flujo {pais_origen}→{pais_destino}: {error}")
        return None

def descargar_precios(pais, nombre_archivo):
    print(f"Descargando precios day-ahead de {pais}...")
    try:
        datos = cliente.query_day_ahead_prices(
            country_code=pais,
            start=FECHA_INICIO,
            end=FECHA_FIN
        )
        df = datos.to_frame(name=f"precio_{pais}_EUR_MWh")
        ruta = os.path.join(CARPETA_RAW, nombre_archivo)
        df.to_csv(ruta)
        print(f"  ✓ Guardado en {ruta}")
        return df
    except Exception as error:
        print(f"  ✗ Error descargando precios de {pais}: {error}")
        return None

def descargar_capacidad(pais_origen, pais_destino, nombre_archivo):
    print(f"Descargando capacidad NTC {pais_origen} → {pais_destino}...")
    try:
        datos = cliente.query_net_transfer_capacity_dayahead(
            country_code_from=pais_origen,
            country_code_to=pais_destino,
            start=FECHA_INICIO,
            end=FECHA_FIN
        )
        df = datos.to_frame(name=f"ntc_{pais_origen}_{pais_destino}_MW")
        ruta = os.path.join(CARPETA_RAW, nombre_archivo)
        df.to_csv(ruta)
        print(f"  ✓ Guardado en {ruta}")
        return df
    except Exception as error:
        print(f"  ✗ Error descargando NTC, se intentará descargar intercambios programados: {error}")
        descargar_intercambio_programado(pais_origen, pais_destino, nombre_archivo)
        return None

def descargar_intercambio_programado(pais_origen, pais_destino, nombre_archivo):
    print(f"Descargando intercambios comerciales (Scheduled) {pais_origen} → {pais_destino}...")
    try:
        datos = cliente.query_scheduled_exchanges(
            country_code_from=pais_origen,
            country_code_to=pais_destino,
            start=FECHA_INICIO,
            end=FECHA_FIN
        )
        df = datos.to_frame(name=f"scheduled_{pais_origen}_{pais_destino}_MW")
        ruta = os.path.join(CARPETA_RAW, nombre_archivo)
        df.to_csv(ruta)
        print(f"  ✓ Guardado en {ruta}")
        return df
    except Exception as error:
        print(f"  ✗ Error descargando intercambios {pais_origen}→{pais_destino}: {error}")
        return None
# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------

def descargar_todo():
    print("=" * 50)
    print("INICIANDO DESCARGA DE DATOS — GRUPO 4")
    print(f"Periodo: {FECHA_INICIO.date()} → {FECHA_FIN.date()}")
    print("=" * 50)

    # --- Flujos físicos ---
    descargar_flujo(ES, FR, "flujos_ES_FR.csv")
    descargar_flujo(FR, ES, "flujos_FR_ES.csv")
    descargar_flujo(FR, DE, "flujos_FR_DE.csv")
    descargar_flujo(DE, FR, "flujos_DE_FR.csv")

    # --- Capacidades (NTC) ---
    descargar_capacidad(ES, FR, "ntc_ES_FR.csv")
    descargar_capacidad(FR, ES, "ntc_FR_ES.csv")
    descargar_capacidad(FR, DE, "ntc_FR_DE.csv")
    descargar_capacidad(DE, FR, "ntc_DE_FR.csv")

    # --- Precios ---
    descargar_precios(ES, "precios_ES.csv")
    descargar_precios(FR, "precios_FR.csv")
    descargar_precios(DE, "precios_DE.csv")

    print("=" * 50)
    print("DESCARGA COMPLETADA")
    print(f"Archivos guardados en: {CARPETA_RAW}/")
    print("=" * 50)

if __name__ == "__main__":
    descargar_todo()