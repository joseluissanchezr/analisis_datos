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



# Average Daily Peak-to-Valley Ratio
# Measures how deep the nightly valley is compared to the daily peak
# It shows the available structural room to shift consumption to off-peak hours
print("\n2. AVERAGE DAILY PEAK-TO-VALLEY RATIO (Minimum / Maximum):")
for country in countries:
    df_daily = df_flex[country].resample('D').agg(['min', 'max'])
    df_daily['peak_to_valley'] = df_daily['min'] / df_daily['max']
    mean_peak_to_valley = df_daily['peak_to_valley'].mean()
    print(f"   * {country}: {mean_peak_to_valley:.3f} (The valley represents {mean_peak_to_valley*100:.1f}% of the daily peak)")


# LOAD FACTOR SEGMENTATION BY WEEKDAYS AND WEEKENDS

# Group the data by weekend flag and hour and calculate the mean demand for each country
profile_days = df_flex.groupby(['is_weekend', 'hour'])[countries].mean()

# Separate into Weekdays and Weekends
weekday_profile = profile_days.loc[False]
weekend_profile = profile_days.loc[True]

# Calculate and print the Load Factor for both scenarios
print("\nLOAD FACTOR SEGMENTATION:")
for country in countries:
    
    df_weekdays = df_flex[df_flex['is_weekend'] == False][country]
    df_weekends = df_flex[df_flex['is_weekend'] == True][country]
    
    lf_weekday = df_weekdays.mean() / df_weekdays.max()
    lf_weekend = df_weekends.mean() / df_weekends.max()
    
    print(f"   * {country}:")
    print(f"     - Weekdays Load Factor: {lf_weekday:.3f}")
    print(f"     - Weekends Load Factor: {lf_weekend:.3f}")

# Plotting the comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
sns.set_theme(style="whitegrid")

colors = {'France': '#1f77b4', 'Germany': '#ff7f0e', 'Spain': '#2ca02c'}

# Weekdays Plot
for country in countries:
    axes[0].plot(weekday_profile.index, weekday_profile[country], 
                 marker='o', linewidth=2, color=colors[country], label=country)
axes[0].set_title('Weekdays Average Demand Profile (Mon-Fri)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Hour of the Day')
axes[0].set_ylabel('Average Demand (MWh)')
axes[0].set_xticks(range(0, 24))
axes[0].set_xlim(0, 23)
axes[0].legend()

# Weekends Plot
for country in countries:
    axes[1].plot(weekend_profile.index, weekend_profile[country], 
                 marker='^', linewidth=2, linestyle='--', color=colors[country], label=country)
axes[1].set_title('Weekends Average Demand Profile (Sat-Sun)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Hour of the Day')
axes[1].set_xticks(range(0, 24))
axes[1].set_xlim(0, 23)
axes[1].legend()

plt.suptitle('Demand Profile Comparison: Weekdays vs Weekends', fontsize=14, fontweight='bold')
plt.tight_layout()


# FLEXIBILITY SCORE
# We can create a composite flexibility score based on the calculated metrics
# We will create a simple composite index (from 0 to 100)
# A country has a higher flexibility potential if:
# 1. It has a lower Load Factor (more "peaky" curve needing optimization)
# 2. It has a lower Peak-to-Valley ratio (deeper daily valleys to shift load)

print("\nFINAL ENERGY DEMAND FLEXIBILITY SCORE (0 to 100):")
for country in countries:
    lf = df_flex[country].mean() / df_flex[country].max()
    df_daily = df_flex[country].resample('D').agg(['min', 'max'])
    p2v = (df_daily['min'] / df_daily['max']).mean()
    
    # 2. Mathematical formulation for the score
    # We invert the metrics (1 - value) because lower ratios = higher flexibility potential/need.
    # We give 50% weight to seasonal peakiness (Load Factor) and 50% to daily shifting room (Peak-to-Valley).
    flexibility_score = ((1 - lf) + (1 - p2v)) / 2 * 100
    
    print(f"   * {country}: {flexibility_score:.1f} points")

print("\n--> ANALYSIS CONCLUSION:")
print("   * GERMANY presents the deepest daily valleys, making it the best suited for short-term Load Shifting.")
print("   * FRANCE shows the lowest global load factor, indicating a critical need for seasonal Peak Shaving due to temperature sensitivity.")
print("   * SPAIN displays the most stable macro-demand baseline, meaning its structural grid stress from demand variation is lower compared to its peers.")


plt.show()