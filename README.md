# Analisis_datos
Este es el repositorio oficial de la asignatura "ANALISIS DE DATOS" del Master Universitario de Ingeniería de la Energía MUIE

# Hechos Relevantes. 
Extrae automa ticamente los Hechos Relevantes del ultimo mes que pueden afectar al mercado ele ctrico en https://umm.omie.es/electricity-list

# Mercado diario “Day ahead “incluyendo ofertas”
Ficheros mensuales con curvas agregadas de oferta y demanda del mercado diario “Day ahead “incluyendo ofertas” para mercado electrico contenidas en los archivos “curva_pbc_uof”  https://www.omie.es/en/file-accesslist#Mercado%20DiarioCurvas?parent=Mercado%20Diario 

# Mercado diario “intra-day“ incluyendo ofertas
Ficheros mensuales con curvas agregadas de oferta y demanda del mercado diario “intra-day“ incluyendo ofertas para mercado electrico contenidas en los archivos  “curva_pibc_uof”

# Indisponibilidades del u ltimo mes. “indisp2024_0X”

## Overview

This repository contains two Python scripts: `extract_data_grupo_4.py`, `clean_data_grupo_4.py` and `visualize_data_grupo_4.py`. These scripts are designed to extract data related to the unavailability declarations of Spanish bid units from a specified website and then visualize the data using bar charts.

### `extract_data_grupo_4.py`

This script downloads the latest unavailability declarations from the OMIE website, extracts any zip files, and saves the data in a local directory.

### `clean_data_grupo_4.py`

This script clean the wrong data contained in the files

### `visualize_data_grupo_4.py`

This script reads the downloaded data files, analyzes them to find the most common values in a specific column, and visualizes these values using bar charts.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/joseluissanchezr/analisis_datos.git
   ```
   ```bash
   cd analisis_datos
   ```
   
2. Move to source code : 
   ```bash
   cd grupo_4
   ```

## Usage

### Extract Data

To download and extract the unavailability data, run the following command:

```bash
python extract_data_grupo_4.py
```

This will create a data directory (if it does not already exist) and download the latest unavailability data files from the OMIE website.

### Visualize Data

To analyze and visualize the data, run the following command:

```bash
python visualize_data_grupo_4.py <top_n>
```

Replace <top_n> with the number of top occurrences you want to visualize. For example:

```bash
python visualize_data_grupo_4.py 30
```

![Exemple_of_usage](exemple_of_visualisation_30.png)

Please wait for the others programs ! 

# 🌬️ Análisis de Datos de Producción Eólica - Grupo 2

Este proyecto realiza un análisis exploratorio y visualización de los datos de **producción eólica en España** a través de la API de [ESIOS](https://www.esios.ree.es/), utilizando Python y diversas bibliotecas de análisis y visualización de datos.

---

## 🧰 Tecnologías y Librerías Utilizadas

- Python 3
- requests
- pandas
- numpy
- matplotlib
- seaborn
- plotly

---

## 🔑 Requisitos Previos

1. Tener una clave de API válida de ESIOS.
2. Instalar las siguientes dependencias (puedes usar `pip`):

```bash
pip install requests pandas numpy matplotlib seaborn plotly
```

---

## 🚀 Uso del Notebook

1. **Configura tu API Token** en la celda correspondiente del notebook:
    ```python
    TOKEN = 'tu_token_aquí'
    ```

2. **Introduce las fechas de inicio y fin** para la consulta de datos cuando se solicite en el notebook (formato `dd/mm/yyyy`).

---

## 📥 Descarga de Datos desde la API

Se realiza una conexión a la API de ESIOS para obtener los siguientes datos:
- Previsión diaria de generación eólica
- Producción real de energía eólica

También se define una función general para facilitar estas descargas a partir de los identificadores de la API.

---

## 🧹 Limpieza y Procesamiento de Datos

Los datos crudos son tratados para:
- Convertir formatos de fecha y hora
- Unificar las fuentes de datos
- Eliminar entradas nulas o inconsistentes

---

## 💾 Exportación de Datos a Excel

Una vez procesados y limpiados los datos, se exportan a un archivo `.xlsx`, permitiendo su análisis posterior fuera de Python.

---

## 📈 Análisis Estadístico y Visual

Se realizan distintos análisis y visualizaciones:
- Correlación entre la previsión y la producción real
- Agrupación diaria de datos
- Cálculo del error diario absoluto
- Gráficas de barras y líneas para comparar tendencias

---

## 🔄 Comparativa con el Grupo 1 (Zona 7 - Castilla-La Mancha)

Se obtienen y analizan datos adicionales correspondientes a la **Zona 7 (Grupo 1)**, una región concreta (Castilla-La Mancha), para comparar con los datos globales.

Esto permite examinar:
- Similitudes y diferencias regionales
- Desviaciones entre previsión nacional y producción regional

---

## 📉 Comparación Visual con Datos del Grupo 1

Se generan gráficas superpuestas para comparar:
- Previsión nacional vs. producción real
- Producción real vs. generación regional (Zona 7)

---

## 📊 Dashboard Interactivo en Jupyter

Se crea un dashboard dinámico con Plotly que permite explorar:

- Producción real vs previsión
- Generación en Zona 7
- Errores y correlaciones
- Evolución temporal

Este dashboard se puede visualizar directamente dentro del entorno Jupyter Notebook.

---

## 👨‍💻 Autor

Este notebook fue desarrollado por **Javier** como parte de un trabajo de la asignatura Data Analysys.

---

## 📎 Licencia

Este proyecto está bajo licencia MIT. Puedes usarlo, modificarlo y compartirlo libremente, dando el crédito correspondiente.
