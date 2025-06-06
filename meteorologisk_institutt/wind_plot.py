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

def plot_mean_wind_timeseries(df_wide, station_name):
    if 'mean(wind_speed P1D)' not in df_wide.columns:
        print("Mean wind speed data not available. Skipping plot.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df_wide['referenceTime'], df_wide['mean(wind_speed P1D)'], marker='x', label='Mean Wind Speed')
    plt.title(f"Daily Mean Wind Speed at {station_name}")
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_mean_wind_bar_chart(df_wide, station_name):
    """
    Plots a bar chart of mean wind speed, only if the time range is <= 31 days.
    """
    df = df_wide.copy()
    df = df.dropna(subset=['mean(wind_speed P1D)'])
    df = df.sort_values("referenceTime")

    if df.empty:
        print("No valid mean wind data to plot.")
        return

    time_span = (df['referenceTime'].max() - df['referenceTime'].min()).days
    if time_span > 31:
        print(f"Mean wind bar chart skipped: selected time range is {time_span} days (max allowed is 31).")
        return

    plt.figure(figsize=(12, 6))
    plt.bar(df['referenceTime'].dt.strftime('%Y-%m-%d'), df['mean(wind_speed P1D)'])
    plt.title(f"Daily Mean Wind Speed at {station_name}")
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
