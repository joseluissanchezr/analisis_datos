import os
import glob
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# 1. Buscar archivo Excel generado
# -------------------------
print("📁 Buscando archivo Excel generado por el Grupo 1...")
archivos = glob.glob("generacion_*.xlsx")
if not archivos:
    print("❌ No se encontró ningún archivo Excel.")
    print("ℹ️  Asegúrate de haber ejecutado primero el script:")
    print("    ➤ Group4_data_analysis/scripts/request_data_grupo1.py")
    print("    ✅ Introduce región y fechas cuando se te pidan.")
    exit()

archivo_generado = max(archivos, key=os.path.getctime)
print(f"✅ Archivo encontrado: {archivo_generado}")

# Extraer nombre de región del nombre del archivo
nombre_base = os.path.basename(archivo_generado)
try:
    region = nombre_base.split("_")[1]
    print(f"🌍 Región detectada: {region}")
except IndexError:
    region = "desconocida"
    print("⚠️ No se pudo extraer la región. Usando 'desconocida'.")

# -------------------------
# 2. Mover archivo a carpeta destino
# -------------------------
destino = "Group4_data_analysis/data"
os.makedirs(destino, exist_ok=True)
archivo_destino = os.path.join(destino, nombre_base)

try:
    if os.path.exists(archivo_destino):
        os.remove(archivo_destino)
except PermissionError:
    print(f"🔒 El archivo {archivo_destino} está abierto. Ciérralo e inténtalo de nuevo.")
    exit()

shutil.move(archivo_generado, archivo_destino)
print(f"📦 Archivo movido a: {archivo_destino}")

# -------------------------
# 3. Cargar y procesar datos
# -------------------------
print("🌬️ Cargando datos de viento NOAA...")
df_wind = pd.read_csv("Group4_data_analysis/data/noaa_wind_miami_2015_2023.csv")
df_wind['date'] = pd.to_datetime(df_wind['date'])
df_wind = df_wind[['date', 'value']].rename(columns={'value': 'wind_speed'})
df_wind['month'] = df_wind['date'].dt.to_period('M')
df_wind = df_wind.groupby('month')['wind_speed'].mean().reset_index()
df_wind['date'] = df_wind['month'].dt.to_timestamp()
df_wind.drop(columns='month', inplace=True)

print("⚡ Cargando datos de generación eléctrica...")
df_energy = pd.read_excel(archivo_destino)

if 'datetime' not in df_energy.columns:
    raise ValueError("❌ No se encontró la columna 'datetime' en el Excel.")

df_energy['datetime'] = df_energy['datetime'].astype(str).str.strip()
df_energy['datetime'] = pd.to_datetime(df_energy['datetime'], errors='coerce', utc=True)
df_energy['datetime'] = df_energy['datetime'].dt.tz_convert(None)

if df_energy['datetime'].isna().all():
    raise ValueError("❌ Falló la conversión a datetime.")

df_energy = df_energy[df_energy['technology'].str.lower() == 'eólica']
df_energy['month'] = df_energy['datetime'].dt.to_period('M')
df_energy = df_energy.groupby('month')['value'].sum().reset_index()
df_energy['date'] = df_energy['month'].dt.to_timestamp()
df_energy.drop(columns='month', inplace=True)

# -------------------------
# 4. Calcular correlación
# -------------------------
df = pd.merge(df_wind, df_energy, on='date', how='inner')
df.rename(columns={'value': 'eolic_generation'}, inplace=True)
correlacion = df['wind_speed'].corr(df['eolic_generation'])
print(f"\n📊 Correlación entre viento (Miami) y generación eólica ({region.title()}): {correlacion:.4f}")

# -------------------------
# 5. Guardar CSV
# -------------------------
csv_path = f"Group4_data_analysis/data/correlacion_resultadogrupo1_{region.lower()}.csv"
df.to_csv(csv_path, index=False)
print(f"📄 Datos exportados a: {csv_path}")

# -------------------------
# 6. Guardar gráfico
# -------------------------
figures_path = "Group4_data_analysis/figures"
os.makedirs(figures_path, exist_ok=True)
png_path = os.path.join(figures_path, f"correlacion_resultadogrupo1_{region.lower()}.png")

x = df['wind_speed']
y = df['eolic_generation']
m, b = np.polyfit(x, y, 1)

plt.figure(figsize=(8, 5))
plt.scatter(x, y, alpha=0.7, label="Datos reales")
plt.plot(x, m * x + b, color='red', label=f"Recta de regresión (r = {correlacion:.2f})")
plt.title(f"Correlación: Viento en Miami vs. Generación Eólica en {region.title()}")
plt.xlabel("Velocidad del viento (m/s)")
plt.ylabel("Generación eólica (MWh)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(png_path)
print(f"🖼️ Gráfico guardado como: {png_path}")
plt.show()







