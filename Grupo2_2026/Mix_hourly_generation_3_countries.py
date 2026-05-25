# =================================================================
# PROYECTO: Análisis de Datos de Generación Eléctrica 2026
# GRUPO 2: Generación Renovable (ES, FR, DE)
# AUTOR: MarcosBello.
# DESCRIPCIÓN: Extracción horaria de mix energético vía API.
# =================================================================
import os
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests


# Put here the Electricity Maps API key used by the group
API_KEY = os.getenv("ELECTRICITY_MAPS_API_KEY")

if not API_KEY:
    raise ValueError(
        "Missing API key. Please set ELECTRICITY_MAPS_API_KEY as an environment variable."
    )

# Countries required for Group 2
COUNTRIES = ["ES", "FR", "DE"]

# Period agreed by the group: January, February and March 2026
START_DATE = datetime(2026, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 4, 1, tzinfo=timezone.utc)

# Electricity Maps hourly requests have to be split into smaller periods
CHUNK_DAYS = 10

# We use the solar source endpoint because it returns a full "mix" field
# in the API response, which includes solar, wind, hydro, gas, coal, etc.
BASE_URL = "https://api.electricitymaps.com/v4/electricity-mix/solar/past-range"
OUTPUT_FILE = "Mix_hourly_generation_3_countries.csv"

TECHNOLOGIES = [
    "solar",
    "wind",
    "hydro",
    "gas",
    "coal",
    "nuclear",
    "biomass",
    "oil",
    "geothermal",
    "unknown",
]

RENEWABLE_TECHNOLOGIES = [
    "solar",
    "wind",
    "hydro",
    "biomass",
    "geothermal",
]


def split_date_range(start_date, end_date, chunk_days=10):
    """
    Split the full period into chunks of maximum 10 days.
    This avoids API limits for hourly data.
    """
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=chunk_days), end_date)
        yield current_start, current_end
        current_start = current_end


def extract_datetime(record):
    """
    Extract datetime from one API record.
    """
    return record.get("datetime") or record.get("time")


def extract_mix(record):
    """
    Extract the electricity mix from one API record.
    In Electricity Maps, the mix is usually stored in record["mix"].
    """
    if "mix" in record and isinstance(record["mix"], dict):
        return record["mix"]

    if "powerProductionBreakdown" in record and isinstance(
        record["powerProductionBreakdown"], dict
    ):
        return record["powerProductionBreakdown"]

    if "powerConsumptionBreakdown" in record and isinstance(
        record["powerConsumptionBreakdown"], dict
    ):
        return record["powerConsumptionBreakdown"]

    if "electricityMix" in record and isinstance(record["electricityMix"], dict):
        return record["electricityMix"]

    return {}


def fetch_mix_data_for_country(country, start_date, end_date):
    """
    Download hourly electricity mix data for one country.
    """
    headers = {"auth-token": API_KEY}
    all_rows = []

    for chunk_start, chunk_end in split_date_range(start_date, end_date, CHUNK_DAYS):
        params = {
            "zone": country,
            "start": chunk_start.isoformat().replace("+00:00", "Z"),
            "end": chunk_end.isoformat().replace("+00:00", "Z"),
            "temporalGranularity": "hourly",
            "flowTraced": "false",
        }

        print(
            f"Downloading mix data for {country}: "
            f"{params['start']} to {params['end']}"
        )

        response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"API error for {country}: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()
        records = data.get("history", data.get("data", []))

        if not records:
            print(f"Warning: no records returned for {country}.")
            continue

        for record in records:
            mix = extract_mix(record)

            row = {
                "datetime": extract_datetime(record),
                "country": country,
                "source": "Electricity Maps",
            }

            for technology in TECHNOLOGIES:
                row[technology] = mix.get(technology)

            all_rows.append(row)

    return pd.DataFrame(all_rows)


def download_mix_generation():
    """
    Download hourly electricity mix data for ES, FR and DE.
    Final dataframe: mix_df
    """
    country_dataframes = []

    for country in COUNTRIES:
        country_df = fetch_mix_data_for_country(country, START_DATE, END_DATE)
        country_dataframes.append(country_df)

    mix_df = pd.concat(country_dataframes, ignore_index=True)
    # Eliminamos posibles registros duplicados para asegurar la precisión del análisis
    mix_df = mix_df.drop_duplicates().reset_index(drop=True)

    mix_df["datetime"] = pd.to_datetime(mix_df["datetime"], errors="coerce")
    mix_df = mix_df.dropna(subset=["datetime"])

    for technology in TECHNOLOGIES:
        mix_df[technology] = pd.to_numeric(mix_df[technology], errors="coerce")

    return mix_df


def add_mix_indicators(mix_df):
    """
    Add total generation, renewable generation and renewable share.
    """
    mix_df = mix_df.copy()

    mix_df["total_generation_mw"] = mix_df[TECHNOLOGIES].sum(axis=1, skipna=True)

    mix_df["renewable_generation_mw"] = mix_df[
        RENEWABLE_TECHNOLOGIES
    ].sum(axis=1, skipna=True)

    mix_df["renewable_share_percent"] = (
        mix_df["renewable_generation_mw"] / mix_df["total_generation_mw"]
    ) * 100

    return mix_df


def calculate_mix_statistics(mix_df):
    """
    Calculate summary statistics by country.
    """
    statistics = (
        mix_df.groupby("country")
        .agg(
            average_total_generation_mw=("total_generation_mw", "mean"),
            average_renewable_generation_mw=("renewable_generation_mw", "mean"),
            average_renewable_share_percent=("renewable_share_percent", "mean"),
            max_renewable_share_percent=("renewable_share_percent", "max"),
            min_renewable_share_percent=("renewable_share_percent", "min"),
        )
        .reset_index()
    )

    return statistics


def calculate_daily_mix(mix_df):
    """
    Calculate daily average electricity mix by country.
    """
    daily_df = mix_df.copy()
    daily_df["date"] = daily_df["datetime"].dt.date

    columns_to_average = TECHNOLOGIES + [
        "total_generation_mw",
        "renewable_generation_mw",
        "renewable_share_percent",
    ]

    daily_mix = (
        daily_df.groupby(["date", "country"])[columns_to_average]
        .mean()
        .reset_index()
    )

    return daily_mix


def plot_renewable_share(daily_mix):
    """
    Plot daily renewable share for ES, FR and DE.
    """
    plt.figure(figsize=(12, 6))

    for country in daily_mix["country"].unique():
        country_data = daily_mix[daily_mix["country"] == country]

        plt.plot(
            country_data["date"],
            country_data["renewable_share_percent"],
            label=country,
        )

    plt.title("Daily Renewable Share - ES, FR and DE")
    plt.xlabel("Date")
    plt.ylabel("Renewable share (%)")
    plt.xticks(rotation=45)
    # Añadimos una rejilla para facilitar la lectura de los porcentajes
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_energy_mix_by_country(daily_mix):
    """
    Plot daily average electricity mix for each country.
    """
    for country in daily_mix["country"].unique():
        country_data = daily_mix[daily_mix["country"] == country]

        country_data.plot(
            x="date",
            y=TECHNOLOGIES,
            kind="area",
            figsize=(12, 6),
            stacked=True,
        )

        plt.title(f"Daily Average Electricity Mix - {country}")
        plt.xlabel("Date")
        plt.ylabel("Generation (MW)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def save_processed_data(mix_df):
    """
    Save processed mix data locally.
    This CSV should not be uploaded to GitHub.
    """
    mix_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Processed mix data saved as {OUTPUT_FILE}")


def main():
    """
    Main execution for the electricity mix analysis.

    Period:
    2026-01-01 to 2026-04-01

    Countries:
    ES, FR, DE

    Granularity:
    hourly
    """
    mix_df = download_mix_generation()
    mix_df = add_mix_indicators(mix_df)

    print("\nFirst rows of mix data:")
    print(mix_df.head())

    statistics = calculate_mix_statistics(mix_df)
    print("\nElectricity mix statistics by country:")
    print(statistics)

    daily_mix = calculate_daily_mix(mix_df)
    print("\nDaily electricity mix:")
    print(daily_mix.head())

    save_processed_data(mix_df)

    plot_renewable_share(daily_mix)
    plot_energy_mix_by_country(daily_mix)


if __name__ == "__main__":
    main()
