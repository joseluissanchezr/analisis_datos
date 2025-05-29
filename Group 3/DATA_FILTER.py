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

    df_limpio = None

    match tipo_int:
        case 1:  # Climatología diaria
            columnas_viento = ["fecha", "estacion", "velmedia", "racha", "dir_racha"]
            if not all(col in df.columns for col in columnas_viento):
                print("⚠️ Falta alguna columna para climatología diaria.")
                return None
            df_viento = df[columnas_viento].copy()

            def es_valido_diario(row):
                try:
                    return (0 <= row["velmedia"] <= 150 and
                            0 <= row["racha"] <= 300 and
                            0 <= row["dir_racha"] <= 360)
                except:
                    return False

            df_limpio = df_viento[df_viento.apply(es_valido_diario, axis=1)]

        case 2:  # Climatología mensual/anual
            columnas_viento = ["fecha", "estacion", "w_racha", "w_med", "w_rec"]
            if not all(col in df.columns for col in columnas_viento):
                print("⚠️ Falta alguna columna para climatología mensual/anual.")
                return None
            df_viento = df[columnas_viento].copy()
            df_viento["fecha"] = pd.to_datetime(
                df_viento["fecha"].astype(str) + "-01",
                format="%Y-%m-%d", errors="coerce"
            )
            df_viento["mes_anio"] = df_viento["fecha"].dt.strftime("%Y-%m")
            for col in ["w_racha", "w_med", "w_rec"]:
                df_viento[col] = df_viento[col].apply(limpiar_valor)

            def es_valido_mensual(row):
                try:
                    return (0 <= row["w_racha"] <= 300 and
                            0 <= row["w_med"] <= 150 and
                            0 <= row["w_rec"] <= 300)
                except:
                    return False

            df_limpio = df_viento[df_viento.apply(es_valido_mensual, axis=1)].copy()
            df_limpio = df_limpio.sort_values(by="mes_anio")
            df_limpio["fecha"] = df_limpio["mes_anio"]
            df_limpio = df_limpio.drop(columns=["mes_anio"])

        case 3:  # Extremos registrados
            cols_requeridas = ["rachMax_kmh", "dirRachMax_grados", "fecha_ocurrencia"]
            if not all(col in df.columns for col in cols_requeridas):
                print("⚠️ Falta alguna columna para extremos registrados.")
                return None
            df_ext = df.copy()
            df_ext["fecha_ocurrencia"] = pd.to_datetime(df_ext["fecha_ocurrencia"], errors="coerce")

            def valido_extremo(row):
                try:
                    return (
                        0 <= row["rachMax_kmh"] <= 300 and
                        0 <= row["dirRachMax_grados"] <= 360 and
                        pd.notnull(row["fecha_ocurrencia"])
                    )
                except:
                    return False

            df_limpio = df_ext[df_ext.apply(valido_extremo, axis=1)].copy()

        case 4:  # Valores normales
            columnas_viento = [
                "w_racha_max", "w_racha_min", "w_racha_md", "w_racha_cv",
                "w_med_max", "w_med_min", "w_med_md", "w_med_cv",
                "w_med_n", "w_med_s"
            ]
            columnas_presentes = [col for col in columnas_viento if col in df.columns]
            if not columnas_presentes:
                print("⚠️ No hay columnas de viento en valores normales.")
                return None

            # Limpieza
            for col in columnas_presentes:
                df[col] = df[col].apply(limpiar_valor)

            def es_valido_viento(row):
                try:
                    return all(0 <= row[col] <= 200 for col in columnas_presentes if pd.notnull(row[col]))
                except:
                    return False

            df_limpio = df[df.apply(es_valido_viento, axis=1)].copy()
            # Mantener solo fecha, estacion y viento
            columnas_salida = [c for c in ["fecha", "estacion"] + columnas_presentes if c in df_limpio.columns]
            df_limpio = df_limpio[columnas_salida]

        case _:
            print("❌ Tipo de archivo no soportado para filtrado.")
            return None

    # Guardado y retorno
    if df_limpio is not None and not df_limpio.empty:
        salida = os.path.splitext(ruta_csv)[0] + "_viento_limpio.csv"
        df_limpio.to_csv(salida, index=False, sep=';', decimal=',', quoting=csv.QUOTE_NONNUMERIC)
        print(f"✅ Guardado {len(df_limpio)} registros válidos en: {salida}")
        return df_limpio
    else:
        print("⚠️ Tras el filtrado, no quedaron registros válidos.")
        return None

