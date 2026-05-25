import requests
import pandas as pd
import matplotlib.pyplot as plt

import os
# Electricity Maps API key
API_KEY = os.getenv("ELECTRICITY_MAPS_API_KEY")

if not API_KEY:
    raise ValueError(
        "Missing API key. Please set ELECTRICITY_MAPS_API_KEY as an environment variable."
    )

url = "https://api.electricitymaps.com/v3/electricity-source/hydro/past-range"

headers = {
"auth-token": API_KEY
}

params1 = {
    "zone": "FR",
    "start": "2026-01-01T00:00:00.000Z",
    "end": "2026-01-02T00:00:00.000Z",
    "temporalGranularity": "hourly"
}

params2 = {
    "zone": "ES",
    "start": "2026-01-01T00:00:00.000Z",
    "end": "2026-01-02T00:00:00.000Z",
    "temporalGranularity": "hourly"
}

params3 = {
    "zone": "DE",
    "start": "2026-01-01T00:00:00.000Z",
    "end": "2026-01-02T00:00:00.000Z",
    "temporalGranularity": "hourly"
}

response1 = requests.get(url, headers=headers, params=params1)
response2 = requests.get(url, headers=headers, params=params2)
response3 = requests.get(url, headers=headers, params=params3)

data1 = response1.json()
data2 = response2.json()
data3 = response3.json()


rows1 = data1["data"]
rows2 = data2["data"]
rows3 = data3["data"]
df1 = pd.json_normalize(rows1)
df2 = pd.json_normalize(rows2)
df3 = pd.json_normalize(rows3)

df1 = df1[["datetime", "value"]]
df2 = df2[["datetime", "value"]]
df3 = df3[["datetime", "value"]]


df1["datetime"] = pd.to_datetime(df1["datetime"])
df1["hour"] = df1["datetime"].dt.hour
df1["value"] = df1["value"]/1000
df2["datetime"] = pd.to_datetime(df2["datetime"])
df2["hour"] = df2["datetime"].dt.hour
df2["value"] = df2["value"]/1000
df3["datetime"] = pd.to_datetime(df3["datetime"])
df3["hour"] = df3["datetime"].dt.hour
df3["value"] = df3["value"]/1000

france_values = df1["value"]
spain_values = df2["value"]
germany_values = df3["value"]

bar_width = 0.35
x = range(len(df1["datetime"]))

plt.figure(figsize=(13, 4))
plt.bar([i - bar_width/3 for i in x], france_values, width=bar_width/3, label = "France", color = "blue")
plt.bar([i + bar_width/3 for i in x], spain_values, width=bar_width/3, label = "Spain", color = "orange")
plt.bar([i for i in x], germany_values, width=bar_width/3, label = "Germany", color = "red")
plt.title("Hydroelectricity generation per hour (01/01/2026)")
plt.xlabel("Day")
plt.ylabel("Hydroelectricity Generation (GWh)/hour")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, df1["hour"])
plt.legend()
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "Source : API Electricity Maps.",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  
)


plt.figure(figsize=(13, 4))
plt.bar([i for i in x], france_values, width=bar_width, label = "France", color = "blue")
plt.title("Hydroelectricity generation per hour France (01/01/2026)")
plt.xlabel("Day")
plt.ylabel("Hydroelectricity Generation (GWh)/hour")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, df1["hour"])
plt.legend()
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "Source : API Electricity Maps.",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  
)

plt.figure(figsize=(13, 4))
plt.bar([i for i in x], spain_values, width=bar_width, label = "Spain", color = "orange")
plt.title("Hydroelectricity generation per hour Spain (01/01/2026)")
plt.xlabel("Day")
plt.ylabel("Hydroelectricity Generation (GWh)/hour")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, df1["hour"])
plt.legend()
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "Source : API Electricity Maps.",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  
)

plt.figure(figsize=(13, 4))
plt.bar([i for i in x], germany_values, width=bar_width, label = "Germany", color = "red")
plt.title("Hydroelectricity generation per hour Germany (01/01/2026)")
plt.xlabel("Day")
plt.ylabel("Hydroelectricity Generation (GWh)/hour")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.xticks(x, df1["hour"])
plt.legend()
plt.tight_layout()

plt.figtext(
    0.5,  
    0.01, 
    "Source : API Electricity Maps.",
    ha="center",  
    fontsize=9, 
    bbox={"facecolor": "lightgray", "alpha": 0.5, "pad": 5}  
)


plt.show()