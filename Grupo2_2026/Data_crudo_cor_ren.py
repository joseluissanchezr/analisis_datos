# In this code we extract the prices of electricity in Spain, France and Germany from the API of Electricity Maps. 
# We will use this data to analyze the correlation between renewable energy generation and electricity prices in these three countries.

import pandas as pd
import requests


API_KEY = "patCytbSzwwY9ZZhgner"

url = "https://api.electricitymaps.com/v3/price-day-ahead/past-range"

headers = {
"auth-token": API_KEY
}

paramsES = {
    "zone": "ES",
    "start": "2026-01-02T00:00:00.000Z",
    "end": "2026-04-01T00:00:00.000Z",
    "temporalGranularity": "hourly"
}

paramsFR = {
    "zone": "FR",
    "start": "2026-01-02T00:00:00.000Z",
    "end": "2026-04-01T00:00:00.000Z",
    "temporalGranularity": "hourly"
}

paramsDE = {
    "zone": "DE",
    "start": "2026-01-02T00:00:00.000Z",
    "end": "2026-04-01T00:00:00.000Z",
    "temporalGranularity": "hourly "
}

responseES = requests.get(url, headers=headers, params=paramsES)
responseFR = requests.get(url, headers=headers, params=paramsFR)
responseDE = requests.get(url, headers=headers, params=paramsDE)

dataFR = responseFR.json()
dataES = responseES.json()
dataDE = responseDE.json()

rowsFR = dataFR["data"]
rowsES = dataES["data"]
rowsDE = dataDE["data"]

dfFR = pd.json_normalize(rowsFR)
dfES = pd.json_normalize(rowsES)
dfDE = pd.json_normalize(rowsDE)

dfFR = dfFR[["datetime", "value"]]
dfES = dfES[["datetime", "value"]]
dfDE = dfDE[["datetime", "value"]]


dfFR["datetime"] = pd.to_datetime(dfFR["datetime"])
dfFR["day"] = dfFR["datetime"].dt.day
dfFR["value"] = dfFR["value"]/1000

dfES["datetime"] = pd.to_datetime(dfES["datetime"])
dfES["day"] = dfES["datetime"].dt.day
dfES["value"] = dfES["value"]/1000

dfDE["datetime"] = pd.to_datetime(dfDE["datetime"])
dfDE["day"] = dfDE["datetime"].dt.day
dfDE["value"] = dfDE["value"]/1000

FRANCE_Price = dfFR["value"]
SPAIN_Price = dfES["value"]
GERMANY_Price = dfDE["value"]

dfES = dfES.rename(columns={"value": "precio_es"})
dfFR = dfFR.rename(columns={"value": "precio_fr"})
dfDE = dfDE.rename(columns={"value": "precio_de"})
