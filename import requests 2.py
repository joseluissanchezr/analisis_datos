import requests
import pandas as pd
import time

API_KEY  = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqaW5lbGEuZ29uemFsZXpAYWx1bW5vcy51cG0uZXMiLCJqdGkiOiJmZjU4ZTJlNi1iMjVhLTQ1ZTAtYTUzYi0xZDBmNDY3OGJhZDgiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc0NjgyMjkxNywidXNlcklkIjoiZmY1OGUyZTYtYjI1YS00NWUwLWE1M2ItMWQwZjQ2NzhiYWQ4Iiwicm9sZSI6IiJ9.Cy_fCJ8NZSgQHadQEOoH-feniDOlu6CgaJ1ZBFX4y5c"
BASE_URL = "https://opendata.aemet.es/opendata/api"


def seleccionar_opcion(opciones, mensaje):
    """Muestra un menú numerado y devuelve la opción elegida."""
    print("\n" + mensaje)
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")
    idx = int(input("Seleccione una opción: ").strip())
    return opciones[idx - 1]


def obtener_estaciones():
    """
    Obtiene el inventario completo de estaciones climatológicas (todasestaciones).
    Devuelve una lista de dicts con 'indicativo', 'nombre' y 'provincia'.
    """
    path = "/valores/climatologicos/inventarioestaciones/todasestaciones"
    resp = requests.get(BASE_URL + path, params={"api_key": API_KEY})
    resp.raise_for_status()
    datos_url = resp.json()["datos"]
    estaciones = requests.get(datos_url).json()
    return estaciones


def filtrar_provincia(estaciones, provincia):
    return [e for e in estaciones if e.get("provincia") == provincia]


def pedir_parametros(tipo):
    """
    Según el tipo de dato, pide fechas / año / variable extra.
    Devuelve un dict con los parámetros.
    """
    params = {}
    if tipo == "Climatologías diarias":
        params["start"] = input("Fecha inicio (YYYY-MM-DD): ").strip()
        params["end"]   = input("Fecha fin    (YYYY-MM-DD): ").strip()
    elif tipo == "Climatologías mensuales/anuales":
        params["start"] = input("Fecha inicio (YYYY-MM-DD): ").strip()
        params["end"]   = input("Fecha fin    (YYYY-MM-DD): ").strip()
    elif tipo == "Valores normales":
        params["year"] = input("Año (AAAA): ").strip()
    elif tipo == "Extremos registrados":
        params["start"]   = input("Fecha inicio (YYYY-MM-DD): ").strip()
        params["end"]     = input("Fecha fin    (YYYY-MM-DD): ").strip()
        # por simplicidad, pedimos la misma variable usada en AEMET:
        vars_disp = ["tmax", "tmin", "prec", "velmedia", "racha", "dir"]
        params["variable"] = seleccionar_opcion(vars_disp, "Seleccione variable para extremos:")
    return params


def obtener_url_datos(tipo, estacion_id, **kw):
    """
    Construye el endpoint correcto según el tipo y los parámetros.
    Devuelve la URL de descarga en kw['datos'].
    """
    if tipo == "Climatologías diarias":
        ini = f"{kw['start']}T00:00:00UTC"
        fin = f"{kw['end']}T23:59:59UTC"
        path = (f"/valores/climatologicos/diarios/datos/"
                f"fechaini/{ini}/fechafin/{fin}/estacion/{estacion_id}")
    elif tipo == "Climatologías mensuales/anuales":
        # ejemplo: /valores/climatologicos/diarios/anio/{AAAA}/estacion/{id}
        ini = f"{kw['start']}T00:00:00UTC"
        fin = f"{kw['end']}T23:59:59UTC"
        path = (f"/valores/climatologicos/diarios/datos/"
                f"fechaini/{ini}/fechafin/{fin}/estacion/{estacion_id}")
    elif tipo == "Valores normales":
        path = (f"/valores/climatologicos/normales/anio/{kw['year']}"
                f"/estacion/{estacion_id}")
    elif tipo == "Extremos registrados":
        ini = f"{kw['start']}T00:00:00UTC"
        fin = f"{kw['end']}T23:59:59UTC"
        var = kw["variable"]
        path = (f"/valores/climatologicos/extremos/fechaini/{ini}"
                f"/fechafin/{fin}/variable/{var}/estacion/{estacion_id}")
    else:
        raise ValueError("Tipo no soportado")
    
    resp = requests.get(BASE_URL + path, params={"api_key": API_KEY})
    resp.raise_for_status()
    j = resp.json()
    if "datos" not in j:
        raise RuntimeError(f"AEMET error {j.get('estado')}: {j.get('descripcion')}")
    return j["datos"]


def descargar_json(datos_url):
    """Descarga el JSON completo desde datos_url."""
    resp = requests.get(datos_url)
    resp.raise_for_status()
    return resp.json()


def procesar_registros(tipo, records):
    """
    Convierte la lista de registros en DataFrame según el tipo.
    Para simplificar aquí sólo implementamos 'diarias' y 'extremos';
    el resto se deja como passtrough.
    """
    rows = []
    for r in records:
        base = {
            "estacion": r.get("indicativo"),
            "fecha":    r.get("fecha")
        }
        if tipo == "Climatologías diarias":
            if r.get("velmedia") is None:
                continue
            base.update({
                "velmedia_m_s": float(str(r["velmedia"]).replace(",", ".")),
                "racha_m_s":    float(str(r["racha"]  ).replace(",", ".")) if r.get("racha") else None,
                "dir_racha":    float(str(r["dir"]    ).replace(",", ".")) if r.get("dir")   else None,
            })
        elif tipo == "Extremos registrados":
            base.update({
                "valor": r.get("valor"),
                "unidad": r.get("unidad")
            })
        else:
            # Para otros tipos: vuelca todo el dict
            rows.append({**base, **r})
            continue
        
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

    # 1) Cargar estaciones y filtrar por provincia
    estaciones = obtener_estaciones()
    provincias = sorted({e["provincia"] for e in estaciones if e.get("provincia")})
    provincia = seleccionar_opcion(provincias, "Seleccione una provincia:")
    estaciones_prov = filtrar_provincia(estaciones, provincia)

    # 2) Selección de estación
    listado = [f"{e['nombre']} ({e['indicativo']})" for e in estaciones_prov]
    esc = seleccionar_opcion(listado, "Seleccione una estación:")
    estacion_id = esc.split("(")[-1].strip(")")

    # 3) Parámetros según tipo
    params = pedir_parametros(tipo)

    # 4) Obtener URL de datos y descargar todo en un solo request
    print("\n📡 Solicitando URL de descarga...")
    url_datos = obtener_url_datos(tipo, estacion_id, **params)
    time.sleep(1)  # práctica recomendada
    print("📥 Descargando datos...")
    records = descargar_json(url_datos)

    # 5) Procesar y guardar
    df = procesar_registros(tipo, records)
    nombre_csv = tipo.lower().replace(" ", "_") + ".csv"
    df.to_csv(nombre_csv, index=False)
    print(f"✅ Guardado {len(df)} registros en '{nombre_csv}'")


if __name__ == "__main__":
    main()