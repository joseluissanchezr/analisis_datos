# =============================================================
# analysis.py
# Módulo de análisis e indicadores
# Grupo 4 — Intercambios Internacionales
# =============================================================

import os
import pandas as pd
import numpy as np

# -------------------------------------------------------------
# CONFIGURACIÓN DE CARPETAS
# -------------------------------------------------------------

CARPETA_PROCESSED = os.path.join("data", "processed")
CARPETA_RESULTADOS = os.path.join("data", "processed", "resultados")

os.makedirs(CARPETA_RESULTADOS, exist_ok=True)


# -------------------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------------------

def cargar_datos_limpios():
    ruta = os.path.join(CARPETA_PROCESSED, "datos_limpios.csv")

    if not os.path.exists(ruta):
        print("✗ No se encontró datos_limpios.csv")
        print("  Ejecuta primero clean.py")
        return None

    df = pd.read_csv(ruta, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True)

    print(f"✓ Datos cargados: {len(df)} filas, periodo {df.index.min().date()} → {df.index.max().date()}")
    return df


# -------------------------------------------------------------
# INDICADOR 1: IMPORT / EXPORT
# -------------------------------------------------------------

def analizar_importexport(df):
    print("\n--- ANÁLISIS IMPORT/EXPORT ---")

    flujos_netos = df[["neto_ES_FR_MWh", "neto_FR_DE_MWh"]].copy()

    print("\nEstadísticas globales (MWh/hora):")
    print(flujos_netos.describe().round(1))

    resumen_mensual = flujos_netos.resample("ME").agg(
        media=("neto_ES_FR_MWh", "mean"),
        total_exportado=("neto_ES_FR_MWh", lambda x: x[x > 0].sum()),
        total_importado=("neto_ES_FR_MWh", lambda x: x[x < 0].sum()),
        horas_exportando=("neto_ES_FR_MWh", lambda x: (x > 0).sum()),
        horas_importando=("neto_ES_FR_MWh", lambda x: (x < 0).sum()),
    )

    print("\nResumen mensual ES→FR:")
    print(resumen_mensual.round(1))

    ruta = os.path.join(CARPETA_RESULTADOS, "importexport_mensual.csv")
    resumen_mensual.to_csv(ruta)
    print(f"\n✓ Guardado en {ruta}")

    return resumen_mensual

# -------------------------------------------------------------
# INDICADOR 3: CORRELACIÓN DE PRECIOS
# -------------------------------------------------------------

def analizar_correlacion(df):
    """
    Analiza la correlación de precios entre los tres mercados.

    La correlación mide si los precios de dos países se mueven
    a la vez en la misma dirección.
        Correlación = 1.0  → se mueven exactamente igual
        Correlación = 0.0  → no hay relación entre ellos
        Correlación = -1.0 → se mueven en direcciones opuestas

    Una correlación alta indica mercados bien integrados.

    Parámetros:
        df: el DataFrame con los datos limpios

    Retorna:
        La matriz de correlación entre los tres países
    """

    print("\n--- ANÁLISIS DE CORRELACIÓN DE PRECIOS ---")

    # Seleccionamos solo las columnas de precios
    precios = df[["precio_ES_EUR_MWh", "precio_FR_EUR_MWh", "precio_DE_EUR_MWh"]].copy()

    # Calculamos la matriz de correlación de Pearson
    # Es la más común y mide relaciones lineales entre variables
    correlacion = precios.corr(method="pearson").round(3)

    print("\nMatriz de correlación de precios (Pearson):")
    print(correlacion)

    # Correlación mensual para ver si cambia a lo largo del tiempo
    # Calculamos la correlación ES-FR y FR-DE mes a mes
    correlacion_mensual = precios.resample("ME").apply(
        lambda mes: mes["precio_ES_EUR_MWh"].corr(mes["precio_FR_EUR_MWh"])
    ).to_frame(name="correlacion_ES_FR")

    correlacion_mensual["correlacion_FR_DE"] = precios.resample("ME").apply(
        lambda mes: mes["precio_FR_EUR_MWh"].corr(mes["precio_DE_EUR_MWh"])
    )

    print("\nCorrelación mensual entre países:")
    print(correlacion_mensual.round(3))

    # Guardamos resultados
    ruta_global = os.path.join(CARPETA_RESULTADOS, "correlacion_global.csv")
    ruta_mensual = os.path.join(CARPETA_RESULTADOS, "correlacion_mensual.csv")
    correlacion.to_csv(ruta_global)
    correlacion_mensual.to_csv(ruta_mensual)
    print(f"\n✓ Guardado en {ruta_global}")
    print(f"✓ Guardado en {ruta_mensual}")

    return correlacion, correlacion_mensual


# -------------------------------------------------------------
# INDICADOR 4: CONVERGENCIA DE PRECIOS
# -------------------------------------------------------------

def analizar_convergencia(df):
    """
    Analiza la convergencia de precios entre países.

    La convergencia de precios mide si los precios tienden a igualarse
    entre países. Cuando los mercados están bien conectados e integrados,
    los precios convergen (se parecen mucho).

    Medimos esto con el SPREAD: diferencia de precio entre dos países.
        Spread ES-FR = precio_ES - precio_FR
        Si el spread es cercano a 0 → precios convergentes
        Si el spread es grande → mercados poco integrados o congestionados

    Parámetros:
        df: el DataFrame con los datos limpios

    Retorna:
        Un DataFrame con los spreads y métricas de convergencia
    """

    print("\n--- ANÁLISIS DE CONVERGENCIA DE PRECIOS ---")

    resultado = pd.DataFrame(index=df.index)

    # Calculamos los spreads entre pares de países
    resultado["spread_ES_FR"] = df["precio_ES_EUR_MWh"] - df["precio_FR_EUR_MWh"]
    resultado["spread_FR_DE"] = df["precio_FR_EUR_MWh"] - df["precio_DE_EUR_MWh"]
    resultado["spread_ES_DE"] = df["precio_ES_EUR_MWh"] - df["precio_DE_EUR_MWh"]

    # Calculamos el spread absoluto (sin importar quién tiene precio mayor)
    resultado["spread_abs_ES_FR"] = resultado["spread_ES_FR"].abs()
    resultado["spread_abs_FR_DE"] = resultado["spread_FR_DE"].abs()
    resultado["spread_abs_ES_DE"] = resultado["spread_ES_DE"].abs()

    # Marcamos las horas con precios convergentes
    # Definimos convergencia como spread absoluto < 5 EUR/MWh
    UMBRAL_CONVERGENCIA = 5  # EUR/MWh

    resultado["convergencia_ES_FR"] = resultado["spread_abs_ES_FR"] < UMBRAL_CONVERGENCIA
    resultado["convergencia_FR_DE"] = resultado["spread_abs_FR_DE"] < UMBRAL_CONVERGENCIA

    # Estadísticas globales del spread
    print("\nEstadísticas del spread ES-FR (EUR/MWh):")
    print(resultado["spread_ES_FR"].describe().round(2))

    print("\nEstadísticas del spread FR-DE (EUR/MWh):")
    print(resultado["spread_FR_DE"].describe().round(2))

    # Resumen mensual de convergencia
    resumen = resultado.resample("ME").agg(
        spread_medio_ES_FR=("spread_abs_ES_FR", "mean"),
        spread_medio_FR_DE=("spread_abs_FR_DE", "mean"),
        spread_medio_ES_DE=("spread_abs_ES_DE", "mean"),
        horas_convergencia_ES_FR=("convergencia_ES_FR", "sum"),
        horas_convergencia_FR_DE=("convergencia_FR_DE", "sum"),
        spread_maximo_ES_FR=("spread_abs_ES_FR", "max"),
        spread_maximo_FR_DE=("spread_abs_FR_DE", "max"),
    ).round(2)

    print("\nResumen mensual de convergencia:")
    print(resumen)

    # Calculamos el porcentaje de horas con convergencia
    horas_totales = len(resultado)
    pct_conv_es_fr = resultado["convergencia_ES_FR"].sum() / horas_totales * 100
    pct_conv_fr_de = resultado["convergencia_FR_DE"].sum() / horas_totales * 100

    print(f"\nPorcentaje de horas con precios convergentes (<{UMBRAL_CONVERGENCIA} EUR/MWh):")
    print(f"  ES-FR: {pct_conv_es_fr:.1f}%")
    print(f"  FR-DE: {pct_conv_fr_de:.1f}%")

    # Guardamos resultados
    ruta_detalle = os.path.join(CARPETA_RESULTADOS, "convergencia_detalle.csv")
    ruta_resumen = os.path.join(CARPETA_RESULTADOS, "convergencia_mensual.csv")
    resultado.to_csv(ruta_detalle)
    resumen.to_csv(ruta_resumen)
    print(f"\n✓ Guardado en {ruta_detalle}")
    print(f"✓ Guardado en {ruta_resumen}")

    return resultado, resumen
# -------------------------------------------------------------
# INDICADOR 2: CONGESTIONES
# -------------------------------------------------------------

def analizar_congestiones(df):
    """
    Detecta horas en que las interconexiones estaban congestionadas.
    Una congestión ocurre cuando el flujo real supera el 90%
    de la capacidad máxima de la línea (NTC).
    """

    print("\n--- ANÁLISIS DE CONGESTIONES ---")

    resultado = pd.DataFrame(index=df.index)

    # Porcentaje de uso de cada interconexión
    resultado["uso_ES_FR_pct"] = (
        df["flujo_ES_FR_MWh"].abs() / df["ntc_ES_FR_MW"] * 100
    ).round(1)

    resultado["uso_FR_DE_pct"] = (
        df["flujo_FR_DE_MWh"].abs() / df["ntc_FR_DE_MW"] * 100
    ).round(1)

    # Horas congestionadas (uso >= 90%)
    UMBRAL = 90
    resultado["congestion_ES_FR"] = resultado["uso_ES_FR_pct"] >= UMBRAL
    resultado["congestion_FR_DE"] = resultado["uso_FR_DE_pct"] >= UMBRAL

    # Resumen por mes
    resumen = resultado.resample("ME").agg(
        horas_congestion_ES_FR=("congestion_ES_FR", "sum"),
        horas_congestion_FR_DE=("congestion_FR_DE", "sum"),
        uso_medio_ES_FR=("uso_ES_FR_pct", "mean"),
        uso_medio_FR_DE=("uso_FR_DE_pct", "mean"),
        uso_maximo_ES_FR=("uso_ES_FR_pct", "max"),
        uso_maximo_FR_DE=("uso_FR_DE_pct", "max"),
    ).round(1)

    print("\nResumen mensual de congestiones:")
    print(resumen)

    top = resultado["uso_ES_FR_pct"].nlargest(10)
    print("\nTop 10 horas de mayor uso en ES→FR (%):")
    print(top)

    ruta_detalle = os.path.join(CARPETA_RESULTADOS, "congestiones_detalle.csv")
    ruta_resumen = os.path.join(CARPETA_RESULTADOS, "congestiones_mensual.csv")
    resultado.to_csv(ruta_detalle)
    resumen.to_csv(ruta_resumen)

    print(f"\n✓ Guardado: {ruta_detalle}")
    print(f"✓ Guardado: {ruta_resumen}")

    return resultado, resumen

# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL (esqueleto — tus compañeras añadirán sus partes)
# -------------------------------------------------------------

def analizar_todo():
    print("=" * 50)
    print("INICIANDO ANÁLISIS — GRUPO 4")
    print("=" * 50)

    df = cargar_datos_limpios()
    if df is None:
        return

    analizar_importexport(df)
    analizar_correlacion(df)
    analizar_convergencia(df)
    analizar_congestiones(df)
    print("\n" + "=" * 50)
    print("ANÁLISIS COMPLETADO")
    print("=" * 50)


if __name__ == "__main__":
    analizar_todo()