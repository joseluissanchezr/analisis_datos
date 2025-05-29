import os
import glob
import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np

import plotly.io as pio
pio.renderers.default = 'browser'

        
def custom_autopct(pct, values):
    if pct<1: 
        return ''
    elif pct>1 and pct <1.5:  
        return f'{pct:.0f}% \n' 
    elif 1.5<pct and pct<2 :
        return f'\n {pct:.0f}%'  
    else:
        return f'{pct:.0f}%'

        

def graph_annuals(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ DataFrame vacío para anual.")
        return

    year = df['fecha_dt'].dt.year.iloc[0]
    station = df["estacion"].iloc[0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['w_med'], mode='lines+markers', name='Velocidad media'))
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['w_racha'], mode='lines+markers', name='Racha máxima'))
    fig.add_trace(go.Bar(x=df['fecha_dt'], y=df['w_rec'], name='Recorrido viento'))

    fig.update_layout(
        title=f"Climatología mensual - {year} - Estación {station}",
        xaxis_title='Fecha',
        yaxis_title='Valores',
        legend_title_text='Variable'
    )
    fig.show()
    
    months = df['fecha_dt'].dt.month_name()
    
    fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax_pie.pie(df["w_med"], startangle=90, autopct=lambda pct: custom_autopct(pct, df["w_med"]))

    for i, wedge in enumerate(wedges):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))

        ax_pie.text(
            x * 1.31, y * 1.1,
            months[i],
            ha='center', va='center', fontsize=12, color='black'
        )

    ax_pie.set_aspect('equal')

    for autotext in autotexts:
        autotext.set_fontsize(11)
    plt.show()

def graph_daily(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ DataFrame vacío para diaria.")
        return

    station = df["estacion"].iloc[0]


    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['velmedia'], mode='lines+markers', name='Vel. media'))
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['racha'], mode='lines+markers', name='Racha máx.'))
    fig.add_trace(go.Bar(x=df['fecha_dt'], y=df['dir_racha'], name='Dir. racha', opacity=0.4, yaxis='y2'))

    fig.update_layout(
        title=f"Climatología diaria - Estación {station}",
        xaxis_title='Fecha',
        yaxis=dict(title='Vel. / Racha', side='left'),
        yaxis2=dict(title='Dirección (°)', overlaying='y', side='right'),
        legend_title_text='Variable'
    )
    fig.show()
    
    months = df['fecha_dt'].dt.month_name()

    fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax_pie.pie(df["velmedia"], startangle=90, autopct=lambda pct: custom_autopct(pct, df["velmedia"]))

    for i, wedge in enumerate(wedges):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))

        ax_pie.text(
            x * 1.31, y * 1.1,
            months[i],
            ha='center', va='center', fontsize=12, color='black'
        )

    ax_pie.set_aspect('equal')

    for autotext in autotexts:
        autotext.set_fontsize(11)
    plt.show()
    
    # --- GRAPH 2 : velmedia with direction
    df['dir_10'] = (df['dir_racha'] // 10 * 10).astype(int)
    polar_df = df.groupby('dir_10')['velmedia'].mean().reset_index()
    polar_df = polar_df.sort_values(by='dir_10')

    all_dirs = pd.DataFrame({'dir_10': np.arange(0, 360, 10)})
    polar_df = pd.merge(all_dirs, polar_df, on='dir_10', how='left').fillna(0)

    fig_polar = go.Figure()

    fig_polar.add_trace(go.Scatterpolar(
        r=polar_df['velmedia'],
        theta=polar_df['dir_10'],
        mode='lines+markers',
        name='Vel. media',
        fill='toself',
        marker=dict(color='blue')
    ))

    fig_polar.update_layout(
        title=f"Distribución direccional - Velocidad media ({station})",
        polar=dict(
            angularaxis=dict(direction="clockwise", rotation=90),
            radialaxis=dict(title='m/s')
        ),
        height=500,
        showlegend=False
    )

    fig_polar.show()

def graph_extremos(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha_ocurrencia'], errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ DataFrame vacío para extremos.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['fecha_dt'], y=df['rachMax_kmh'], mode='markers', name='Racha máx (km/h)'))
    fig.add_trace(go.Bar(x=df['fecha_dt'], y=df['dirRachMax_grados'], name='Dirección racha (°)', opacity=0.5, yaxis='y2'))

    fig.update_layout(
        title="Extremos registrados",
        xaxis_title='Fecha',
        yaxis=dict(title='Racha máxima (km/h)', side='left'),
        yaxis2=dict(title='Dirección (°)', overlaying='y', side='right'),
        legend_title_text='Variable'
    )
    fig.show()

def graph_normales(df):
    columnas_viento = [
        "w_racha_max", "w_racha_min", "w_racha_md", "w_racha_cv",
        "w_med_max", "w_med_min", "w_med_md", "w_med_cv",
        "w_med_n", "w_med_s"
    ]

    if df.empty or len(df) < 2:
        print("❌ DataFrame vacío para normales.")
        return

    station = df["estacion"].iloc[0] if "estacion" in df.columns else "Desconocida"
    fig = go.Figure()

    eje_x = df.index  # Eje X artificial: 0, 1, 2, ...

    for col in columnas_viento:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=eje_x, y=df[col], mode='lines+markers', name=col))

    fig.update_layout(
        title=f"Valores normales de viento - Estación {station}",
        xaxis_title='Índice (sin fecha)',
        yaxis_title='Velocidad del viento (km/h o m/s)',
        legend_title_text='Variable'
    )
    fig.show()

def visualizar_datos_aemet(tipo_int):
    """
    tipo_int:
    - 1: Climatología diaria
    - 2: Climatología mensual/anual
    - 3: Extremos registrados
    - 4: Valores normales
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

        if tipo_int == 1 and "diaria" in filename:
            graph_daily(df)
        elif tipo_int == 2 and ("mensual" in filename or "anual" in filename):
            graph_annuals(df)
        elif tipo_int == 3 and "extremo" in filename:
            graph_extremos(df)
        elif tipo_int == 4 and "normal" in filename:
            graph_normales(df)
