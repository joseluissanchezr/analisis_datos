# scripts/clean_wind_data.py

import pandas as pd
import os

# Cargar los datos
file_path = "Group4_data_analysis/data/noaa_wind_miami_2015_2023.csv"
df = pd.read_csv(file_path)

# Imprimir información inicial
print("📊 Dimensiones originales:", df.shape)
print("🧼 Limpiando datos nulos...")

# Eliminar filas con valores nulos
df_clean = df.dropna()
print("✅ Después de eliminar nulos:", df_clean.shape)

# Filtrar outliers usando el método IQR
print("📦 Filtrando outliers con método IQR...")

Q1 = df_clean['value'].quantile(0.25)
Q3 = df_clean['value'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_clean = df_clean[(df_clean['value'] >= lower_bound) & (df_clean['value'] <= upper_bound)]

print("✅ Después de eliminar outliers:", df_clean.shape)

# Convertir fechas si existen
if 'date' in df_clean.columns:
    df_clean['date'] = pd.to_datetime(df_clean['date'])

# Guardar el resultado limpio
output_path = "Group4_data_analysis/data/noaa_wind_miami_cleaned.csv"
os.makedirs("data", exist_ok=True)
df_clean.to_csv(output_path, index=False)

print(f"📁 Datos limpios guardados en: {output_path}")
