import requests
import pandas as pd
import time
import os
import re
import unicodedata
import csv
from datetime import datetime

def filtrar_y_guardar(df, tipo_int, ruta_csv):
    # Función para limpiar valores tipo "28.4(01)" o "28/22.2(01)"
    def limpiar_valor(v):
        if isinstance(v, str):
            v = v.strip()
            if '/' in v:
                partes = v.split('/')
                v = partes[-1]
            v = re.sub(r"\(.*?\)", "", v)
            v = v.replace(',', '.')
        try:
            return float(v)
        except:
            return None

    match tipo_int:
        case 1:  # Climatología diaria
            columnas_viento = ["fecha", "estacion", "velmedia", "racha", "dir_racha"]
            df_viento = df[columnas_viento].copy()
            def es_valido_diario(row):
                try:
                    return (0 <= float(row["velmedia"]) <= 150 and
                            0 <= float(row["racha"]) <= 300 and
                            0 <= float(row["dir_racha"]) <= 360)
                except:
                    return False
            df_limpio = df_viento[df_viento.apply(es_valido_diario, axis=1)]

        case 2:  # Climatología mensual/anual
            columnas_viento = ["fecha", "estacion", "w_racha", "w_med", "w_rec"]
            df_viento = df[columnas_viento].copy()
            df_viento["fecha"] = pd.to_datetime(df_viento["fecha"].astype(str) + "-01", format="%Y-%m-%d", errors="coerce")
            df_viento["mes_anio"] = df_viento["fecha"].dt.strftime("%Y-%m")
            for col in ["w_racha", "w_med", "w_rec"]:
                df_viento[col] = df_viento[col].apply(limpiar_valor)
            def es_valido_mensual(row):
                try:
                    return (0 <= float(row["w_racha"]) <= 300 and
                            0 <= float(row["w_med"]) <= 150 and
                            0 <= float(row["w_rec"]) <= 300)
                except:
                    return False
            df_limpio = df_viento[df_viento.apply(es_valido_mensual, axis=1)]
            df_limpio = df_limpio.sort_values(by="mes_anio")
            df_limpio["fecha"] = df_limpio["mes_anio"]
            df_limpio = df_limpio.drop(columns=["mes_anio"])

        case 3:  # Extremos registrados
            cols_requeridas = ["rachMax_kmh", "dirRachMax_grados", "fecha_ocurrencia"]
            if not all(col in df.columns for col in cols_requeridas):
                print("⚠️ Datos no tienen las columnas esperadas para filtro de extremos registrados.")
                df_limpio = df.copy()
            else:
                df["fecha_ocurrencia"] = pd.to_datetime(df["fecha_ocurrencia"], errors="coerce")

                def valido_extremo(row):
                    try:
                        return (
                            0 <= float(row["rachMax_kmh"]) <= 300 and
                            0 <= float(row["dirRachMax_grados"]) <= 360 and
                            pd.notnull(row["fecha_ocurrencia"])
                        )
                    except:
                        return False

                df_limpio = df[df.apply(valido_extremo, axis=1)]

        case 4:  # Valores normales
        # Lista de columnas relevantes del viento
            columnas_viento = [
        "w_racha_max", "w_racha_min", "w_racha_md", "w_racha_cv",
        "w_med_max", "w_med_min", "w_med_md", "w_med_cv",
        "w_med_n", "w_med_s"
            ]

    # Filtra solo las columnas de viento presentes en el DataFrame
            columnas_presentes = [col for col in columnas_viento if col in df.columns]

    # Aplica limpieza y convierte a float
            for col in columnas_presentes:
                df[col] = df[col].apply(limpiar_valor)

    # Filtro: viento entre 0 y 200 (puedes ajustar)
            def es_valido_viento(row):
                try:
                    return all(0 <= row[col] <= 200 for col in columnas_presentes if pd.notnull(row[col]))
                except:
                    return False

    # Filtra el DataFrame con los datos válidos
            df_limpio = df[df.apply(es_valido_viento, axis=1)]

        case _:
            print("❌ Tipo de archivo no soportado para filtrado.")
            return

    salida = os.path.splitext(ruta_csv)[0] + "_viento_limpio.csv"
    df_limpio.to_csv(salida, index=False, sep=';', decimal=',', quoting=csv.QUOTE_NONNUMERIC)
    print(f"✅ Guardado {len(df_limpio)} registros válidos en: {salida}")


