# analisis_datos
Este es el repositorio oficial de la asignatura "ANALISIS DE DATOS" del Master Universitario de Ingeniería de la Energía MUIE

# Grupo 4 Codigo 

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

Please wait for the others programs ! 
