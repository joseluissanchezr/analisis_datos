# =============================================================
# bonus_storage.py
# BONUS 1 — Almacenamiento Energético
# Grupo 4 — Intercambios Internacionales
# =============================================================
# Simula un sistema simplificado de baterías que aprovecha
# las diferencias de precio para hacer arbitraje energético.
#
# Lógica:
#   - Carga la batería cuando el precio está por debajo de la mediana
#   - Descarga la batería cuando el precio está por encima de la mediana
#   - Calcula el beneficio teórico por país
# =============================================================

import os
import pandas as pd
import numpy as np

# -------------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------------

CARPETA_PROCESSED = os.path.join("group4-2026", "data", "Processed")
CARPETA_RESULTADOS = os.path.join("group4-2026", "data", "Processed", "resultados")

os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

# Parámetros de la batería
CAPACIDAD_MWH = 100        # capacidad máxima de la batería en MWh
POTENCIA_MW = 25           # potencia máxima de carga/descarga en MW por hora
EFICIENCIA = 0.90          # eficiencia del ciclo carga/descarga (90%)

# -------------------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------------------

def cargar_precios():
    """
    Carga los precios day-ahead de datos_limpios.csv
    """
    ruta = os.path.join(CARPETA_PROCESSED, "datos_limpios.csv")

    if not os.path.exists(ruta):
        print("✗ No se encontró datos_limpios.csv")
        print("  Ejecuta primero clean.py")
        return None

    df = pd.read_csv(ruta, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True)

    precios = df[["precio_ES_EUR_MWh", "precio_FR_EUR_MWh", "precio_DE_EUR_MWh"]].copy()
    print(f"✓ Precios cargados: {len(precios)} filas")
    return precios


# -------------------------------------------------------------
# SIMULACIÓN DE BATERÍA
# -------------------------------------------------------------

def simular_bateria(precios_serie, nombre_pais):
    """
    Simula el comportamiento de una batería de almacenamiento
    usando una estrategia de arbitraje simple basada en la mediana.

    Estrategia:
        - Si precio < mediana → CARGAR (compramos energía barata)
        - Si precio > mediana → DESCARGAR (vendemos energía cara)
        - Si precio == mediana → no hacemos nada

    Parámetros:
        precios_serie: Serie de pandas con los precios horarios
        nombre_pais  : Nombre del país para mostrar en pantalla

    Retorna:
        DataFrame con el estado de la batería hora a hora
    """

    print(f"\nSimulando batería para {nombre_pais}...")

    mediana = precios_serie.median()
    print(f"  Precio mediano: {mediana:.2f} EUR/MWh")

    resultado = pd.DataFrame(index=precios_serie.index)
    resultado["precio"] = precios_serie

    # Estado de la batería (MWh almacenados)
    estado = []
    energia_actual = 0.0

    # Flujo de energía (+ = carga, - = descarga)
    flujo = []

    # Beneficio acumulado
    beneficio = []
    beneficio_acumulado = 0.0

    for precio in precios_serie:
        if precio < mediana and energia_actual < CAPACIDAD_MWH:
            # CARGAR: compramos energía barata
            energia_cargada = min(POTENCIA_MW, CAPACIDAD_MWH - energia_actual)
            energia_actual += energia_cargada * EFICIENCIA
            coste = energia_cargada * precio
            beneficio_acumulado -= coste
            flujo.append(energia_cargada)

        elif precio > mediana and energia_actual > 0:
            # DESCARGAR: vendemos energía cara
            energia_descargada = min(POTENCIA_MW, energia_actual) * EFICIENCIA
            energia_actual -= energia_descargada
            ingreso = energia_descargada * precio
            beneficio_acumulado += ingreso
            flujo.append(-energia_descargada)

        else:
            # No hacemos nada
            flujo.append(0)

        estado.append(energia_actual)
        beneficio.append(beneficio_acumulado)

    resultado["estado_bateria_MWh"] = estado
    resultado["flujo_MW"] = flujo
    resultado["beneficio_acumulado_EUR"] = beneficio

    return resultado


# -------------------------------------------------------------
# ANÁLISIS DE RESULTADOS
# -------------------------------------------------------------

def analizar_resultados(resultado, nombre_pais):
    """
    Calcula y muestra las métricas principales de la simulación.
    """

    beneficio_total = resultado["beneficio_acumulado_EUR"].iloc[-1]
    horas_cargando = (resultado["flujo_MW"] > 0).sum()
    horas_descargando = (resultado["flujo_MW"] < 0).sum()
    energia_max = resultado["estado_bateria_MWh"].max()

    print(f"\n  Resultados {nombre_pais}:")
    print(f"    Beneficio total    : {beneficio_total:,.0f} EUR")
    print(f"    Horas cargando     : {horas_cargando}")
    print(f"    Horas descargando  : {horas_descargando}")
    print(f"    Energía máx. almac.: {energia_max:.1f} MWh")

    # Resumen mensual
    resumen = resultado.resample("ME").agg(
        beneficio_mensual=("beneficio_acumulado_EUR", lambda x: x.iloc[-1] - x.iloc[0]),
        horas_cargando=("flujo_MW", lambda x: (x > 0).sum()),
        horas_descargando=("flujo_MW", lambda x: (x < 0).sum()),
        precio_medio=("precio", "mean"),
    ).round(2)

    return resumen, beneficio_total


# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------

def simular_todo():
    print("=" * 50)
    print("BONUS 1 — SIMULACIÓN DE ALMACENAMIENTO")
    print(f"Capacidad: {CAPACIDAD_MWH} MWh | Potencia: {POTENCIA_MW} MW | Eficiencia: {EFICIENCIA*100:.0f}%")
    print("=" * 50)

    precios = cargar_precios()
    if precios is None:
        return

    paises = {
        "España":   "precio_ES_EUR_MWh",
        "Francia":  "precio_FR_EUR_MWh",
        "Alemania": "precio_DE_EUR_MWh",
    }

    resumen_global = {}

    for nombre, columna in paises.items():
        resultado = simular_bateria(precios[columna], nombre)
        resumen_mensual, beneficio_total = analizar_resultados(resultado, nombre)

        resumen_global[nombre] = beneficio_total

        # Guardamos los resultados detallados
        ruta = os.path.join(CARPETA_RESULTADOS, f"storage_{nombre.lower()}.csv")
        resultado.to_csv(ruta)
        resumen_mensual.to_csv(
            os.path.join(CARPETA_RESULTADOS, f"storage_{nombre.lower()}_mensual.csv")
        )
        print(f"  ✓ Guardado en {ruta}")

    # Comparativa entre países
    print("\n" + "=" * 50)
    print("COMPARATIVA DE BENEFICIO TEÓRICO POR PAÍS")
    print("=" * 50)
    for pais, beneficio in resumen_global.items():
        print(f"  {pais:10}: {beneficio:>12,.0f} EUR")

    # Guardamos comparativa
    df_comparativa = pd.DataFrame(
        list(resumen_global.items()),
        columns=["Pais", "Beneficio_EUR"]
    )
    ruta_comp = os.path.join(CARPETA_RESULTADOS, "storage_comparativa.csv")
    df_comparativa.to_csv(ruta_comp, index=False)
    print(f"\n✓ Comparativa guardada en {ruta_comp}")
    print("=" * 50)


# -------------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------------

if __name__ == "__main__":
    simular_todo()