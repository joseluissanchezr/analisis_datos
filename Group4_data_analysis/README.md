# 🌬️ Análisis de Datos de Viento Marítimo (NOAA)

Este repositorio contiene un proyecto desarrollado dentro del curso de Data Analysis, enfocado en la extracción, procesamiento y análisis de datos de viento marítimo proporcionados por la API pública del NOAA - National Data Buoy Center. El análisis se centra en estaciones ubicadas en proximidad a las costas españolas.

⚠️ **Nota:** Aunque el análisis se planteó originalmente para estaciones ubicadas en las costas españolas, se utilizó una estación cercana a **Miami (Florida, EE.UU.)** debido a la **falta de disponibilidad de datos detallados en tiempo real** para España dentro de la fuente NOAA.

---

## 📌 Objetivos del proyecto

- Automatizar la descarga de observaciones de viento desde NOAA
- Limpiar y transformar los datos crudos para análisis técnico
- Visualizar comportamientos, distribuciones y patrones horarios
- (Opcional) Estudiar correlaciones entre fuentes como AEMET, ESIOS, NOAA

## 🗂️ Estructura del repositorio

```
Proyecto_Data_Analysis/
│
├── data/               # Archivos descargados (crudos y limpios)
├── scripts/            # Scripts Python: extracción, limpieza, visualización
├── figures/            # Gráficas generadas
├── notebooks/          # (Opcional) Jupyter Notebooks
└── README.md           # Descripción general del proyecto
```
## 🧠 Descripción de los scripts

### 🔹 `extract_noaa_api.py`
Consulta los datasets disponibles desde la API del NOAA y guarda su descripción en `data/noaa_datasets.csv`. Es útil para explorar qué fuentes de datos están disponibles y con qué cobertura.

### 🔹 `noaa_wind_miami_2015_2023.py`
Extrae las observaciones de **velocidad media mensual del viento** para la estación NOAA de Miami (2015–2023) y guarda los datos crudos en `data/noaa_wind_miami_2015_2023.csv`.

### 🔹 `clean_wind_data.py`
Limpia el archivo anterior:
- Elimina registros nulos
- Filtra outliers 
- Convierte fechas
- Estándariza columnas  
Guarda el archivo limpio en `data/noaa_wind_miami_cleaned.csv`.

### 🔹 `get_top_wind_speed.py`
Extrae para cada mes entre 2015 y 2023 el día con la mayor velocidad media del viento.  
Guarda los picos mensuales en `data/noaa_top_speed_monthly.csv`.


## 🖼️ Visualizaciones generadas y su utilidad

El script `visualize_wind_data.py` genera los siguientes gráficos automáticamente:

1. **Gráfico de líneas – Evolución temporal**  
   Muestra cómo varía la velocidad del viento a lo largo del tiempo. Útil para ver la tendencia general.

2. **Histograma – Distribución de velocidades**  
   Representa la frecuencia de distintas velocidades del viento. Ayuda a identificar valores típicos o extremos.

3. **Boxplot mensual – Variación por mes**  
   Muestra la dispersión y los valores atípicos por cada mes. Útil para detectar estacionalidad.

4. **Violin plot mensual – Distribución y densidad**  
   Visualiza la distribución mensual con densidad y simetría. Más rico que el boxplot para datos asimétricos.

5. **Evolución mensual (Año-Mes)**  
   Muestra la media mensual agrupada por año. Permite detectar tendencias de largo plazo.

6. **Heatmap hora vs mes**  
   Visualiza la velocidad media del viento por hora del día y mes. Útil para ver patrones horarios estacionales.

7. **Media móvil (30 días)**  
   Suaviza las fluctuaciones diarias para mostrar la tendencia a corto y medio plazo.

---

## 🔧 Tecnologías utilizadas

- Python 3.x
- Requests
- Pandas
- Matplotlib
- Seaborn

## 🚀 Cómo ejecutar

1. Instalar dependencias (solo si usas entorno local):

```bash
pip install requests pandas matplotlib seaborn
```

2. Ejecutar scripts desde la raíz del proyecto:

```bash
# 1. Obtener metadatos (opcional)
python Group4_data_analysis/scripts/extract_noaa_api.py

# 2. Extraer datos de viento crudos
python Group4_data_analysis/scripts/noaa_wind_miami_2015_2023.py

# 3. Limpiar los datos
python Group4_data_analysis/scripts/clean_wind_data.py

# 4. Obtener máximos mensuales de viento
python Group4_data_analysis/scripts/get_top_wind_speed.py

# 5. Generar visualizaciones
python Group4_data_analysis/scripts/visualize_wind_data.py

```

## 🔗 Fuente de datos

Datos obtenidos desde:  
🌐 [NOAA National Data Buoy Center](https://www.ndbc.noaa.gov/)

---

📌 Proyecto desarrollado por:   
**Juan Cervantes**  
**Karen Lopez**  
**Alba Arnoso**  
**Marouan Berkouat**  
**Veronica Moreno**  
**Daouda Keita**  
Máster en Ingeniería de la Energía · UPM  
Año académico 2024-2025
