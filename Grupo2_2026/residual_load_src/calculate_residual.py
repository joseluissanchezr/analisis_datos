import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "gHCKjHZ6f2AvhZKfCqg7"

countries = {
    "Spain": "ES",
    "France": "FR",
    "Germany": "DE"
}

headers = {"auth-token": API_KEY}

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 4, 1)
step = timedelta(days=10)

load_url = "https://api.electricitymaps.com/v4/total-load/past-range"
mix_url = "https://api.electricitymaps.com/v4/electricity-mix/past-range"


def fetch_data(url, zone):
    all_data = []
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + step, end_date)

        params = {
            "zone": zone,
            "start": current_start.strftime("%Y-%m-%dT00:00:00Z"),
            "end": current_end.strftime("%Y-%m-%dT00:00:00Z")
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()

        if isinstance(data, list):
            all_data.extend(data)
        elif isinstance(data, dict) and "data" in data:
            all_data.extend(data["data"])
        elif isinstance(data, dict) and "history" in data:
            all_data.extend(data["history"])
        else:
            print("Unexpected response:", data)

        current_start = current_end

    return pd.DataFrame(all_data)


residual_load_data = {}

for country, zone in countries.items():

    print(f"\nDownloading data for {country}...")

    load_df = fetch_data(load_url, zone)
    mix_df = fetch_data(mix_url, zone)

    load_df["datetime"] = pd.to_datetime(load_df["datetime"])
    mix_df["datetime"] = pd.to_datetime(mix_df["datetime"])

    mix_df["solar"] = mix_df["mix"].apply(lambda x: x.get("solar", 0))
    mix_df["wind"] = mix_df["mix"].apply(lambda x: x.get("wind", 0))
    mix_df["hydro"] = mix_df["mix"].apply(lambda x: x.get("hydro", 0))

    merged = pd.merge(
        load_df[["datetime", "value"]],
        mix_df[["datetime", "solar", "wind", "hydro"]],
        on="datetime",
        how="inner"
    )

    merged = merged.rename(columns={"value": "total_load"})

    merged["renewable_generation"] = (
        merged["solar"] + merged["wind"] + merged["hydro"]
    )

    merged["residual_load"] = (
        merged["total_load"] - merged["renewable_generation"]
    )

    residual_load_data[country] = merged

    print(f"{country} rows:", len(merged))
    print(merged.head())


print("\nResidual load calculation finished.")