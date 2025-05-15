# esios_eolica_analysis.py
# Autor: Marite Villar Zebadua - Grupo 2
# Descripción: Extracción de datos por hora desde la API de ESIOS de los indicadores:
# - Previsión de producción eólica (ID 541)
# - Generación total real eólica (ID 551)

import requests
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DEL TOKEN PERSONAL ---
TOKEN = '255c4529289ed8e7cfcfdc5cff2c43d0f101fe5b3adaa20273c01b0deafa80d4'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'x-api-key': TOKEN,
    'User-Agent': 'esios-api-client'
}

# --- CONFIGURACIÓN DE FECHAS ---
end = datetime.utcnow()
start = end - timedelta(days=2)  # últimos 2 días

# --- FUNCIÓN GENERAL PARA CONSULTAR INDICADORES POR HORA ---
def get_esios_data(indicator_id, start_date, end_date):
    url = f'https://api.esios.ree.es/indicators/{indicator_id}'
    params = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'time_trunc': 'hour'
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        values = data['indicator']['values']
        df = pd.DataFrame(values)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df[['datetime', 'value']].rename(columns={'value': f'indicator_{indicator_id}'})
        return df
    else:
        print(f"Error {response.status_code}: {response.text}")
        return pd.DataFrame(columns=['datetime', f'indicator_{indicator_id}'])

# --- DESCARGA DE DATOS ---
df_forecast = get_esios_data(541, start, end)   # Previsión de eólica
print("Previsión descargada:")
print(df_forecast.head())

df_real = get_esios_data(551, start, end)       # Producción real eólica
print("Producción real descargada:")
print(df_real.head())

# --- MERGE DE AMBAS SERIES ---
df = pd.merge(df_forecast, df_real, on='datetime', how='outer').sort_values('datetime')

# --- EXPORTACIÓN OPCIONAL A CSV ---
df.to_csv("datos_eolica_541_551.csv", index=False)
print("\nDatos combinados exportados a 'datos_eolica_541_551.csv'")
