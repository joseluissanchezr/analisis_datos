# scripts/noaa_wind_miami_2015_2023.py

import requests
import pandas as pd
import os

# NOAA API Token
API_TOKEN = "gAeZlUchXkUzxowblhWeDzERXSYcXmdw"
headers = {"token": API_TOKEN}

# API base URL
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

# Parámetros para la consulta mensual de viento
params = {
    "datasetid": "GSOM",                  # Global Summary of the Month
    "stationid": "GHCND:USW00093193",     # Estación en Miami
    "datatypeid": "AWND",                 # Average Wind Speed
    "startdate": "2015-01-01",
    "enddate": "2023-12-31",
    "units": "metric",
    "limit": 1000
}

def fetch_monthly_wind_data():
    print("📘 Consultando velocidad mensual del viento en Miami (2015-2023)...")
    response = requests.get(BASE_URL, headers=headers, params=params)
    print("📑 Estado de la respuesta:", response.status_code)

    if response.status_code == 200:
        results = response.json().get("results", [])
        if not results:
            print("⚠️ No se encontraron resultados.")
            return
        df = pd.DataFrame(results)
        os.makedirs("data", exist_ok=True)
        df.to_csv("Group4_data_analysis/data/noaa_wind_miami_2015_2023.csv", index=False)
        print("✅ Datos guardados en data/noaa_wind_miami_2015_2023.csv")
    else:
        print("❌ Error al consultar datos NOAA:")
        print(response.text)

if __name__ == "__main__":
    fetch_monthly_wind_data()
