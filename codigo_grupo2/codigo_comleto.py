# === PARTE 1 ─ Configuración e importaciones básicas ===
# DATA ANALYSIS PROJECT · GROUP 2
# Descripción: extracción y limpieza de datos horarios de la API de ESIOS
# Indicadores: 541 (previsión) y 551 (producción real)

import requests
import pandas as pd
from datetime import datetime, timedelta

TOKEN = '255c4529289ed8e7cfcfdc5cff2c43d0f101fe5b3adaa20273c01b0deafa80d4'            
HEADERS = {
    'Accept'      : 'application/json',
    'Content-Type': 'application/json',
    'x-api-key'   : TOKEN,
    'User-Agent'  : 'esios-api-client'
}

start = datetime.strptime((input("Introduce una fecha Inicio en formato dd/mm/yyyy: ")), "%d/%m/%Y")
end =  datetime.strptime((input("Introduce una fecha Fin en formato dd/mm/yyyy: ")), "%d/%m/%Y")


# FUNCIÓN CODIGO ORIGINAL FECHAS
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

# Descarga y combinación de datos

df_forecast = get_esios_data(541, start, end)   # Previsión
print("Previsión descargada:\n", df_forecast.head())

df_real     = get_esios_data(551, start, end)   # Producción real
print("Producción real descargada:\n", df_real.head())

df = (pd.merge(df_forecast, df_real, on='datetime', how='outer')
        .sort_values('datetime'))