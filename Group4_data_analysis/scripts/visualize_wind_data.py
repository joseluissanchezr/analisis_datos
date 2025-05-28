import pandas as pd
import matplotlib.pyplot as plt

# Verificar si seaborn está instalado
try:
    import seaborn as sns
except ImportError:
    print("❌ La librería 'seaborn' no está instalada.")
    print("👉 Por favor, ejecuta: pip install seaborn")
    exit()

# Cargar datos limpios
file_path = "Group4_data_analysis/data/noaa_wind_miami_cleaned.csv"
df = pd.read_csv(file_path)

# Asegurarse de que la fecha esté en formato datetime
df['date'] = pd.to_datetime(df['date'])

# Crear carpeta de salida dentro de Group4_data_analysis
output_folder = "Group4_data_analysis/figures"

# Configurar estilo visual
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# 1. Gráfica de líneas: evolución temporal
plt.figure()
sns.lineplot(x="date", y="value", data=df)
plt.title("Evolución de la velocidad del viento en Miami (2015-2023)")
plt.xlabel("Fecha")
plt.ylabel("Velocidad del viento (m/s)")
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_linea_evolucion.png")
print("✅ Gráfico de líneas guardado.")

# 2. Histograma: distribución de velocidades
plt.figure()
sns.histplot(df["value"], bins=30, kde=True, color='skyblue')
plt.title("Distribución de la velocidad del viento (2015-2023)")
plt.xlabel("Velocidad del viento (m/s)")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_histograma_distribucion.png")
print("✅ Histograma guardado.")

# 3. Boxplot mensual: variación por mes
plt.figure()
df["month"] = df["date"].dt.month
sns.boxplot(x="month", y="value", data=df, hue="month", palette="Set2", legend=False)
plt.title("Distribución mensual de la velocidad del viento")
plt.xlabel("Mes")
plt.ylabel("Velocidad del viento (m/s)")
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_boxplot_mensual.png")
print("✅ Boxplot mensual guardado.")

# 4. Violin plot mensual: distribución y densidad por mes
plt.figure()
sns.violinplot(x="month", y="value", data=df, hue="month", palette="muted", legend=False)
plt.title("Distribución mensual del viento (Violin Plot)")
plt.xlabel("Mes")
plt.ylabel("Velocidad del viento (m/s)")
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_violin_mensual.png")
print("✅ Violin plot mensual guardado.")

# 5. Media mensual agrupada por año-mes
df["year_month"] = df["date"].dt.to_period("M").astype(str)
monthly_avg = df.groupby("year_month")["value"].mean().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(
    x="year_month",
    y="value",
    data=monthly_avg,
    marker="o",
    linewidth=2.5,
    color="royalblue"
)
xticks_to_show = monthly_avg["year_month"].iloc[::6]
plt.xticks(
    ticks=range(0, len(monthly_avg), 6),
    labels=xticks_to_show,
    rotation=45
)
plt.title("Velocidad media mensual del viento (2015–2023)")
plt.xlabel("Año-Mes")
plt.ylabel("Velocidad del viento (m/s)")
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_media_mensual_evolucion_mejorado.png")
print("✅ Media mensual del viento (mejorada) guardada.")

# 6. Heatmap hora-mes: velocidad media por hora y mes
plt.figure(figsize=(10, 6))
df["hour"] = df["date"].dt.hour
heatmap_data = df.pivot_table(values="value", index="hour", columns="month", aggfunc="mean")
sns.heatmap(heatmap_data, cmap="coolwarm")
plt.title("Velocidad media del viento por hora y mes")
plt.xlabel("Mes")
plt.ylabel("Hora del día")
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_heatmap_hora_mes.png")
print("✅ Heatmap hora-mes guardado.")

# 7. Media móvil de 30 días
plt.figure(figsize=(12, 6))
df_sorted = df.sort_values("date")
df_sorted["rolling_mean"] = df_sorted["value"].rolling(window=30).mean()
sns.lineplot(data=df_sorted, x="date", y="rolling_mean", color="darkgreen")
plt.title("Tendencia suavizada (Media móvil 30 días)")
plt.xlabel("Fecha")
plt.ylabel("Velocidad del viento (m/s)")
plt.tight_layout()
plt.savefig(f"{output_folder}/plot_media_movil_30dias.png")
print("✅ Gráfico de media móvil guardado.")
