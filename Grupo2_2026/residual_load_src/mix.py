import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "gHCKjHZ6f2AvhZKfCqg7"

countries = {
    "Spain": "ES",
    "France": "FR",
    "Germany": "DE"
}

url = "https://api.electricitymaps.com/v4/electricity-mix/past-range"

headers = {
    "auth-token": API_KEY
}

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 4, 1)

step = timedelta(days=10)

mix_data = {}

for country, zone in countries.items():

    all_data = []
    current_start = start_date

    while current_start < end_date:

        current_end = min(current_start + step, end_date)

        params = {
            "zone": zone,
            "start": current_start.strftime("%Y-%m-%dT00:00:00Z"),
            "end": current_end.strftime("%Y-%m-%dT00:00:00Z")
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        data = response.json()

        if isinstance(data, list):
            all_data.extend(data)

        elif isinstance(data, dict) and "data" in data:
            all_data.extend(data["data"])

        elif isinstance(data, dict) and "history" in data:
            all_data.extend(data["history"])

        else:
            print("Unexpected response:", data)

        print(f"{country}: {current_start} -> {current_end}")

        current_start = current_end

    df = pd.DataFrame(all_data)

    mix_data[country] = df

    print(f"{country} rows:", len(df))

spain_mix = mix_data["Spain"]
france_mix = mix_data["France"]
germany_mix = mix_data["Germany"]

print(spain_mix.head())