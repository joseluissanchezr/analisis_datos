import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import warnings
import urllib3
warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)

from tqdm import tqdm

import pandas as pd
import numpy as np

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
                        'Unavailable capacity': unavailable_capacity})

df = pd.DataFrame(data_list)

# Visualización de los primeros registros del dataframe
print("-------------------------------------------------")
print(df.head())
print("-------------------------------------------------")

# Analizar si los datos tienen algún registro con NaN (no es el caso) #

valuesrow_with_nan=df[df.isnull().any(axis=1)]

# Análisis outliers en las capacidades con Z-score#

cols=list(df.columns)
cols.remove("MessageId")
cols.remove("Market participant")
cols.remove("Publication date")
cols.remove("Unavailability type")
cols.remove("Fuel type")
# visualización de las columnas objetivo #
print("Visualización de las columnas a las que se les calculará el Zscore")
print(df[cols])

# cálculo de la Z-score #
for col in cols:
    col_zscore= col + "_zscore"
    df[col_zscore]=(df[col] - df[col].mean())/df[col].std(ddof=0)


print (df)
# Se añade al dataframe original los zscores de las columnas seleccionadas #

