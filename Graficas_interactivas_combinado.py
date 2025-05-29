import os
import glob
import pandas as pd
import plotly.graph_objs as go

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
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['w_med'], mode='lines+markers', name='Velocidad media (m/s)'))
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['w_racha'], mode='lines+markers', name='Racha máxima (m/s)'))
    fig.add_trace(go.Bar(x=df['fecha_dt'], y=df['w_rec'], name='Recorrido viento'))

    fig.update_layout(
        title=f"Variables de viento en {year} - Estación {station}",
        xaxis_title='Fecha',
        yaxis_title='Velocidad / Racha (m/s) y Recorrido viento',
        updatemenus=[
            dict(
                type="buttons",
                direction="down",
                buttons=[
                    dict(label="Todas", args=[{"visible": [True, True, True]}], method="update"),
                    dict(label="Sólo Velocidad media", args=[{"visible": [True, False, False]}], method="update"),
                    dict(label="Sólo Racha máxima", args=[{"visible": [False, True, False]}], method="update"),
                    dict(label="Sólo Recorrido viento", args=[{"visible": [False, False, True]}], method="update"),
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
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['velmedia'], mode='lines+markers', name='Velocidad media (m/s)', yaxis='y1'))
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['racha'], mode='lines+markers', name='Racha máxima (m/s)', yaxis='y1'))
    fig.add_trace(go.Bar(x=df['fecha_dt'], y=df['dir_racha'], name='Dirección de racha (°)', yaxis='y2', opacity=0.5))

    fig.update_layout(
        title=f"Viento diario del {date_1} al {date_2} - Estación {station}",
        xaxis_title='Fecha',
        yaxis=dict(title='Velocidad (m/s)', side='left', visible=True),
        yaxis2=dict(title='Dirección (°)', overlaying='y', side='right', visible=True),
        updatemenus=[
            dict(
                type="buttons",
                direction="down",
                buttons=[
                    dict(label="Todas", args=[{"visible": [True, True, True]}, {"yaxis.visible": True, "yaxis2.visible": True}], method="update"),
                    dict(label="Solo Velocidad media", args=[{"visible": [True, False, False]}, {"yaxis.visible": True, "yaxis2.visible": False}], method="update"),
                    dict(label="Solo Racha máxima", args=[{"visible": [False, True, False]}, {"yaxis.visible": True, "yaxis2.visible": False}], method="update"),
                    dict(label="Solo Dirección de racha", args=[{"visible": [False, False, True]}, {"yaxis.visible": False, "yaxis2.visible": True}], method="update"),
                ],
                showactive=True
            )
        ],
        legend_title_text='Variable'
    )
    fig.show()

def visualizar_datos_aemet(tipo_int):
    """
    Visualiza las gráficas de datos climáticos según tipo:
    - tipo_int = 1: Climatologías diarias
    - tipo_int = 2: Climatologías mensuales/anuales
    """

    folder = os.path.expanduser(r"~\Documents\AEMET_output")
    pattern = os.path.join(folder, "*_limpio.csv")
    csv_files = glob.glob(pattern)

    if not csv_files:
        print("❌ No se encontraron archivos *_limpio.csv.")
        return

    print("✅ Archivos encontrados:")
    for f in csv_files:
        print("  -", os.path.basename(f))

    for file_path in csv_files:
        filename = os.path.basename(file_path).lower()
        df = pd.read_csv(file_path, sep=';', decimal=',', quoting=2)

        if "diaria" in filename and tipo_int == 1:
            graph_daily(df)
        elif "anual" in filename and tipo_int == 2:
            graph_annuals(df)