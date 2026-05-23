# prueba 
import pandas as pd

# loading the cleaned data for France, Germany, and Spain
df_fr = pd.read_csv("data\\processed\\france_cleaned.csv")
df_de = pd.read_csv("data\\processed\\germany_cleaned.csv")

# creating a new column for the date and time