import requests
import pandas as pd
import time
import os
import re
import unicodedata
import csv

# Tu API key de AEMET:
API_KEY  = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqaW5lbGEuZ29uemFsZXpAYWx1bW5vcy51cG0uZXMiLCJqdGkiOiJmZjU4ZTJlNi1iMjVhLTQ1ZTAtYTUzYi0xZDBmNDY3OGJhZDgiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc0NjgyMjkxNywidXNlcklkIjoiZmY1OGUyZTYtYjI1YS00NWUwLWE1M2ItMWQwZjQ2NzhiYWQ4Iiwicm9sZSI6IiJ9.Cy_fCJ8NZSgQHadQEOoH-feniDOlu6CgaJ1ZBFX4y5c"
BASE_URL = "https://opendata.aemet.es/opendata/api"


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^0-9A-Za-z]+', '_', text)
    return text.strip('_').lower()


def seleccionar_opcion(opciones, mensaje):
    print(f"\n{mensaje}")
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")
    idx = int(input("Seleccione una opción: ").strip())
    return opciones[idx - 1]


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
        params["start"] = input("Fecha inicio (YYYY-MM-DD): ").strip()
        params["end"]   = input("Fecha fin    (YYYY-MM-DD): ").strip()
    elif tipo == "Climatologías mensuales/anuales":
        params["year"] = input("Año (YYYY): ").strip()
    # Para Valores normales y Extremos registrados no pedimos más parámetros
    return params


def obtener_url_datos(tipo, estacion_id, **kw):
    if tipo == "Climatologías diarias":
        ini = f"{kw['start']}T00:00:00UTC"
        fin = f"{kw['end']}T23:59:59UTC"
        path = f"/valores/climatologicos/diarios/datos/fechaini/{ini}/fechafin/{fin}/estacion/{estacion_id}"
    elif tipo == "Climatologías mensuales/anuales":
        year = kw['year']
        path = f"/valores/climatologicos/diarios/anio/{year}/estacion/{estacion_id}"
    elif tipo == "Valores normales":
        path = f"/valores/climatologicos/normales/anio/{estacion_id}"
        # La API no requiere año, devuelve todos los años disponibles
    elif tipo == "Extremos registrados":
        # Selección automática de valores de viento: velmedia
        start = "0000-01-01"
        end   = "9999-12-31"
        var   = "velmedia"
        # Nota: el orden debe ser estacion antes de variable para evitar 404
        path = (
            f"/valores/climatologicos/extremos/fechaini/{start}T00:00:00UTC/"
            f"fechafin/{end}T23:59:59UTC/estacion/{estacion_id}/variable/{var}"
        )
    else:
        raise ValueError("Tipo no soportado")
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
    rows = []
    for r in records:
        base = {"estacion": r.get("indicativo"), "fecha": r.get("fecha")}
        if tipo == "Climatologías diarias":
            if r.get("velmedia") is None: continue
            base.update({
                "velmedia_m_s": float(str(r["velmedia"]).replace(",", ".")),
                "racha_m_s":    float(str(r.get("racha")).replace(",", ".")) if r.get("racha") else None,
                "dir_racha":    float(str(r.get("dir")).replace(",", "."))   if r.get("dir")   else None,
            })
        elif tipo == "Extremos registrados":
            base.update({"valor": r.get("valor"), "unidad": r.get("unidad")})
        else:
            rows.append({**base, **r}); continue
        rows.append(base)
    return pd.DataFrame(rows)


def main():
    print("\n=== DESCARGA AEMET INTERACTIVA ===")
    tipos = [
        "Climatologías diarias",
        "Climatologías mensuales/anuales",
        "Valores normales",
        "Extremos registrados"
    ]
    tipo = seleccionar_opcion(tipos, "¿Qué datos desea obtener?")

    estaciones = obtener_estaciones()
    provincias = sorted({e["provincia"] for e in estaciones if e.get("provincia")})
    provincia = seleccionar_opcion(provincias, "Seleccione una provincia:")
    estaciones_prov = filtrar_provincia(estaciones, provincia)
    listado = [f"{e['nombre']} ({e['indicativo']})" for e in estaciones_prov]
    esc = seleccionar_opcion(listado, "Seleccione una estación:")
    estacion_id = esc.split("(")[-1].strip(")")

    params = pesar_parametros = pedir_parametros(tipo)
    url_datos = obtener_url_datos(tipo, estacion_id, **params)
    print("\n📥 Descargando datos...")
    records = descargar_json(url_datos)

    df = procesar_registros(tipo, records)
    output_dir = os.path.expanduser(r"~\Documents\AEMET_output")
    os.makedirs(output_dir, exist_ok=True)
    nombre_csv = os.path.join(output_dir, slugify(tipo) + ".csv")
    df.to_csv(nombre_csv, index=False, sep=';', decimal=',', quoting=csv.QUOTE_NONE, escapechar='\\')
    print(f"✅ Guardado {len(df)} registros en '{nombre_csv}'")

if __name__ == "__main__":
    main()
