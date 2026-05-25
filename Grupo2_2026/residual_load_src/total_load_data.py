import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "gHCKjHZ6f2AvhZKfCqg7"

countries = {
    "Spain": "ES",
    "France": "FR",
    "Germany": "DE"
}

url = "https://api.electricitymaps.com/v4/total-load/past-range"

headers = {
    "auth-token": API_KEY
}

start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 4, 1)

step = timedelta(days=10)

# 用字典直接保存 DataFrame
country_data = {}

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
            print("Unexpected data:", data)

        print(f"{country}: {current_start} -> {current_end}")

        current_start = current_end

    # 直接转 DataFrame
    df = pd.DataFrame(all_data)

    # 保存到字典
    country_data[country] = df

    print(f"{country} rows:", len(df))

# 后续直接引用
spain_df = country_data["Spain"]
france_df = country_data["France"]
germany_df = country_data["Germany"]

print(spain_df.head())