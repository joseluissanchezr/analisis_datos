import os
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests


# Electricity Maps API key
API_KEY = os.getenv("ELECTRICITY_MAPS_API_KEY")

if not API_KEY:
    raise ValueError(
        "Missing API key. Please set ELECTRICITY_MAPS_API_KEY as an environment variable."
    )


# Countries required for the assignment:
# Spain = ES, France = FR, Germany = DE
COUNTRIES = ["ES", "FR", "DE"]

COUNTRY_NAMES = {
    "ES": "Spain",
    "FR": "France",
    "DE": "Germany",
}

COLORS = {
    "ES": "#F39C12",
    "FR": "#3498DB",
    "DE": "#2ECC71",
}

SOURCE_TYPE = "solar"
BASE_URL = "https://api.electricitymaps.com/v4/electricity-mix"
OUTPUT_FILE = "Solar_hourly_generation_3_countries_imen.csv"


def split_date_range(start_date, end_date, chunk_days=10):
    """
    Split a long period into chunks of maximum 10 days.
    Electricity Maps limits hourly past-range requests to 10 days.
    """
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + timedelta(days=chunk_days), end_date)
        yield current_start, current_end
        current_start = current_end


def extract_solar_value(record):
    """
    Extract solar generation from one API record.
    Electricity Maps returns solar generation inside record["mix"]["solar"].
    """
    if "mix" in record and isinstance(record["mix"], dict):
        return record["mix"].get("solar")

    if "powerProductionBreakdown" in record:
        breakdown = record["powerProductionBreakdown"]
        if isinstance(breakdown, dict):
            return breakdown.get("solar")

    if "powerConsumptionBreakdown" in record:
        breakdown = record["powerConsumptionBreakdown"]
        if isinstance(breakdown, dict):
            return breakdown.get("solar")

    for key in ["value", "powerProduction", "generation", "solar"]:
        if key in record and record[key] is not None:
            return record[key]

    return None


def extract_datetime(record):
    """
    Extract datetime from one API record.
    """
    for key in ["datetime", "time"]:
        if key in record and record[key] is not None:
            return record[key]

    return None


def fetch_solar_data_for_country(country, start_date, end_date):
    """
    Download hourly solar generation data for one country.
    """
    headers = {"auth-token": API_KEY}
    all_rows = []

    for chunk_start, chunk_end in split_date_range(start_date, end_date):
        url = f"{BASE_URL}/{SOURCE_TYPE}/past-range"

        params = {
            "zone": country,
            "start": chunk_start.isoformat().replace("+00:00", "Z"),
            "end": chunk_end.isoformat().replace("+00:00", "Z"),
            "temporalGranularity": "hourly",
            "flowTraced": "false",
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(
                f"API error for {country}: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()
        records = data.get("history", data.get("data", []))

        if not records:
            print(f"No records returned for {country} in this period.")
            continue

        for record in records:
            datetime_value = extract_datetime(record)
            solar_value = extract_solar_value(record)

            all_rows.append(
                {
                    "datetime": datetime_value,
                    "country": country,
                    "solar_generation_mw": solar_value,
                    "source": "Electricity Maps",
                }
            )

    return pd.DataFrame(all_rows)


def download_solar_generation(start_date, end_date):
    """
    Download solar generation data for Spain, France and Germany.
    """
    country_dataframes = []

    print("Downloading hourly solar generation data from Electricity Maps...")

    for country in COUNTRIES:
        print(f"  - {COUNTRY_NAMES[country]} ({country})")
        country_df = fetch_solar_data_for_country(country, start_date, end_date)
        country_dataframes.append(country_df)

    solar_df = pd.concat(country_dataframes, ignore_index=True)
    solar_df = solar_df.drop_duplicates().reset_index(drop=True)

    solar_df["datetime"] = pd.to_datetime(solar_df["datetime"], errors="coerce")
    solar_df["solar_generation_mw"] = pd.to_numeric(
        solar_df["solar_generation_mw"], errors="coerce"
    )

    solar_df = solar_df.dropna(subset=["datetime"])
    solar_df = solar_df.sort_values(["country", "datetime"]).reset_index(drop=True)

    return solar_df


def calculate_solar_statistics(solar_df):
    """
    Calculate basic solar generation statistics by country.
    """
    statistics = (
        solar_df.groupby("country")["solar_generation_mw"]
        .agg(["mean", "max", "min", "std"])
        .rename(
            columns={
                "mean": "Average solar generation (MW)",
                "max": "Maximum solar generation (MW)",
                "min": "Minimum solar generation (MW)",
                "std": "Solar generation standard deviation (MW)",
            }
        )
        .round(2)
    )

    return statistics


def calculate_daily_solar_generation(solar_df):
    """
    Calculate daily average solar generation by country.
    """
    daily_df = solar_df.copy()
    daily_df["date"] = daily_df["datetime"].dt.date

    daily_solar = (
        daily_df.groupby(["date", "country"])["solar_generation_mw"]
        .mean()
        .reset_index()
    )

    return daily_solar


def calculate_total_solar_generation(solar_df):
    """
    Calculate total solar generation by country for the analysed period.
    """
    total_solar = (
        solar_df.groupby("country")["solar_generation_mw"]
        .sum()
        .reset_index()
        .rename(columns={"solar_generation_mw": "Total solar generation (MW)"})
    )

    total_solar["Total solar generation (MW)"] = total_solar[
        "Total solar generation (MW)"
    ].round(2)

    return total_solar


def identify_highest_average_solar_country(statistics):
    """
    Identify the country with the highest average solar generation
    during the analysed period.
    """
    highest_country = statistics["Average solar generation (MW)"].idxmax()
    highest_value = statistics.loc[
        highest_country, "Average solar generation (MW)"
    ]

    return highest_country, highest_value


def format_plot(title, xlabel, ylabel):
    """
    Apply common formatting to all solar plots.
    """
    plt.title(title, fontsize=16, fontweight="bold", pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend(frameon=True)
    plt.tight_layout()


def plot_daily_solar_generation(daily_solar):
    """
    Plot daily average solar generation for ES, FR and DE.
    """
    plt.figure(figsize=(13, 6))

    for country in COUNTRIES:
        country_data = daily_solar[daily_solar["country"] == country]

        plt.plot(
            country_data["date"],
            country_data["solar_generation_mw"],
            label=f"{COUNTRY_NAMES[country]} ({country})",
            color=COLORS[country],
            linewidth=2.5,
            marker="o",
            markersize=3.5,
            alpha=0.9,
        )

    format_plot(
        "Daily Average Solar Generation - Spain, France and Germany",
        "Date",
        "Average solar generation (MW)",
    )

    plt.show()


def plot_hourly_solar_generation(solar_df):
    """
    Plot hourly solar generation for each country.
    """
    for country in COUNTRIES:
        country_data = solar_df[solar_df["country"] == country]

        plt.figure(figsize=(13, 5.5))
        plt.plot(
            country_data["datetime"],
            country_data["solar_generation_mw"],
            label=f"{COUNTRY_NAMES[country]} ({country})",
            color=COLORS[country],
            linewidth=1.6,
            alpha=0.9,
        )

        plt.fill_between(
            country_data["datetime"],
            country_data["solar_generation_mw"],
            color=COLORS[country],
            alpha=0.18,
        )

        format_plot(
            f"Hourly Solar Generation - {COUNTRY_NAMES[country]} ({country})",
            "Datetime",
            "Solar generation (MW)",
        )

        plt.show()


def plot_total_solar_generation(total_solar):
    """
    Plot total solar generation by country.
    """
    plot_data = total_solar.copy()
    plot_data["country_name"] = plot_data["country"].map(COUNTRY_NAMES)

    colors = [COLORS[country] for country in plot_data["country"]]

    plt.figure(figsize=(9, 5.5))
    bars = plt.bar(
        plot_data["country_name"],
        plot_data["Total solar generation (MW)"],
        color=colors,
        alpha=0.85,
        edgecolor="black",
        linewidth=0.8,
    )

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,.0f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.title(
        "Total Solar Generation by Country",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Country", fontsize=12)
    plt.ylabel("Total solar generation (MW)", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.show()


def plot_average_daily_profile(solar_df):
    """
    Plot the average hourly daily solar profile by country.
    This shows the typical daily solar cycle.
    """
    profile_df = solar_df.copy()
    profile_df["hour"] = profile_df["datetime"].dt.hour

    hourly_profile = (
        profile_df.groupby(["hour", "country"])["solar_generation_mw"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(11, 5.5))

    for country in COUNTRIES:
        country_data = hourly_profile[hourly_profile["country"] == country]

        plt.plot(
            country_data["hour"],
            country_data["solar_generation_mw"],
            label=f"{COUNTRY_NAMES[country]} ({country})",
            color=COLORS[country],
            linewidth=3,
            marker="o",
            markersize=4,
        )

    plt.title(
        "Average Daily Solar Generation Profile",
        fontsize=16,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Hour of the day", fontsize=12)
    plt.ylabel("Average solar generation (MW)", fontsize=12)
    plt.xticks(range(0, 24, 2))
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend(frameon=True)
    plt.tight_layout()
    plt.show()


def save_processed_data(solar_df):
    """
    Save processed solar data locally.
    The CSV should not be uploaded to GitHub.
    """
    solar_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Processed solar data saved locally as {OUTPUT_FILE}")


def main():
    """
    Main execution for Imen's solar generation analysis.

    The assignment asks for hourly data over a maximum of 3 months.
    Here we analyse January, February and March 2026.
    """
    start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 4, 1, tzinfo=timezone.utc)

    solar_df = download_solar_generation(start_date, end_date)

    statistics = calculate_solar_statistics(solar_df)
    total_solar = calculate_total_solar_generation(solar_df)
    daily_solar = calculate_daily_solar_generation(solar_df)

    highest_country, highest_value = identify_highest_average_solar_country(statistics)

    print("\nSolar generation analysis completed successfully.")
    print(f"Analysed period: {start_date.date()} to {end_date.date()}")
    print(f"Countries analysed: {', '.join(COUNTRIES)}")
    print(f"Number of hourly records: {len(solar_df)}")

    print("\nSolar generation statistics by country:")
    print(statistics)

    print(
        f"\nCountry with the highest average solar generation: "
        f"{COUNTRY_NAMES[highest_country]} ({highest_country}) "
        f"with {highest_value:.2f} MW"
    )

    print("\nTotal solar generation by country:")
    print(total_solar)

    save_processed_data(solar_df)

    plot_daily_solar_generation(daily_solar)
    plot_total_solar_generation(total_solar)
    plot_average_daily_profile(solar_df)
    plot_hourly_solar_generation(solar_df)


if __name__ == "__main__":
    main()