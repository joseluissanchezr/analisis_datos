# scripts/extract_noaa_api.py

import requests
import json
import pandas as pd

# Tu token de NOAA
API_TOKEN = "gAeZlUchXkUzxowblhWeDzERXSYcXmdw"

# Encabezado de autenticación
headers = {
    "token": API_TOKEN
}

# Endpoint para obtener datasets
url = "https://www.ncei.noaa.gov/cdo-web/api/v2/datasets"

def get_noaa_datasets():
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datasets = response.json()['results']
        print("✅ Datasets recibidos correctamente.")
        
        # Guardar como CSV para inspección
        df = pd.DataFrame(datasets)
        df.to_csv("Group4_data_analysis/data/noaa_datasets.csv", index=False)
        print("📁 Guardado en /data/noaa_datasets.csv")
    
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    get_noaa_datasets()
