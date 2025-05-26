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
python scripts/extract_noaa_data.py
python scripts/clean_noaa_data.py
python scripts/visualize_wind_data.py
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
