#  README: Wind Power Production Analysis using the ESIOS API

##  Overview
This project is a Python script designed to **download, process, clean, and analyze** wind power **forecast and actual production data** in Spain. It utilizes the **ESIOS (REE)** API, fills in missing data through interpolation, removes outliers, and generates **interactive plots** and **correlation analysis** between forecasted and real wind power.

##  Project Structure
```
wind-analysis/
├── wind_data.py              # Main script
├── README.md                 # Documentation (this file)
├── WIND_DATAv2.xlsx          # Excel file with cleaned data
├── forecast_vs_real_time.html      # Interactive time series plot
└── forecast_vs_real_scatter.html   # Interactive correlation plot
```

##  Requirements
- Python 3.7+
- Required libraries:
```bash
pip install pandas requests matplotlib seaborn plotly openpyxl
```

##  How to Run
1. **Insert your ESIOS API token** into the `TOKEN = '...'` field in `wind_data.py`.  
   You can obtain a free token at <https://www.esios.ree.es/>.

2. Run the script:
```bash
python wind_data.py
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
You can contrast this information in this link:
https://www.esios.ree.es/es/analisis/551?vis=1&start_date=03-03-2023T00%3A00&end_date=05-03-2023T23%3A55&compare_start_date=02-03-2023T00%3A00&groupby=hour&compare_indicators=541

This project demonstrates skills in **API usage**, **energy data analysis**, and **scientific visualization**.  
Applicable in Energy Engineering, Environmental Sciences, Applied Statistics, and Data Science.

## License & Credits
For academic use only.  
Author: *[Grupo2]*  
University: *[Universidad Politécnica de Madrid]*  
Course: *[Data analysis]*