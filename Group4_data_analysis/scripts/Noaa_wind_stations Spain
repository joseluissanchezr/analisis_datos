import requests
import pandas as pd

# API TOKEN
token = 'lGubFmZGdaHJhROutmxcGnDknyspIdDZ'

headers = {'token': token}

# Datos de viento de estaciones costeras de España
url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/stations/'

params = {
    'datasetid': 'GSOY',
    'locationid': 'FIPS:SP',
    # 'startdate': '1958-10-01',
    # 'enddate': '2002-12-31',
    'stationid': 'GHCND:SPW00013025',
    'limit': 1000
}

# Hacer la petición
response = requests.get(url, headers=headers, params=params)

# Validar la respuesta
if response.status_code == 200:
    data = response.json()

    if 'results' in data:
        df = pd.DataFrame(data['results'])
        df.to_csv('data/stations_espana.csv', index=False)

        print("✅ Datos descargados correctamente.")
        print("💾 Archivo guardado en: data/stations_espana.csv")
    else:
        print("⚠️ No se encontraron resultados en la respuesta.")
else:
    print(f"❌ Error {response.status_code}: No se pudo acceder a la API.")
