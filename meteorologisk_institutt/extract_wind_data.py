import requests
import pandas as pd
from datetime import datetime
import os
from wind_plot import plot_mean_wind_timeseries, plot_wind_timeseries, plot_wind_bar_chart, plot_mean_wind_bar_chart


# --------------config
CLIENT_ID = '366b5b06-e25d-44db-907d-bd21c64dccd5'
BASE_URL = 'https://frost.met.no'
OBS_ENDPOINT = f'{BASE_URL}/observations/v0.jsonld'
SOURCES_ENDPOINT = f'{BASE_URL}/sources/v0.jsonld'
AVAIL_ENDPOINT = f'{BASE_URL}/observations/availableTimeSeries/v0.jsonld'


# -------------utils

def select_option(options, message):
    print(f"\n{message}")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    while True:
        try:
            idx = int(input("Enter a number: "))
            if 1 <= idx <= len(options):
                return options[idx - 1]
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a valid integer.")

def ask_dates():
    while True:
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            if start_dt > end_dt:
                raise ValueError
            return f"{start}/{end}"
        except ValueError:
            print("Invalid dates. Please use correct format and order.")

# ----------api calls

def fetch_sources():
    print("Fetching station data...")
    r = requests.get(SOURCES_ENDPOINT, auth=(CLIENT_ID, ''))
    r.raise_for_status()
    data = r.json()['data']
    norwegian = [
        s for s in data if s.get("countryCode") == "NO" and s.get("id", "").startswith("SN")
    ]
    print(f"Total Norwegian stations: {len(norwegian)}")
    return norwegian

def fetch_available_wind_sources():
    print("Filtering stations that measure wind...")
    try:
        r = requests.get(
            f"{BASE_URL}/observations/availableTimeSeries/v0.jsonld",
            params={'elements': 'wind_speed'},
            auth=(CLIENT_ID, '')
        )
        r.raise_for_status()
        response = r.json()
        data = response.get('data', [])
        if not data:
            print("Warning: No data returned from availableTimeSeries.")
        ids = set(entry['sourceId'] for entry in data if 'sourceId' in entry)
        print(f"Stations with wind data: {len(ids)}")
        return ids
    except Exception as e:
        print(f"Error fetching available time series: {e}")
        return set()

def build_filtered_station_list(all_sources, wind_sources):
    print("Filtering stations with matching ID format...")

    cleaned_wind_ids = set(wid.split(":")[0] for wid in wind_sources)

    filtered = []
    for s in all_sources:
        sid = s.get("id")
        if sid in cleaned_wind_ids and s.get("name"):
            county = s.get("county") or "Unknown"
            filtered.append({
                "name": s["name"],
                "id": sid,
                "county": county
            })

    print(f"Stations after filtering: {len(filtered)}")
    return filtered

def fetch_wind_data(source_id, referencetime):
    r = requests.get(
        OBS_ENDPOINT,
        params={
            'sources': source_id,
            'elements': 'max(wind_speed P1D),mean(wind_speed P1D)',
            'referencetime': referencetime
        },
        auth=(CLIENT_ID, '')
    )
    if r.status_code != 200:
        error = r.json().get("error", {})
        raise Exception(f"API error {r.status_code}: {error.get('message', '')} - {error.get('reason', '')}")
    
    data = r.json()['data']
    rows = []
    for item in data:
        for obs in item['observations']:
            rows.append({
                'sourceId': item['sourceId'],
                'referenceTime': item['referenceTime'],
                'elementId': obs['elementId'],
                'value': obs['value'],
                'unit': obs['unit']
            })
    return pd.DataFrame(rows)

# -----------main

def main():
    print("=== WIND DATA FROM FROST API ===")

    try:
        all_sources = fetch_sources()
        wind_sources = fetch_available_wind_sources()
        filtered = build_filtered_station_list(all_sources, wind_sources)

        if not filtered:
            print("No stations with wind data found.")
            return

        counties = sorted(set(sta['county'] for sta in filtered))
        selected_county = select_option(counties, "Select a county / region:")
        candidates = [sta for sta in filtered if sta['county'] == selected_county]

        if not candidates:
            print(f"No stations found in {selected_county}.")
            return

        station_names = [sta['name'] for sta in candidates]
        selected_name = select_option(station_names, "Select a weather station:")
        selected_station = next(s for s in candidates if s['name'] == selected_name)

        referencetime = ask_dates()
        print(f"\nFetching wind data for {selected_name} ({selected_station['id']})...")

        df = fetch_wind_data(selected_station['id'], referencetime)
        df['referenceTime'] = pd.to_datetime(df['referenceTime'])

        #pivot so each element becomes a column for max and mean
        df_wide = df.pivot_table(index='referenceTime', columns='elementId', values='value').reset_index()
        df_wide.columns.name = None  # clean up

        plot_wind_timeseries(df, selected_name)
        plot_wind_bar_chart(df, selected_name)
        plot_mean_wind_timeseries(df_wide, selected_name)
        plot_mean_wind_bar_chart(df_wide, selected_name)


        output_dir = os.path.expanduser("~/Documents/Frost_output")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{selected_station['id']}_wind.csv"
        path = os.path.join(output_dir, filename)
        df.to_csv(path, index=False)

        print(f"\nSaved data to: {path}")
        print(df.head())

    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()

