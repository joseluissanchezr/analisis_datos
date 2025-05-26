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
def get_esios_data(indicator_id, start_date, end_date, column_name):
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
        df = df[['datetime', 'value']].rename(columns={'value': column_name})
        return df
    else:
        print(f"Error {response.status_code}: {response.text}")
        return pd.DataFrame(columns=['datetime',column_name])

#

def merge_and_clean_data(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(df1, df2, on='datetime', how='outer').sort_values('datetime')

    # Índice datetime para interpolación temporal
    df.set_index('datetime', inplace=True)
    
    # Interpolación para rellenar valores faltantes basados en tiempo
    df.interpolate(method='time', inplace=True)
    
    # Eliminar filas que sigan con valores NaN (por ejemplo, al inicio o fin)
    df.dropna(inplace=True)

    # Eliminación de outliers usando método IQR para cada columna numérica
    for col in df.select_dtypes(include=['float', 'int']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df.loc[~df[col].between(lower_bound, upper_bound), col] = pd.NA

    # Segunda interpolación para rellenar los valores NaN generados por outliers
    df.interpolate(method='time', inplace=True)
    
    df.reset_index(inplace=True)
    return df

# --- DESCARGA DE DATOS ---
df_forecast = get_esios_data(541, start, end, "Prevision Eolica")   # Previsión de eólica
print("Previsión descargada:")
print(df_forecast.head())

df_real = get_esios_data(551, start, end, "Generacion Eolica Real")       # Producción real eólica
print("Producción real descargada:")
print(df_real.head())

# --- MERGE DE AMBAS SERIES ---
df = merge_and_clean_data(df_forecast, df_real)

# --- EXPORTACIÓN OPCIONAL A CSV ---
df.to_csv("datos_eolica_541_551.csv", index=False)
print("\nDatos combinados exportados a 'datos_eolica_541_551.csv'")
