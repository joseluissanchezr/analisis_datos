# -*- coding: utf-8 -*-
"""
Created on Sat May 17 10:31:46 2025

@author: lisac
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

folder = os.path.expanduser(r"~\Documents\AEMET_output")

# 2. All CSV file with _limpio
pattern = os.path.join(folder, "*_limpio.csv")
csv_files = glob.glob(pattern)


if not csv_files:
    print("❌ No file *_limpio.csv find.")
else:
    print("✅ Files find :")
    for f in csv_files:
        print("  -", os.path.basename(f))


def custom_autopct(pct, values):
    """
    This is for the creation of the pie chart
    """
    
    
    if pct<1: 
        return ''
    elif pct>1 and pct <1.5:  # Seuil de 5%
        return f'{pct:.0f}% \n'  # Ajoute la valeur réelle si nécessaire
    elif 1.5<pct and pct<2 :
        return f'\n {pct:.0f}%'  # Ajoute la valeur réelle si nécessaire
    else:
        return f'{pct:.0f}%'




def graph_annuals(df):
    """

    Parameters
    ----------
    df : file in csv

    Returns 
    ------- 
    Error plot showing the wind speed
    bar graph showing the wind maximum speed
    Pie chart showing which months have more wind

    """
    
    df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')
    year = df['fecha_dt'].dt.year.iloc[1]
    station = df["estacion"].iloc[1]
   
    yerr = df["w_rec"]/24
    
    plt.figure(figsize=(10, 5))
    plt.title(f"Wind speed of year {year} at station {station}")
    plt.errorbar(df['fecha_dt'],df["w_med"], yerr=yerr,fmt='o-', label="± average wind run")
    plt.xticks(df["fecha_dt"], rotation=45, ha='right')
    plt.legend()
    save_path = os.path.join(folder, f"wind_{station}_{year}.svg")
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()
    
    
    plt.figure(figsize=(10, 5))
    plt.title(f"Maximum wind speed of year {year} at station {station}")
    
    bars = plt.bar(df['fecha_dt'], df["w_racha"], width=10)
    
    plt.xticks(df["fecha_dt"], rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # position horizontale (centre de la barre)
            height,                              # position verticale (au sommet)
            f"{height:.1f}",                     # texte (formaté à 1 décimale)
            ha='center',                        # alignement horizontal
            va='bottom'                         # alignement vertical
        )
    
    plt.tight_layout()
    save_path = os.path.join(folder, f"max_wind_{station}_{year}.svg")
    plt.savefig(save_path, bbox_inches='tight')
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
    
    plt.title(f"Windest month of year {year} at station {station}")
    save_path = os.path.join(folder, f"windy_month_{station}_{year}.svg")
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()


def graph_daily(df):
    """

    Parameters
    ----------
    df : file in csv

    Returns 
    ------- 
    Error plot showing the wind speed
    bar graph showing the wind maximum speed
    Pie chart showing which months have more wind

    """
    
    df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')
    date_1 = df['fecha_dt'].dt.date.iloc[1]
    date_2 = df['fecha_dt'].dt.date.iloc[-1]
    station = df["estacion"].iloc[1]
   
    yerr = df["dir_racha"]/24
    
    plt.figure(figsize=(10, 5))
    plt.title(f"Wind speed of {date_1} to {date_2} at station {station}")
    plt.errorbar(df['fecha_dt'],df["velmedia"], yerr=yerr,fmt='o-', label="± average wind run")
    plt.xticks(df["fecha_dt"], rotation=45, ha='right')
    plt.legend()
    save_path = os.path.join(folder, f"wind_{station}_{date_1}_to_{date_2}.svg")
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()
    
    
    plt.figure(figsize=(10, 5))
    plt.title(f"Maximum wind speed of {date_1} to {date_2} at station {station}")
    
    bars = plt.bar(df['fecha_dt'], df["racha"])
    
    plt.xticks(df["fecha_dt"], rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # position horizontale (centre de la barre)
            height,                              # position verticale (au sommet)
            f"{height:.1f}",                     # texte (formaté à 1 décimale)
            ha='center',                        # alignement horizontal
            va='bottom'                         # alignement vertical
        )
    
    plt.tight_layout()
    save_path = os.path.join(folder, f"max_wind_{station}_{date_1}_to_{date_2}.svg")
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()
    
    year = df['fecha_dt'].dt.year.astype(str)
    month = df['fecha_dt'].dt.month_name()
    day = df['fecha_dt'].dt.day.astype(str)
    
    date = date = day + " " + month + " " + year

    fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax_pie.pie(df["velmedia"], startangle=90, autopct=lambda pct: custom_autopct(pct, df["velmedia"]))

    for i, wedge in enumerate(wedges):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))

        ax_pie.text(
            x * 1.44, y * 1.1,
            date[i],
            ha='center', va='center', fontsize=12, color='black'
        )

    ax_pie.set_aspect('equal')

    for autotext in autotexts:
        autotext.set_fontsize(11)
    
    plt.title(f"Windest month of {date_1} to {date_2} at station {station}")
    save_path = os.path.join(folder, f"windy_month_{station}_{date_1}_to_{date_2}.svg")
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()


for file_path in csv_files:
    filename = os.path.splitext(os.path.basename(file_path))[0]
    df = pd.read_csv(file_path, sep=';', decimal=',', quoting=2)

    if filename == "climatologias_mensuales_anuales_viento_limpio":
        graph_annuals(df)
    elif filename == "climatologias_diarias_viento_limpio":
        graph_daily(df)
    else:
        print("Non recognized file :", filename)


