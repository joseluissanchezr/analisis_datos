# Renewables_price_correlation_3_countries
# Here we will analyze the correlation between renewable energy generation and electricity prices in Spain, France, and Germany. 
# We will use the data obtained by our group and perform statistical analysis to find patterns and insights.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from Mix_hourly_generation_3_countries import download_mix_generation, add_mix_indicators
from Price_data_raw import get_precio_data

def run_pipeline():
    
    print("--- Obtaining MIX data ---")
    mix_df = download_mix_generation()
    mix_df = add_mix_indicators(mix_df)
    
    print("--- Obtaining PRICE data ---")
    precio_df = get_precio_data()
    

    print("--- Merging datasets ---")
    df_final = pd.merge(mix_df, precio_df, on=['datetime', 'country'], how='inner')
    
    return df_final

def visualizar_datos(df):
    
    df['date'] = df['datetime'].dt.date
    df_diario = df.groupby(['date', 'country'])[['price_mwh', 'renewable_share_percent']].mean().reset_index()
        
    sns.set_theme(style="whitegrid")
    
    plt.figure(figsize=(14, 6))
    sns.barplot(data=df_diario, x='date', y='price_mwh', hue='country')
    
    plt.title("Precio Promedio Diario por País (€/MWh)", fontsize=15)
    plt.ylabel("Precio (€/MWh)")
    plt.xlabel("Fecha")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def visualizar_correlacion_renovables(df):
    plt.figure(figsize=(10, 6))
    
    sns.scatterplot(
        data=df, 
        x='renewable_share_percent', 
        y='price_mwh', 
        hue='country', 
        alpha=0.6
    )
    
    sns.regplot(data=df, x='renewable_share_percent', y='price_mwh', 
                scatter=False, color='black', label='Tendencia Global')
    
    plt.title("Correlation between % Renewables and Electricity Price")
    plt.xlabel("% of Renewables in the Mix")
    plt.ylabel("Price (€/MWh)")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    df_maestro = run_pipeline()
    
    print("\n--- Analysis Completed ---")
    print(f"Total of merged records: {len(df_maestro)}")
    
    print("\n--- Correlation between Renovables and Price by Country ---")

    correlacion = df_maestro.groupby('country')[['renewable_share_percent', 'price_mwh']].corr().iloc[0::2, -1]
    print(correlacion)
    
    print("\nFirst rows of the master dataset:")
    print(df_maestro.head())
    
    visualizar_datos(df_maestro)
    visualizar_correlacion_renovables(df_maestro)
    