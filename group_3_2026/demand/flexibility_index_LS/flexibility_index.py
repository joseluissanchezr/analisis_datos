import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# SEARCH DATA
script_dir = os.path.dirname(os.path.abspath(__file__))

group_root = os.path.abspath(os.path.join(script_dir, '../..'))

france_path = os.path.join(group_root, 'data', 'processed', 'france_cleaned.csv')
germany_path = os.path.join(group_root, 'data', 'processed', 'germany_cleaned.csv')
spain_path = os.path.join(group_root, 'data', 'processed', 'spain_cleaned.csv')

# LOAD DATA
df_fr = pd.read_csv(france_path)
df_de = pd.read_csv(germany_path)
df_es = pd.read_csv(spain_path)

# Datetime conversion
for df_temp in [df_fr, df_de, df_es]:
    df_temp['datetime'] = pd.to_datetime(df_temp['datetime'])

# France
df_fr.set_index('datetime', inplace=True)
df_fr = df_fr.resample('h').mean(numeric_only=True).reset_index()
df_fr['country'] = 'France'

# Germany
df_de.set_index('datetime', inplace=True)
df_de = df_de.resample('h').mean(numeric_only=True).reset_index()
df_de['country'] = 'Germany'

# Spain
df_es.set_index('datetime', inplace=True)
df_es = df_es.resample('h').mean(numeric_only=True).reset_index()
df_es['country'] = 'Spain'

# Concatenate all dataframes
df_all = pd.concat([df_fr, df_de, df_es], ignore_index=True)

df_flex = df_all.pivot(index='datetime', columns='country', values='demand_mwh')

# Clean NaNs
df_flex = df_flex.dropna()

# Temporal features
df_flex['hour'] = df_flex.index.hour
df_flex['day_of_week'] = df_flex.index.dayofweek
df_flex['is_weekend'] = df_flex['day_of_week'].isin([5, 6])


# Visualisation of the average hourly demand profile for each country
# Mean hourly demand profile for each country
perfil_horario = df_flex.groupby('hour')[['France', 'Germany', 'Spain']].mean()

# plot configuration
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")

# Plotting the average hourly demand profile for each country
for pais in ['France', 'Germany', 'Spain']:
    plt.plot(perfil_horario.index, perfil_horario[pais], marker='o', linewidth=2, label=pais)


plt.title('Average Daily Electricity Demand Profile', fontsize=14, fontweight='bold')
plt.xlabel('Hour of the Day', fontsize=12)
plt.ylabel('Average Demand (MWh)', fontsize=12)
plt.xticks(range(0, 24))  # Forzar a que salgan todas las horas de la 0 a la 23
plt.xlim(0, 23)
plt.legend(title='Country', fontsize=11)
plt.tight_layout()

# Show the plot
plt.show()


# FLEXIBILITY STATISTICS
# Global Load Factor (GLF)
# The Global Load Factor is a common metric used to assess the variability of electricity demand
# It is calculated as the ratio of the average demand to the peak demand over a specific period
# A lower load factor indicates a more "peaky" demand curve,
# which implies a higher need for flexibility in the energy system to manage these peaks effectively.
countries = ['France', 'Germany', 'Spain']

print("\n1. GLOBAL LOAD FACTOR (Mean / Maximum):")
for country in countries:
    mean_demand = df_flex[country].mean()
    max_demand = df_flex[country].max()
    load_factor = mean_demand / max_demand
    print(f"   * {country}: {load_factor:.3f}")