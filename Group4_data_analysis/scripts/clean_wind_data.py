# clean_wind_data.py

import pandas as pd
import os
import sys

# === Configuración de rutas ===
input_path = "Group4_data_analysis/data/noaa_wind_miami_2015_2023.csv"
output_path = "Group4_data_analysis/data/noaa_wind_miami_cleaned.csv"

# === Cargar el archivo original ===
try:
    df = pd.read_csv(input_path)
    print(f"📥 Archivo cargado correctamente desde: {input_path}")
except Exception as e:
    print(f"❌ Error al leer el archivo: {e}")
    sys.exit(1)

# === Mostrar tamaño inicial del conjunto de datos ===
print("🔢 Tamaño inicial del dataset:", df.shape)

# === Eliminar espacios en nombres de columnas y convertir a minúsculas ===
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# === Verificar existencia de columnas necesarias ===
if 'value' not in df.columns or 'date' not in df.columns:
    print("⚠️ Las columnas 'value' y/o 'date' no se encuentran en el archivo.")
    sys.exit(1)

# === Eliminación de datos faltantes ===
print("🧹 Eliminando registros con valores nulos...")
df_clean = df.dropna()
print("✔️ Tamaño después de eliminar nulos:", df_clean.shape)

# === Detección y eliminación de outliers con el método IQR ===
print("📊 Aplicando detección de outliers con IQR...")
Q1 = df_clean['value'].quantile(0.25)
Q3 = df_clean['value'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

df_clean = df_clean[(df_clean['value'] >= lower_bound) & (df_clean['value'] <= upper_bound)]
print("✔️ Tamaño tras eliminar outliers:", df_clean.shape)

# === Conversión de fechas si existe la columna correspondiente ===
if 'date' in df_clean.columns:
    try:
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
        df_clean = df_clean.dropna(subset=['date'])
        print("📆 Fechas convertidas correctamente")
    except Exception as e:
        print(f"⚠️ Error al convertir fechas: {e}")
        sys.exit(1)

# === Guardar archivo limpio ===
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_clean.to_csv(output_path, index=False)
print(f"💾 Archivo limpio  guardado en: {output_path}")
