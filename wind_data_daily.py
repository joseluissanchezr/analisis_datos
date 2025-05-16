import requests
import pandas as pd



#Clave API para ingresr a AEMET
# https://opendata.aemet.es/centrodedescargas/inicio
API_KEY    = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqaW5lbGEuZ29uemFsZXpAYWx1bW5vcy51cG0uZXMiLCJqdGkiOiJmZjU4ZTJlNi1iMjVhLTQ1ZTAtYTUzYi0xZDBmNDY3OGJhZDgiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc0NjgyMjkxNywidXNlcklkIjoiZmY1OGUyZTYtYjI1YS00NWUwLWE1M2ItMWQwZjQ2NzhiYWQ4Iiwicm9sZSI6IiJ9.Cy_fCJ8NZSgQHadQEOoH-feniDOlu6CgaJ1ZBFX4y5c"
BASE_URL   = "https://opendata.aemet.es/opendata/api"

# Funcion para obtener el link de descarga de los datos diarios de viento
# Encontramos el link para descargar los datos diarios de una estación

def obtener_daily_datos_url(day, station_id=None):
    
    #day: Formato de fecha "YYYY-MM-DD"
    #station_id: ejemplo "9073X", or ninguno para todas las estaciones
    
    ini = f"{day}T00:00:00UTC"
    fin = f"{day}T23:59:59UTC"
    if station_id:
        path = (
            f"/valores/climatologicos/diarios/datos/"
            f"fechaini/{ini}/fechafin/{fin}/estacion/{station_id}"
        )
    else:
        path = (
            f"/valores/climatologicos/diarios/datos/"
            f"fechaini/{ini}/fechafin/{fin}/todasestaciones"
        )

    resp = requests.get(BASE_URL + path, params={"api_key": API_KEY})
    resp.raise_for_status()
    j = resp.json()
    if "datos" not in j:
        raise RuntimeError(f"AEMET error {j.get('estado')}: {j.get('descripcion')}")
    return j["datos"]
#descargar el json de los datos
def descargar_daily_datos(datos_url):
    resp = requests.get(datos_url)
    resp.raise_for_status()
    return resp.json()
#procesar los datos
def procesar_daily_datos(records):
    
    #cada registro es un diccionario con los siguientes campos:
    
    # indicativo : ID de la estación
    # velmedia   : velocidad media del viento (m/s)
    # racha    : racha máxima del viento (m/s)
    # dir        : dirección del viento (grados)

    
    rows = []
    for r in records:
        if r.get("velmedia") is None:
            continue
        rows.append({
            "station_id":      r["indicativo"],
            "date":            pd.to_datetime(r["fecha"]).date(),
           # "wind_vmean_m_s":   r["velmedia"],
          "wind_vmean_m_s": float(str(r.get("velmedia")).replace(",", "."))  if r.get("velmedia") else None,
          "wind_racha_m_s": float(str(r.get("racha")).replace(",", "."))  if r.get("racha") else None,
          "wind_dir_racha_d_g": float(str(r.get("dir")).replace(",", "."))  if r.get("dir") else None,
        #Puede tardar en cargar, ya que son muchos datos. Si demora más de lo previsto, 
        #se puede volver a ejecutar el script.
        })
    return pd.DataFrame(rows)

# Función principal para obtener los datos diarios de viento

def get_daily_datos(day, station_id=None):
    datos_url = obtener_daily_datos_url(day, station_id)
    recs      = descargar_daily_datos(datos_url)
    return procesar_daily_datos(recs)

def get_daily_datos_range(start_day: str,
                               end_day:   str,
                               station_id: str = None) -> pd.DataFrame:

#Obtiene los datos diarios de viento para cada fecha entre start_day y end_day.
#Si se proporciona station_id, se limita a esa estación; si no, obtiene todas.
#devuelve un DataFrame concatenado.

    dates = pd.date_range(start=start_day, end=end_day, freq="D").strftime("%Y-%m-%d")
    
    dfs = []
    for day in dates:
        try:
            df_day = get_daily_datos(day, station_id=station_id)
            dfs.append(df_day)
        except Exception as e:
            print(f" {day} failed: {e}")
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["station_id","date","mean_wind_m_s"])

# Personalizacion de la salida

if __name__ == "__main__":

    # Todas las estaciones, para el día deseado
   # df_all = get_daily_datos("2025-04-28")
    #df_all.to_csv("daily_wind_all_stations_date.csv", index=False)

    #Estacion deseada, para el día deseado
    #df_Station = get_daily_datos("2025-04-28", station_id="9073X")
    #print(df_Station)
    #df_Station.to_csv("daily_wind_stationdesired_date.csv", index=False)

    # Todas las estaciones, para el rango de fechas deseado
    #df_all_range = get_daily_datos_range("2025-04-25", "2025-04-30")
    #print(df_all_range)
    #df_all_range.to_csv("daily_wind_all_station_range.csv", index=False)

    # Estacion deseada, para el rango de fechas deseado
    df_Station = get_daily_datos_range("2025-03-25", "2025-04-13", station_id="9073X")
    print(df_Station)
    df_Station.to_csv("daily_wind_stationdesired_range.csv", index=False)
