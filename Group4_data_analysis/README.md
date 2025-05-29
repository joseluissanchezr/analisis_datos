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

## Informe de correlación entre el Grupo 2 y el Grupo 4

###  1. Objetivo del análisis

El propósito de este análisis es evaluar la **correlación entre la velocidad del viento en Miami** (obtenida desde NOAA, Grupo 4) y la **producción eólica real en España** (obtenida desde la API de ESIOS, Grupo 2). Se ha tomado como año de referencia **2023**, ya que es el año más reciente disponible en ambas fuentes de datos.

###  2. Problema encontrado con los datos originales

Inicialmente, los datos del Grupo 2 y del Grupo 4 **no coincidían en el rango temporal**, lo que impedía cualquier intento de análisis conjunto. En concreto:

- El código original del Grupo 2 permitía obtener datos solo de años completos.
- Los datos disponibles más antiguos no coincidían con los del Grupo 4.

###  3. Solución aplicada

Para resolver esta incompatibilidad:

- Se **adaptó el código del Grupo 2** para descargar únicamente datos correspondientes a **2023**, garantizando así su alineación temporal con los datos de velocidad del viento del Grupo 4.
- Este nuevo script se ha nombrado como `download_clean_wind_data_group2.py` y se ha guardado en la carpeta `Group4_data_analysis/scripts`.
- El archivo resultante con los datos procesados se ha guardado como `WIND_VALID_DATA.xlsx` en `Group4_data_analysis`.

###  4. Cálculo de la correlación

Para analizar la relación entre las dos variables se ha creado el script:

- `correlation_group2_group4.py`, que:
  - Carga los datos mensuales medios de ambas fuentes (producción eólica real y velocidad del viento).
  - Realiza una **media mensual** de cada variable.
  - Fusiona los dos DataFrames por fechas comunes.
  - Calcula el **coeficiente de correlación de Pearson**.
  - Genera una **gráfica de dispersión con línea de regresión** para representar visualmente la relación.
  - La gráfica se guarda como imagen en `Group4_data_analysis/figures/correlation_group2_group4_2023.png`.

###  5. Resultados obtenidos

La gráfica muestra la relación entre la **velocidad media del viento mensual en Miami** y la **producción eólica mensual en España**, ambas correspondientes al año **2023**:
- El coeficiente de correlación de Pearson fue **r = -0.52**, lo que indica una **correlación moderadamente negativa**.

**📉 Interpretación:**

- A mayor velocidad del viento en Miami, tiende a observarse una **menor producción eólica en España**.
- Aunque no se trata de una relación causal, este patrón sugiere que existe una cierta **anticorrelación climática** entre ambas regiones, al menos en el año estudiado.
- La nube de puntos presenta una dispersión apreciable, lo que implica que **la relación no es perfecta ni totalmente lineal**, pero sí relevante desde un punto de vista exploratorio.

**🗂 Archivos generados:**

- Datos limpios del Grupo 2: `Group4_data_analysis/WIND_VALID_DATA.xlsx`
- Gráfico de correlación: `Group4_data_analysis/figures/correlation_group2_group4_2023.png`
- Script de descarga y limpieza: `Group4_data_analysis/scripts/download_clean_wind_data_group2.py`
- Script de correlación: `Group4_data_analysis/correlation_group2_group4.py`

### ✅ Conclusión

Gracias a la limpieza y alineación temporal de los datos, se ha podido ejecutar un análisis de correlación útil entre las fuentes del Grupo 2 y Grupo 4. Este trabajo no solo permite **explorar relaciones geográficas inesperadas**, sino que también demuestra la importancia del **preprocesamiento y sincronización de datos** en proyectos de análisis conjunto.



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
