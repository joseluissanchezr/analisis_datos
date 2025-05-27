
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
            # Filtrado según valores válidos de ráfaga, dirección y fecha
            cols_requeridas = ["rachMax_kmh", "dirRachMax_grados", "fecha_ocurrencia"]
            if not all(col in df.columns for col in cols_requeridas):
                print("⚠️ Datos no tienen las columnas esperadas para filtro extremos registrados.")
                df_limpio = df.copy()
            else:
                def valido_extremo(row):
                    try:
                        return (0 <= float(row["rachMax_kmh"]) <= 300 and
                                0 <= float(row["dirRachMax_grados"]) <= 360 and
                                datetime.strptime(row["fecha_ocurrencia"], "%Y-%m-%d"))
                    except:
                        return False
                df_limpio = df[df.apply(valido_extremo, axis=1)]

        case 4:  # Valores normales
            # Asumiendo estructura similar, validamos que ciertas columnas sean numéricas y plausibles
            # Puedes ajustar columnas y rangos según datos reales
            cols_numericas = [col for col in df.columns if col not in ["estacion", "fecha"]]
            for col in cols_numericas:
                df[col] = df[col].apply(limpiar_valor)
            # Filtro ejemplo: valores entre 0 y 300 para todos los numéricos
            def valido_normal(row):
                try:
                    return all(0 <= (row[col] if row[col] is not None else 0) <= 300 for col in cols_numericas)
                except:
                    return False
            df_limpio = df[df.apply(valido_normal, axis=1)]

        case _:
            print("❌ Tipo de archivo no soportado para filtrado.")
            return

    salida = os.path.splitext(ruta_csv)[0] + "_viento_limpio.csv"
    df_limpio.to_csv(salida, index=False, sep=';', decimal=',', quoting=csv.QUOTE_NONNUMERIC)
    print(f"✅ Guardado {len(df_limpio)} registros válidos en: {salida}")


