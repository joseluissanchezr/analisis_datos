import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path

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

output_dir = Path("residual_load_data_processed")
output_dir.mkdir(exist_ok=True)


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

        current_start = current_end

    return pd.DataFrame(all_data)


residual_data = {}
statistics_results = []

for country, zone in countries.items():

    print(f"\nProcessing {country}...")

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

    residual_data[country] = merged

    statistics_results.append({
        "Country": country,
        "Average Residual Load": round(merged["residual_load"].mean(), 2),
        "Maximum Residual Load": round(merged["residual_load"].max(), 2),
        "Minimum Residual Load": round(merged["residual_load"].min(), 2),
        "Standard Deviation": round(merged["residual_load"].std(), 2)
    })

    plt.figure(figsize=(12, 5))
    plt.plot(merged["datetime"], merged["residual_load"])
    plt.title(f"Residual Load in {country}")
    plt.xlabel("Datetime")
    plt.ylabel("Residual Load")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_file = output_dir / f"{country}_residual_load.png"
    plt.savefig(plot_file)
    plt.close()

    print(f"{country} plot saved: {plot_file}")


stats_df = pd.DataFrame(statistics_results)

print("\nResidual Load Statistics:")
print(stats_df)

stats_file = output_dir / "residual_load_statistics.csv"
stats_df.to_csv(stats_file, index=False)

print(f"\nStatistics saved: {stats_file}")
print("\nAll plots and statistics generated successfully.")

plt.figure(figsize=(15, 7))

for country, zone in countries.items():

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
        merged["solar"] +
        merged["wind"] +
        merged["hydro"]
    )

    merged["residual_load"] = (
        merged["total_load"] -
        merged["renewable_generation"]
    )

    # 7-day rolling average
    merged["rolling_avg"] = (
        merged["residual_load"]
        .rolling(window=168)
        .mean()
    )

    # Transparent hourly data
    plt.plot(
        merged["datetime"],
        merged["residual_load"],
        alpha=0.15
    )

    # Bright rolling average
    plt.plot(
        merged["datetime"],
        merged["rolling_avg"],
        linewidth=2.5,
        label=f"{country} 7d avg"
    )

plt.title("Residual Load Comparison in Europe")
plt.xlabel("Datetime")
plt.ylabel("Residual Load")
plt.legend()
plt.xticks(rotation=45)

plt.tight_layout()

comparison_plot = output_dir / "residual_load_comparison.png"

plt.savefig(comparison_plot)

plt.close()

print(f"\nComparison plot saved: {comparison_plot}")