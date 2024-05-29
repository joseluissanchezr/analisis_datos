import pandas as pd

# Definir una función para cargar y procesar cada archivo individualmente
def cargar_y_procesar_archivo(file_path):

    # Cargar el archivo CSV
    df = pd.read_csv(file_path, encoding='latin1', sep=';', skiprows=2)
    # Eliminar la columna 'Unnamed'
    del df["Unnamed: 8"]

    # Suprimir los datos que faltan
    df.dropna(inplace=True)

    # Modificar tipos de datos:

    #1 'Hora' modificar la hora para números enteros.
    df['Hora'] = df['Hora'].astype(int)
    #2 'Fecha' modificar las fechas actuales de los archivos.csv 
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
    #3 'Energía_Compra_Venta' modificar los valores flotantes despues de reemplazar comas por puntos.
    df['Energía Compra/Venta'] = df['Energía Compra/Venta'].str.replace(".", "").str.replace(',', '.').astype(float)
    #4 'Precio_Compra_Venta' modificar los valores flotantes despues de reemplazar comas por puntos.
    df['Precio Compra/Venta'] = df['Precio Compra/Venta'].str.replace('.', '').str.replace(',', '.').astype(float)

    # A continuación,se eliminaran los valores límites que nos estaban distorsionando la señal de precios del OMIE.
    # Creación de un data_frame_filtrado, Nuestra condición de operación de datos es entre un intervalo de precios de [>-4€/Mwh,<1500€/Mwh] 
    
    #df = df[(df['Precio_Compra_Venta'] >= -5) & (df['Precio_Compra_Venta'] <= 1000)]

    # Se guarda la dataframe en el mismo archivo
    df.to_csv(file_path, index=False, sep=";", encoding="latin-1")

    # Liberar espacio en la memoria
    del df