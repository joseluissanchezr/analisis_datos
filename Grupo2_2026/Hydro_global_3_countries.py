from datetime import datetime, timedelta, timezone
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
headers = {"auth-token": API_KEY}


countries = ["FR", "ES", "DE"]
start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
end_date = datetime(2026, 4, 1, tzinfo=timezone.utc)
chunk_days = 10  
# creating the dataframe of hourly generation for 3 months beacuse the API has a limit of 10 days for hourly requests.


all_data = {country: [] for country in countries}

for country in countries:
    current_start = start_date

    while current_start < end_date:
        current_end = current_start + timedelta(days=chunk_days)
        if current_end > end_date:
            current_end = end_date

        params = {
            "zone": country,
            "start": current_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "temporalGranularity": "hourly",
            "flowTraced": "false",
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_data[country].extend(data["data"])
        except requests.exceptions.RequestException as e:
            print(f"Error for {country} between {current_start.date()} and {current_end.date()}: {e}")
            break

        current_start = current_end

dfs = {}
for country in countries:
    if all_data[country]:
        df = pd.DataFrame(all_data[country])
        df = df[["datetime", "value"]]
        df["value"] = df["value"] / 1000  
        df["country"] = country  
        dfs[country] = df
    else:
        print(f"No data obtained for {country}")



def calculate_hydro_statistics(hydro_df):
    statistics = (
        hydro_df.groupby("country")["value"]
        .agg(["mean", "max", "min", "std"])
        .rename(
            columns={
                "mean": "average_hydro_generation_gw",
                "max": "maximum_hydro_generation_gw",
                "min": "minimum_hydro_generation_gw",
                "std": "hydro_generation_std_gw",
            }
        )
        .reset_index()
    )
    return statistics


if dfs:
    combined_df = pd.concat(dfs.values(), ignore_index=True)
    combined_df["datetime"] = pd.to_datetime(combined_df["datetime"])

    stats_df = calculate_hydro_statistics(combined_df)
    print("\nHydro statistics :")
    print(stats_df.to_string(index=False))


    plt.figure(figsize=(14, 7))
    for country in countries:
        if country in dfs:
            country_df = combined_df[combined_df["country"] == country]
            plt.plot(
                country_df["datetime"],
                country_df["value"],
                label=country,
            )

    plt.title("Hourly Hydro Generation - France, Spain, Germany (January-March 2026)")
    plt.xlabel("Datetime")
    plt.ylabel("Hydro generation (GW)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

