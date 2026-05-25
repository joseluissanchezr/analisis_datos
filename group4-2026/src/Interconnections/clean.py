# =============================================================
# clean.py
# Módulo de limpieza y procesado de datos
# Grupo 4 — Intercambios Internacionales
# =============================================================
# Este archivo toma los datos en bruto de data/raw/ y los limpia:
#   - Corrige el formato de fechas
#   - Detecta y rellena huecos en los datos
#   - Unifica la zona horaria
#   - Combina todos los archivos en uno solo
#   - Guarda el resultado en data/processed/
# =============================================================

import os
import pandas as pd

# -------------------------------------------------------------
# CONFIGURACIÓN DE CARPETAS
# -------------------------------------------------------------

CARPETA_RAW = os.path.join("data", "raw")
CARPETA_PROCESSED = os.path.join("data", "processed")
os.makedirs(CARPETA_PROCESSED, exist_ok=True)

# -------------------------------------------------------------
# FUNCIONES DE AYUDA
# -------------------------------------------------------------
# limit=3 significa que solo rellenamos hasta 3 horas seguidas de huecos
# Si hay más de 3 horas seguidas sin datos, las dejamos como NaN
# para no inventar datos en periodos largos sin información

def cargar_csv(nombre_archivo):
    """
    Carga un archivo CSV de la carpeta data/raw/ y prepara
    el índice de fechas para que Python lo entienda bien.

    Parámetros:
        nombre_archivo: nombre del archivo (ej: "flujos_ES_FR.csv")

    Retorna:
        Un DataFrame con el índice como fechas, o None si hay error
    """

    ruta = os.path.join(CARPETA_RAW, nombre_archivo)

    if not os.path.exists(ruta):
        print(f"  ✗ Archivo no encontrado: {ruta}")
        return None

    try:
        df = pd.read_csv(ruta, index_col=0, parse_dates=True)
        df.index = pd.to_datetime(df.index, utc=True)

        return df

    except Exception as error:
        print(f"  ✗ Error leyendo {nombre_archivo}: {error}")
        return None


def detectar_huecos(df, nombre):
    """
    Comprueba si faltan horas en los datos.
    Los datos de ENTSO-E deberían tener un valor por cada hora.

    Parámetros:
        df    : el DataFrame a comprobar
        nombre: nombre descriptivo para mostrar en pantalla
    """

    nulos = df.isnull().sum().sum()

    if nulos > 0:
        print(f"  ⚠ {nombre}: {nulos} valores nulos encontrados")
    else:
        print(f"  ✓ {nombre}: sin valores nulos")

    indice_completo = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="h",
        tz="UTC"
    )

    horas_que_faltan = indice_completo.difference(df.index)

    if len(horas_que_faltan) > 0:
        print(f"  ⚠ {nombre}: faltan {len(horas_que_faltan)} horas en el índice")
    else:
        print(f"  ✓ {nombre}: índice de fechas completo")

def rellenar_huecos(df):
    """
    Rellena los valores nulos con interpolación lineal.

    Interpolación lineal significa: si falta el valor de las 14:00
    y tenemos 100 a las 13:00 y 200 a las 15:00, ponemos 150 a las 14:00.
    Es una estimación sencilla y razonable para datos de energía.

    Parámetros:
        df: el DataFrame con posibles huecos

    Retorna:
        El DataFrame sin huecos
    """

    indice_completo = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="h",
        tz="UTC"
    )

    df = df.reindex(indice_completo)

    df = df.interpolate(method="linear", limit=3)

    return df


def limpiar_flujos():
    """
    Carga, limpia y combina todos los archivos de flujos físicos.

    Los flujos entre dos países vienen en dos archivos : uno de ida y uno de vuelta.
    Este programa les combina en un solo DataFrame y calcula el flujo neto.

    Ejemplo:
    Flujo neto ES→FR = flujo ES→FR - flujo FR→ES
    Si es positivo: España exporta a Francia
    Si es negativo: España importa de Francia

    Retorna:
        Un DataFrame con todos los flujos limpios y el flujo neto
    """

    print("\nLimpiando flujos físicos...")

    # Carga los 4 archivos de datos
    flujo_es_fr = cargar_csv("flujos_ES_FR.csv")
    flujo_fr_es = cargar_csv("flujos_FR_ES.csv")
    flujo_fr_de = cargar_csv("flujos_FR_DE.csv")
    flujo_de_fr = cargar_csv("flujos_DE_FR.csv")

    # Comproba que se cargaron bien
    archivos = {
        "ES→FR": flujo_es_fr,
        "FR→ES": flujo_fr_es,
        "FR→DE": flujo_fr_de,
        "DE→FR": flujo_de_fr
    }

    for nombre, df in archivos.items():
        if df is not None:
            detectar_huecos(df, nombre)
    
    # Rellena huecos en cada archivo
    flujo_es_fr = rellenar_huecos(flujo_es_fr) if flujo_es_fr is not None else None
    flujo_fr_es = rellenar_huecos(flujo_fr_es) if flujo_fr_es is not None else None
    flujo_fr_de = rellenar_huecos(flujo_fr_de) if flujo_fr_de is not None else None
    flujo_de_fr = rellenar_huecos(flujo_de_fr) if flujo_de_fr is not None else None

    # Combina todo en un solo DataFrame : cada columna es un flujo diferente
    df_flujos = pd.DataFrame({
        "flujo_ES_FR_MWh": flujo_es_fr.iloc[:, 0] if flujo_es_fr is not None else None,
        "flujo_FR_ES_MWh": flujo_fr_es.iloc[:, 0] if flujo_fr_es is not None else None,
        "flujo_FR_DE_MWh": flujo_fr_de.iloc[:, 0] if flujo_fr_de is not None else None,
        "flujo_DE_FR_MWh": flujo_de_fr.iloc[:, 0] if flujo_de_fr is not None else None,
    })

    # Calcula flujos netos (exportación neta de cada país hacia el vecino) : àositivo = exporta, Negativo = importa
    df_flujos["neto_ES_FR_MWh"] = df_flujos["flujo_ES_FR_MWh"] - df_flujos["flujo_FR_ES_MWh"]
    df_flujos["neto_FR_DE_MWh"] = df_flujos["flujo_FR_DE_MWh"] - df_flujos["flujo_DE_FR_MWh"]

    print(f"  ✓ Flujos combinados: {len(df_flujos)} filas, {len(df_flujos.columns)} columnas")
    return df_flujos


def limpiar_capacidades():
    """
    Carga y limpia los archivos de capacidad de interconexión (NTC).

    Retorna:
        Un DataFrame con las capacidades limpias
    """

    print("\nLimpiando capacidades NTC...")

    # Carga los archivos de capacidad de interconexión
    ntc_es_fr = cargar_csv("ntc_ES_FR.csv")
    ntc_fr_es = cargar_csv("ntc_FR_ES.csv")
    ntc_fr_de = cargar_csv("ntc_FR_DE.csv")
    ntc_de_fr = cargar_csv("ntc_DE_FR.csv")

    archivos = {
        "NTC ES→FR": ntc_es_fr,
        "NTC FR→ES": ntc_fr_es,
        "NTC FR→DE": ntc_fr_de,
        "NTC DE→FR": ntc_de_fr
    }

    # Comproba que se cargaron bien
    for nombre, df in archivos.items():
        if df is not None:
            detectar_huecos(df, nombre)

    # Rellena los huecos
    ntc_es_fr = rellenar_huecos(ntc_es_fr) if ntc_es_fr is not None else None
    ntc_fr_es = rellenar_huecos(ntc_fr_es) if ntc_fr_es is not None else None
    ntc_fr_de = rellenar_huecos(ntc_fr_de) if ntc_fr_de is not None else None
    ntc_de_fr = rellenar_huecos(ntc_de_fr) if ntc_de_fr is not None else None

    # Combina todo en un solo DataFrame
    df_ntc = pd.DataFrame({
        "ntc_ES_FR_MW": ntc_es_fr.iloc[:, 0] if ntc_es_fr is not None else None,
        "ntc_FR_ES_MW": ntc_fr_es.iloc[:, 0] if ntc_fr_es is not None else None,
        "ntc_FR_DE_MW": ntc_fr_de.iloc[:, 0] if ntc_fr_de is not None else None,
        "ntc_DE_FR_MW": ntc_de_fr.iloc[:, 0] if ntc_de_fr is not None else None,
    })

    print(f"  ✓ Capacidades combinadas: {len(df_ntc)} filas, {len(df_ntc.columns)} columnas")
    return df_ntc

def limpiar_precios():
    """
     Carga y limpia los archivos de precios day-ahead de cada país.
     Retorna:
         Un DataFrame con los precios limpios de los tres países
     """
    print("\nLimpiando precios day-ahead...")

    # Carga los datos de precio per día en cada país
    precios_es = cargar_csv("precios_ES.csv")
    precios_fr = cargar_csv("precios_FR.csv")
    precios_de = cargar_csv("precios_DE.csv")

    archivos = {
        "Precios ES": precios_es,
        "Precios FR": precios_fr,
        "Precios DE": precios_de
    }

    for nombre, df in archivos.items():
        if df is not None:
            detectar_huecos(df, nombre)
    
    # Rellena los huecos previamente detectados
    precios_es = rellenar_huecos(precios_es) if precios_es is not None else None
    precios_fr = rellenar_huecos(precios_fr) if precios_fr is not None else None
    precios_de = rellenar_huecos(precios_de) if precios_de is not None else None

    # Combina todos los datos de precio limpiados en un unico DataFrame
    df_precios = pd.DataFrame({
        "precio_ES_EUR_MWh": precios_es.iloc[:, 0] if precios_es is not None else None,
        "precio_FR_EUR_MWh": precios_fr.iloc[:, 0] if precios_fr is not None else None,
        "precio_DE_EUR_MWh": precios_de.iloc[:, 0] if precios_de is not None else None,
    })

    print(f"  ✓ Precios combinados: {len(df_precios)} filas, {len(df_precios.columns)} columnas")
    return df_precios

# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------

def limpiar_todo():
    """
    Ejecuta la limpieza completa de todos los datos.
    Al final guarda un único archivo CSV listo para analizar.
    """

    print("=" * 50)
    print("INICIANDO LIMPIEZA DE DATOS")
    print("=" * 50)

    # Limpia cada tipo de dato por separado
    df_flujos = limpiar_flujos()
    df_ntc = limpiar_capacidades()
    df_precios = limpiar_precios()

    # Combina los tres DataFrames en uno solo. Los une por el índice (la fecha), común a todos
    print("\nCombinando todos los datos...")
    df_final = pd.concat([df_flujos, df_ntc, df_precios], axis=1)

    # Elimina filas donde todos los valores son nulos
    df_final = df_final.dropna(how="all")

    # Guarda el resultado en data/processed/
    ruta_salida = os.path.join(CARPETA_PROCESSED, "datos_limpios.csv")
    df_final.to_csv(ruta_salida)

    print(f"\n{'=' * 50}")
    print("LIMPIEZA COMPLETADA")
    print(f"Periodo        : {df_final.index.min()} → {df_final.index.max()}")
    print(f"Archivo guardado en: {ruta_salida}")
    print("=" * 50)

    return df_final

# -------------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------------

if __name__ == "__main__":
    limpiar_todo()