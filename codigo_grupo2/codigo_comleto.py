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

while True:
    try:
        start = datetime.strptime(input("Enter start date (dd/mm/yyyy): "), "%d/%m/%Y")
        end = datetime.strptime(input("Enter end date (dd/mm/yyyy): "), "%d/%m/%Y")
        if start > end:
            print(" Start date must be earlier than end date. Try again.\n")
            continue
        break
    except ValueError:
        print(" Invalid format. Please use dd/mm/yyyy. Try again.\n")

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
df['datetime'] = df['datetime'].dt.tz_localize(None)
df.loc[df['datetime'] > datetime.now(), 'indicator_551'] = 0
df['datetime'] = df['datetime'].astype(str)

df['indicator_551'] = df['indicator_551'] / 12     # real
df['indicator_541'] = df['indicator_541'] / 4    # forecast

df = df.drop(df.index[-1])

df.to_excel("WIND_DATAv2.xlsx", index=False)
print("Datos limpios exportados a 'WIND_DATAv2.xlsx'")

import matplotlib.pyplot as plt
import seaborn as sns

df_corr    = df.dropna(subset=['indicator_541', 'indicator_551'])
correlation = df_corr['indicator_541'].corr(df_corr['indicator_551'])
print("Coeficiente de correlación:", correlation)

plt.figure(figsize=(10, 6))
sns.regplot(data=df_corr,
            x='indicator_541', y='indicator_551',
            line_kws={'color':'red'}, scatter_kws={'alpha':0.5})
plt.title(f'Correlación previsión vs real (r = {correlation:.2f})')
plt.xlabel('Previsión eólica (MW)');  plt.ylabel('Producción real (MW)')
plt.grid(True);  plt.tight_layout();  plt.show()

#Interactive graphics
import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot

df_corr = df.dropna(subset=['indicator_541', 'indicator_551'])
correlation = df_corr['indicator_541'].corr(df_corr['indicator_551'])

# Gráfico 1: Líneas de forecast y real vs tiempo
fig_time = go.Figure()
fig_time.add_trace(go.Scatter(
    x=df_corr['datetime'], y=df_corr['indicator_541'],
    mode='lines', name='Forecast Power',
    line=dict(color='blue')
))
fig_time.add_trace(go.Scatter(
    x=df_corr['datetime'], y=df_corr['indicator_551'],
    mode='lines', name='Real Power',
    line=dict(color='green')
))
fig_time.update_layout(
    title="Forecast vs Real Power over Time",
    xaxis_title="Datetime",
    yaxis_title="Power (MW)",
    template='plotly_white'
)

plot(fig_time, filename="forecast_vs_real_time.html", auto_open=False)


# Calcular la regresión lineal
m, b = np.polyfit(df_corr['indicator_541'], df_corr['indicator_551'], 1)

# Gráfico 2: Dispersión + línea de tendencia
fig_scatter = go.Figure()
fig_scatter.add_trace(go.Scatter(
    x=df_corr['indicator_541'], y=df_corr['indicator_551'],
    mode='markers',
    name='Data Points',
    marker=dict(color='dodgerblue')
))
fig_scatter.add_trace(go.Scatter(
    x=df_corr['indicator_541'], y=m * df_corr['indicator_541'] + b,
    mode='lines',
    name='Trend Line',
    line=dict(color='firebrick', dash='dash', width=2)
))
fig_scatter.update_layout(
    title=f'Forecast vs Real Correlation (r = {correlation:.2f})',
    xaxis_title='Forecast Wind Power (MW)',
    yaxis_title='Real Wind Power (MW)',
    template='plotly_white'
)

plot(fig_scatter, filename="forecast_vs_real_scatter.html", auto_open=False)

import webbrowser

webbrowser.open("forecast_vs_real_time.html")
webbrowser.open("forecast_vs_real_scatter.html")
