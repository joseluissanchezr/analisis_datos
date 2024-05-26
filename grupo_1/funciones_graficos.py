import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import seaborn as sns


def grafico_tipo_combustible (df):
   
    #Tipo de combustible
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Fuel type', palette='viridis')
    plt.title('Frecuencia por Tipo de Combustible')
    plt.xlabel('Tipo de Combustible')
    plt.ylabel('Frecuencia')
    plt.xticks(rotation=45)
    plt.show()

def grafico_indisponibilidad(df):
    
    #Indisponibilidad por participante del mercado
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, y='Market participant', hue='Unavailability type', palette='viridis')
    plt.title('Tipo de Indisponibilidad por Participante del Mercado')
    plt.ylabel('Participante del Mercado')
    plt.xlabel('Conteo de Indisponibilidad')
    plt.show()



def grafico_de_razones(df, columna_original='Reason for Unavailability', nueva_columna='Reason'):
    """
    Función para estandarizar las razones de indisponibilidad en un DataFrame
    utilizando un diccionario de relaciones entre frases.

    Parámetros:
        df (DataFrame): El DataFrame de pandas que contiene los datos.
        diccionario (dict): Un diccionario que relaciona las frases originales con las estandarizadas.
        columna_original (str): El nombre de la columna que contiene las razones originales.
        nueva_columna (str): El nombre de la nueva columna que se creará para las razones estandarizadas.

    """
    diccionario ={
        "Generador no disponible": ["generator partially unavailable","generator unavailable"],
        "Falla mecánica": ["fallo feeding screw failure","fallo feeding crew failure","mechanical failure", "pumping mode unavailable","fallo turbine failure", "fallo trip turbine", "fallo stop turbine","failure", "fallo", "fallo boiler failure", "fallo engine failure","problems with a turbine","fallo boiler leak","valve failure","fallo redler failure","fallo high volumen flow","trip"],
        "Indisponibilidad": ["unplanned unavailability","indisponibilidad","fuera de servicio","paro planta"],
        "Corto plazo": ["short term"],
        "Mantenimiento": [ "indisponibilidad operacional, trabajos inspección alta tensión","parada programada por mantenimiento de la unidad","indisponibilidad planificada, trabajos mtto planificado en sistema agua enfriamiento","trabajos mtto planificado en generador","mantenimiento previsto", "planes de mantenimiento", "hrsg maintenance", "revision de mantenimiento", "fallo lacking biomass", "mantenimiento previsto scheduled maintenance", "major maintenance - gt"],
        "Falla operativa": ["fallo maintenance","fallo scheduled stop", "yearly scheduling", "fallo annual stop", "stop","fallo opertional issues", "indisponibilidad operacional", "fallo operational issues", "fallo operational isuues", "fallo operational failure", "fallo operarional issues","averia"],
        "Falla eléctrica": ["fallo electrical failure", "fallo electrofilter failure", "parada total de fabrica y corte electrico general incluida planta d e energia"]
    }

    def aplicar_diccionario(razon):
        for clave, valor in diccionario.items():
            if razon.lower() in valor:
                return clave
        return 'Unknown'
    
    # Aplicar la función a la columna original y crear la nueva columna
    df[nueva_columna] = df[columna_original].apply(aplicar_diccionario)
    
    # Contar las ocurrencias de cada razón
    reason_counts = df['Reason'].value_counts()

    # Crear el gráfico de pastel
    plt.figure(figsize=(10, 8))
    plt.pie(reason_counts, labels=reason_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('rainbow', len(reason_counts)))

    # Añadir título
    plt.title('Distribución de las Razones de Indisponibilidad')

    # Mostrar el gráfico
    plt.axis('equal')  # Asegura que el pie chart sea circular
    plt.show()

def incidencia_por_combustible(df):
    fuel_types = df['Fuel type'].unique()

    # Configuración del estilo de los gráficos
    sns.set(style="whitegrid")

    # Crear un gráfico de barras para cada tipo de combustible
    for fuel in fuel_types:
        plt.figure(figsize=(12, 6))
        
        # Filtrar el DataFrame para el tipo de combustible actual
        df_fuel = df[df['Fuel type'] == fuel]
        
        # Contar las ocurrencias de cada razón para el tipo de combustible actual
        reason_counts = df_fuel['Reason'].value_counts()
        
        # Crear el gráfico de barras
        sns.barplot(x=reason_counts.values, y=reason_counts.index, palette='viridis')
        
        # Configurar el gráfico
        plt.title(f'Distribución de Razones de Indisponibilidad para {fuel}')
        plt.xlabel('Conteo de Indisponibilidad')
        plt.ylabel('Razón')
        
        # Mostrar el gráfico
        plt.show()


