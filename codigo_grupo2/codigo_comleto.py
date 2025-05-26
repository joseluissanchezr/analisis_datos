# === PART 1 ─ Basic Setup and Imports ===
# DATA ANALYSIS PROJECT · GROUP 2
# Description: Extraction and cleaning of hourly data from the ESIOS API
# Indicators: 541 (forecast) and 551 (actual production)

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


# FUNCTION ORIGINAL CODE DATES

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

# Download and combination of data

df_forecast = get_esios_data(541, start, end)   # Forecast
print("Previsión descargada:\n", df_forecast.head())

df_real     = get_esios_data(551, start, end)   # Actual production
print("Producción real descargada:\n", df_real.head())

df = (pd.merge(df_forecast, df_real, on='datetime', how='outer')
        .sort_values('datetime'))

# === PART 4 ─ Cleaning and handling of outliers ===

def cleaning(df):
    df = df.copy()
    df.set_index('datetime', inplace=True)
    df.interpolate('linear', inplace=True)
    return df.reset_index()

df = cleaning(df)     ## Initial gap filling

for col in ['indicator_541', 'indicator_551']:      # IQR outliers
    Q1, Q3 = df[col].quantile([0.25, 0.75])
    IQR    = Q3 - Q1
    df[col] = df[col].where(df[col].between(0, Q3 + 1.5 * IQR))

df = cleaning(df)     #Second pass after removing outliers

# From the current hour onward, there is no actual generation → 0 MW
df.loc[df['datetime'] > datetime.now(), 'indicator_551'] = 0
