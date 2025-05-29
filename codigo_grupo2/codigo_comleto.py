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


# ─────────────────────────────────────────────────────────────
# Construction of information for analysis 
# ───

# 1. Correlation Static chart (in case the user prefers to view the chart statically) 

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

import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot

df_corr = df.dropna(subset=['indicator_541', 'indicator_551'])
correlation = df_corr['indicator_541'].corr(df_corr['indicator_551'])

# Calculate linear regression, daily sum and comparative
m, b = np.polyfit(df_corr['indicator_541'], df_corr['indicator_551'], 1)

df['datetime'] = pd.to_datetime(df['datetime'])
df['date'] = df['datetime'].dt.date
df_daily = df.groupby('date', as_index=False)[['indicator_541', 'indicator_551']].sum()

# Static char of daily energy (in case the user prefers to view the chart statically) 

x = np.arange(len(df_daily['date']))  # Índices
width = 0.35  # Ancho de las barras

plt.figure(figsize=(12, 6))
plt.bar(x - width/2, df_daily['indicator_541'], width, label='Previsión diaria', color='skyblue')
plt.bar(x + width/2, df_daily['indicator_551'], width, label='Producción real diaria', color='lightgreen')
plt.xticks(x, df_daily['date'], rotation=45)
plt.xlabel('Fecha')
plt.ylabel('Energía diaria total (MW·h)')
plt.title('Comparación diaria de energía: Previsión vs Producción real (barras)')
plt.legend()
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()

df_daily['error'] = df_daily['indicator_541'] - df_daily['indicator_551']
 

# ─────────────────────────────────────────────────────────────
# Comparison of data with group 1 information for zone 7 (Castilla-La Mancha) - optional item 
# ───

# 1. Obtain data from the other group for zone 7 

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime as dt

# REE API callin function 

def get_generacion_zona7(start, end):
    url = "https://apidatos.ree.es/es/datos/generacion/estructura-generacion"
    headers = {"Accept": "application/json"}
    params = {
        "start_date": start.strftime("%Y-%m-%dT%H:%M"),
        "end_date": end.strftime("%Y-%m-%dT%H:%M"),
        "time_trunc": "day",
        "geo_limit":  "ccaa",
        "geo_id": 7  # Castilla-La Mancha
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"⛔ Error {response.status_code}")
        return pd.DataFrame()

    data = response.json()
    rows = []
    for tech in data["included"]:
        if tech["attributes"]["title"] == "Eólica":
            for v in tech["attributes"]["values"]:
                rows.append({
                    "date": v["datetime"][:10],
                    "eolica_zona7": v["value"]
                })
    return pd.DataFrame(rows)

# Calling the function 

df_zona7 = get_generacion_zona7(start, end)
df_zona7["date"] = pd.to_datetime(df_zona7["date"])

# Combine information group 1 and group 2 

df_daily["date"] = pd.to_datetime(df_daily["date"])
df_zona7["date"] = pd.to_datetime(df_zona7["date"])

df_comparado = pd.merge(df_daily, df_zona7, on="date", how="inner")

# static chart of comparative (in case the user prefers to view the chart statically) 

plt.figure(figsize=(12, 6))
df_melted = df_comparado.melt(id_vars="date", 
                              value_vars=["indicator_541", "indicator_551", "eolica_zona7"],
                              var_name="Fuente", 
                              value_name="Energía (MWh)")

nombre_dict = {
    "indicator_541": "Previsión (grupo 2-ESIOS)",
    "indicator_551": "Producción real (grupo2-ESIOS)",
    "eolica_zona7": "Generación eólica real Zona 7 (grupo1)"
}
df_melted["Fuente"] = df_melted["Fuente"].map(nombre_dict)

sns.lineplot(data=df_melted, x="date", y="Energía (MWh)", hue="Fuente", marker="o")
plt.title("Comparación diaria de generación eólica")
plt.xlabel("Fecha")
plt.ylabel("Energía (MWh)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()


# ─────────────────────────────────────────────────────────────
# DASHBOARD IN CELL
# ───

import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Create figure  with subplot

fig_dashboard = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Forecast vs Real Power over Time",
        "Forecast vs Real Correlation (scatter)",
        "Comparación diaria de generación eólica GRUPO2-GRUPO1",
        "Error diario de previsión"
    )
)

# Gráfico 1: Líneas de forecast y real vs tiempo
fig_dashboard.add_trace(
    go.Scatter(x=df_corr['datetime'], y=df_corr['indicator_541'], mode='lines', name='Forecast Power', line=dict(color='blue')),
    row=1, col=1
)
fig_dashboard.add_trace(
    go.Scatter(x=df_corr['datetime'], y=df_corr['indicator_551'], mode='lines', name='Real Power', line=dict(color='green')),
    row=1, col=1
)

# Gráfico 2: Dispersión + línea de tendencia
fig_dashboard.add_trace(
    go.Scatter(x=df_corr['indicator_541'], y=df_corr['indicator_551'], mode='markers', name='Data Points', marker=dict(color='dodgerblue')),
    row=1, col=2
)
fig_dashboard.add_trace(
    go.Scatter(x=df_corr['indicator_541'], y=m * df_corr['indicator_541'] + b, mode='lines', name='Trend Line', line=dict(color='firebrick', dash='dash', width=2)),
    row=1, col=2
)

# Gráfico 3: Comparación diaria de generación eólica GRUPO2-GRUPO1 (líneas)
fig_dashboard.add_trace(
    go.Scatter(x=df_comparado['date'], y=df_comparado['indicator_541'], mode='lines+markers', name='Previsión diaria (GRUPO2)', line=dict(color='dodgerblue')),
    row=2, col=1
)
fig_dashboard.add_trace(
    go.Scatter(x=df_comparado['date'], y=df_comparado['indicator_551'], mode='lines+markers', name='Producción real diaria (GRUPO2)', line=dict(color='mediumseagreen')),
    row=2, col=1
)
fig_dashboard.add_trace(
    go.Scatter(x=df_comparado['date'], y=df_comparado['eolica_zona7'], mode='lines+markers', name='Generación eólica Zona 7 (GRUPO1)', line=dict(color='orange')),
    row=2, col=1
)

# Gráfico 4: Error diario
fig_dashboard.add_trace(
    go.Bar(x=df_daily['date'], y=df_daily['error'], marker_color='indianred', name='Error diario'),
    row=2, col=2
)

fig_dashboard.update_layout(
    height=900, width=1200,
    title_text="Dashboard Comparativo Energía Eólica",
    showlegend=True,
    template="plotly_white"
)

# Mostrar todo junto
fig_dashboard.show()


# ─────────────────────────────────────────────────────────────
# INTERACTIVE DASHBOARD IN A SEPARATE BROWSER 
# ───

from plotly.subplots import make_subplots
import plotly.graph_objs as go

# Crear una figura con 5 subplots (2 filas, 3 columnas, y uno vacío)
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Forecast vs Real Time",
        "Scatter Forecast vs Real",
        "Barras Diarias",
        "Error Diario",
        "Comparación Grupo2 vs Grupo1"
    ),
    specs=[[{"colspan": 2}, None],
           [{}, {}],
           [{}, {}]]
)

# Gráfico 1: Forecast vs Real Time (ocupa fila 1, columnas 1 y 2)
fig.add_trace(go.Scatter(x=df_corr['datetime'], y=df_corr['indicator_541'], mode='lines', name='Forecast Power', line=dict(color='blue')), row=1, col=1)
fig.add_trace(go.Scatter(x=df_corr['datetime'], y=df_corr['indicator_551'], mode='lines', name='Real Power', line=dict(color='green')), row=1, col=1)

# Gráfico 2: Scatter plot (fila 2, col 1)
m, b = np.polyfit(df_corr['indicator_541'], df_corr['indicator_551'], 1)
fig.add_trace(go.Scatter(x=df_corr['indicator_541'], y=df_corr['indicator_551'], mode='markers', name='Data Points', marker=dict(color='dodgerblue')), row=2, col=1)
fig.add_trace(go.Scatter(x=df_corr['indicator_541'], y=m * df_corr['indicator_541'] + b, mode='lines', name='Trend Line', line=dict(color='firebrick', dash='dash', width=2)), row=2, col=1)

# Gráfico 3: Barras diarias (fila 2, col 2)
fig.add_trace(go.Bar(name='Previsión diaria', x=df_daily['date'], y=df_daily['indicator_541'], marker_color='dodgerblue'), row=2, col=2)
fig.add_trace(go.Bar(name='Producción real diaria', x=df_daily['date'], y=df_daily['indicator_551'], marker_color='mediumseagreen'), row=2, col=2)

# Gráfico 4: Error diario (fila 3, col 1)
fig.add_trace(go.Bar(x=df_daily['date'], y=df_daily['error'], marker_color='indianred', name='Error diario'), row=3, col=1)

# Gráfico 5: Comparación Grupo 2 vs Grupo 1 (adaptar al formato plotly, fila 3, col 2)
# Aquí asumo que df_comparado ya está definido y tienes las columnas que quieres graficar.
import plotly.express as px
df_melted = df_comparado.melt(id_vars="date", value_vars=["indicator_541", "indicator_551", "eolica_zona7"],
                              var_name="Fuente", value_name="Energía (MWh)")

# Para insertar gráfico de líneas en subplot, hay que hacer líneas separadas:
fuentes = df_melted['Fuente'].unique()
colors = {'indicator_541': 'blue', 'indicator_551': 'green', 'eolica_zona7': 'orange'}

for fuente in fuentes:
    dff = df_melted[df_melted['Fuente'] == fuente]
    fig.add_trace(go.Scatter(x=dff['date'], y=dff['Energía (MWh)'], mode='lines+markers', name=fuente, line=dict(color=colors.get(fuente, 'black'))), row=3, col=2)

fig.update_layout(height=900, width=1200, title_text="Dashboard eólico completo", template='plotly_white')

# Guardar un único archivo HTML y abrirlo
plot(fig, filename="dashboard_eolico_completo.html", auto_open=True)
