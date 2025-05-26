
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import numpy as np

# 1. Resolver la ruta ~ al path absoluto
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
        
def custom_autopct(pct, values):
    if pct<1: 
        return ''
    elif pct>1 and pct <1.5:  
        return f'{pct:.0f}% \n' 
    elif 1.5<pct and pct<2 :
        return f'\n {pct:.0f}%'  
    else:
        return f'{pct:.0f}%'

        
        

def graph_annuals(df, case):
    df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ El DataFrame está vacío o tiene menos de 2 filas válidas para annuals.")
        print(df.head())
        return

    year = df['fecha_dt'].dt.year.iloc[1]
    station = df["estacion"].iloc[1]

    
    
    if case==1:
        plt.plot(df['fecha_dt'], df['w_med'], label='Velocidad media (m/s)')
        plt.xticks(df["fecha_dt"], rotation=45, ha='right')
        plt.title(f"Variables de viento en {year} - Estación {station}")
        plt.xlabel('Fecha')
        plt.legend()
        plt.show()
   
    elif case==2:
        plt.plot(df['fecha_dt'], df['w_racha'],label='Racha máxima (m/s)')
        plt.xticks(df["fecha_dt"], rotation=45, ha='right')
        plt.title(f"Variables de viento en {year} - Estación {station}")
        plt.xlabel('Fecha')
        plt.legend()
        plt.show()
        
    elif case==3:
        bars = plt.bar(df['fecha_dt'], df['w_rec'],label='Recorrido viento', width=5)
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
            
        plt.title(f"Variables de viento en {year} - Estación {station}")
        plt.xlabel('Fecha')
        plt.legend()
        plt.show()
        
    elif case==4:
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
        
    elif case==5:
        
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
            
    else:
        print("Error")
            

    

def graph_daily(df, case):
    df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['fecha_dt'])

    if df.empty or len(df) < 2:
        print("❌ El DataFrame está vacío o tiene menos de 2 filas válidas para daily.")
        print(df.head())
        return

    date_1 = df['fecha_dt'].dt.date.iloc[0]
    date_2 = df['fecha_dt'].dt.date.iloc[-1]
    station = df["estacion"].iloc[0]
    
    plt.figure()

    
    if case==1:
        plt.plot(df['fecha_dt'],df['velmedia'],label='Velocidad media (m/s)')
        plt.xticks(df["fecha_dt"], rotation=45, ha='right')
        plt.title(f"Viento diario del {date_1} al {date_2} - Estación {station}")
        plt.xlabel('Fecha')
        plt.legend()
        plt.show()
   
    elif case==2:
        plt.plot(df['fecha_dt'],df['racha'],label='Racha máxima (m/s)')
        plt.xticks(df["fecha_dt"], rotation=45, ha='right')
        plt.title(f"Viento diario del {date_1} al {date_2} - Estación {station}")
        plt.xlabel('Fecha')
        plt.legend()
        plt.show()
        
    elif case==3:
        bars = plt.bar(df['fecha_dt'], df['dir_racha'], label='Dirección de racha (°)')
        plt.xticks(df["fecha_dt"], rotation=45, ha='right')
        plt.title(f"Viento diario del {date_1} al {date_2} - Estación {station}")
        plt.xlabel('Fecha')
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,  # position horizontale (centre de la barre)
                height,                              # position verticale (au sommet)
                f"{height:.1f}",                     # texte (formaté à 1 décimale)
                ha='center',                        # alignement horizontal
                va='bottom'                         # alignement vertical
            )
        plt.legend()
        plt.show()
        
    elif case==4:
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
        
    elif case==5:
        
        
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
    
    else:
        print("Error")

# 3. Preguntar al usuario qué tipo de datos quiere graficar
print("\n¿Qué datos deseas visualizar?")
print("1 - Climatologías diarias")
print("2 - Climatologías mensuales/anuales")
choice = input("Introduce 1 o 2: ")

for file_path in csv_files:
    filename = os.path.basename(file_path).lower()
    df = pd.read_csv(file_path, sep=';', decimal=',', quoting=2)

    if "diaria" in filename and choice == "1":
        print("Would you like to see :\n")
        print("1 : the average wind speed")
        print("2 : the maximum wind speed")
        print("3 : the dirrection of the wind")
        print("4 : the proportion of wind per months")
        print("5 : all of the above")
        graph = input("Introduce 1, 2, 3, 4 or 5 :").strip()
        graph_int = int(graph)
        match graph_int:
            case 1:
                graph_daily(df, 1)
            case 2:
                graph_daily(df, 2)
            case 3:
                graph_daily(df, 3)
            case 4:
                graph_daily(df, 4)
            case 5:
                graph_daily(df, 5)
                
    elif "anual" in filename and choice == "2":
        print("Would you like to see :\n")
        print("1 : the average wind speed")
        print("2 : the maximum wind speed")
        print("3 : the wind recorded")
        print("4 : the proportion of wind per months")
        print("5 : all of the above")
        graph = input("Introduce 1, 2, 3, 4 or 5 :").strip()
        graph_int = int(graph)
        match graph_int:
            case 1:
                graph_annuals(df, 1)
            case 2:
                graph_annuals(df, 2)
            case 3:
                graph_annuals(df, 3)
            case 4:
                graph_annuals(df, 4)
            case 5:
                graph_annuals(df, 5)
