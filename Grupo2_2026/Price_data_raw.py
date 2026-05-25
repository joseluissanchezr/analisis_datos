# In this code we extract the prices of electricity in Spain, France and Germany from the API of Electricity Maps. 
# We will use this data to analyze the correlation between renewable energy generation and electricity prices in these three countries.

import pandas as pd
import requests
from datetime import datetime, timedelta

def get_precio_data():
    API_KEY = "patCytbSzwwY9ZZhgner"
    url = "https://api.electricitymaps.com/v3/price-day-ahead/past-range"
    headers = {"auth-token": API_KEY}
    paises = ["ES", "FR", "DE"]
    lista_dfs = []

    start_date = datetime(2026, 1, 2)
    end_total = datetime(2026, 4, 1)

    for zona in paises:
        current_start = start_date
        while current_start < end_total:
            
            current_end = min(current_start + timedelta(days=9), end_total)
            
            params = {
                "zone": zona,
                "start": current_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "temporalGranularity": "hourly"
            }
            
            print(f"Descargando {zona} del {current_start.date()} al {current_end.date()}")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                data_list = data.get("history", data.get("data", []))
                if data_list:
                    df = pd.json_normalize(data_list)
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df = df.rename(columns={"value": "price_mwh"})
                    df["country"] = zona
                    lista_dfs.append(df[["datetime", "country", "price_mwh"]])
            else:
                print(f"Error en {zona}: {response.text}")
                
            current_start = current_end

    return pd.concat(lista_dfs, ignore_index=True)