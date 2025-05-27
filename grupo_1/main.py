import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Read data into dataframe
df = pd.read_excel('generacion_aragón_20240301_20250101.xlsx')

# 2. Display first 5 rows of the Dataframe
print(df.head())

# 3. Display information about the data
df.info()

# 4. Display descriptive statistics
df.describe()

# 5. Check for missing values and drop columns with them if they exist
if df.isna().sum().sum() == 0:
    print("No null values found")
else:
    sum = df.isna().sum().sum()
    print(f"Null values found: {sum}. Data must be cleaned")
    print(df.isna().sum())
    df = df.dropna()
    sum_new = df.isna().sum().sum()
    print(f"Data was cleaned. Null values now: {sum_new}")

#TODO: understand why
# Delete duplicates in datetime and technology
#df_clean = df.drop_duplicates(subset=["datetime", "technology"], keep="first")
#print(df_clean.head())
#print(df_clean.tail())"""

#df = df[df['technology'] != 'Generación total']

# 6. Check data for outliers
# create boxplot
"""plt.figure(figsize=(12,6))
sns.boxplot(x='technology', y='value', data=df)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()"""

# Use IQR to identify outliers
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1

outliers = df[(df['value'] < Q1 - 1.5 * IQR) | (df['value'] > Q3 + 1.5 * IQR)]
#print(outliers.head())
if outliers.empty == False:
    df_clean = df[~((df['value'] < Q1 - 1.5 * IQR) | (df['value'] > Q3 + 1.5 * IQR))]
    print("Outliers of column value were detected and removed. Head of cleaned dataframe:")
    print(df_clean.head())
else:
    print("No outliers detected")


# 7. Check for duplicates
if df.duplicated().sum() == 0:
    print("No duplicates found")
else:
    sum = df.duplicated().sum()
    print(f"Duplicates found in Dataframe: {sum}. Data has to be cleaned")
    df = df.drop_duplicates()
    print("Data was cleaned")


# Save cleaned data to excel
df.to_excel("cleaned_data.xlsx", index=False)

#TODO: Discuss with teammates
""" Split datetime into date and time:
Complicated because of timezones 
df_new = df.copy()
print(df_new['datetime'].head())
print(df_new['datetime'].dtype)
print(df_new['datetime'].isna().sum())
df_new['datetime'] = pd.to_datetime(df_new['datetime'], errors='coerce')
#df_new['date'] = df_new['datetime'].dt.date
#df_new['time'] = df_new['datetime'].dt.time
#df_new = df_new.drop(columns=['datetime'])
#print(df_new.head())
"""


