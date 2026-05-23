import pandas as pd

# loading the cleaned data for France, Germany, and Spain
df_fr = pd.read_csv("data\\processed\\france_cleaned.csv")
df_de = pd.read_csv("data\\processed\\germany_cleaned.csv")
df_es = pd.read_csv("data\\processed\\spain_cleaned.csv")


# converting the datetime column to datetime format
for df in [df_fr, df_de, df_es]:
    df["datetime"] = pd.to_datetime(df["datetime"])


# function to analyze peaks in the demand data for a given country
def analyze_peaks(df, country_name):
    
    # global peak value and time
    peak_value = df["demand_mwh"].max()
    peak_time = df.loc[df["demand_mwh"].idxmax(), "datetime"]
    
    # Top 5 peaks
    top_peaks = df.nlargest(5, "demand_mwh")[["datetime", "demand_mwh"]]
    
    # day with the highest demand
    daily_max = df.groupby(df["datetime"].dt.date)["demand_mwh"].max()
    max_day = daily_max.idxmax()
    max_day_value = daily_max.max()


    print(f"\n===== {country_name} =====")
    print(f"Peak max : {peak_value:.0f} MWh")
    print(f"Date du peak : {peak_time}")
    print(f"Peak journalier max : {max_day_value:.0f} MWh (le {max_day})")
    
    print("\nTop 5 peaks :")
    print(top_peaks)
    
    return peak_value, peak_time

#Analyzing peaks for each country
analyze_peaks(df_fr, "France")
analyze_peaks(df_de, "Germany")
analyze_peaks(df_es, "Spain")

#adding the local maxima function to find all local peaks in the demand data

def find_local_maxima(df, value_col="demand_mwh"):
    """
    detects local maxima in the demand data. A local maximum is defined as a point that is greater than its immediate neighbors.
    """

    df = df.sort_values("datetime").reset_index(drop=True)

    local_maxima = df[
        (df[value_col] > df[value_col].shift(1)) &
        (df[value_col] > df[value_col].shift(-1))
    ]

    return local_maxima


import matplotlib.pyplot as plt

def plot_with_local_maxima(df, country):
    df = df.sort_values("datetime").reset_index(drop=True)

    # Maximum global
    global_peak_idx = df["demand_mwh"].idxmax()

    # Maxima locaux
    local_maxima = find_local_maxima(df)

    plt.figure(figsize=(14, 5))

    # Courbe de demande
    plt.plot(
        df["datetime"],
        df["demand_mwh"],
        label="Demand",
        color="blue"
    )

    # Maxima locaux en vert
    plt.scatter(
        local_maxima["datetime"],
        local_maxima["demand_mwh"],
        color="green",
        s=25,
        label="Local maxima",
        zorder=4
    )

    # Maximum global en rouge
    plt.scatter(
        df.loc[global_peak_idx, "datetime"],
        df.loc[global_peak_idx, "demand_mwh"],
        color="red",
        s=80,
        label="Global maximum",
        zorder=5
    )

    plt.title(f"Demand peaks - {country}")
    plt.xlabel("Date")
    plt.ylabel("Demand (MWh)")
    plt.legend()
    plt.tight_layout()


plot_with_local_maxima(df_fr, "France")
plot_with_local_maxima(df_de, "Germany")
plot_with_local_maxima(df_es, "Spain")
plt.show()