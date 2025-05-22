import requests
import pandas as pd
import time
import os
import re
import unicodedata
import csv
from datetime import datetime

# Configuración inicial de la API AEMET
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqaW5lbGEuZ29uemFsZXpAYWx1bW5vcy51cG0uZXMiLCJqdGkiOiJmZjU4ZTJlNi1iMjVhLTQ1ZTAtYTUzYi0xZDBmNDY3OGJhZDgiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc0NjgyMjkxNywidXNlcklkIjoiZmY1OGUyZTYtYjI1YS00NWUwLWE1M2ItMWQwZjQ2NzhiYWQ4Iiwicm9sZSI6IiJ9.Cy_fCJ8NZSgQHadQEOoH-feniDOlu6CgaJ1ZBFX4y5c"
BASE_URL = "https://opendata.aemet.es/opendata/api"

def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^0-9A-Za-z]+', '_', text)
    return text.strip('_').lower()

def seleccionar_opcion(opciones, mensaje):
    print(f"\n{mensaje}")
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")
    while True:
        try:
            idx = int(input("Seleccione una opción: ").strip())
            if 1 <= idx <= len(opciones):
                return opciones[idx - 1]
            else:
                print(f"Por favor, ingrese un número entre 1 y {len(opciones)}")
        except:
            print("Entrada inválida. Intente de nuevo.")

def obtener_estaciones():
    path = "/valores/climatologicos/inventarioestaciones/todasestaciones"
    resp = requests.get(BASE_URL + path, params={"api_key": API_KEY})
    resp.raise_for_status()
    datos_url = resp.json().get("datos")
    return requests.get(datos_url).json()

def filtrar_provincia(estaciones, provincia):
    return [e for e in estaciones if e.get("provincia") == provincia]

def pedir_parametros(tipo):
    params = {}
    if tipo == "Climatologías diarias":
        while True:
            start = input("Fecha inicio (YYYY-MM-DD): ").strip()
            end = input("Fecha fin    (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
                params.update({"start": start, "end": end})
                break
            except ValueError:
                print("Formato de fecha inválido. Use YYYY-MM-DD")
    elif tipo == "Climatologías mensuales/anuales":
        current_year = datetime.now().year
        while True:
            year = input(f"Año (1900-{current_year}): ").strip()
            if year.isdigit() and 1900 <= int(year) <= current_year:
                params["year"] = year
                break
            print(f"Año inválido. Debe ser entre 1900 y {current_year}")
    return params

def obtener_url_datos(tipo, estacion_id, **kw):
    if tipo == "Climatologías diarias":
        ini = f"{kw['start']}T00:00:00UTC"
        fin = f"{kw['end']}T23:59:59UTC"
        path = f"/valores/climatologicos/diarios/datos/fechaini/{ini}/fechafin/{fin}/estacion/{estacion_id}"
    elif tipo == "Climatologías mensuales/anuales":
        year = kw['year']
        path = f"/valores/climatologicos/mensualesanuales/datos/anioini/{year}/aniofin/{year}/estacion/{estacion_id}"
    elif tipo == "Valores normales":
        path = f"/valores/climatologicos/normales/estacion/{estacion_id}"
    elif tipo == "Extremos registrados":
        parametro = "V"
        path = f"/valores/climatologicos/valoresextremos/parametro/{parametro}/estacion/{estacion_id}/"
    else:
        raise ValueError("Tipo no soportado")

    resp = requests.get(BASE_URL + path, params={"api_key": API_KEY})
    resp.raise_for_status()
    j = resp.json()
    if "datos" not in j:
        raise RuntimeError(f"AEMET error {j.get('estado')}: {j.get('descripcion')}")
    return j["datos"]

def descargar_json(datos_url):
    resp = requests.get(datos_url)
    resp.raise_for_status()
    return resp.json()

def procesar_registros(tipo, records):
    if tipo == "Extremos registrados":
        n_registros = len(records["rachMax"])
        return pd.DataFrame({
            "estacion": [records["indicativo"]] * n_registros,
            "ubicacion": [records["ubicacion"]] * n_registros,
            "mes": [records["mes"]] * n_registros,
            "rachMax_kmh": list(map(int, records["rachMax"])),
            "dirRachMax_grados": list(map(int, records["dirRachMax"])),
            "hora": records["hora"],
            "dia": list(map(int, records["dia"])),
            "anio": list(map(int, records["anio"])),
            "fecha_ocurrencia": [
                f"{a}-{m}-{str(d).zfill(2)}" 
                for a, m, d in zip(
                    records["anio"], 
                    [records["mes"]] * n_registros, 
                    records["dia"]
                )
            ]
        })
    elif tipo == "Valores normales":
        rows = []
        for registro in records:
            fila = {
                "estacion": registro.get("indicativo"),
                "fecha": registro.get("fecha")
            }
            for clave, valor in registro.items():
                if clave not in ["indicativo", "fecha"]:
                    fila[clave] = valor
            rows.append(fila)
        return pd.DataFrame(rows)
    elif tipo == "Climatologías mensuales/anuales":
        rows = []
        for registro in records:
            fila = {
                "estacion": registro.get("indicativo"),
                "fecha": registro.get("fecha")
            }
            for clave, valor in registro.items():
                if clave not in ["indicativo", "fecha"]:
                    fila[clave] = valor
            rows.append(fila)
        return pd.DataFrame(rows)
    else:
        rows = []
        for r in records:
            base = {"estacion": r.get("indicativo"), "fecha": r.get("fecha")}
            if tipo == "Climatologías diarias":
                if r.get("velmedia") is None: 
                    continue
                base.update({
                    "tmed": float(str(r.get("tmed", "")).replace(",", ".")) if r.get("tmed") else None,
                    "prec": float(str(r.get("prec", "")).replace(",", ".")) if r.get("prec") else None,
                    "velmedia": float(str(r.get("velmedia", "")).replace(",", ".")),
                    "racha": float(str(r.get("racha", "")).replace(",", ".")) if r.get("racha") else None,
                    "dir_racha": r.get("dir")
                })
            rows.append(base)
        return pd.DataFrame(rows)

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

def main():
    print("\n=== DESCARGA AEMET INTERACTIVA ===")
    tipos = [
        "Climatologías diarias",
        "Climatologías mensuales/anuales",
        "Valores normales",
        "Extremos registrados"
    ]
    tipo = seleccionar_opcion(tipos, "¿Qué datos desea obtener?")
    tipo_map = {
        "Climatologías diarias": 1,
        "Climatologías mensuales/anuales": 2,
        "Valores normales": 4,
        "Extremos registrados": 3,
    }
    tipo_int = tipo_map[tipo]

    estaciones = obtener_estaciones()
    provincias = sorted({e["provincia"] for e in estaciones if e.get("provincia")})
    provincia = seleccionar_opcion(provincias, "Seleccione una provincia:")
    estaciones_prov = filtrar_provincia(estaciones, provincia)
    listado = [f"{e['nombre']} ({e['indicativo']})" for e in estaciones_prov]
    esc = seleccionar_opcion(listado, "Seleccione una estación:")
    estacion_id = esc.split("(")[-1].strip(")")

    params = pedir_parametros(tipo)
    print("\n📡 Solicitando URL de descarga...")
    url_datos = obtener_url_datos(tipo, estacion_id, **params)
    time.sleep(1)
    print("📥 Descargando datos...")
    records = descargar_json(url_datos)

    df = procesar_registros(tipo, records)
    output_dir = os.path.expanduser(r"~\Documents\AEMET_output")
    os.makedirs(output_dir, exist_ok=True)
    nombre_csv = os.path.join(output_dir, slugify(tipo) + ".csv")
    df.to_csv(nombre_csv, index=False, sep=';', decimal=',', quoting=csv.QUOTE_NONNUMERIC)
    print(f"📥 Guardado datos originales en '{nombre_csv}'")

    filtrar_y_guardar(df, tipo_int, nombre_csv)

if __name__ == "__main__":
    main()
