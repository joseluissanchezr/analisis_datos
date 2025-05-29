
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import numpy as np


        
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
        print("❌ El DataFrame está vacío o tiene menos de 2 filas válidas para annuals.")
        print(df.head())
        return

    year = df['fecha_dt'].dt.year.iloc[1]
    station = df["estacion"].iloc[1]
        
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Velocidad media
    axs[0].plot(df['fecha_dt'], df['w_med'], label='Velocidad media (m/s)', color='blue')
    axs[0].legend()
    axs[0].set_ylabel('m/s')
    
    # Plot 2: Racha máxima
    axs[1].plot(df['fecha_dt'], df['w_racha'], label='Racha máxima (m/s)', color='orange')
    axs[1].legend()
    axs[1].set_ylabel('m/s')
    
    # Plot 3: Recorrido viento (bar chart)
    bars = axs[2].bar(df['fecha_dt'], df['w_rec'], label='Recorrido viento', width=5, color='green')
    axs[2].legend()
    axs[2].set_ylabel('m')
    
    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        axs[2].text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}",
            ha='center',
            va='bottom'
        )
    
    # Rotate x-axis labels on the last subplot
    axs[2].tick_params(axis='x', rotation=45)
    axs[2].set_xlabel('Fecha')
    
    # Adjust layout
    plt.tight_layout()
    axs[0].set_title(f"Variables de viento en {year} - Estación {station}")
    plt.xlabel('Fecha')
    plt.show()
    
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
        print("❌ El DataFrame está vacío o tiene menos de 2 filas válidas para daily.")
        print(df.head())
        return

    date_1 = df['fecha_dt'].dt.date.iloc[0]
    date_2 = df['fecha_dt'].dt.date.iloc[-1]
    station = df["estacion"].iloc[0]
    

    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Velocidad media
    axs[0].plot(df['fecha_dt'], df['velmedia'], label='Velocidad media (m/s)', color='blue')
    axs[0].legend()
    axs[0].set_ylabel('m/s')
    
    # Plot 2: Racha máxima
    axs[1].plot(df['fecha_dt'], df['racha'], label='Racha máxima (m/s)', color='orange')
    axs[1].legend()
    axs[1].set_ylabel('m/s')
    
    # Plot 3: Recorrido viento (bar chart)
    bars = axs[2].bar(df['fecha_dt'], df['dir_racha'], label='Dirección de racha (°)', color='green')
    axs[2].legend()
    axs[2].set_ylabel('m')
    
    # Annotate bar values
    for bar in bars:
        height = bar.get_height()
        axs[2].text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}",
            ha='center',
            va='bottom'
        )
    
    # Rotate x-axis labels on the last subplot
    axs[2].tick_params(axis='x', rotation=45)
    axs[2].set_xlabel('Fecha')
    
    # Adjust layout
    plt.tight_layout()
    axs[0].set_title(f"Viento diario del {date_1} al {date_2} - Estación {station}")
    plt.xlabel('Fecha')
    plt.show()
    
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



def graph_extremos(df):
    df['fecha_dt'] = pd.to_datetime(df['fecha_ocurrencia'], errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ DataFrame vacío para extremos.")
        return
    
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    ax[0].set_title("Extremos registrados")
    ax[0].scatter(df['fecha_dt'], df["rachMax_kmh"], label="max wind run")
    ax[0].legend()
    ax[0].set_ylabel("Viento km/h")
    
    bars = ax[1].bar(df['fecha_dt'], df["dirRachMax_grados"], width=50)
    
    ax[1].tick_params(axis='x', rotation=45)
    ax[1].set_ylabel("Dirección racha (°)")
    ax[1].set_xlabel("Fecha")
    
    for bar in bars:
        height = bar.get_height()
        ax[1].text(
            bar.get_x() + bar.get_width(),  # position horizontale (centre de la barre)
            height,                              # position verticale (au sommet)
            f"{height:.1f}",                     # texte (formaté à 1 décimale)
            ha='center',                        # alignement horizontal
            va='bottom'                         # alignement vertical
        )
    
    plt.tight_layout()
    plt.show()


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
    
    x = np.arange(len(df))

    fig, axes = plt.subplots(len(columnas_viento), 1, figsize=(12, 2 * len(columnas_viento)), sharex=True)
    fig.suptitle(f"Valores normales de viento - Estación {station}")

    for i, col in enumerate(columnas_viento):
        if col in df.columns:
            axes[i].plot(x, df[col], label=col)
            axes[i].legend()
            axes[i].set_ylabel(col)

    axes[-1].set_xlabel("Índice (sin fecha)")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()
    


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
