#  README: Wind Power Production Analysis using the ESIOS API 🌍⚡️

##  Overview
This project uses a Python script named **`código_completo.py`** to extract, clean, and analyze hourly wind power **forecast and real production data** from the **ESIOS (REE)** API in Spain. It includes interpolation, outlier detection, correlation analysis, and multiple static and interactive visualizations. The latest version incorporates **daily energy aggregation**, **forecast error metrics**, and **comparisons with external data sources (Zona 7 – Castilla-La Mancha)**.

##  Project Structure
```
wind-analysis/
├── código_completo.py         # Main script 
├── README_EN_Codigo_Completo.md   # Documentation (this file)
├── WIND_DATAv2.xlsx           # Cleaned and normalized dataset
├── forecast_vs_real_time.html      # Interactive time series visualization
└── forecast_vs_real_scatter.html   # Interactive correlation visualization
├── dashboard_eolico_completo.html   # Full interactive dashboard
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

## Script Workflow

### 1. Data Extraction 📥
- Indicator **541** → Forecasted wind power
- Indicator **551** → Actual wind power production
- External dataset for **Zone 7 (Castilla-La Mancha)** obtained from `https://apidatos.ree.es/`

### 2. Preprocessing 🧼
- Merge dataframes and convert timestamps
- Interpolate missing values
- Detect and remove outliers using the Interquartile Range (IQR)
- Normalize values: forecast ÷ 4, real ÷ 12
- Set future production values to zero

### 3. Daily Aggregation & Error 🧮
- Aggregates daily forecast and real production
- Calculates **daily forecast error**: forecast − real

### 4. Visualization Outputs 📊 

####  Static Plots (Matplotlib)
- Forecast vs Real (scatter + regression)
- Daily comparison bars
- Comparative line plot with Zone 7 data

####  Interactive Plots (Plotly)
- **Time series**: Forecast vs Real
- **Scatter plot** with regression line
- **Daily bar chart**: Forecast vs Real
- **Error bar plot**: Daily error
- **Comparative line plot**: Forecast, Real, Zone 7 (from another team)
- **Full interactive dashboard** in `dashboard_eolico_completo.html`

### 5. Dashboard Summary 🌐

| Visualization | Description |
|---------------|-------------|
| `dashboard_eolico_completo.html` | Interactive 5-panel dashboard: includes forecast vs real, error, daily bars, and comparison with external Zone 7 data |

##  Academic Notes
This project exemplifies real-world applications in:
- **Energy Analytics**
- **API Data Collection**
- **Statistical Cleaning**
- **Daily Aggregation & Comparison**
- **Scientific Visualization**

It is particularly useful for students and professionals in **Energy Engineering**, **Environmental Sciences**, **Data Science**, and **Applied Statistics**.

You may verify official data on the REE portal:  
[https://www.esios.ree.es/es/analisis/551](https://www.esios.ree.es/es/analisis/551)

## License & Credits
For academic use only.  
Author: *[Grupo2]*  
University: *[Universidad Politécnica de Madrid]*  
Course: *[Data analysis]*
