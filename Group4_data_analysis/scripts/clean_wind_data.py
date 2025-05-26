import pandas as pd
import os
import sys

# ==== CONFIGURACIÓN ====
INPUT_PATH = "Group4_data_analysis/data/noaa_wind_miami_2015_2023.csv"
OUTPUT_PATH = "Group4_data_analysis/data/noaa_wind_miami_cleaned.csv"

# ==== FUNCIONES AUXILIARES ====

def log(msg, symbol="🔹"):
    print(f"{symbol} {msg}")

def check_columns(df, required_cols):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        log(f"❌ Columnas faltantes: {missing}", "⚠️")
        sys.exit(1)

def clean_column_names(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

# ==== INICIO ====

log("📥 Cargando archivo CSV...")
try:
    df = pd.read_csv(INPUT_PATH)
except Exception as e:
    log(f"❌ Error al cargar el archivo: {e}", "⚠️")
    sys.exit(1)

log(f"✅ Archivo cargado: {INPUT_PATH}")
log(f"📊 Dimensiones originales: {df.shape}")

# Limpieza de nombres de columnas
df = clean_column_names(df)

# Verificación de columnas esenciales
check_columns(df, ['value', 'date'])

# Eliminar filas nulas
log("🧼 Eliminando filas con valores nulos...")
df_clean = df.dropna()
log(f"✅ Dimensiones tras eliminar nulos: {df_clean.shape}")

# Filtrar outliers con IQR
log("📦 Aplicando método IQR para detectar outliers...")
Q1 = df_clean['value'].quantile(0.25)
Q3 = df_clean['value'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
df_clean = df_clean[(df_clean['value'] >= lower) & (df_clean['value'] <= upper)]
log(f"✅ Dimensiones tras eliminar outliers: {df_clean.shape}")

# Convertir fechas
log("🗓️ Convirtiendo columna 'date' a formato datetime...")
try:
    df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
    df_clean = df_clean.dropna(subset=['date'])
except Exception as e:
    log(f"⚠️ Error al convertir fechas: {e}")
    sys.exit(1)

# Guardar archivo limpio
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df_clean.to_csv(OUTPUT_PATH, index=False)
log(f"📁 Datos limpios guardados en: {OUTPUT_PATH}", "✅")
