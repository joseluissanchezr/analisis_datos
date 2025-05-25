import requests
import json
import pandas as pd
from datetime import datetime as dt

# Geo_id per region according to the REE API:
# https://www.ree.es/es/datos/apidatos
# ───────────────────────────────────────────────────────────────────────────
# 1. Dictionary REGIONS  →  readable key  →  API id
# ───────────────────────────────────────────────────────────────────────────
REGIONES = {
    "Andalucía": 4,
    "Aragón": 5,
    "Cantabria": 6,
    "Asturias": 11,
    "Castilla y León": 8,
    "Castilla-La Mancha": 7,
    "Cataluña": 9,
    "Comunidad Valenciana": 15,
    "Extremadura": 16,
    "Galicia": 17,
    "Madrid": 8752,
    "Murcia": 21,
    "Navarra": 14,
    "País Vasco": 10,
    "La Rioja": 20,
    "Islas Baleares": 8743,
    "Islas Canarias": 8742,
    "Ceuta": 8744,
    "Melilla": 8745,
    "Península": 8741,
}

# ───────────────────────────────────────────────────────────────────────────
# 2. Interactive selection (region + dates)
# ───────────────────────────────────────────────────────────────────────────
print("╔══════════════════════════════════════════╗")
print("║   Available Regions (geo_limit=ccaa)     ║")
print("╚══════════════════════════════════════════╝")
for n, reg in enumerate(REGIONES, 1):
    print(f"{n:>2}. {reg}")

# --- Select region ---
while True:
    try:
        idx = int(input("\nNumber of desired region: "))
        region_name = list(REGIONES)[idx - 1]
        geo_id = REGIONES[region_name]
        break
    except (ValueError, IndexError):
        print("⛔ Invalid choice, try again…")

# --- Date input ---
def ask_date(prompt):
    while True:
        try:
            txt = input(prompt)
            return dt.strptime(txt.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            print("⛔ Invalid format. Example: 2019-01-01 00:00")

start = ask_date("\nStart date (YYYY-MM-DD HH:MM): ")
end   = ask_date("End date   (YYYY-MM-DD HH:MM): ")
if end <= start:
    raise ValueError("End date must be after the start date.")

print(f"\n▶ Region: {region_name}  (geo_id = {geo_id})")
print(f"▶ Period: {start}  →  {end}\n")

# ───────────────────────────────────────────────────────────────────────────
# 3. API call function (daily granularity)
# ───────────────────────────────────────────────────────────────────────────
def get_gen(geo_id, start_date, end_date):
    url = "https://apidatos.ree.es/es/datos/generacion/estructura-generacion"

    headers = {
        "Accept": "application/json",
    }

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "time_trunc": "day",
        "geo_limit":  "ccaa",
        "geo_id": geo_id
    }

    response = requests.get(url, headers=headers, params=params)
    print(response.url)
    
    if response.status_code != 200:
        print(f"⛔ Error {response.status_code}")
        print(response.text)
        return pd.DataFrame()  # <- Return empty DataFrame on failure

    data = response.json()

    # Extract generation data
    rows = []
    for technology in data["included"]:
        name = technology["attributes"]["title"]
        for v in technology["attributes"]["values"]:
            rows.append({
                "datetime": v["datetime"],
                "value": v["value"],
                "percentage": v["percentage"],
                "technology": name
            })

    return pd.DataFrame(rows)

# Call API
df = get_gen(geo_id, start, end)

if df.empty:
    print("❗ No data found. Please verify your input.")
else:
    print(df.head())
    # Format dates to string
    start_str = start.strftime("%Y%m%d")
    end_str   = end.strftime("%Y%m%d")

    # Export to Excel
    archivo_excel = f"generacion_{region_name.replace(' ', '_').lower()}_{start_str}_{end_str}.xlsx"
    df.to_excel(archivo_excel, index=False)
    print(f"✅ Data saved to: {archivo_excel}")
