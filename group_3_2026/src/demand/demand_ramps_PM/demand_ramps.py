# prueba 
import pandas as pd

# loading the cleaned data for France, Germany, and Spain
df_fr = pd.read_csv("group_3_2026/src/data/processed/france_cleaned.csv")
df_de = pd.read_csv("group_3_2026/src/data/processed/germany_cleaned.csv")
df_es = pd.read_csv("group_3_2026/src/data/processed/spain_cleaned.csv")


# creating a new column for the date and time