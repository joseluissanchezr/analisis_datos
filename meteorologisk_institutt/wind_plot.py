import matplotlib.pyplot as plt
import pandas as pd

def plot_wind_timeseries(df, station_name):
    """
    Plots a time series of wind speed values.
    """
    if 'referenceTime' not in df.columns:
        print("No referenceTime column found. Skipping time series plot.")
        return

    df = df.copy()
    df['referenceTime'] = pd.to_datetime(df['referenceTime'], errors='coerce')
    df = df.dropna(subset=['referenceTime'])

    plt.figure(figsize=(12, 6))
    plt.plot(df['referenceTime'], df['value'], marker='o', linestyle='-')
    plt.title(f"Daily Max Wind Speed at {station_name}")
    plt.xlabel("Date")
    plt.ylabel(f"Wind Speed ({df['unit'].iloc[0]})")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_wind_bar_chart(df, station_name):
    """
    Plots a bar chart of wind speed, but only if the time range is <= 31 days.
    """
    # Ensure datetime
    df = df.copy()
    df['referenceTime'] = pd.to_datetime(df['referenceTime'], errors='coerce')
    df = df.dropna(subset=['referenceTime'])
    df = df.sort_values("referenceTime")

    if df.empty:
        print("No valid wind data to plot.")
        return

    # Check date range
    time_span = (df['referenceTime'].max() - df['referenceTime'].min()).days
    if time_span > 31:
        print(f"Bar chart skipped: selected time range is {time_span} days (max allowed is 31).")
        return

    # Plot
    plt.figure(figsize=(12, 6))
    plt.bar(df['referenceTime'].dt.strftime('%Y-%m-%d'), df['value'])
    plt.title(f"Daily Max Wind Speed at {station_name}")
    plt.xlabel("Date")
    plt.ylabel(f"Wind Speed ({df['unit'].iloc[0]})")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()