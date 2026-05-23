import pandas as pd
import matplotlib.pyplot as plt

# loading the cleaned data for France, Germany, and Spain
df_fr = pd.read_csv("data\\processed\\france_cleaned.csv")
df_de = pd.read_csv("data\\processed\\germany_cleaned.csv")
df_es = pd.read_csv("data\\processed\\spain_cleaned.csv")

# Convert the datetime column to date format
for df in [df_fr, df_de, df_es]:
    df["datetime"] = pd.to_datetime(df["datetime"])

    def analyze_variability(df, country_name):
    # Standard deviation and Coefficient of Variation (CV)
        std_dev = df["demand_mwh"].std()
        mean_demand = df["demand_mwh"].mean()
        cv = (std_dev / mean_demand) * 100

    # Daily range (difference between max and min per day)
        daily_var = df.groupby(df["datetime"].dt.date)["demand_mwh"].agg(
            amplitude=lambda x: x.max() - x.min()
        )
        avg_daily_amplitude = daily_var["amplitude"].mean()

        print(f"\n===== Variabilidad en {country_name} =====")
        print(f"Desviación Estándar: {std_dev:.0f} MWh")
        print(f"Coeficiente de Variación: {cv:.2f}%")
        print(f"Amplitud Media Diaria (Max-Min): {avg_daily_amplitude:.0f} MWh")
        
        return cv, avg_daily_amplitude
    
    # Analyze variability for each country
analyze_variability(df_fr, "Francia")
analyze_variability(df_de, "Alemania")
analyze_variability(df_es, "España")

def plot_rolling_variability(df, country):
    df = df.sort_values("datetime").reset_index(drop=True)
    # Calculate the 24-hour rolling standard deviation to see how it fluctuates
    df['rolling_std'] = df['demand_mwh'].rolling(window=24).std()

    plt.figure(figsize=(14, 5))
    plt.plot(df["datetime"], df['rolling_std'], label="Desviación Estándar (24h)", color="orange")
    
    plt.title(f"Variabilidad de la Demanda (Rolling 24h) - {country}")
    plt.xlabel("Fecha")
    plt.ylabel("Desviación Estándar (MWh)")
    plt.legend()
    plt.tight_layout()


