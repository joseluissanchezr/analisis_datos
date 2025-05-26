# scripts/save_monthly_top_wind.py

import requests
import pandas as pd
import os
from datetime import datetime

# NOAA API Token
API_TOKEN = "gAeZlUchXkUzxowblhWeDzERXSYcXmdw"
headers = {"token": API_TOKEN}
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"

# Base request parameters
base_params = {
    "datasetid": "GHCND",
    "stationid": "GHCND:USW00093193",  # Miami station
    "datatypeid": "AWND",              # Average wind speed
    "units": "metric",
    "limit": 1000
}

def fetch_monthly_top_speeds(start_year=2015, end_year=2023):
    top_speeds = []

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            start = f"{year}-{month:02d}-01"
            # Calculer le dernier jour du mois
            if month == 12:
                end = f"{year + 1}-01-01"
            else:
                end = f"{year}-{month + 1:02d}-01"

            print(f"📅 Processing {year}-{month:02d}...")

            params = base_params.copy()
            params["startdate"] = start
            params["enddate"] = end

            response = requests.get(BASE_URL, headers=headers, params=params)

            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    df = pd.DataFrame(results)
                    max_speed = df["value"].max()
                    max_date = df[df["value"] == max_speed]["date"].values[0]
                    top_speeds.append({
                        "year": year,
                        "month": month,
                        "top_speed": max_speed,
                        "date": max_date
                    })
                    print(f"✅ Max: {max_speed} m/s on {max_date}")
                else:
                    print("⚠️ No data for this month.")
            else:
                print(f"❌ Error {response.status_code} - {response.text}")

    return pd.DataFrame(top_speeds)

def save_to_csv(df, filename):
    output_path = os.path.join("Group4_data_analysis", "data", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"📁 Monthly top speeds saved to: {output_path}")

if __name__ == "__main__":
    df_monthly = fetch_monthly_top_speeds()
    save_to_csv(df_monthly, "noaa_top_speed_monthly.csv")
