import pandas as pd

# Cargar el CSV
df = pd.read_csv('data/stations_espana.csv')

# Mostrar las primeras filas para verificar columnas
print(df.head())

# Filtrar filas donde la elevación sea menor a 50
df_filtrado = df[df['elevation'] < 50]

# Verificar si se encontraron estaciones filtradas
if not df_filtrado.empty:
    print(f"✅ Se encontraron {len(df_filtrado)} estaciones con elevación < 50 m.")
    df_filtrado.to_csv('data/stations_espana_filtrado.csv', index=False)
    print("💾 Archivo guardado como: data/stations_espana_filtrado.csv")
else:
    print("⚠️ No se encontraron estaciones con elevación menor a 50 m.")