#  README: Wind Power Production Analysis using the ESIOS API

##  Overview
This project is a Python script named **`codigo_completo.py`**, designed to **extract, clean, and analyze** hourly wind power **forecast and real production data** from the **ESIOS (REE)** API in Spain. It handles data interpolation, outlier removal, and correlation analysis, and generates both **static and interactive visualizations**.

##  Project Structure
```
wind-analysis/
├── código_completo.py         # Main script (Spanish title)
├── README_EN_Codigo_Completo.md   # Documentation (this file)
├── WIND_DATAv2.xlsx           # Cleaned and normalized dataset
├── forecast_vs_real_time.html      # Interactive time series visualization
└── forecast_vs_real_scatter.html   # Interactive correlation visualization
```

##  Requirements
- Python 3.7+
- Required libraries:
```bash
pip install pandas requests matplotlib seaborn plotly openpyxl
```

##  How to Run
1. **Replace the token** in the line `TOKEN = '...'` inside `código_completo.py` with your personal ESIOS API token.  
   Tokens are available for free at: [https://www.esios.ree.es/](https://www.esios.ree.es/)

2. Execute the script:
```bash
python código_completo.py
```

3. Enter the start and end dates in `dd/mm/yyyy` format when prompted.

4. The script will generate:
   - A cleaned Excel file: `WIND_DATAv2.xlsx`
   - Two interactive `.html` plots that open in your browser.

##  What the Script Does

### 1. Data Download
- Indicator **541** → forecasted wind power.  
- Indicator **551** → actual wind power production.

### 2. Preprocessing
- Converts dates to `datetime`.
- Merges both series by hour (`merge`).
- Interpolates missing data.
- Removes outliers using Interquartile Range (IQR).
- Re-interpolates after removing outliers.

### 3. Normalization and Cleaning
- Applied corrections:  
  - Forecast divided by 4.  
  - Actual production divided by 12.
- Future actual production values are set to 0 MW.

### 4. Exporting Results
- Cleaned data exported to `WIND_DATAv2.xlsx`.

### 5. Correlation Analysis
- Calculates Pearson correlation coefficient (r) between forecast and actual data.
- Generates a scatter plot with a regression line.

### 6. Interactive Visualization
- Time series plot: `forecast_vs_real_time.html`
- Scatter plot: `forecast_vs_real_scatter.html`

##  Sample Graphs Output
| File | Description |
|------|-------------|
| `forecast_vs_real_time.html` | Time series comparing forecast and actual production |
| `forecast_vs_real_scatter.html` | Correlation and trend between both variables |

##  Academic Notes
This project exemplifies real-world applications in:
- **Energy Data Analytics**
- **Time Series Processing**
- **API Integration**
- **Scientific Visualization**

It is particularly useful for students and professionals in **Energy Engineering**, **Environmental Sciences**, **Data Science**, and **Applied Statistics**.

You may verify official data on the REE portal:  
[https://www.esios.ree.es/es/analisis/551](https://www.esios.ree.es/es/analisis/551)

## License & Credits
For academic use only.  
Author: *[Grupo2]*  
University: *[Universidad Politécnica de Madrid]*  
Course: *[Data analysis]*
