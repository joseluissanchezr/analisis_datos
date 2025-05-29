
import os
import glob
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# 1. Resolver la ruta al path absoluto
folder = os.path.expanduser(r"~\Documents\AEMET_output")

# 2. Buscar archivos *_limpio.csv
pattern = os.path.join(folder, "*_limpio.csv")
csv_files = glob.glob(pattern)

if not csv_files:
    print("❌ No se encontraron archivos *_limpio.csv.")
else:
    print("✅ Archivos encontrados:")
    for f in csv_files:
        print("  -", os.path.basename(f))

def graph_annuals(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ El DataFrame está vacío o tiene menos de 2 filas válidas para annuals.")
        print(df.head())
        return

    year = df['fecha_dt'].dt.year.iloc[1]
    station = df["estacion"].iloc[1]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['w_med'],
                             mode='lines+markers', name='Velocidad media (m/s)'))
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['w_racha'],
                             mode='lines+markers', name='Racha máxima (m/s)'))
    fig.add_trace(go.Bar(x=df['fecha_dt'], y=df['w_rec'],
                         name='Recorrido viento'))

    fig.update_layout(
        title=f"Variables de viento en {year} - Estación {station}",
        xaxis_title='Fecha',
        yaxis_title='Velocidad / Racha (m/s) y Recorrido viento',
        updatemenus=[
            dict(
                type="buttons",
                direction="down",
                buttons=[
                    dict(label="Todas",
                         method="update",
                         args=[{"visible": [True, True, True]}]),
                    dict(label="Sólo Velocidad media",
                         method="update",
                         args=[{"visible": [True, False, False]}]),
                    dict(label="Sólo Racha máxima",
                         method="update",
                         args=[{"visible": [False, True, False]}]),
                    dict(label="Sólo Recorrido viento",
                         method="update",
                         args=[{"visible": [False, False, True]}])
                ],
                showactive=True
            )
        ],
        legend_title_text='Variable'
    )

    fig.show()

def graph_daily(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ El DataFrame está vacío o tiene menos de 2 filas válidas para daily.")
        print(df.head())
        return

    date_1 = df['fecha_dt'].dt.date.iloc[0]
    date_2 = df['fecha_dt'].dt.date.iloc[-1]
    station = df["estacion"].iloc[0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['fecha_dt'],
        y=df['velmedia'],
        mode='lines+markers',
        name='Velocidad media (m/s)',
        yaxis='y1'
    ))

    fig.add_trace(go.Scatter(
        x=df['fecha_dt'],
        y=df['racha'],
        mode='lines+markers',
        name='Racha máxima (m/s)',
        yaxis='y1'
    ))

    fig.add_trace(go.Bar(
        x=df['fecha_dt'],
        y=df['dir_racha'],
        name='Dirección de racha (°)',
        yaxis='y2',
        opacity=0.5
    ))

    fig.update_layout(
        title=f"Viento diario del {date_1} al {date_2} - Estación {station}",
        xaxis_title='Fecha',
        yaxis=dict(
            title='Velocidad (m/s)',
            side='left',
            visible=True
        ),
        yaxis2=dict(
            title='Dirección (°)',
            overlaying='y',
            side='right',
            visible=True
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="down",
                buttons=[
                    dict(
                        label="Todas",
                        method="update",
                        args=[
                            {"visible": [True, True, True]},
                            {"yaxis.visible": True, "yaxis2.visible": True}
                        ]
                    ),
                    dict(
                        label="Solo Velocidad media",
                        method="update",
                        args=[
                            {"visible": [True, False, False]},
                            {"yaxis.visible": True, "yaxis2.visible": False}
                        ]
                    ),
                    dict(
                        label="Solo Racha máxima",
                        method="update",
                        args=[
                            {"visible": [False, True, False]},
                            {"yaxis.visible": True, "yaxis2.visible": False}
                        ]
                    ),
                    dict(
                        label="Solo Dirección de racha",
                        method="update",
                        args=[
                            {"visible": [False, False, True]},
                            {"yaxis.visible": False, "yaxis2.visible": True}
                        ]
                    )
                ],
                showactive=True
            )
        ],
        legend_title_text='Variable'
    )

    fig.show()

# 3. Preguntar al usuario qué tipo de datos quiere graficar
print("\n¿Qué datos deseas visualizar?")
print("1 - Climatologías diarias")
print("2 - Climatologías mensuales/anuales")
choice = input("Introduce 1 o 2: ")

for file_path in csv_files:
    filename = os.path.basename(file_path).lower()
    df = pd.read_csv(file_path, sep=';', decimal=',', quoting=2)

    if "diaria" in filename and choice == "1":
        graph_daily(df)
    elif "anual" in filename and choice == "2":
        graph_annuals(df)
