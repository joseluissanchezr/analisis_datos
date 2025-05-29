# Empezamos con la importacion de todos los modulos necesarios
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

# Definimos tres valores con referencia a la capacidad
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
    '''_
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

def plotCapInst(dataFrame,xlabel,ylabel,title):
    try:
        x=dataFrame["MessageId"]
        y=dataFrame["Installed capacity"]
        plt.scatter(x,y,c="blue")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks([])
        plt.show()
    except Exception as e:
        print(f"Error plotting Installed Capacity: {e}")

# Recopilación de los datos con fecha de publicación del mes pasado
current_date = datetime.now()
first_day_of_current_month = current_date.replace(day=1)
last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
first_day_of_last_month = last_day_of_last_month.replace(day=1)
day = first_day_of_last_month

# Lista de fechas del mes pasado
last_month = []
while day <= last_day_of_last_month:
    last_month.append(day.strftime('%Y-%m-%d'))
    day += timedelta(days=1)

general_url = 'https://umm.omie.es/feeds/electricity?date='

data_list = []

# Recopilación de datos de cada día del mes pasado
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

# Gráfico de barras para visualizar los participantes del mercado
fig = plt.figure(figsize = (10, 5))
# Creacion del bar plot
values_counts = df['Market participant'].value_counts()
values_counts.plot(kind='bar')
# Titulo y axis 
plt.xlabel("Participante")
plt.ylabel("No. de ocurencias")
plt.title("Frecuencia de unavailabilities segun el participante")
plt.show()

# Gráfico de Pareto de los participantes
# Ocurencias y % cumulativo
values_counts = df['Market participant'].value_counts().sort_values(ascending=False)
cumulative_percentage = values_counts.cumsum() / values_counts.sum() * 100
# Creacion del grafico
fig, ax1 = plt.subplots()
ax1.bar(values_counts.index, values_counts, color='C0')
ax1.set_xlabel('Participante')
ax1.set_ylabel('No. de ocurencias', color='C0')
ax1.tick_params(axis='y', labelcolor='C0')
# Creacion del segundo grafico
ax2 = ax1.twinx()
ax2.plot(values_counts.index, cumulative_percentage, color='C1', marker='o', linestyle='-')
ax2.set_ylabel('"%" cumulado', color='C1')
ax2.tick_params(axis='y', labelcolor='C1')
ax2.set_ylim(0, 100)
# Titulo
plt.title('Pareto de los participantes')
plt.show()

# Extracción de columnas no numéricos
numValues=list(df.columns.drop(["MessageId","Market participant",
                           "Publication date","Unavailability type", 'Reason for Unavailability', 
                           "Fuel type"]))
print("-"*49)
print("\nCálculo del Zscore a las siguientes columnas: \n")
print(numValues)
print("-"*49)

# Cálculo de la Z-score 
for col in numValues:
    col_zscore= col + "_zscore"
    df[col_zscore]=(df[col] - df[col].mean())/df[col].std(ddof=0) 

# Boxplot para visualizar los Zscores de las capacidades
data_zscore = [df['Installed capacity_zscore'], df['Available capacity_zscore'], df['Unavailable capacity_zscore']]
fig = plt.figure(figsize =(10, 5))
ax = fig.add_subplot(111)
bp = ax.boxplot(data_zscore, vert = 0)
# Cambiar como aparecen las valores extranas
for flier in bp['fliers']:
    flier.set(marker ='D',
              color ='#e7298a',
              alpha = 0.2)
# Dar un nombre al x-axis
ax.set_yticklabels(['Installed capacity', 'Available capacity', 'Unavailable capacity'])
# Dar un titulo al grafico
plt.title("Boxplot de los zscores de las capacidades")
# Mostrar el boxplot
plt.show()
print("Vemos que hay valores raras que se necesitan limpiar")

#Se añaden al dataframe original los zscores de las columnas seleccionadas
'''
Uso de la ZSCORE para limpiar datos más relevantes:
La ZSCORE es un indicador de la desviacion estándar respecto a la media. 
Una ZSCORE de -2 indica que el valor está 2 desviaciones medias por debajo de la media y equivale al percentil -2. 
Siendo la desviación media .std
'''
print("-"*49)
print(" \nSe añaden al dataframe los Zscores de las columnas descritas anteriormente:")
print (df.head()) 
print("-"*49)
print("\nvalores máximos y minimos \n")
#Tabulación de valores máximos y mínimos
createMinMax(df)
print("-"*49)
print("\n Se muestran a continuación los datos de capacidad instalada sin filtrar \n ")
plotCapInst(df,"Proyectos (sin limpieza)","Potencia Instalada","Proyectos sin limpieza según la potencia instalada")
print("-"*49)

# IMPORTANTE - se muestran los valores de potencia instalada en las líneas de arriba (da error pero funciona(por eso el try y el except))
# Se eliminan del dataframe los valores de capacidad instalada = 0 (es decir valores irrelevantes)
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
plotCapInst(df,"Proyectos","Potencia Instalada","Proyectos según la potencia instalada")
print("máximos y mínimos tras primera limpieza:")
createMinMax(df)
print("-"*49)
print("Las capacidades parecen dividirse en tres grandes tramos:")
print("De 0 a 200 MW, de 200 a 350 MW y mas de 400 MW.")
print("Dado que los datos se dividen en tres categorías, podríamos seguir desarrollando este código en aprendizaje automático, en el que el propio ordenador puede adivinar la capacidad en función de las diferentes características")
print("Debido a la falta de tiempo, esto no se puede hacer en este proyecto, pero es algo interesante para perseguir en el futuro")
print("-"*49)


# Se añaden gráficos para ver diferentes tipos de indisponibilidades y los razones
print("Ahora, vamos a ver a algunos graficos para entender mejor esta situacion")
funciones_graficos.grafico_tipo_combustible(df)
funciones_graficos.grafico_indisponibilidad(df)
funciones_graficos.grafico_de_razones(df)
funciones_graficos.incidencia_por_combustible(df)

# Gráfico de barras para comparar la capacidad instalada por tipo de combustible
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='Fuel type', y='Installed capacity', estimator=sum)
plt.xlabel('Fuel Type')
plt.ylabel('Installed Capacity')
plt.title('Installed Capacity by Fuel Type')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

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

# Gráficos que permiten comprender mejor las tendencias y la distribución de la capacidad
# y un análisis más detallado de las interrupciones por parte de los distintos participantes en el mercado.

# Análisis de las tendencias de capacidad a lo largo del tiempo
df['Publication date'] = pd.to_datetime(df['Publication date'])
df = df.sort_values('Publication date')

# Media móvil de la capacidad instalada, disponible e indisponible
df['Installed capacity MA'] = df['Installed capacity'].rolling(window=7).mean()
df['Available capacity MA'] = df['Available capacity'].rolling(window=7).mean()
df['Unavailable capacity MA'] = df['Unavailable capacity'].rolling(window=7).mean()
plt.figure(figsize=(10, 6))
plt.plot(df['Publication date'], df['Installed capacity MA'], label='Installed capacity MA')
plt.plot(df['Publication date'], df['Available capacity MA'], label='Available capacity MA')
plt.plot(df['Publication date'], df['Unavailable capacity MA'], label='Unavailable capacity MA')
plt.xlabel('Fecha')
plt.ylabel('Capacidad')
plt.title('Media móvil de capacidades a lo largo del tiempo')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Histogramas para visualizar la distribución de las distintas capacidades
# Installed
plt.figure(figsize=(10, 6))
sns.histplot(df['Installed capacity'], bins=20, kde=True)
plt.xlabel('Installed Capacity')
plt.title('Distribución de la capacidad instalada')
plt.show()
# Available
plt.figure(figsize=(10, 6))
sns.histplot(df['Available capacity'], bins=20, kde=True)
plt.xlabel('Available Capacity')
plt.title('Distribución de la capacidad disponible')
plt.show()
#Unavailable
plt.figure(figsize=(10, 6))
sns.histplot(df['Unavailable capacity'], bins=20, kde=True)
plt.xlabel('Unavailable Capacity')
plt.title('Distribución de la capacidad no disponible')
plt.show()

# Intervalos de confianza para las capacidades
from scipy import stats
def confidence_interval(data, confidence=0.95):
    mean = np.mean(data)
    sem = stats.sem(data)
    h = sem * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
    return mean, mean - h, mean + h
installed_confidence = confidence_interval(df['Installed capacity'].dropna())
available_confidence = confidence_interval(df['Available capacity'].dropna())
unavailable_confidence = confidence_interval(df['Unavailable capacity'].dropna())
print("-"*49)
print ("La media y los intervalos de confianza para las capacidades son los siguientes :")
print(f"Installed Capacity: Media={installed_confidence[0]}, IC=({installed_confidence[1]}, {installed_confidence[2]})")
print(f"Available Capacity: Media={available_confidence[0]}, IC=({available_confidence[1]}, {available_confidence[2]})")
print(f"Unavailable Capacity: Media={unavailable_confidence[0]}, IC=({unavailable_confidence[1]}, {unavailable_confidence[2]})")

# Análisis de las interrupciones por tipo de participante
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='Market participant', order=df['Market participant'].value_counts().index)
plt.xticks(rotation=90)
plt.xlabel('Participante del mercado')
plt.ylabel('No. de interupciones')
plt.title('Interupciones según el participante del mercado')
plt.show()

# Conclusión general
print("-"*49)
print("Conclusión general del workshop:")
print("Tras analizar los gráficos anteriores, podemos afirmar que, aunque cada tipo de energía tiene diferentes motivos de indisponibilidad, la causa principal en general es un generador no disponible. Por lo tanto, si queremos mejorar la situación, podemos aconsejar que la cantidad de generadores siga la tendencia de la demanda, realizando inversiones cuando sea necesario, pero sobre todo gestionando bien la producción.")