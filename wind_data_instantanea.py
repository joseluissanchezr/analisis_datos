import requests
import pandas as pd
#clave API para ingresr a AEMET
# https://opendata.aemet.es/centrodedescargas/inicio
API_KEY    = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqaW5lbGEuZ29uemFsZXpAYWx1bW5vcy51cG0uZXMiLCJqdGkiOiJmZjU4ZTJlNi1iMjVhLTQ1ZTAtYTUzYi0xZDBmNDY3OGJhZDgiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTc0NjgyMjkxNywidXNlcklkIjoiZmY1OGUyZTYtYjI1YS00NWUwLWE1M2ItMWQwZjQ2NzhiYWQ4Iiwicm9sZSI6IiJ9.Cy_fCJ8NZSgQHadQEOoH-feniDOlu6CgaJ1ZBFX4y5c"
BASE_URL   = "https://opendata.aemet.es/opendata/api"
#definicion de la funcion para obtener el link de descarga de los datos instantaneos (últimas horas)
def observaciones_link():
    url = f"{BASE_URL}/observacion/convencional/todas"
    resp = requests.get(url, params={"api_key": API_KEY})
    resp.raise_for_status()
    return resp.json()["datos"]
#definicion de la funcion para descargar los datos instantaneos
def descargar_observaciones(datos_url):
    resp = requests.get(datos_url)
    resp.raise_for_status()
    return resp.json()
#definicion de la funcion para extraer los datos de viento
def extraer_wind_data(obs_list):
    records = []
    for obs in obs_list:
        speed_raw = obs.get("vv")
        if speed_raw is None:
            continue

        records.append({
            "station_id":      obs.get("idema"),                 
            "timestamp":       pd.to_datetime(obs.get("fint")),
            "wind_vv_m_s":  speed_raw ,                  
            "wind_vmax_m_s": float(str(obs.get("vmax")).replace(",", "."))  if obs.get("vmax") else None,
            "wind_dv_g": float(str(obs.get("dv")).replace(",", "."))  if obs.get("dv") else None,
            "wind_dmax_g": float(str(obs.get("dmax")).replace(",", "."))  if obs.get("dmax") else None,
        })
    return pd.DataFrame.from_records(records)
#definicion de la funcion principal donde se ejecutan las funciones anteriores
#se personalizan los datos y se guardan en un archivo csv
def main():
    datos_url    = observaciones_link()
    observations = descargar_observaciones(datos_url)

    print(f" {len(observations)} station records encontrados")
    df_wind = extraer_wind_data(observations)
    print(f"Estaciones con wind data: {len(df_wind)}")

    df_wind.to_csv("aemet_wind_observations.csv", index=False)
    print("wind data guardado en aemet_wind_observations.csv")

    station_id = "9073X"   # ID estacion deseada
    df_single = df_wind[df_wind["station_id"] == station_id]
    print(df_single)


if __name__ == "__main__":
    main()
