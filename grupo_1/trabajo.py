import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import pandas as pd


# First test with data from one day
url = "https://umm.omie.es/feeds/electricity?date=2024-05-06"

response = requests.get(url, verify=False)

soup = BeautifulSoup(response.text, 'lxml')
raw_data = soup.find_all('summary')[0]


installed = 'installedCapacity'
available = 'availableCapacity'
unavailable = 'unavailableCapacity'


def find_capacities(capacity_type, summary):
    '''
    inputs:
        capacity_type: str, either 'installedCapacity', 'availableCapacity' or 'unavailableCapacity'
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        value (int) of the corresponding capacity for the given event
    '''
    start_index = summary.find(':'+capacity_type)
    stop_index = summary.find('</umm:'+capacity_type)
    value = summary[start_index+len(':'+capacity_type)+1:stop_index]
    return float(value)

def find_fuel_type(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        fuel_type: str, of the market participant of the given event
    '''
    start_index = summary.find('fuelType')
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
    stop_index = summary.find('</cm:name><cm:ace>')
    fuel_type = summary[start_index+len('marketParticipant><cm:name>')+1:stop_index]
    return fuel_type

def find_unavailability_type(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, type of unavailability ('Planned' or 'Unplanned')
    '''
    start_index = summary.find('unavailabilityType')
    stop_index = summary.find('</umm:unavailabilityType')
    fuel_type = summary[start_index+len('unavailabilityType')+1:stop_index]
    return fuel_type

def find_messageId(summary):
    '''
    inputs:
        summary: str, element of soup.find_all('summary') converted with '.text'
    output:
        name: str, messageId
    '''
    start_index = summary.find('messageId')
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
    stop_index = summary.find('</umm:publicationDateTime')
    messageId = summary[start_index+len('publicationDateTime')+1:stop_index]
    return messageId



print(find_capacities('installedCapacity', raw_data.text))
print(find_capacities('availableCapacity', raw_data.text))
print(find_capacities('unavailableCapacity', raw_data.text))
print(find_fuel_type(raw_data.text))
print(find_market_participant(raw_data.text))
print(find_unavailability_type(raw_data.text))
print(find_messageId(raw_data.text))
print(find_publication_date(raw_data.text))