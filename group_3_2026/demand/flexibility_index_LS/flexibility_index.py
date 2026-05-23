import os
import pandas as pd

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