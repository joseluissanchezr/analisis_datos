import requests
import pandas as pd
from datetime import datetime
import os

# ==============================
# GENERAL CONFIGURATION
# ==============================

# API Token for ESIOS (do not change)
TOKEN = '255c4529289ed8e7cfcfdc5cff2c43d0f101fe5b3adaa20273c01b0deafa80d4'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'x-api-key': TOKEN,
    'User-Agent': 'esios-api-client'
}

# Download only 2023 to match NOAA group 4 data
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

# ==============================
# FUNCTION TO FETCH DATA FROM ESIOS API
# ==============================

def get_esios_data(indicator_id, start, end):
    url = f'https://api.esios.ree.es/indicators/{indicator_id}'
    params = {
        'start_date': start.isoformat(),
        'end_date': end.isoformat(),
        'time_trunc': 'hour'
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()['indicator']['values']
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        df = df[['datetime', 'value']].rename(columns={'value': f'indicator_{indicator_id}'})
        return df
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return pd.DataFrame(columns=['datetime', f'indicator_{indicator_id}'])

# ==============================
# FETCH WIND FORECAST AND REAL GENERATION
# ==============================

print("📥 Downloading wind data from ESIOS (2023 only)...")
df_541 = get_esios_data(541, start_date, end_date)  # Wind forecast
df_551 = get_esios_data(551, start_date, end_date)  # Real wind generation

# Merge both datasets
df = pd.merge(df_541, df_551, on='datetime', how='outer').sort_values('datetime')

# ==============================
# CLEANING AND NORMALIZATION
# ==============================

# Interpolation and IQR-based outlier removal
df.set_index('datetime', inplace=True)
df.interpolate(method='linear', inplace=True)
for col in df.columns:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    df[col] = df[col].where(df[col].between(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR))
df.reset_index(inplace=True)

# Normalize for comparison
df['indicator_541'] = df['indicator_541'] / 4  # Forecast wind power
df['indicator_551'] = df['indicator_551'] / 12  # Real wind power

# Remove timezone info to be Excel-compatible
df['datetime'] = df['datetime'].dt.tz_localize(None)

# Save to Excel for correlation analysis
output_path = "Group4_data_analysis/WIND_VALID_DATA.xlsx"
os.makedirs("Group4_data_analysis", exist_ok=True)
df.to_excel(output_path, index=False)
print(f"✅ Clean wind data exported to {output_path}")



