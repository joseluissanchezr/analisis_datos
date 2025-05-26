# DATA ANALYSIS PROYECT
# GROUP 2
# Description: Extraction and cleaning of hourly data from the ESIOS API for the following indicators
# - Forecast of wind power production (ID 541)
# - Actual total wind power generation (ID 551)

import requests
import pandas as pd
from datetime import datetime, timedelta

# PERSONAL TOKEN CONFIGURATION
TOKEN = '255c4529289ed8e7cfcfdc5cff2c43d0f101fe5b3adaa20273c01b0deafa80d4'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'x-api-key': TOKEN,
    'User-Agent': 'esios-api-client'
}

# DATE CONFIGURATION
end = datetime.utcnow()
start = end - timedelta(days=2)  

# GENERAL FUNCTION TO QUERY HOURLY INDICATORS
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

# DATA DOWNLOAD
df_forecast = get_esios_data(541, start, end)   # Forecast
print("Previsión descargada:")
print(df_forecast.head())

df_real = get_esios_data(551, start, end)       # Real
print("Producción real descargada:")
print(df_real.head())

# MERGE
df = pd.merge(df_forecast, df_real, on='datetime', how='outer').sort_values('datetime')

# DATA CLEANING
# Fill missing values using time-based interpolation (requires indexing by datetime)
df.set_index('datetime', inplace=True)
df.interpolate(method='time', inplace=True)
df.reset_index(inplace=True)

# Outlier removal using the IQR method
for col in ['indicator_541', 'indicator_551']:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df[col] = df[col].where(df[col].between(lower_bound, upper_bound))

# EXPORT TO CSV
df.to_csv("WIND_DATA.csv", index=False)
print("\nDatos limpios exportados a 'WIND_DATA.csv'")

## CÁLCULO DE LA CORRELACIÓN DE LOS DATOS APARTADO OPCIONAL

import matplotlib.pyplot as plt
import seaborn as sns

df_corr = df.dropna(subset=['indicator_541','indicator_551'])
correlation = df_corr['indicator_541'].corr(df_corr['indicator_551'])
print (correlation)