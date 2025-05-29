# 🌬️ Análisis de Datos de Viento Marítimo (NOAA)

Este repositorio contiene un proyecto desarrollado dentro del curso de Data Analysis, enfocado en la extracción, procesamiento y análisis de datos de viento marítimo proporcionados por la API pública del NOAA - National Data Buoy Center. El análisis se centra en estaciones costeras.

⚠️ **Nota:** Aunque el análisis se planteó originalmente para estaciones ubicadas en las costas españolas, se utilizó una estación cercana a **Miami (Florida, EE.UU.)** debido a la **falta de disponibilidad actual de datos** para España dentro de la fuente NOAA.

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
└── README.md           # Descripción general del proyecto
```
## 🧭 Descripción del flujo del proyecto

1. **Consulta de estaciones españolas**  
   Se utilizó el script `Noaa_wind_stations_Spain.py` para obtener las estaciones registradas por NOAA en España. El resultado se guardó en el archivo `stations_espana.csv`.

2. **Filtrado por elevación**  
   Con el script `Noaa_wind_stations_Spain_filtrado.py` se filtraron las estaciones con elevación menor a 50 metros, generando un archivo también llamado `stations_espana_filtrado.csv` actualizado.

3. **Problemas con datos actuales**  
   Al intentar consultar información para las estaciones filtradas, se observó que **no hay datos recientes disponibles en NOAA**. Por este motivo, se seleccionó como alternativa una estación activa ubicada en **Miami** para continuar el análisis.

4. **Extracción de datos históricos**  
   Primero, con `extract_noaa_api.py` se listaron los datasets disponibles que se pueden visualizar en `noaa_datasets.csv`. 
   Luego, se usó `noaa_wind_miami_2015_2023.py` para consultar los datos GSOM (resumen mensual) de 2015 a 2023, generando un archivo `noaa_wind_miami_2015_2023.csv`.

5. **Limpieza de datos**  
   El script `clean_wind_data.py` se encargó de:
   - Eliminar espacios y valores nulos
   - Filtrar valores atípicos usando el método IQR
   - Convertir la columna `date` al formato `datetime`
   - Guardar el dataset limpio en `noaa_wind_miami_cleaned.csv`

6. **Visualización de resultados**  
   Finalmente, `visualize_wind_data.py` genera múltiples gráficos explicativos sobre el comportamiento del viento, los cuales se detallan a continuación.

---

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
---
## Análisis correlación existente entre el grupo 4 y el grupo 1.

El script `CorrelationWithGropu1.py' tiene como objetivo estudiar la correlación entre la velocidad del viento registrada en Miami (datos de NOAA) hecho por el grupo 4 y la generación eléctrica de origen eólico en diferentes comunidades autónomas de España (datos del operador REE), dentro de un mismo periodo hecho por el grupo 1. El funcionamiento es el siguiente:

1. El usuario debe ejecutar primero el script del Grupo 1 (request_data_grupo1.py), que solicita: Selección de una comunidad autónoma e introducción de un rango de fechas con el formato: YYYY-MM-DD HH:MM. Se ha introducido el script del grupo 1 tambien en el script del grupo 4 para que ante posibles cambios realizados por el otro grupo, no afecte a este análisis.
2. El script del Grupo 1 descargará un archivo .xlsx con los datos de generación y lo guardará en la raíz del proyecto.
3. Despues se ejecuta el script principal de correlación (CorrelationWithGroup1.py) que realiza lo siguiente: Busca automáticamente el archivo de generación creado más reciente (generacion_...xlsx)
2. Detecta la región a partir del nombre del archivo Excel generado.
3. Mueve y organiza el archivo generado a la carpeta Group4_data_analysis/data para mantener una estructura limpia.
4. Carga y transforma los datos de viento de NOAA (Miami, 2015–2023), agrupándolos por mes.
5. Filtra los datos de REE para conservar únicamente los valores de generación eólica y los agrupa también por mes.
6. Une ambos datasets por mes y calcula el coeficiente de correlación de Pearson (r).
7. Exporta en la ruta Group4_data_analysis/data un archivo .csv con los valores combinados.
8. Exporta en la ruta Group4_data_analysis/figures una imagen .png con un gráfico de dispersión y la recta de regresión.
Ambos archivos se nombran automáticamente según la comunidad analizada. El script muestra en consola el valor de correlación obtenido. Esto indica si existe (o no) una relación lineal entre las dos fuentes de datos.
**Ejemplo**: Se ha realizado el análisis con la Comunidad de Madrid en un periodo de fechas de 2022-02-01 00:00  →  2022-10-31 23:00 y se ha observado una correlación entre viento (Miami) y generación eólica (Madrid): 0.2695. Eso significa que existe una correlación débil y positiva entre ambas variables.Este valor no implica causalidad, ya que Miami y Madrid no tienen conexión meteorológica directa.La dispersión de los puntos en la imagen guardada lo demuestra: no siguen una línea clara, aunque haya cierta pendiente positiva.
**Interpretación**: Dado que las regiones analizadas están separadas geográficamente por miles de kilómetros y no comparten sistemas meteorológicos directos, no se espera una relación causal entre ambas variables. Este resultado sirve como validación del procedimiento técnico (limpieza, integración y análisis de datos), más que como hallazgo climático.
_______________________________________

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
