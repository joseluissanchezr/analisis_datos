import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import warnings
import urllib3
warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter('ignore', FutureWarning)
from tqdm import tqdm

from tabulate import tabulate
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import funciones_graficos


installed = 'installedCapacity'
available = 'availableCapacity'
unavailable = 'unavailableCapacity'

# Funciones para recopilar datos relevantes
def find_capacities(capacity_type, summary):
    '''
    inputs:
        capacity_type: str, either 'installedCapacity', 'availableCapacity' or 'unavailableCapacity'
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        value (int) of the corresponding capacity for the given event
    '''
    start_index = summary.find(':'+capacity_type)
    if start_index == -1:
        return np.nan

    stop_index = summary.find('</umm:'+capacity_type)
    value = summary[start_index+len(':'+capacity_type)+1:stop_index]
    return float(value)

def find_fuel_type(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        fuel_type: str, of the fuel type of the given event
    '''
    start_index = summary.find('fuelType')
    if start_index == -1:
        return "Unknown"
   
    stop_index = summary.find('</umm:fuelType')
    fuel_type = summary[start_index+len('fuelType')+1:stop_index]
    return fuel_type

def find_market_participant(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, name of the market participant of the given event
    '''
    start_index = summary.find('marketParticipant><cm:name>')
    if start_index == -1:
        return "Unknown"

    stop_index = summary.find('</cm:name><cm:ace>')
    market_participant = summary[start_index+len('marketParticipant><cm:name>'):stop_index]
    return market_participant

def find_unavailability_type(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, type of unavailability ('Planned' or 'Unplanned')
    '''
    start_index = summary.find('unavailabilityType')
    if start_index == -1:
        return "Unknown"

    stop_index = summary.find('</umm:unavailabilityType')
    unavailability_type = summary[start_index+len('unavailabilityType')+1:stop_index]
    return unavailability_type

def find_messageId(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, messageId
    '''
    start_index = summary.find('messageId')
    if start_index == -1:
        return "Unknown"
    
    stop_index = summary.find('</umm:messageId')
    messageId = summary[start_index+len('messageId')+1:stop_index]
    return messageId

def find_publication_date(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, publication date
    '''
    start_index = summary.find('publicationDateTime')
    if start_index == -1:
        return "Unknown"
    
    stop_index = summary.find('</umm:publicationDateTime')
    publication_date = summary[start_index+len('publicationDateTime')+1:stop_index]
    return publication_date

#Extraigo una columna de datos extra para analizar las razones de indisponibilidad
def find_reason_unavailability(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, type of unavailability (different reasons)
    '''
    start_index = summary.find('unavailabilityReason')
    if start_index == -1:
        return "Unknown"

    stop_index = summary.find('</umm:unavailabilityReason')
    unavailability_reason = summary[start_index+len('unavailabilityReason')+1:stop_index]
    return unavailability_reason
        
#Esta función crea una tabla de los valores máximos y mínimos del dataframe
def createMinMax(dataFrame):
    headers=["Values","maxVal","minVal"]
    values=list(dataFrame.columns)
    maxval=list(dataFrame.max(axis=0))
    minval=list(dataFrame.min(axis=0))
    table=zip(values,maxval,minval)
    print(tabulate(table,headers=headers),"\n")

def plotCapInst(dataFrame,xlabel,ylabel):
    try:
        x=dataFrame["MessageId"]
        y=dataFrame["Installed capacity"]

        plt.scatter(x,y,c="blue")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks([])
        plt.show()
    
    except:
        pass
# Recopilación de los datos con fecha de publicación del mes pasado
current_date = datetime.now()

first_day_of_current_month = current_date.replace(day=1)

last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
first_day_of_last_month = last_day_of_last_month.replace(day=1)

day = first_day_of_last_month
last_month = []

while day <= last_day_of_last_month:
    last_month.append(day.strftime('%Y-%m-%d'))
    day += timedelta(days=1)

general_url = 'https://umm.omie.es/feeds/electricity?date='

data_list = []

for day in tqdm(last_month):
    url = general_url+day
    response = requests.get(url, verify=False)
    
    soup = BeautifulSoup(response.text, 'lxml')
    raw_data = soup.find_all('summary')
            
    for entry in raw_data:
        string = entry.text
        
        messageId = find_messageId(string)
        market_participant = find_market_participant(string)
        publication_date = find_publication_date(string)
        unavailability_type = find_unavailability_type(string)
        unavailability_reason = find_reason_unavailability(string)

        installed_capacity = find_capacities(installed, string)
        available_capacity = find_capacities(available, string)
        unavailable_capacity = find_capacities(unavailable, string)
        fuel_type = find_fuel_type(string)

        data_list.append({
                        'MessageId': messageId,
                        'Market participant': market_participant,
                        'Publication date': publication_date,
                        'Unavailability type': unavailability_type,
                        'Fuel type': fuel_type,
                        'Installed capacity': installed_capacity,
                        'Available capacity': available_capacity,
                        'Reason for Unavailability':unavailability_reason,
                        'Unavailable capacity': unavailable_capacity})

df = pd.DataFrame(data_list)

# Visualización de los primeros registros del dataframe
print("-------------------------------------------------")
print(df.head())
print("-------------------------------------------------")

# Analizar si los datos tienen algún registro con NaN (no es el caso) #
valuesrow_with_nan=df[df.isnull().any(axis=1)]

print("\nValores nulos del dataframe: \n ")
print("-"*49)
print(valuesrow_with_nan) 
print("-"*49)
# Extracción de columnas no numéricos
numValues=list(df.columns.drop(["MessageId","Market participant",
                           "Publication date","Unavailability type", 'Reason for Unavailability', 
                           "Fuel type"]))
print("-"*49)
print("\nCálculo del Zscore a las siguientes columnas: \n")
print(numValues)
print("-"*49)
# cálculo de la Z-score 
for col in numValues:
    col_zscore= col + "_zscore"
    df[col_zscore]=(df[col] - df[col].mean())/df[col].std(ddof=0) 

#Se añade al dataframe original los zscores
#de las columnas seleccionadas
#Uso de la ZSCORE para limpiar datos más relevantes:
#la ZSCORE es un indicador de la desviacion estándar respecto a la media. 
#Una ZSCORE de -2 indica que el valor está 2 desviaciones medias por debajo de la media y equivale al percentil -2. 
#Siendo la desviación media .std
print("-"*49)
print(" \nSe añaden al dataframe los Zscores de las columnas descritas anteriormente:")
print (df.head()) 
print("-"*49)
print("\nvalores máximos y minimos \n")
#Tabulación de valores máximos y mínimos
createMinMax(df)
print("-"*49)
print("\n Se muestran a continuación los datos de capacidad instalada sin filtrar \n ")
plotCapInst(df,"Proyectos (sin limpieza)","Potencia Instalada")
print("-"*49)
# IMPORTANTE - se muestran los valores de potencia instalada
# en las líneas de arriba (da error pero funciona(por eso el try y el except))
#Se eliminan del dataframe los valores de capacidad instalada = 0
countZeros=df["Installed capacity"].value_counts()[0]
print("Se eliminarán primero aquellos valores que tienen una capacidad instalada = 0  ")
print("Número de filas antes de filtrar: ")
print(len(df))
df=df.drop(df[df["Installed capacity"]== 0].index)
print("Se han eliminado: " + str(countZeros) + " valores")
print("Número de filas: ")
print(len(df))
print("-"*49)
#Se cuentan los valores negativos del dataframe y se eliminan
countNegatives=len(df[df["Available capacity"]<0])
print("En la columna de mínimos puede verse que ""Available Capacity"" tiene valores negativos. No tiene sentido y se eliminan.")
df=df.drop(df[df["Available capacity"] < 0].index)
print("Se han eliminado: " + str(countNegatives) + " valores")
print("Número de filas: ")
print(len(df))
print("-"*49)
#Uso de la Zscore para eliminar valores.
print("Ahora se eliminarán los valores con un Zscore >2.")
print("Esto se corresponde a eliminar los valores por encima del percentil 98.")
#Estas tres líneas siguientes filtran los valores del df con aquellos cuyo Zscore es menor que dos
lenBeforeZscoreFilter=len(df)
filtro1=df["Installed capacity_zscore"]<2
filtro2=df["Available capacity_zscore"]<2
filtro3=df["Unavailable capacity_zscore"]<2
#Se cambian los valores del df por los valores del df con los filtros
df=df[filtro1 & filtro2 & filtro3]
print("Se han eliminado: " + str(lenBeforeZscoreFilter-len(df)) + " valores")
print("Numero de filas:")
print(len(df))
print("-"*49)
print("Datos tras primera limpieza:")
plotCapInst(df,"Proyectos","Potencia Instalada")
print("máximos y mínimos tras primera limpieza:")
createMinMax(df)
print("-"*49)
print("Las capacidades parecen dividirse en tres grandes tramos:")
print("De 0 a 200 MW, de 200 a 350 MW y mas de 400 MW.")

# Funciones para graficar y analizar la columna extraida  de causas de falla

def grafico_tipo_combustible(df):
    
     #Tipo de combustible
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Fuel type', color='rainbow')
    plt.title('Frecuencia por Tipo de Combustible')
    plt.xlabel('Tipo de Combustible')
    plt.ylabel('Frecuencia')
    plt.xticks(rotation=45)
    plt.show()

def grafico_indisponibilidad(df):
    
    #Indisponibilidad por participante del mercado
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, y='Market participant', hue='Unavailability type', palette='rainbow')
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
        sns.barplot(x=reason_counts.values, y=reason_counts.index, color='rainbow')
        
        # Configurar el gráfico
        plt.title(f'Distribución de Razones de Indisponibilidad para {fuel}')
        plt.xlabel('Conteo de Indisponibilidad')
        plt.ylabel('Razón')
        
        # Mostrar el gráfico
        plt.show()

# Se añaden gráficos
funciones_graficos.grafico_tipo_combustible(df)
funciones_graficos.grafico_indisponibilidad(df)
funciones_graficos.grafico_de_razones(df)
funciones_graficos.incidencia_por_combustible(df)

import seaborn as sns

# Visualización de la evolución temporal de la capacidad instalada, disponible y no disponible
plt.figure(figsize=(10, 6))
plt.plot(df['Publication date'], df['Installed capacity'], label='Installed capacity')
plt.plot(df['Publication date'], df['Available capacity'], label='Available capacity')
plt.plot(df['Publication date'], df['Unavailable capacity'], label='Unavailable capacity')
plt.xlabel('Date')
plt.ylabel('Capacity')
plt.title('Evolution of Capacity Over Time')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gráfico de barras para comparar la capacidad instalada por tipo de combustible
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='Fuel type', y='Installed capacity', estimator=sum)
plt.xlabel('Fuel Type')
plt.ylabel('Installed Capacity')
plt.title('Installed Capacity by Fuel Type')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Análisis de correlación entre las diferentes capacidades
correlation_matrix = df[['Installed capacity', 'Available capacity', 'Unavailable capacity']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()

# Identificación de insights
# Por ejemplo, podríamos explorar si hay una correlación entre la capacidad instalada y la disponible
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='Installed capacity', y='Available capacity')
plt.xlabel('Installed Capacity')
plt.ylabel('Available Capacity')
plt.title('Installed vs Available Capacity')
plt.tight_layout()
plt.show()
